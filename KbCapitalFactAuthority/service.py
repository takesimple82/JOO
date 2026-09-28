from __future__ import annotations

from datetime import datetime, timezone

from FactStore.models import ExplicitFactAppendRequest
from FactStore.store import FactStore
from KbPortfolioVerticalSlice.service import run_kb_portfolio_vertical_slice
from ProviderGateway.models import (
    ExplicitBrokerCollectRequest,
    ExplicitCollectOutcome,
    ExplicitProviderPayloadEnvelope,
)
from ProviderGateway.validation.validators import (
    validate_explicit_collect_outcome,
)

from KbCapitalFactAuthority.models import (
    ExplicitBalancesNormalizationRequest,
    ExplicitCapitalFactPlaneResult,
    ExplicitCapitalFactPolicy,
    ExplicitCapitalPortfolioBinding,
    ExplicitCapitalSnapshot,
    ExplicitCapitalSnapshotIdentity,
    ExplicitHoldingsCapitalNormalizationRequest,
)
from KbCapitalFactAuthority.normalization import (
    normalize_ssqm0004_balances,
    normalize_ssqm2952_capital_facts,
)
from KbCapitalFactAuthority.validation import (
    validate_capital_fact_policy,
    validate_capital_portfolio_binding,
    validate_capital_snapshot_consistency,
    validate_capital_snapshot_identity,
    validate_freshness,
)
from KbCapitalFactAuthority.vocabularies import (
    DOMESTIC_CURRENCY_CODE,
    FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION,
    FACT_KIND_DEPOSIT_D1,
    FACT_KIND_DEPOSIT_D2,
    FACT_KIND_DEPOSIT_TODAY,
    FACT_KIND_ORDERABLE_CASH,
    FACT_KIND_ORDERABLE_TOTAL,
    FACT_KIND_POSITION_MARKET_VALUE,
    FACT_KIND_WITHDRAWABLE_CASH,
    SIZING_AUTHORITY_NONE,
)


def _failure(
    code: str,
    *,
    raw_balances_fact_id: str | None = None,
) -> ExplicitCapitalFactPlaneResult:
    return ExplicitCapitalFactPlaneResult(
        "failure",
        code,
        None,
        raw_balances_fact_id,
        (),
    )


def _collect_and_append_raw(
    *,
    adapter,
    collect_request: ExplicitBrokerCollectRequest,
    raw_fact_id: str,
    fact_store: FactStore,
    expected_kind: str,
) -> tuple[object, ExplicitProviderPayloadEnvelope] | ExplicitCapitalFactPlaneResult:
    if type(collect_request) is not ExplicitBrokerCollectRequest:
        raise TypeError(
            "collect_request must be ExplicitBrokerCollectRequest"
        )
    if collect_request.request_kind != expected_kind:
        raise ValueError(f"request_kind must be {expected_kind}")
    outcome = adapter.collect(collect_request)
    if type(outcome) is not ExplicitCollectOutcome:
        raise TypeError("adapter outcome must be ExplicitCollectOutcome")
    validate_explicit_collect_outcome(outcome)
    if outcome.result_kind != "success" or outcome.envelope is None:
        return _failure("PROVIDER_UNAVAILABLE")
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
    return raw_record, raw_envelope


def _id_for_kind(facts, kind: str) -> str:
    for fact in facts:
        if fact.fact_kind == kind:
            return fact.append_request.fact_id
    raise ValueError(f"missing canonical fact kind {kind}")


def _ids_for_kind(facts, kind: str) -> tuple[str, ...]:
    return tuple(
        fact.append_request.fact_id
        for fact in facts
        if fact.fact_kind == kind
    )


def run_kb_capital_fact_plane(
    *,
    adapter,
    balances_collect_request: ExplicitBrokerCollectRequest,
    balances_raw_fact_id: str,
    balances_normalization_request: ExplicitBalancesNormalizationRequest,
    fact_store: FactStore,
    snapshot_identity: ExplicitCapitalSnapshotIdentity,
    portfolio_binding: ExplicitCapitalPortfolioBinding,
    policy: ExplicitCapitalFactPolicy,
    now: datetime,
    holdings_raw_fact_id: str | None = None,
    holdings_raw_envelope: ExplicitProviderPayloadEnvelope | None = None,
    holdings_capital_normalization_request: (
        ExplicitHoldingsCapitalNormalizationRequest | None
    ) = None,
) -> ExplicitCapitalFactPlaneResult:
    if type(fact_store) is not FactStore:
        raise TypeError("fact_store must be FactStore")
    validate_capital_snapshot_identity(snapshot_identity)
    validate_capital_portfolio_binding(portfolio_binding)
    validate_capital_fact_policy(policy)
    if type(now) is not datetime or now.tzinfo is not timezone.utc:
        raise ValueError("now must be UTC datetime")
    if (
        balances_normalization_request.raw_fact_id
        != balances_raw_fact_id
    ):
        raise ValueError("balances raw fact identity mismatch")
    if (
        balances_normalization_request.account_selector
        != balances_collect_request.binding.parameter_profile.account_selector
    ):
        raise ValueError("balances account_selector mismatch")
    if (
        snapshot_identity.account_selector
        != balances_normalization_request.account_selector
    ):
        raise ValueError("snapshot account_selector mismatch")

    collected = _collect_and_append_raw(
        adapter=adapter,
        collect_request=balances_collect_request,
        raw_fact_id=balances_raw_fact_id,
        fact_store=fact_store,
        expected_kind="balances",
    )
    if type(collected) is ExplicitCapitalFactPlaneResult:
        return collected
    balances_raw_record, balances_raw_envelope = collected
    try:
        validate_freshness(
            collected_at=balances_raw_record.collected_at,
            now=now,
            policy=policy,
        )
    except ValueError:
        return _failure(
            "STALE_OR_MISSING_FRESHNESS",
            raw_balances_fact_id=balances_raw_record.fact_id,
        )

    try:
        balances_normalized = normalize_ssqm0004_balances(
            raw_record=balances_raw_record,
            raw_envelope=balances_raw_envelope,
            request=balances_normalization_request,
        )
    except (TypeError, ValueError):
        # Raw remains durable; canonical batch is not attempted.
        return _failure(
            "BALANCES_NORMALIZATION_FAILED",
            raw_balances_fact_id=balances_raw_record.fact_id,
        )

    holdings_facts = ()
    raw_holdings_fact_id = None
    if holdings_capital_normalization_request is not None:
        if holdings_raw_fact_id is None or holdings_raw_envelope is None:
            raise ValueError("holdings raw provenance required")
        holdings_raw_record = fact_store.get_by_fact_id(holdings_raw_fact_id)
        fact_store.verify_integrity(holdings_raw_record.fact_id)
        if holdings_raw_record.payload != holdings_raw_envelope.payload:
            raise ValueError("holdings raw envelope mismatch")
        try:
            validate_freshness(
                collected_at=holdings_raw_record.collected_at,
                now=now,
                policy=policy,
            )
            holdings_normalized = normalize_ssqm2952_capital_facts(
                raw_record=holdings_raw_record,
                raw_envelope=holdings_raw_envelope,
                request=holdings_capital_normalization_request,
            )
        except (TypeError, ValueError):
            return _failure(
                "HOLDINGS_CAPITAL_NORMALIZATION_FAILED",
                raw_balances_fact_id=balances_raw_record.fact_id,
            )
        holdings_facts = holdings_normalized.facts
        raw_holdings_fact_id = holdings_raw_record.fact_id
        if holdings_normalized.exclusion_provenance_append_request is not None:
            exclusion_record = fact_store.append(
                holdings_normalized.exclusion_provenance_append_request
            )
            fact_store.verify_integrity(exclusion_record.fact_id)

    canonical_facts = balances_normalized.facts + holdings_facts
    append_requests = tuple(
        fact.append_request for fact in canonical_facts
    )
    if len(append_requests) == 0:
        raise ValueError("canonical capital batch empty")
    canonical_records = fact_store.append_batch(append_requests)
    for record in canonical_records:
        fact_store.verify_integrity(record.fact_id)

    orderable_cash_fact_id = _id_for_kind(
        canonical_facts, FACT_KIND_ORDERABLE_CASH
    )
    snapshot = ExplicitCapitalSnapshot(
        snapshot_identity.capital_snapshot_id,
        snapshot_identity.account_selector,
        balances_raw_record.provider_id,
        DOMESTIC_CURRENCY_CODE,
        balances_raw_record.collected_at,
        policy.freshness_max_age,
        portfolio_binding.portfolio_snapshot_id,
        portfolio_binding.portfolio_id,
        portfolio_binding.observation_context_id,
        balances_raw_record.fact_id,
        raw_holdings_fact_id,
        orderable_cash_fact_id,
        _id_for_kind(canonical_facts, FACT_KIND_DEPOSIT_TODAY),
        _id_for_kind(canonical_facts, FACT_KIND_DEPOSIT_D1),
        _id_for_kind(canonical_facts, FACT_KIND_DEPOSIT_D2),
        _id_for_kind(canonical_facts, FACT_KIND_WITHDRAWABLE_CASH),
        _id_for_kind(canonical_facts, FACT_KIND_ORDERABLE_TOTAL),
        (
            None
            if len(
                _ids_for_kind(
                    canonical_facts,
                    FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION,
                )
            )
            == 0
            else _id_for_kind(
                canonical_facts,
                FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION,
            )
        ),
        _ids_for_kind(canonical_facts, FACT_KIND_POSITION_MARKET_VALUE),
        SIZING_AUTHORITY_NONE,
    )
    records_by_id = {
        record.fact_id: record for record in canonical_records
    }
    validate_capital_snapshot_consistency(
        snapshot,
        records_by_id=records_by_id,
    )
    return ExplicitCapitalFactPlaneResult(
        "success",
        None,
        snapshot,
        balances_raw_record.fact_id,
        tuple(record.fact_id for record in canonical_records),
    )


def run_kb_capital_fact_plane_with_portfolio_slice(
    *,
    portfolio_slice_kwargs: dict,
    adapter,
    balances_collect_request: ExplicitBrokerCollectRequest,
    balances_raw_fact_id: str,
    balances_normalization_request: ExplicitBalancesNormalizationRequest,
    fact_store: FactStore,
    snapshot_identity: ExplicitCapitalSnapshotIdentity,
    policy: ExplicitCapitalFactPolicy,
    now: datetime,
    holdings_capital_normalization_request: (
        ExplicitHoldingsCapitalNormalizationRequest | None
    ) = None,
) -> tuple[object, ExplicitCapitalFactPlaneResult]:
    """Compose First Slice holdings path with SSQM0004 capital path."""
    if type(portfolio_slice_kwargs) is not dict:
        raise TypeError("portfolio_slice_kwargs must be dict")
    portfolio_result = run_kb_portfolio_vertical_slice(
        **portfolio_slice_kwargs
    )
    holdings_raw_fact_id = None
    holdings_raw_envelope = None
    portfolio_binding = ExplicitCapitalPortfolioBinding(
        None,
        None,
        None,
    )
    if (
        portfolio_result.result_kind == "success"
        and portfolio_result.snapshot is not None
    ):
        raw_id = None
        if portfolio_result.ingress is not None:
            raw_id = portfolio_result.ingress.raw_fact_id
        elif "raw_fact_id" in portfolio_slice_kwargs:
            raw_id = portfolio_slice_kwargs["raw_fact_id"]
        if raw_id is not None:
            holdings_raw_record = fact_store.get_by_fact_id(raw_id)
            holdings_raw_fact_id = holdings_raw_record.fact_id
            holdings_raw_envelope = ExplicitProviderPayloadEnvelope(
                holdings_raw_record.envelope_id,
                holdings_raw_record.provider_id,
                holdings_raw_record.source_class,
                holdings_raw_record.collected_at,
                holdings_raw_record.status,
                holdings_raw_record.payload,
                None,
                portfolio_slice_kwargs[
                    "collect_request"
                ].request_correlation_id,
            )
        portfolio_binding = ExplicitCapitalPortfolioBinding(
            portfolio_result.snapshot.portfolio_snapshot_id,
            portfolio_slice_kwargs[
                "snapshot_identity"
            ].portfolio_id,
            portfolio_slice_kwargs[
                "snapshot_identity"
            ].observation_context_id,
        )
    holdings_request = None
    if (
        holdings_raw_fact_id is not None
        and holdings_raw_envelope is not None
    ):
        holdings_request = holdings_capital_normalization_request
    capital_result = run_kb_capital_fact_plane(
        adapter=adapter,
        balances_collect_request=balances_collect_request,
        balances_raw_fact_id=balances_raw_fact_id,
        balances_normalization_request=balances_normalization_request,
        fact_store=fact_store,
        snapshot_identity=snapshot_identity,
        portfolio_binding=portfolio_binding,
        policy=policy,
        now=now,
        holdings_raw_fact_id=holdings_raw_fact_id,
        holdings_raw_envelope=holdings_raw_envelope,
        holdings_capital_normalization_request=holdings_request,
    )
    return portfolio_result, capital_result
