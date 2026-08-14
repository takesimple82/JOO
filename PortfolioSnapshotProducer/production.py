from __future__ import annotations

from datetime import datetime, timezone

from FactStore.models import ExplicitStoredFactRecord
from FactStore.store import FactStore
from PortfolioHoldingObservation.validation import (
    validate_explicit_portfolio_holding_observation,
)
from PortfolioHoldingSnapshot.validation import (
    validate_explicit_portfolio_holding_snapshot,
)
from PortfolioObservationContext.validation import (
    validate_explicit_portfolio_observation_context,
)
from PortfolioSnapshot.validation import (
    validate_explicit_portfolio_snapshot,
)
from PortfolioWatchlistEntry.validation import (
    validate_explicit_portfolio_watchlist_entry,
)

from PortfolioSnapshotProducer.composition.compose import (
    build_explicit_portfolio_holding_observation,
    build_explicit_portfolio_holding_snapshot,
    build_explicit_portfolio_membership,
    build_explicit_portfolio_observation_context,
    build_explicit_portfolio_position,
    build_explicit_portfolio_snapshot,
    build_explicit_portfolio_watchlist_entry,
    project_bound_quantity,
)
from PortfolioSnapshotProducer.models.types import (
    ExplicitPortfolioHoldingFactBinding,
    ExplicitPortfolioSnapshotProductionFailure,
    ExplicitPortfolioSnapshotProductionProvenance,
    ExplicitPortfolioSnapshotProductionRequest,
    ExplicitPortfolioSnapshotProductionResult,
    ExplicitPortfolioUsedFactProvenance,
)
from PortfolioSnapshotProducer.policy.evaluate import (
    classify_retrieved_fact,
    is_missing_required_fact_error,
)
from PortfolioSnapshotProducer.retrieval.boundary import (
    retrieve_by_fact_id,
    verify_retrieved_fact_integrity,
)
from PortfolioSnapshotProducer.validation.validators import (
    validate_explicit_portfolio_snapshot_production_request,
)


class PortfolioSnapshotProducer:
    def __init__(self, fact_store, utc_clock) -> None:
        if type(fact_store) is not FactStore:
            raise TypeError("fact_store must be FactStore")
        if not callable(utc_clock):
            raise TypeError("utc_clock must be callable")
        self._fact_store = fact_store
        self._utc_clock = utc_clock

    def produce(
        self,
        request: ExplicitPortfolioSnapshotProductionRequest,
    ) -> ExplicitPortfolioSnapshotProductionResult:
        validate_explicit_portfolio_snapshot_production_request(
            request
        )
        policy = request.production_policy
        composed = []
        evaluation_time = None
        for binding in request.holding_fact_bindings:
            try:
                record = retrieve_by_fact_id(
                    self._fact_store,
                    binding.fact_id,
                )
                verify_retrieved_fact_integrity(
                    self._fact_store,
                    binding.fact_id,
                )
            except Exception as exc:
                if is_missing_required_fact_error(exc):
                    return self._failure_result(
                        "MISSING_REQUIRED_FACT",
                        binding,
                    )
                raise
            if type(record) is not ExplicitStoredFactRecord:
                raise TypeError(
                    "record must be ExplicitStoredFactRecord"
                )
            if (
                policy.freshness_max_age is not None
                and evaluation_time is None
            ):
                evaluation_time = self._read_evaluation_time()
            failure_code = classify_retrieved_fact(
                record,
                request.fact_selection,
                evaluation_time,
                policy.freshness_max_age,
            )
            if failure_code is not None:
                return self._failure_result(
                    failure_code,
                    binding,
                )
            quantity = project_bound_quantity(
                record.payload,
                binding.quantity_payload_key,
            )
            if quantity is None:
                return self._failure_result(
                    "PROJECTION_FAILURE",
                    binding,
                )
            composed.append((binding, record, quantity))
        snapshot = self._emit_snapshot(request, composed)
        used_facts = tuple(
            ExplicitPortfolioUsedFactProvenance(
                record.fact_id,
                record.collected_at,
                record.provider_id,
            )
            for _binding, record, _quantity in composed
        )
        return ExplicitPortfolioSnapshotProductionResult(
            "success",
            snapshot,
            None,
            ExplicitPortfolioSnapshotProductionProvenance(
                used_facts
            ),
        )

    def _read_evaluation_time(self) -> datetime:
        evaluation_time = self._utc_clock()
        if type(evaluation_time) is not datetime:
            raise TypeError(
                "evaluation_time must be datetime"
            )
        if evaluation_time.tzinfo is not timezone.utc:
            raise ValueError(
                "evaluation_time tzinfo must be "
                "datetime.timezone.utc"
            )
        return evaluation_time

    def _emit_snapshot(self, request, composed):
        observation_context = (
            build_explicit_portfolio_observation_context(
                request.observation_context_id,
                request.portfolio_id,
            )
        )
        validate_explicit_portfolio_observation_context(
            observation_context
        )
        holding_observations = []
        for binding, _record, quantity in composed:
            membership = build_explicit_portfolio_membership(
                request.portfolio_id,
                binding.portfolio_subject_id,
            )
            position = build_explicit_portfolio_position(
                binding.position_id,
                membership,
            )
            observation = (
                build_explicit_portfolio_holding_observation(
                    position,
                    observation_context,
                    quantity,
                )
            )
            validate_explicit_portfolio_holding_observation(
                observation
            )
            holding_observations.append(observation)
        holding_snapshot = (
            build_explicit_portfolio_holding_snapshot(
                observation_context,
                tuple(holding_observations),
            )
        )
        validate_explicit_portfolio_holding_snapshot(
            holding_snapshot
        )
        watchlist_entries = []
        for declaration in request.watchlist_memberships:
            membership = build_explicit_portfolio_membership(
                request.portfolio_id,
                declaration.portfolio_subject_id,
            )
            entry = build_explicit_portfolio_watchlist_entry(
                membership
            )
            validate_explicit_portfolio_watchlist_entry(entry)
            watchlist_entries.append(entry)
        snapshot = build_explicit_portfolio_snapshot(
            request.portfolio_snapshot_id,
            observation_context,
            holding_snapshot,
            tuple(watchlist_entries),
        )
        validate_explicit_portfolio_snapshot(snapshot)
        return snapshot

    def _failure_result(
        self,
        failure_code: str,
        binding: ExplicitPortfolioHoldingFactBinding,
    ) -> ExplicitPortfolioSnapshotProductionResult:
        failure = ExplicitPortfolioSnapshotProductionFailure(
            failure_code,
            binding.fact_id,
            binding.position_id,
        )
        return ExplicitPortfolioSnapshotProductionResult(
            "failure",
            None,
            failure,
            None,
        )
