from __future__ import annotations

from FactStore.models import ExplicitFactAppendRequest
from FactStore.store import FactStore
from InvestmentResearchOrchestrator.models.run import IRORun
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot
from PortfolioSnapshotProducer.models import (
    ExplicitPortfolioFactSelectionCriteria,
    ExplicitPortfolioHoldingFactBinding,
    ExplicitPortfolioSnapshotProductionPolicy,
    ExplicitPortfolioSnapshotProductionRequest,
    ExplicitPortfolioWatchlistMembershipDeclaration,
)
from PortfolioSnapshotProducer.production import PortfolioSnapshotProducer
from ProviderGateway.models import (
    ExplicitBrokerCollectRequest,
    ExplicitCollectOutcome,
)
from ProviderGateway.validation.validators import (
    validate_explicit_collect_outcome,
)

from KbPortfolioVerticalSlice.change_detection import (
    classify_snapshot_change,
)
from KbPortfolioVerticalSlice.iro_ingress import (
    build_iro_ingress,
    invoke_existing_iro,
)
from KbPortfolioVerticalSlice.models import (
    ExplicitKbNormalizationRequest,
    ExplicitSnapshotIdentity,
    ExplicitVerticalSlicePolicy,
    ExplicitVerticalSliceResult,
)
from KbPortfolioVerticalSlice.normalization import normalize_ssqm2952
from KbPortfolioVerticalSlice.validation import (
    validate_snapshot_identity,
    validate_vertical_slice_policy,
)


def run_kb_portfolio_vertical_slice(
    *,
    adapter,
    collect_request: ExplicitBrokerCollectRequest,
    raw_fact_id: str,
    normalization_request: ExplicitKbNormalizationRequest,
    fact_store: FactStore,
    snapshot_producer: PortfolioSnapshotProducer,
    snapshot_identity: ExplicitSnapshotIdentity,
    watchlist_memberships: tuple[
        ExplicitPortfolioWatchlistMembershipDeclaration, ...
    ],
    policy: ExplicitVerticalSlicePolicy,
    run: IRORun,
    prior_snapshot: ExplicitPortfolioSnapshot | None,
    ingress_id: str,
    coordinator,
    iro_run_arguments: dict,
) -> ExplicitVerticalSliceResult:
    if type(collect_request) is not ExplicitBrokerCollectRequest:
        raise TypeError(
            "collect_request must be ExplicitBrokerCollectRequest"
        )
    if type(fact_store) is not FactStore:
        raise TypeError("fact_store must be FactStore")
    if type(snapshot_producer) is not PortfolioSnapshotProducer:
        raise TypeError(
            "snapshot_producer must be PortfolioSnapshotProducer"
        )
    validate_snapshot_identity(snapshot_identity)
    validate_vertical_slice_policy(policy)
    if type(watchlist_memberships) is not tuple:
        raise TypeError("watchlist_memberships must be tuple")
    if normalization_request.raw_fact_id != raw_fact_id:
        raise ValueError("raw fact identity mismatch")
    if (
        normalization_request.account_selector
        != collect_request.binding.parameter_profile.account_selector
    ):
        raise ValueError("collect account_selector mismatch")
    if collect_request.request_kind != "holdings":
        raise ValueError("request_kind must be holdings")

    outcome = adapter.collect(collect_request)
    if type(outcome) is not ExplicitCollectOutcome:
        raise TypeError("adapter outcome must be ExplicitCollectOutcome")
    validate_explicit_collect_outcome(outcome)
    if outcome.result_kind != "success" or outcome.envelope is None:
        return ExplicitVerticalSliceResult(
            "failure",
            "PROVIDER_UNAVAILABLE",
            None,
            None,
            None,
            None,
        )
    raw_envelope = outcome.envelope
    if raw_envelope.envelope_id != collect_request.envelope_id:
        raise ValueError("collected envelope identity mismatch")
    if raw_envelope.provider_id != collect_request.binding.provider_id:
        raise ValueError("collected provider identity mismatch")
    if raw_envelope.source_class != "broker_fact":
        raise ValueError("collected source_class mismatch")
    if (
        raw_envelope.request_correlation_id
        != collect_request.request_correlation_id
    ):
        raise ValueError("collected request correlation mismatch")
    raw_record = fact_store.append(
        ExplicitFactAppendRequest(
            raw_fact_id,
            raw_envelope,
            None,
        )
    )
    fact_store.verify_integrity(raw_record.fact_id)
    normalized = normalize_ssqm2952(
        raw_record=raw_record,
        raw_envelope=raw_envelope,
        request=normalization_request,
    )
    normalized_requests = tuple(
        position.append_request
        for position in normalized.positions
    )
    normalized_records = (
        ()
        if len(normalized_requests) == 0
        else fact_store.append_batch(normalized_requests)
    )
    for record in normalized_records:
        fact_store.verify_integrity(record.fact_id)

    active_positions = tuple(
        position
        for position in normalized.positions
        if position.is_active_holding
    )
    production_request = ExplicitPortfolioSnapshotProductionRequest(
        snapshot_identity.portfolio_snapshot_id,
        snapshot_identity.observation_context_id,
        snapshot_identity.portfolio_id,
        tuple(
            ExplicitPortfolioHoldingFactBinding(
                position.append_request.fact_id,
                position.position_id,
                position.portfolio_subject_id,
                "quantity",
            )
            for position in active_positions
        ),
        watchlist_memberships,
        ExplicitPortfolioFactSelectionCriteria(
            "broker_fact",
            raw_record.provider_id,
            raw_record.collected_at,
            raw_record.collected_at,
        ),
        ExplicitPortfolioSnapshotProductionPolicy(
            policy.freshness_max_age
        ),
    )
    production = snapshot_producer.produce(production_request)
    if production.result_kind != "success":
        failure_code = (
            "SNAPSHOT_REJECTED"
            if production.failure is None
            else production.failure.failure_code
        )
        return ExplicitVerticalSliceResult(
            "failure",
            failure_code,
            None,
            None,
            None,
            None,
        )
    snapshot = production.snapshot
    provenance = production.provenance
    if snapshot is None or provenance is None:
        raise ValueError("snapshot success must include artifacts")
    change_class = classify_snapshot_change(
        run_id=run.run_id,
        current_snapshot=snapshot,
        prior_snapshot=prior_snapshot,
    )
    if change_class == "NO_CHANGE":
        return ExplicitVerticalSliceResult(
            "success",
            None,
            snapshot,
            change_class,
            None,
            None,
        )
    ingress = build_iro_ingress(
        ingress_id=ingress_id,
        run=run,
        current_snapshot=snapshot,
        prior_snapshot=prior_snapshot,
        change_class=change_class,
        raw_fact_id=raw_record.fact_id,
        normalized_fact_ids=tuple(
            record.fact_id for record in normalized_records
        ),
        provider_id=raw_record.provider_id,
        collected_at=raw_record.collected_at,
        snapshot_provenance=provenance,
        raw_record=raw_record,
        normalized_records=normalized_records,
    )
    iro_result = invoke_existing_iro(
        coordinator=coordinator,
        artifact=ingress,
        run=run,
        current_snapshot=snapshot,
        prior_snapshot=prior_snapshot,
        run_arguments=iro_run_arguments,
        raw_record=raw_record,
        normalized_records=normalized_records,
    )
    return ExplicitVerticalSliceResult(
        "success",
        None,
        snapshot,
        change_class,
        ingress,
        iro_result,
    )
