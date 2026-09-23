from __future__ import annotations

import json

from InvestmentResearchOrchestrator.models.enums import EvidencePayloadKind
from InvestmentResearchOrchestrator.models.store import EvidenceStoreRecord

from InvestmentDecisionVerticalSlice.models import ResearchEvidenceBundle, ResearchEvidenceReference, TruthClass
from InvestmentDecisionVerticalSlice.validation import validate_evidence_bundle


def admit_iro_evidence(*, bundle_id, iro_run_id, portfolio_snapshot_id, records, subject_by_research_id, unresolved_contradiction_ids, fresh):
    if type(records) is not tuple or type(subject_by_research_id) is not dict:
        raise TypeError("records must be tuple and subject map must be dict")
    evidence = []
    required = []
    completed = []
    for record in records:
        if type(record) is not EvidenceStoreRecord or record.run_id != iro_run_id:
            raise ValueError("IRO evidence record mismatch")
        payload = json.loads(record.payload)
        if record.payload_kind is EvidencePayloadKind.COMPLETENESS:
            required.extend(payload["required"])
            completed.extend(payload["completed"])
        elif record.payload_kind is EvidencePayloadKind.FINDING:
            subject_id = subject_by_research_id.get(record.research_id)
            if subject_id is None:
                raise ValueError("missing research subject binding")
            evidence.append(ResearchEvidenceReference(
                payload["finding_id"], record.research_id,
                record.committee_id, subject_id,
                TruthClass.RESEARCH_AI, payload["statement"],
            ))
    bundle = ResearchEvidenceBundle(
        bundle_id, iro_run_id, portfolio_snapshot_id, tuple(evidence),
        tuple(dict.fromkeys(required)), tuple(dict.fromkeys(completed)),
        unresolved_contradiction_ids, fresh,
    )
    validate_evidence_bundle(bundle)
    return bundle
