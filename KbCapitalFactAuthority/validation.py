from __future__ import annotations

from datetime import datetime, timedelta, timezone

from FactStore.models import ExplicitStoredFactRecord

from KbCapitalFactAuthority.models import (
    ExplicitBalancesNormalizationRequest,
    ExplicitCapitalFactBinding,
    ExplicitCapitalFactPolicy,
    ExplicitCapitalPortfolioBinding,
    ExplicitCapitalSnapshot,
    ExplicitCapitalSnapshotIdentity,
    ExplicitExactAmount,
    ExplicitHoldingsCapitalNormalizationRequest,
    ExplicitPositionMarketValueBinding,
)
from KbCapitalFactAuthority.vocabularies import (
    AMOUNT_PRESENCE_MISSING,
    AMOUNT_PRESENCE_PRESENT,
    BROKER_FIELD_ACCOUNT_VALUATION,
    BROKER_FIELD_DEPOSIT_D1,
    BROKER_FIELD_DEPOSIT_D2,
    BROKER_FIELD_DEPOSIT_TODAY,
    BROKER_FIELD_ORDERABLE_CASH,
    BROKER_FIELD_ORDERABLE_TOTAL,
    BROKER_FIELD_POSITION_MARKET_VALUE,
    BROKER_FIELD_WITHDRAWABLE_CASH,
    DOMESTIC_CURRENCY_CODE,
    FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION,
    FACT_KIND_DEPOSIT_D1,
    FACT_KIND_DEPOSIT_D2,
    FACT_KIND_DEPOSIT_TODAY,
    FACT_KIND_ORDERABLE_CASH,
    FACT_KIND_ORDERABLE_TOTAL,
    FACT_KIND_POSITION_MARKET_VALUE,
    FACT_KIND_WITHDRAWABLE_CASH,
    FORBIDDEN_ORDERABLE_CASH_SUBSTITUTE_FIELDS,
    FORBIDDEN_ORDERABLE_CASH_SUBSTITUTE_PREFIXES,
    SIZING_AUTHORITY_NONE,
)


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


def validate_exact_amount(amount: ExplicitExactAmount) -> None:
    if type(amount) is not ExplicitExactAmount:
        raise TypeError("amount must be ExplicitExactAmount")
    if amount.presence == AMOUNT_PRESENCE_MISSING:
        if amount.canonical_text is not None or amount.raw_text is not None:
            raise ValueError("missing amount must not carry text")
        return
    if amount.presence != AMOUNT_PRESENCE_PRESENT:
        raise ValueError("amount presence invalid")
    _nonblank("canonical_text", amount.canonical_text)
    _nonblank("raw_text", amount.raw_text)


def validate_capital_fact_binding(
    binding: ExplicitCapitalFactBinding,
) -> None:
    if type(binding) is not ExplicitCapitalFactBinding:
        raise TypeError("binding must be ExplicitCapitalFactBinding")
    _nonblank("fact_id", binding.fact_id)
    _nonblank("envelope_id", binding.envelope_id)
    _optional_nonblank("superseded_fact_id", binding.superseded_fact_id)
    if binding.superseded_fact_id == binding.fact_id:
        raise ValueError("superseded_fact_id must not equal fact_id")


def validate_balances_normalization_request(
    request: ExplicitBalancesNormalizationRequest,
) -> None:
    if type(request) is not ExplicitBalancesNormalizationRequest:
        raise TypeError(
            "request must be ExplicitBalancesNormalizationRequest"
        )
    _nonblank("raw_fact_id", request.raw_fact_id)
    _nonblank("account_selector", request.account_selector)
    if request.currency_code != DOMESTIC_CURRENCY_CODE:
        raise ValueError("balances currency must be KRW domestic cash-only")
    bindings = (
        request.orderable_cash,
        request.deposit_today,
        request.deposit_d1,
        request.deposit_d2,
        request.withdrawable_cash,
        request.orderable_total,
    )
    fact_ids = set()
    envelope_ids = set()
    for binding in bindings:
        validate_capital_fact_binding(binding)
        if binding.fact_id in fact_ids:
            raise ValueError("duplicate capital fact_id binding")
        if binding.envelope_id in envelope_ids:
            raise ValueError("duplicate capital envelope_id binding")
        fact_ids.add(binding.fact_id)
        envelope_ids.add(binding.envelope_id)


def validate_position_market_value_binding(
    binding: ExplicitPositionMarketValueBinding,
) -> None:
    if type(binding) is not ExplicitPositionMarketValueBinding:
        raise TypeError(
            "binding must be ExplicitPositionMarketValueBinding"
        )
    for name in (
        "account_selector",
        "position_class",
        "currency_code",
        "provider_symbol",
        "fact_id",
        "envelope_id",
    ):
        _nonblank(name, getattr(binding, name))
    _optional_nonblank("superseded_fact_id", binding.superseded_fact_id)
    if binding.superseded_fact_id == binding.fact_id:
        raise ValueError("superseded_fact_id must not equal fact_id")
    currency = binding.currency_code.strip()
    if currency != DOMESTIC_CURRENCY_CODE:
        raise ValueError("unknown or non-domestic currency fail-closed")


def validate_holdings_capital_normalization_request(
    request: ExplicitHoldingsCapitalNormalizationRequest,
) -> None:
    if type(request) is not ExplicitHoldingsCapitalNormalizationRequest:
        raise TypeError(
            "request must be ExplicitHoldingsCapitalNormalizationRequest"
        )
    _nonblank("raw_fact_id", request.raw_fact_id)
    _nonblank("account_selector", request.account_selector)
    validate_capital_fact_binding(request.account_valuation)
    excl_fact = request.exclusion_provenance_fact_id
    excl_env = request.exclusion_provenance_envelope_id
    if excl_fact is None and excl_env is None:
        pass
    elif excl_fact is None or excl_env is None:
        raise ValueError("exclusion provenance identity incomplete")
    else:
        _nonblank("exclusion_provenance_fact_id", excl_fact)
        _nonblank("exclusion_provenance_envelope_id", excl_env)
        if excl_fact == request.raw_fact_id:
            raise ValueError("exclusion provenance fact_id collision")
    if type(request.position_bindings) is not tuple:
        raise TypeError("position_bindings must be tuple")
    identities = set()
    fact_ids = {request.account_valuation.fact_id}
    envelope_ids = {request.account_valuation.envelope_id}
    for binding in request.position_bindings:
        validate_position_market_value_binding(binding)
        if binding.account_selector != request.account_selector:
            raise ValueError("binding account_selector mismatch")
        identity = (
            binding.account_selector,
            binding.position_class,
            binding.currency_code,
            binding.provider_symbol,
        )
        if identity in identities:
            raise ValueError("duplicate position market value binding")
        if binding.fact_id in fact_ids:
            raise ValueError("duplicate capital fact_id binding")
        if binding.envelope_id in envelope_ids:
            raise ValueError("duplicate capital envelope_id binding")
        identities.add(identity)
        fact_ids.add(binding.fact_id)
        envelope_ids.add(binding.envelope_id)
    if excl_fact is not None:
        if excl_fact in fact_ids:
            raise ValueError("exclusion provenance fact_id collision")
        if excl_env in envelope_ids:
            raise ValueError("exclusion provenance envelope_id collision")


def validate_capital_fact_policy(
    policy: ExplicitCapitalFactPolicy,
) -> None:
    if type(policy) is not ExplicitCapitalFactPolicy:
        raise TypeError("policy must be ExplicitCapitalFactPolicy")
    if type(policy.freshness_max_age) is not timedelta:
        raise TypeError("freshness_max_age must be timedelta")
    if policy.freshness_max_age < timedelta(0):
        raise ValueError("freshness_max_age must not be negative")


def validate_capital_snapshot_identity(
    identity: ExplicitCapitalSnapshotIdentity,
) -> None:
    if type(identity) is not ExplicitCapitalSnapshotIdentity:
        raise TypeError(
            "identity must be ExplicitCapitalSnapshotIdentity"
        )
    _nonblank("capital_snapshot_id", identity.capital_snapshot_id)
    _nonblank("account_selector", identity.account_selector)


def validate_capital_portfolio_binding(
    binding: ExplicitCapitalPortfolioBinding,
) -> None:
    if type(binding) is not ExplicitCapitalPortfolioBinding:
        raise TypeError(
            "binding must be ExplicitCapitalPortfolioBinding"
        )
    _optional_nonblank(
        "portfolio_snapshot_id", binding.portfolio_snapshot_id
    )
    _optional_nonblank("portfolio_id", binding.portfolio_id)
    _optional_nonblank(
        "observation_context_id", binding.observation_context_id
    )


def validate_domestic_currency_code(currency_code: object) -> str:
    if type(currency_code) is not str:
        raise TypeError("currency_code must be str")
    normalized = currency_code.strip()
    if normalized == "":
        return DOMESTIC_CURRENCY_CODE
    if normalized != DOMESTIC_CURRENCY_CODE:
        raise ValueError("unknown or non-domestic currency fail-closed")
    return DOMESTIC_CURRENCY_CODE


def assert_orderable_cash_field(broker_field: str) -> None:
    _nonblank("broker_field", broker_field)
    if broker_field != BROKER_FIELD_ORDERABLE_CASH:
        raise ValueError(
            "OrderableCashFact broker_field must be ordr_psbl_csh"
        )
    if broker_field in FORBIDDEN_ORDERABLE_CASH_SUBSTITUTE_FIELDS:
        raise ValueError("forbidden orderable cash substitute")
    for prefix in FORBIDDEN_ORDERABLE_CASH_SUBSTITUTE_PREFIXES:
        if broker_field.startswith(prefix):
            raise ValueError("forbidden orderable cash substitute prefix")


def validate_orderable_cash_semantic_safety(
    *,
    broker_field: str,
    raw_body: dict,
    amount: ExplicitExactAmount,
) -> None:
    assert_orderable_cash_field(broker_field)
    if type(raw_body) is not dict:
        raise TypeError("raw_body must be dict")
    validate_exact_amount(amount)
    if amount.presence != AMOUNT_PRESENCE_PRESENT:
        raise ValueError("OrderableCashFact amount must be present")
    raw_value = raw_body.get(BROKER_FIELD_ORDERABLE_CASH)
    if raw_value != amount.raw_text:
        raise ValueError(
            "OrderableCashFact must equal raw ordr_psbl_csh"
        )
    for field in FORBIDDEN_ORDERABLE_CASH_SUBSTITUTE_FIELDS:
        substitute = raw_body.get(field)
        if (
            substitute is not None
            and type(substitute) is str
            and substitute == amount.raw_text
            and field != BROKER_FIELD_ORDERABLE_CASH
        ):
            # Equality alone is allowed; substitution of field identity is not.
            pass
    if amount.raw_text != raw_body.get(BROKER_FIELD_ORDERABLE_CASH):
        raise ValueError("orderable cash semantic mismatch")


def validate_freshness(
    *,
    collected_at: datetime,
    now: datetime,
    policy: ExplicitCapitalFactPolicy,
) -> None:
    validate_capital_fact_policy(policy)
    _utc("collected_at", collected_at)
    _utc("now", now)
    if now < collected_at:
        raise ValueError("now precedes collected_at")
    if now - collected_at > policy.freshness_max_age:
        raise ValueError("capital facts stale under freshness policy")


def _payload_kind(record: ExplicitStoredFactRecord) -> str:
    payload = record.payload
    if type(payload) is not dict:
        raise TypeError("canonical payload must be dict")
    kind = payload.get("fact_kind")
    if type(kind) is not str or kind.strip() == "":
        raise ValueError("canonical fact_kind missing")
    return kind


def _payload_broker_field(record: ExplicitStoredFactRecord) -> str:
    field = record.payload.get("broker_field")
    if type(field) is not str or field.strip() == "":
        raise ValueError("canonical broker_field missing")
    return field


def validate_capital_snapshot_consistency(
    snapshot: ExplicitCapitalSnapshot,
    *,
    records_by_id: dict[str, ExplicitStoredFactRecord],
) -> None:
    if type(snapshot) is not ExplicitCapitalSnapshot:
        raise TypeError("snapshot must be ExplicitCapitalSnapshot")
    if snapshot.sizing_authority != SIZING_AUTHORITY_NONE:
        raise ValueError("CapitalSnapshot has no sizing authority")
    if snapshot.currency_code != DOMESTIC_CURRENCY_CODE:
        raise ValueError("CapitalSnapshot currency must be KRW")
    required = {
        snapshot.orderable_cash_fact_id: (
            FACT_KIND_ORDERABLE_CASH,
            BROKER_FIELD_ORDERABLE_CASH,
        ),
        snapshot.deposit_today_fact_id: (
            FACT_KIND_DEPOSIT_TODAY,
            BROKER_FIELD_DEPOSIT_TODAY,
        ),
        snapshot.deposit_d1_fact_id: (
            FACT_KIND_DEPOSIT_D1,
            BROKER_FIELD_DEPOSIT_D1,
        ),
        snapshot.deposit_d2_fact_id: (
            FACT_KIND_DEPOSIT_D2,
            BROKER_FIELD_DEPOSIT_D2,
        ),
        snapshot.withdrawable_cash_fact_id: (
            FACT_KIND_WITHDRAWABLE_CASH,
            BROKER_FIELD_WITHDRAWABLE_CASH,
        ),
        snapshot.orderable_total_fact_id: (
            FACT_KIND_ORDERABLE_TOTAL,
            BROKER_FIELD_ORDERABLE_TOTAL,
        ),
    }
    ids = list(required)
    if len(set(ids)) != len(ids):
        raise ValueError("capital fact identities must remain distinct")
    if snapshot.withdrawable_cash_fact_id == snapshot.orderable_cash_fact_id:
        raise ValueError("withdrawable must not equal orderable cash")
    if snapshot.orderable_total_fact_id == snapshot.orderable_cash_fact_id:
        raise ValueError("orderable total must not equal orderable cash")
    for fact_id, (kind, field) in required.items():
        record = records_by_id.get(fact_id)
        if record is None:
            raise ValueError("required capital fact missing from store")
        if _payload_kind(record) != kind:
            raise ValueError("capital fact kind mismatch")
        if _payload_broker_field(record) != field:
            raise ValueError("capital fact broker_field mismatch")
        if kind == FACT_KIND_ORDERABLE_CASH:
            assert_orderable_cash_field(field)
            presence = record.payload.get("amount_presence")
            if presence != AMOUNT_PRESENCE_PRESENT:
                raise ValueError("orderable cash must be present")
    if snapshot.broker_reported_account_valuation_fact_id is not None:
        record = records_by_id[
            snapshot.broker_reported_account_valuation_fact_id
        ]
        if _payload_kind(record) != FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION:
            raise ValueError("account valuation kind mismatch")
        if _payload_broker_field(record) != BROKER_FIELD_ACCOUNT_VALUATION:
            raise ValueError("account valuation field mismatch")
        if record.payload.get("sizing_authority") != SIZING_AUTHORITY_NONE:
            raise ValueError(
                "nt_asts_val_amt is not sizing/weights/investable authority"
            )
    for fact_id in snapshot.position_market_value_fact_ids:
        record = records_by_id[fact_id]
        if _payload_kind(record) != FACT_KIND_POSITION_MARKET_VALUE:
            raise ValueError("position market value kind mismatch")
        if _payload_broker_field(record) != BROKER_FIELD_POSITION_MARKET_VALUE:
            raise ValueError("position market value field mismatch")
        if "computed_from_quantity_price" in record.payload:
            raise ValueError("position MV must never be hld_q times now_prc")
