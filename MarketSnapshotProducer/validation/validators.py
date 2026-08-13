from __future__ import annotations

from MarketInstrument.models import ExplicitMarketInstrument
from MarketInstrument.validation import (
    validate_explicit_market_instrument,
)

from MarketSnapshotProducer.models.types import (
    ExplicitMarketFactSelectionCriteria,
    ExplicitMarketSessionProfile,
    ExplicitMarketSnapshotProductionPolicy,
    ExplicitMarketSnapshotProductionRequest,
    ExplicitMarketSubjectBinding,
)
from MarketSnapshotProducer.models.vocabularies import (
    COMPOSITION_SOURCE_CLASS,
)
from MarketSnapshotProducer.validation.common import (
    require_exact_bool,
    require_exact_type,
    require_nonblank_string,
    require_optional_nonblank_string,
    require_optional_nonnegative_timedelta,
    require_utc_datetime,
)


def validate_explicit_market_session_profile(
    profile: ExplicitMarketSessionProfile,
) -> None:
    require_exact_type(
        "profile",
        profile,
        ExplicitMarketSessionProfile,
    )
    require_nonblank_string(
        "session_profile_id",
        profile.session_profile_id,
    )
    require_nonblank_string("market_id", profile.market_id)
    require_nonblank_string("venue_id", profile.venue_id)
    require_nonblank_string(
        "timezone_id",
        profile.timezone_id,
    )
    require_nonblank_string(
        "calendar_id",
        profile.calendar_id,
    )


def validate_explicit_market_subject_binding(
    binding: ExplicitMarketSubjectBinding,
) -> None:
    require_exact_type(
        "binding",
        binding,
        ExplicitMarketSubjectBinding,
    )
    require_exact_type(
        "instrument",
        binding.instrument,
        ExplicitMarketInstrument,
    )
    validate_explicit_market_instrument(binding.instrument)
    require_nonblank_string("fact_id", binding.fact_id)
    require_nonblank_string(
        "last_price_payload_key",
        binding.last_price_payload_key,
    )
    require_nonblank_string(
        "market_status_payload_key",
        binding.market_status_payload_key,
    )


def validate_explicit_market_fact_selection_criteria(
    criteria: ExplicitMarketFactSelectionCriteria,
) -> None:
    require_exact_type(
        "criteria",
        criteria,
        ExplicitMarketFactSelectionCriteria,
    )
    require_exact_type(
        "required_source_class",
        criteria.required_source_class,
        str,
    )
    if criteria.required_source_class != COMPOSITION_SOURCE_CLASS:
        raise ValueError(
            "required_source_class must be market_fact"
        )
    require_optional_nonblank_string(
        "required_source_identity",
        criteria.required_source_identity,
    )
    start = criteria.collected_at_start
    end = criteria.collected_at_end
    if start is None and end is None:
        return
    if start is None or end is None:
        raise ValueError(
            "collected_at_start and collected_at_end must "
            "both be None or both be set"
        )
    require_utc_datetime("collected_at_start", start)
    require_utc_datetime("collected_at_end", end)
    if start > end:
        raise ValueError(
            "collected_at_start must not be after "
            "collected_at_end"
        )


def validate_explicit_market_snapshot_production_policy(
    policy: ExplicitMarketSnapshotProductionPolicy,
) -> None:
    require_exact_type(
        "policy",
        policy,
        ExplicitMarketSnapshotProductionPolicy,
    )
    require_exact_bool(
        "require_all_bound_subjects",
        policy.require_all_bound_subjects,
    )
    require_exact_bool(
        "allow_partial_emission",
        policy.allow_partial_emission,
    )
    if (
        policy.require_all_bound_subjects is True
        and policy.allow_partial_emission is True
    ):
        raise ValueError(
            "require_all_bound_subjects and "
            "allow_partial_emission must not both be True"
        )
    require_optional_nonnegative_timedelta(
        "freshness_max_age",
        policy.freshness_max_age,
    )


def validate_explicit_market_snapshot_production_request(
    request: ExplicitMarketSnapshotProductionRequest,
) -> None:
    require_exact_type(
        "request",
        request,
        ExplicitMarketSnapshotProductionRequest,
    )
    require_nonblank_string(
        "market_snapshot_id",
        request.market_snapshot_id,
    )
    require_nonblank_string(
        "session_context_id",
        request.session_context_id,
    )
    require_exact_type(
        "session_profile",
        request.session_profile,
        ExplicitMarketSessionProfile,
    )
    validate_explicit_market_session_profile(
        request.session_profile
    )
    require_exact_type(
        "subject_bindings",
        request.subject_bindings,
        tuple,
    )
    seen_instrument_ids = set()
    for binding in request.subject_bindings:
        require_exact_type(
            "binding",
            binding,
            ExplicitMarketSubjectBinding,
        )
        validate_explicit_market_subject_binding(binding)
        instrument_id = binding.instrument.instrument_id
        if instrument_id in seen_instrument_ids:
            raise ValueError(
                "subject_bindings must not contain "
                "duplicate instrument_id"
            )
        seen_instrument_ids.add(instrument_id)
    require_exact_type(
        "fact_selection",
        request.fact_selection,
        ExplicitMarketFactSelectionCriteria,
    )
    validate_explicit_market_fact_selection_criteria(
        request.fact_selection
    )
    require_exact_type(
        "production_policy",
        request.production_policy,
        ExplicitMarketSnapshotProductionPolicy,
    )
    validate_explicit_market_snapshot_production_policy(
        request.production_policy
    )
