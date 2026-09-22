from __future__ import annotations

from datetime import datetime, timedelta, timezone

from FactStore.models import ExplicitStoredFactRecord
from InvestmentResearchOrchestrator.models.run import IRORun
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshotProducer.models import (
    ExplicitPortfolioSnapshotProductionProvenance,
)

from KbPortfolioVerticalSlice.models import (
    ExplicitIroIngressArtifact,
    ExplicitKbNormalizationRequest,
    ExplicitKbPositionBinding,
    ExplicitSnapshotIdentity,
    ExplicitVerticalSlicePolicy,
)


CHANGE_CLASSES = ("BASELINE_ABSENT", "CHANGED", "NO_CHANGE")


def _nonblank(name: str, value: object) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be str")
    if value.strip() == "":
        raise ValueError(f"{name} must not be blank")


def _optional_nonblank(name: str, value: object) -> None:
    if value is None:
        return
    _nonblank(name, value)


def _utc(name: str, value: object) -> None:
    if type(value) is not datetime:
        raise TypeError(f"{name} must be datetime")
    if value.tzinfo is not timezone.utc:
        raise ValueError(f"{name} must use datetime.timezone.utc")


def validate_position_binding(
    binding: ExplicitKbPositionBinding,
) -> None:
    if type(binding) is not ExplicitKbPositionBinding:
        raise TypeError("binding must be ExplicitKbPositionBinding")
    for name in (
        "account_selector",
        "position_class",
        "currency_code",
        "provider_symbol",
        "fact_id",
        "envelope_id",
        "position_id",
        "portfolio_subject_id",
    ):
        _nonblank(name, getattr(binding, name))
    _optional_nonblank(
        "superseded_fact_id", binding.superseded_fact_id
    )
    if binding.superseded_fact_id == binding.fact_id:
        raise ValueError("superseded_fact_id must not equal fact_id")


def validate_normalization_request(
    request: ExplicitKbNormalizationRequest,
) -> None:
    if type(request) is not ExplicitKbNormalizationRequest:
        raise TypeError(
            "request must be ExplicitKbNormalizationRequest"
        )
    _nonblank("raw_fact_id", request.raw_fact_id)
    _nonblank("account_selector", request.account_selector)
    if type(request.position_bindings) is not tuple:
        raise TypeError("position_bindings must be tuple")
    identities = set()
    fact_ids = set()
    envelope_ids = set()
    position_ids = set()
    subject_ids = set()
    for binding in request.position_bindings:
        validate_position_binding(binding)
        if binding.account_selector != request.account_selector:
            raise ValueError("binding account_selector mismatch")
        identity = (
            binding.account_selector,
            binding.position_class,
            binding.currency_code,
            binding.provider_symbol,
        )
        if identity in identities:
            raise ValueError("duplicate canonical position binding")
        for value, seen, message in (
            (binding.fact_id, fact_ids, "duplicate fact_id binding"),
            (
                binding.envelope_id,
                envelope_ids,
                "duplicate envelope_id binding",
            ),
            (
                binding.position_id,
                position_ids,
                "duplicate position_id binding",
            ),
            (
                binding.portfolio_subject_id,
                subject_ids,
                "duplicate portfolio_subject_id binding",
            ),
        ):
            if value in seen:
                raise ValueError(message)
            seen.add(value)
        identities.add(identity)


def validate_vertical_slice_policy(
    policy: ExplicitVerticalSlicePolicy,
) -> None:
    if type(policy) is not ExplicitVerticalSlicePolicy:
        raise TypeError(
            "policy must be ExplicitVerticalSlicePolicy"
        )
    if type(policy.freshness_max_age) is not timedelta:
        raise TypeError("freshness_max_age must be timedelta")
    if policy.freshness_max_age < timedelta(0):
        raise ValueError("freshness_max_age must not be negative")


def validate_snapshot_identity(
    identity: ExplicitSnapshotIdentity,
) -> None:
    if type(identity) is not ExplicitSnapshotIdentity:
        raise TypeError("identity must be ExplicitSnapshotIdentity")
    for name in (
        "portfolio_snapshot_id",
        "observation_context_id",
        "portfolio_id",
    ):
        _nonblank(name, getattr(identity, name))


def validate_iro_ingress(
    artifact: ExplicitIroIngressArtifact,
    *,
    run: IRORun,
    current_snapshot: ExplicitPortfolioSnapshot,
    prior_snapshot: ExplicitPortfolioSnapshot | None,
    raw_record: ExplicitStoredFactRecord,
    normalized_records: tuple[ExplicitStoredFactRecord, ...],
) -> None:
    if type(artifact) is not ExplicitIroIngressArtifact:
        raise TypeError("artifact must be ExplicitIroIngressArtifact")
    for name in (
        "ingress_id",
        "run_id",
        "portfolio_snapshot_id",
        "change_class",
        "raw_fact_id",
        "provider_id",
    ):
        _nonblank(name, getattr(artifact, name))
    _optional_nonblank(
        "prior_snapshot_id", artifact.prior_snapshot_id
    )
    if artifact.change_class not in CHANGE_CLASSES[:2]:
        raise ValueError("change_class must admit IRO")
    if type(raw_record) is not ExplicitStoredFactRecord:
        raise TypeError("raw_record must be ExplicitStoredFactRecord")
    if type(normalized_records) is not tuple:
        raise TypeError("normalized_records must be tuple")
    if artifact.raw_fact_id != raw_record.fact_id:
        raise ValueError("raw fact provenance mismatch")
    if raw_record.provider_id != artifact.provider_id:
        raise ValueError("raw provider provenance mismatch")
    if raw_record.collected_at != artifact.collected_at:
        raise ValueError("raw collection provenance mismatch")
    normalized_ids = tuple(
        record.fact_id for record in normalized_records
    )
    if artifact.normalized_fact_ids != normalized_ids:
        raise ValueError("normalized fact provenance mismatch")
    for record in normalized_records:
        if type(record) is not ExplicitStoredFactRecord:
            raise TypeError(
                "normalized record must be ExplicitStoredFactRecord"
            )
        if record.provider_id != artifact.provider_id:
            raise ValueError("normalized provider mismatch")
        if record.source_class != "broker_fact":
            raise ValueError("normalized source_class mismatch")
        if record.collected_at != artifact.collected_at:
            raise ValueError("normalized collection cycle mismatch")
        if record.payload.get("raw_fact_id") != raw_record.fact_id:
            raise ValueError("normalized raw fact linkage mismatch")
        if (
            record.payload.get("raw_envelope_id")
            != raw_record.envelope_id
        ):
            raise ValueError("normalized raw envelope linkage mismatch")
    if type(artifact.normalized_fact_ids) is not tuple:
        raise TypeError("normalized_fact_ids must be tuple")
    if type(artifact.snapshot_used_fact_ids) is not tuple:
        raise TypeError("snapshot_used_fact_ids must be tuple")
    if len(set(artifact.normalized_fact_ids)) != len(
        artifact.normalized_fact_ids
    ):
        raise ValueError("normalized_fact_ids must be unique")
    if len(set(artifact.snapshot_used_fact_ids)) != len(
        artifact.snapshot_used_fact_ids
    ):
        raise ValueError("snapshot_used_fact_ids must be unique")
    if not set(artifact.snapshot_used_fact_ids).issubset(
        set(artifact.normalized_fact_ids)
    ):
        raise ValueError("snapshot facts must be normalized facts")
    _utc("collected_at", artifact.collected_at)
    if (
        type(artifact.snapshot_provenance)
        is not ExplicitPortfolioSnapshotProductionProvenance
    ):
        raise TypeError(
            "snapshot_provenance must be production provenance"
        )
    provenance_ids = tuple(
        fact.fact_id
        for fact in artifact.snapshot_provenance.used_facts
    )
    if provenance_ids != artifact.snapshot_used_fact_ids:
        raise ValueError("snapshot provenance fact ids mismatch")
    for fact in artifact.snapshot_provenance.used_facts:
        if fact.source_identity != artifact.provider_id:
            raise ValueError("snapshot provenance provider mismatch")
        if fact.collected_at != artifact.collected_at:
            raise ValueError("snapshot provenance cycle mismatch")
    if artifact.run_id != run.run_id:
        raise ValueError("run_id mismatch")
    if artifact.portfolio_snapshot_id != run.portfolio_snapshot_id:
        raise ValueError("run snapshot identity mismatch")
    if (
        artifact.portfolio_snapshot_id
        != current_snapshot.portfolio_snapshot_id
    ):
        raise ValueError("current snapshot identity mismatch")
    expected_prior = (
        None
        if prior_snapshot is None
        else prior_snapshot.portfolio_snapshot_id
    )
    if artifact.prior_snapshot_id != expected_prior:
        raise ValueError("prior snapshot identity mismatch")
    if run.prior_baseline_id != expected_prior:
        raise ValueError("run prior baseline identity mismatch")
