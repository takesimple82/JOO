from __future__ import annotations

from PortfolioSnapshotProducer.models.types import (
    ExplicitPortfolioFactSelectionCriteria,
    ExplicitPortfolioHoldingFactBinding,
    ExplicitPortfolioSnapshotProductionPolicy,
    ExplicitPortfolioSnapshotProductionRequest,
    ExplicitPortfolioWatchlistMembershipDeclaration,
)
from PortfolioSnapshotProducer.models.vocabularies import (
    COMPOSITION_SOURCE_CLASS,
)
from PortfolioSnapshotProducer.validation.common import (
    require_exact_type,
    require_nonblank_string,
    require_optional_nonblank_string,
    require_optional_nonnegative_timedelta,
    require_utc_datetime,
)


def validate_explicit_portfolio_holding_fact_binding(
    binding: ExplicitPortfolioHoldingFactBinding,
) -> None:
    require_exact_type(
        "binding",
        binding,
        ExplicitPortfolioHoldingFactBinding,
    )
    require_nonblank_string("fact_id", binding.fact_id)
    require_nonblank_string("position_id", binding.position_id)
    require_nonblank_string(
        "portfolio_subject_id",
        binding.portfolio_subject_id,
    )
    require_nonblank_string(
        "quantity_payload_key",
        binding.quantity_payload_key,
    )


def validate_explicit_portfolio_watchlist_membership_declaration(
    declaration: ExplicitPortfolioWatchlistMembershipDeclaration,
) -> None:
    require_exact_type(
        "declaration",
        declaration,
        ExplicitPortfolioWatchlistMembershipDeclaration,
    )
    require_nonblank_string(
        "portfolio_subject_id",
        declaration.portfolio_subject_id,
    )


def validate_explicit_portfolio_fact_selection_criteria(
    criteria: ExplicitPortfolioFactSelectionCriteria,
) -> None:
    require_exact_type(
        "criteria",
        criteria,
        ExplicitPortfolioFactSelectionCriteria,
    )
    require_exact_type(
        "required_source_class",
        criteria.required_source_class,
        str,
    )
    if criteria.required_source_class != COMPOSITION_SOURCE_CLASS:
        raise ValueError(
            "required_source_class must be broker_fact"
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


def validate_explicit_portfolio_snapshot_production_policy(
    policy: ExplicitPortfolioSnapshotProductionPolicy,
) -> None:
    require_exact_type(
        "policy",
        policy,
        ExplicitPortfolioSnapshotProductionPolicy,
    )
    require_optional_nonnegative_timedelta(
        "freshness_max_age",
        policy.freshness_max_age,
    )


def validate_explicit_portfolio_snapshot_production_request(
    request: ExplicitPortfolioSnapshotProductionRequest,
) -> None:
    require_exact_type(
        "request",
        request,
        ExplicitPortfolioSnapshotProductionRequest,
    )
    require_nonblank_string(
        "portfolio_snapshot_id",
        request.portfolio_snapshot_id,
    )
    require_nonblank_string(
        "observation_context_id",
        request.observation_context_id,
    )
    require_nonblank_string(
        "portfolio_id",
        request.portfolio_id,
    )
    require_exact_type(
        "holding_fact_bindings",
        request.holding_fact_bindings,
        tuple,
    )
    seen_position_ids = set()
    for binding in request.holding_fact_bindings:
        require_exact_type(
            "binding",
            binding,
            ExplicitPortfolioHoldingFactBinding,
        )
        validate_explicit_portfolio_holding_fact_binding(
            binding
        )
        position_id = binding.position_id
        if position_id in seen_position_ids:
            raise ValueError(
                "holding_fact_bindings must not contain "
                "duplicate position_id"
            )
        seen_position_ids.add(position_id)
    require_exact_type(
        "watchlist_memberships",
        request.watchlist_memberships,
        tuple,
    )
    seen_subject_ids = set()
    for declaration in request.watchlist_memberships:
        require_exact_type(
            "declaration",
            declaration,
            ExplicitPortfolioWatchlistMembershipDeclaration,
        )
        validate_explicit_portfolio_watchlist_membership_declaration(
            declaration
        )
        subject_id = declaration.portfolio_subject_id
        if subject_id in seen_subject_ids:
            raise ValueError(
                "watchlist_memberships must not contain "
                "duplicate portfolio_subject_id"
            )
        seen_subject_ids.add(subject_id)
    require_exact_type(
        "fact_selection",
        request.fact_selection,
        ExplicitPortfolioFactSelectionCriteria,
    )
    validate_explicit_portfolio_fact_selection_criteria(
        request.fact_selection
    )
    require_exact_type(
        "production_policy",
        request.production_policy,
        ExplicitPortfolioSnapshotProductionPolicy,
    )
    validate_explicit_portfolio_snapshot_production_policy(
        request.production_policy
    )
