"""Admit an actual completed First Slice and current IRO wave, per subject."""
from datetime import timedelta
import hashlib

from InvestmentResearchOrchestrator.models.enums import EvidencePayloadKind as Kind, IRORunPhase, IRORunStatus
from InvestmentResearchOrchestrator.run_coordinator import IRORunResult
from InvestmentResearchOrchestrator.validation.store import validate_evidence_store_record
from InvestmentResearchOrchestrator.validation.run import validate_iro_run
from InvestmentResearchOrchestrator.validation.plan import validate_research_plan
from InvestmentResearchOrchestrator.validation.contradiction import validate_contradiction_evaluation
from InvestmentDecisionVerticalSlice.evidence_admission import admit_iro_evidence
from KbPortfolioVerticalSlice.models import ExplicitVerticalSliceResult
from KbPortfolioVerticalSlice.validation import validate_iro_ingress
from OperationalCioCycle.semantic import strict_json, ids, keys
from OperationalCioCycle.universe import utc


def admit_first(config, first, records, now, raw_record, normalized_records, prior_snapshot):
    utc(now)
    if type(first) is not ExplicitVerticalSliceResult or first.result_kind != "success" or first.failure_code is not None or first.ingress is None:
        raise ValueError("first slice unavailable/no-change/incomplete")
    iro = first.iro_result
    if type(iro) is not IRORunResult:
        raise ValueError("actual IRO result required")
    validate_iro_run(iro.run)
    if iro.run.updated_at > now or iro.run.created_at > now:
        raise ValueError("IRO timestamp is in the future")
    if (iro.error is not None or iro.run.phase is not IRORunPhase.COMPLETED or iro.run.status is not IRORunStatus.COMPLETED or iro.escalation is not None or iro.plan is None or iro.contradiction is None):
        raise ValueError("IRO incomplete/escalated")
    validate_research_plan(iro.plan)
    validate_contradiction_evaluation(iro.contradiction)
    if iro.contradiction.unresolved or iro.contradiction.run_id != config.iro_run_id:
        raise ValueError("unresolved contradiction/run mismatch")
    if (iro.run.run_id != config.iro_run_id or first.snapshot.portfolio_snapshot_id != config.snapshot_id
            or iro.plan.run_id != config.iro_run_id or first.change_class != first.ingress.change_class):
        raise ValueError("cycle snapshot/run binding mismatch")
    validate_iro_ingress(first.ingress, run=iro.run, current_snapshot=first.snapshot, prior_snapshot=prior_snapshot, raw_record=raw_record, normalized_records=normalized_records)
    age = now - first.ingress.collected_at
    if age < timedelta(0) or age > config.freshness_max_age:
        raise ValueError("snapshot stale/future")
    if type(records) is not tuple or not records:
        raise ValueError("missing IRO evidence")
    for record in records:
        validate_evidence_store_record(record)
        if record.run_id != config.iro_run_id:
            raise ValueError("foreign evidence run")
        utc(record.stored_at)
        if record.stored_at > now or record.stored_at < iro.run.created_at:
            raise ValueError("evidence timestamp outside cycle")
        if record.collected_at is not None and (record.collected_at > now or now - record.collected_at > config.freshness_max_age):
            raise ValueError("stale/future IRO evidence")
    audits = [strict_json(r.payload) for r in records if r.payload_kind is Kind.CONTRADICTION_EVALUATION]
    if not audits:
        raise ValueError("missing/unresolved contradiction audit")
    keys(audits[-1], "attempt unresolved request_count numeric_path_status")
    if (ids(audits[-1]["unresolved"]) or audits[-1]["attempt"] != iro.re_research_attempt
            or audits[-1]["request_count"] != 0
            or audits[-1]["numeric_path_status"] != iro.contradiction.numeric_path_status.value):
        raise ValueError("missing/unresolved contradiction audit")
    if any(r.payload_kind is Kind.ESCALATION for r in records):
        raise ValueError("escalation audit blocks decision")


def subject_bundle(config, first, records, member, provider_by_committee):
    iro = first.iro_result
    units = [u for u in iro.plan.units if u.subject_id == member.subject.subject_id]
    if len(units) != 1:
        raise ValueError("missing/duplicate current subject research unit")
    unit = units[0]
    prefix = (config.iro_run_id + ":unit:" if iro.re_research_attempt == 0
        else f"{config.iro_run_id}:attempt:{iro.re_research_attempt}:unit:")
    if not unit.research_id.startswith(prefix):
        raise ValueError("research unit is not from current wave")
    index, separator, subject = unit.research_id[len(prefix):].partition(":")
    if not index.isdigit() or not separator or subject != unit.subject_id:
        raise ValueError("research unit identity grammar mismatch")
    selected = tuple(r for r in records if r.research_id == unit.research_id)
    complete = [strict_json(r.payload) for r in selected if r.payload_kind is Kind.COMPLETENESS]
    if len(complete) != 1 or any(r.payload_kind is Kind.COLLECTION_FAILURE for r in selected):
        raise ValueError("missing/duplicate completeness or collection failure")
    c = complete[0]
    keys(c, "required completed failed missing")
    required, completed = ids(c["required"]), ids(c["completed"])
    if not required or set(required) != set(completed) or ids(c["failed"]) or ids(c["missing"]):
        raise ValueError("incomplete research unit")
    if len({provider_by_committee.get(x) for x in required}) < 2 or any(x not in provider_by_committee for x in required):
        raise ValueError("Committee First requires independent configured providers")
    artifacts = [a for a in iro.freeze_artifacts if a.research_id == unit.research_id and a.attempt_index == iro.re_research_attempt]
    if {a.committee_id for a in artifacts} != set(required) or len(artifacts) != len(required):
        raise ValueError("committee prompt binding mismatch")
    for artifact in artifacts:
        if hashlib.sha256(artifact.frozen_prompt_bytes).hexdigest() != artifact.prompt_hash:
            raise ValueError("prompt hash mismatch")
        freezes = [r for r in selected if r.payload_kind is Kind.PROMPT_FREEZE and r.committee_id == artifact.committee_id]
        if len(freezes) != 1 or freezes[0].prompt_id != artifact.prompt_id or freezes[0].prompt_hash != artifact.prompt_hash:
            raise ValueError("persisted prompt provenance mismatch")
        if strict_json(freezes[0].payload) != {"attempt_index": iro.re_research_attempt, "prompt_hash": artifact.prompt_hash}:
            raise ValueError("persisted prompt attempt mismatch")
    findings = [r for r in selected if r.payload_kind is Kind.FINDING]
    if {r.committee_id for r in findings} != set(required) or len(findings) != len(required):
        raise ValueError("missing/duplicate committee finding")
    for record in findings:
        artifact = next(a for a in artifacts if a.committee_id == record.committee_id)
        if record.prompt_id != artifact.prompt_id or record.prompt_hash != artifact.prompt_hash:
            raise ValueError("finding frozen prompt provenance mismatch")
        payload = strict_json(record.payload)
        keys(payload, "subject_key finding_id statement category")
        if payload["finding_id"] != f"{unit.research_id}:{record.committee_id}:0":
            raise ValueError("finding identity not bound to research unit")
        if payload["subject_key"] != unit.subject_id or not record.provider_id or record.source_reference != record.provider_id:
            raise ValueError("finding subject/provider provenance mismatch")
        if record.provider_id != provider_by_committee[record.committee_id] or record.collected_at is None:
            raise ValueError("finding configured provider/timestamp mismatch")
    return admit_iro_evidence(bundle_id=f"{config.cycle_id}:bundle:{member.subject.subject_id}", iro_run_id=config.iro_run_id,
        portfolio_snapshot_id=config.snapshot_id, records=selected, subject_by_research_id={unit.research_id: unit.subject_id}, unresolved_contradiction_ids=(), fresh=True)
