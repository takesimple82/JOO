from __future__ import annotations

from InvestmentResearchOrchestrator.models.run import IRORun
from FactStore.models import ExplicitStoredFactRecord
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshotProducer.models import (
    ExplicitPortfolioSnapshotProductionProvenance,
)

from KbPortfolioVerticalSlice.models import (
    ExplicitIroIngressArtifact,
)
from KbPortfolioVerticalSlice.validation import validate_iro_ingress


def build_iro_ingress(
    *,
    ingress_id: str,
    run: IRORun,
    current_snapshot: ExplicitPortfolioSnapshot,
    prior_snapshot: ExplicitPortfolioSnapshot | None,
    change_class: str,
    raw_fact_id: str,
    normalized_fact_ids: tuple[str, ...],
    provider_id: str,
    collected_at,
    snapshot_provenance: ExplicitPortfolioSnapshotProductionProvenance,
    raw_record: ExplicitStoredFactRecord,
    normalized_records: tuple[ExplicitStoredFactRecord, ...],
) -> ExplicitIroIngressArtifact:
    artifact = ExplicitIroIngressArtifact(
        ingress_id,
        run.run_id,
        current_snapshot.portfolio_snapshot_id,
        (
            None
            if prior_snapshot is None
            else prior_snapshot.portfolio_snapshot_id
        ),
        change_class,
        raw_fact_id,
        normalized_fact_ids,
        tuple(
            item.fact_id for item in snapshot_provenance.used_facts
        ),
        provider_id,
        collected_at,
        snapshot_provenance,
    )
    validate_iro_ingress(
        artifact,
        run=run,
        current_snapshot=current_snapshot,
        prior_snapshot=prior_snapshot,
        raw_record=raw_record,
        normalized_records=normalized_records,
    )
    return artifact


def invoke_existing_iro(
    *,
    coordinator,
    artifact: ExplicitIroIngressArtifact,
    run: IRORun,
    current_snapshot: ExplicitPortfolioSnapshot,
    prior_snapshot: ExplicitPortfolioSnapshot | None,
    run_arguments: dict,
    raw_record: ExplicitStoredFactRecord,
    normalized_records: tuple[ExplicitStoredFactRecord, ...],
):
    validate_iro_ingress(
        artifact,
        run=run,
        current_snapshot=current_snapshot,
        prior_snapshot=prior_snapshot,
        raw_record=raw_record,
        normalized_records=normalized_records,
    )
    if type(run_arguments) is not dict:
        raise TypeError("run_arguments must be dict")
    forbidden = {"run", "current_snapshot", "prior_baseline"}
    if forbidden.intersection(run_arguments):
        raise ValueError("run_arguments contain owned arguments")
    return coordinator.run(
        run=run,
        current_snapshot=current_snapshot,
        prior_baseline=prior_snapshot,
        **run_arguments,
    )
