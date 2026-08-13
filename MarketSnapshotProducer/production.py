from __future__ import annotations

from datetime import datetime, timezone

from FactStore.models import ExplicitStoredFactRecord
from FactStore.store import FactStore
from MarketEndpoint.validation import validate_explicit_market
from MarketInstrumentObservation.validation import (
    validate_explicit_market_instrument_observation,
)
from MarketSessionContext.validation import (
    validate_explicit_market_session_context,
)
from MarketSnapshot.validation import (
    validate_explicit_market_snapshot,
)
from MarketVenue.validation import (
    validate_explicit_market_venue,
)

from MarketSnapshotProducer.composition.compose import (
    build_explicit_market,
    build_explicit_market_fact_provenance_reference,
    build_explicit_market_instrument_observation,
    build_explicit_market_session_context,
    build_explicit_market_snapshot,
    build_explicit_market_venue,
    project_bound_payload,
)
from MarketSnapshotProducer.models.types import (
    ExplicitMarketSnapshotProductionFailure,
    ExplicitMarketSnapshotProductionRequest,
    ExplicitMarketSnapshotProductionResult,
)
from MarketSnapshotProducer.policy.evaluate import (
    classify_retrieved_fact,
    is_missing_required_fact_error,
)
from MarketSnapshotProducer.retrieval.boundary import (
    retrieve_by_fact_id,
    verify_retrieved_fact_integrity,
)
from MarketSnapshotProducer.validation.validators import (
    validate_explicit_market_snapshot_production_request,
)


class MarketSnapshotProducer:
    def __init__(self, fact_store, utc_clock) -> None:
        if type(fact_store) is not FactStore:
            raise TypeError("fact_store must be FactStore")
        if not callable(utc_clock):
            raise TypeError("utc_clock must be callable")
        self._fact_store = fact_store
        self._utc_clock = utc_clock

    def produce(
        self,
        request: ExplicitMarketSnapshotProductionRequest,
    ) -> ExplicitMarketSnapshotProductionResult:
        validate_explicit_market_snapshot_production_request(
            request
        )
        policy = request.production_policy
        allow_partial = policy.allow_partial_emission
        composed = []
        omitted = []
        evaluation_time = None
        bindings = request.subject_bindings
        for index, binding in enumerate(bindings):
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
                    if not allow_partial:
                        return self._failure_result(
                            "MISSING_REQUIRED_FACT",
                            self._omitted_from(
                                omitted,
                                bindings,
                                index,
                            ),
                        )
                    omitted.append(
                        binding.instrument.instrument_id
                    )
                    continue
                if not allow_partial:
                    raise
                omitted.append(
                    binding.instrument.instrument_id
                )
                continue
            if type(record) is not ExplicitStoredFactRecord:
                error = TypeError(
                    "record must be ExplicitStoredFactRecord"
                )
                if not allow_partial:
                    raise error
                omitted.append(
                    binding.instrument.instrument_id
                )
                continue
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
                if not allow_partial:
                    return self._failure_result(
                        failure_code,
                        self._omitted_from(
                            omitted,
                            bindings,
                            index,
                        ),
                    )
                omitted.append(
                    binding.instrument.instrument_id
                )
                continue
            projected = project_bound_payload(
                record.payload,
                binding.last_price_payload_key,
                binding.market_status_payload_key,
            )
            if projected is None:
                if not allow_partial:
                    return self._failure_result(
                        "PROJECTION_FAILURE",
                        self._omitted_from(
                            omitted,
                            bindings,
                            index,
                        ),
                    )
                omitted.append(
                    binding.instrument.instrument_id
                )
                continue
            composed.append((binding, record, projected))
        if bindings and not composed:
            return self._failure_result(
                "EMPTY_REQUIRED_EMISSION",
                tuple(omitted),
            )
        snapshot = self._emit_snapshot(request, composed)
        return ExplicitMarketSnapshotProductionResult(
            "success",
            snapshot,
            None,
            tuple(omitted),
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
        profile = request.session_profile
        market = build_explicit_market(profile.market_id)
        venue = build_explicit_market_venue(profile.venue_id)
        session_context = (
            build_explicit_market_session_context(
                request.session_context_id,
                profile,
            )
        )
        validate_explicit_market(market)
        validate_explicit_market_venue(venue)
        validate_explicit_market_session_context(
            session_context
        )
        observations = []
        for binding, record, projected in composed:
            last_price, market_status = projected
            provenance = (
                build_explicit_market_fact_provenance_reference(
                    record
                )
            )
            observation = (
                build_explicit_market_instrument_observation(
                    binding.instrument,
                    session_context,
                    last_price,
                    market_status,
                    provenance,
                )
            )
            validate_explicit_market_instrument_observation(
                observation
            )
            observations.append(observation)
        snapshot = build_explicit_market_snapshot(
            request.market_snapshot_id,
            session_context,
            tuple(observations),
        )
        validate_explicit_market_snapshot(snapshot)
        return snapshot

    def _failure_result(self, failure_code, omitted):
        failure = ExplicitMarketSnapshotProductionFailure(
            failure_code,
            omitted,
        )
        return ExplicitMarketSnapshotProductionResult(
            "failure",
            None,
            failure,
            omitted,
        )

    def _omitted_from(self, omitted, bindings, index):
        remaining = [
            binding.instrument.instrument_id
            for binding in bindings[index:]
        ]
        return tuple(omitted + remaining)
