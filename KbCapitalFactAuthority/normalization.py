from __future__ import annotations

from FactStore.models import (
    ExplicitFactAppendRequest,
    ExplicitStoredFactRecord,
)
from ProviderGateway.models import ExplicitProviderPayloadEnvelope

from KbCapitalFactAuthority.decimal_text import (
    parse_broker_amount,
    require_present_amount,
)
from KbCapitalFactAuthority.models import (
    ExplicitBalancesNormalizationRequest,
    ExplicitBalancesNormalizationResult,
    ExplicitCapitalFactBinding,
    ExplicitDomesticCapitalRowExclusion,
    ExplicitExactAmount,
    ExplicitHoldingsCapitalNormalizationRequest,
    ExplicitHoldingsCapitalNormalizationResult,
    ExplicitNormalizedCapitalFact,
)
from KbCapitalFactAuthority.validation import (
    validate_balances_normalization_request,
    validate_domestic_currency_code,
    validate_holdings_capital_normalization_request,
    validate_orderable_cash_semantic_safety,
)
from KbCapitalFactAuthority.vocabularies import (
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
    SIZING_AUTHORITY_NONE,
)


def _require_raw_broker_success(
    *,
    raw_record: ExplicitStoredFactRecord,
    raw_envelope: ExplicitProviderPayloadEnvelope,
    raw_fact_id: str,
) -> dict:
    if type(raw_record) is not ExplicitStoredFactRecord:
        raise TypeError("raw_record must be ExplicitStoredFactRecord")
    if type(raw_envelope) is not ExplicitProviderPayloadEnvelope:
        raise TypeError(
            "raw_envelope must be ExplicitProviderPayloadEnvelope"
        )
    if raw_record.fact_id != raw_fact_id:
        raise ValueError("raw fact identity mismatch")
    if raw_record.envelope_id != raw_envelope.envelope_id:
        raise ValueError("raw envelope identity mismatch")
    if raw_record.provider_id != "kb_open_api":
        raise ValueError("raw provider must be kb_open_api")
    if raw_record.source_class != "broker_fact":
        raise ValueError("raw source_class must be broker_fact")
    if raw_record.status != "success":
        raise ValueError("raw status must be success")
    if raw_record.payload != raw_envelope.payload:
        raise ValueError("raw payload provenance mismatch")
    if raw_record.collected_at != raw_envelope.collected_at:
        raise ValueError("raw collected_at provenance mismatch")
    payload = raw_record.payload
    if type(payload) is not dict:
        raise TypeError("raw payload must be dict")
    header = payload.get("dataHeader")
    body = payload.get("dataBody")
    if type(header) is not dict:
        raise TypeError("dataHeader must be dict")
    if header.get("processFlag") != "A":
        raise ValueError("processFlag must be A")
    if type(body) is not dict:
        raise TypeError("dataBody must be dict")
    return body


def _amount_payload(amount: ExplicitExactAmount) -> dict:
    return {
        "amount_presence": amount.presence,
        "amount": amount.canonical_text,
        "raw_amount": amount.raw_text,
    }


def _build_fact(
    *,
    binding: ExplicitCapitalFactBinding,
    raw_record: ExplicitStoredFactRecord,
    raw_envelope: ExplicitProviderPayloadEnvelope,
    account_selector: str,
    currency_code: str,
    fact_kind: str,
    broker_field: str,
    amount: ExplicitExactAmount,
    extra: dict | None = None,
) -> ExplicitNormalizedCapitalFact:
    payload = {
        "fact_kind": fact_kind,
        "raw_fact_id": raw_record.fact_id,
        "raw_envelope_id": raw_record.envelope_id,
        "account_selector": account_selector,
        "currency_code": currency_code,
        "broker_field": broker_field,
        **_amount_payload(amount),
    }
    if extra is not None:
        payload.update(extra)
    envelope = ExplicitProviderPayloadEnvelope(
        binding.envelope_id,
        raw_record.provider_id,
        "broker_fact",
        raw_record.collected_at,
        "success",
        payload,
        None,
        raw_envelope.request_correlation_id,
    )
    append_request = ExplicitFactAppendRequest(
        binding.fact_id,
        envelope,
        binding.superseded_fact_id,
    )
    return ExplicitNormalizedCapitalFact(
        append_request,
        fact_kind,
        broker_field,
        amount,
    )


def normalize_ssqm0004_balances(
    *,
    raw_record: ExplicitStoredFactRecord,
    raw_envelope: ExplicitProviderPayloadEnvelope,
    request: ExplicitBalancesNormalizationRequest,
) -> ExplicitBalancesNormalizationResult:
    validate_balances_normalization_request(request)
    body = _require_raw_broker_success(
        raw_record=raw_record,
        raw_envelope=raw_envelope,
        raw_fact_id=request.raw_fact_id,
    )
    orderable = require_present_amount(
        parse_broker_amount(
            body.get(BROKER_FIELD_ORDERABLE_CASH),
            field_name=BROKER_FIELD_ORDERABLE_CASH,
            allow_missing=False,
        ),
        field_name=BROKER_FIELD_ORDERABLE_CASH,
    )
    validate_orderable_cash_semantic_safety(
        broker_field=BROKER_FIELD_ORDERABLE_CASH,
        raw_body=body,
        amount=orderable,
    )
    specs = (
        (
            request.orderable_cash,
            FACT_KIND_ORDERABLE_CASH,
            BROKER_FIELD_ORDERABLE_CASH,
            orderable,
            {"authority": "BROKER_ORDERABLE_CASH_CEILING_NOT_DEPLOYABLE"},
        ),
        (
            request.deposit_today,
            FACT_KIND_DEPOSIT_TODAY,
            BROKER_FIELD_DEPOSIT_TODAY,
            parse_broker_amount(
                body.get(BROKER_FIELD_DEPOSIT_TODAY),
                field_name=BROKER_FIELD_DEPOSIT_TODAY,
                allow_missing=True,
            ),
            None,
        ),
        (
            request.deposit_d1,
            FACT_KIND_DEPOSIT_D1,
            BROKER_FIELD_DEPOSIT_D1,
            parse_broker_amount(
                body.get(BROKER_FIELD_DEPOSIT_D1),
                field_name=BROKER_FIELD_DEPOSIT_D1,
                allow_missing=True,
            ),
            None,
        ),
        (
            request.deposit_d2,
            FACT_KIND_DEPOSIT_D2,
            BROKER_FIELD_DEPOSIT_D2,
            parse_broker_amount(
                body.get(BROKER_FIELD_DEPOSIT_D2),
                field_name=BROKER_FIELD_DEPOSIT_D2,
                allow_missing=True,
            ),
            None,
        ),
        (
            request.withdrawable_cash,
            FACT_KIND_WITHDRAWABLE_CASH,
            BROKER_FIELD_WITHDRAWABLE_CASH,
            parse_broker_amount(
                body.get(BROKER_FIELD_WITHDRAWABLE_CASH),
                field_name=BROKER_FIELD_WITHDRAWABLE_CASH,
                allow_missing=True,
            ),
            {"authority": "WITHDRAWABLE_NOT_ALLOCATION_CEILING"},
        ),
        (
            request.orderable_total,
            FACT_KIND_ORDERABLE_TOTAL,
            BROKER_FIELD_ORDERABLE_TOTAL,
            parse_broker_amount(
                body.get(BROKER_FIELD_ORDERABLE_TOTAL),
                field_name=BROKER_FIELD_ORDERABLE_TOTAL,
                allow_missing=True,
            ),
            {"authority": "ORDERABLE_TOTAL_DISTINCT_FROM_ORDERABLE_CASH"},
        ),
    )
    facts = tuple(
        _build_fact(
            binding=binding,
            raw_record=raw_record,
            raw_envelope=raw_envelope,
            account_selector=request.account_selector,
            currency_code=request.currency_code,
            fact_kind=kind,
            broker_field=field,
            amount=amount,
            extra=extra,
        )
        for binding, kind, field, amount, extra in specs
    )
    return ExplicitBalancesNormalizationResult(
        raw_record.fact_id,
        raw_record.collected_at,
        facts,
    )


_FOREIGN_POSITION_CLASSES = frozenset({"외화증권", "외화증권(M)"})
_EXCLUSION_REASON_NON_DOMESTIC = "EXCLUDED_NON_DOMESTIC"
_EXCLUSION_FACT_KIND = "kb_ssqm2952_domestic_projection_exclusions"


def _is_semantic_blank_currency(value: str) -> bool:
    return value.strip() == ""


def _row_projection_disposition(
    position_class: str, raw_currency: str
) -> str:
    if position_class in _FOREIGN_POSITION_CLASSES:
        return "exclude"
    if _is_semantic_blank_currency(raw_currency):
        return "project"
    if raw_currency == DOMESTIC_CURRENCY_CODE:
        return "project"
    if raw_currency.strip() == DOMESTIC_CURRENCY_CODE:
        raise ValueError("unknown or non-domestic currency fail-closed")
    return "exclude"


def _build_capital_exclusion_provenance_request(
    *,
    request: ExplicitHoldingsCapitalNormalizationRequest,
    raw_record: ExplicitStoredFactRecord,
    raw_envelope: ExplicitProviderPayloadEnvelope,
    exclusions: tuple[ExplicitDomesticCapitalRowExclusion, ...],
    domestic_projected_count: int,
    record1_observed_count: int,
) -> ExplicitFactAppendRequest:
    fact_id = request.exclusion_provenance_fact_id
    envelope_id = request.exclusion_provenance_envelope_id
    if type(fact_id) is not str or fact_id.strip() == "":
        raise ValueError("exclusion provenance identity required")
    if type(envelope_id) is not str or envelope_id.strip() == "":
        raise ValueError("exclusion provenance identity required")
    if fact_id == request.raw_fact_id:
        raise ValueError("exclusion provenance fact_id collision")
    if fact_id == request.account_valuation.fact_id:
        raise ValueError("exclusion provenance fact_id collision")
    for binding in request.position_bindings:
        if fact_id == binding.fact_id or envelope_id == binding.envelope_id:
            raise ValueError("exclusion provenance identity collision")
    payload = {
        "fact_kind": _EXCLUSION_FACT_KIND,
        "raw_fact_id": raw_record.fact_id,
        "raw_envelope_id": raw_record.envelope_id,
        "account_selector": request.account_selector,
        "record1_observed_count": record1_observed_count,
        "domestic_projected_count": domestic_projected_count,
        "excluded_count": len(exclusions),
        "exclusion_reason": _EXCLUSION_REASON_NON_DOMESTIC,
        "exclusions": [
            {
                "row_index": item.row_index,
                "raw_currency_code": item.raw_currency_code,
                "position_class": item.position_class,
                "provider_symbol": item.provider_symbol,
                "reason": item.reason,
            }
            for item in exclusions
        ],
    }
    envelope = ExplicitProviderPayloadEnvelope(
        envelope_id,
        raw_record.provider_id,
        "broker_fact",
        raw_record.collected_at,
        "success",
        payload,
        None,
        raw_envelope.request_correlation_id,
    )
    return ExplicitFactAppendRequest(fact_id, envelope, None)


def normalize_ssqm2952_capital_facts(
    *,
    raw_record: ExplicitStoredFactRecord,
    raw_envelope: ExplicitProviderPayloadEnvelope,
    request: ExplicitHoldingsCapitalNormalizationRequest,
) -> ExplicitHoldingsCapitalNormalizationResult:
    validate_holdings_capital_normalization_request(request)
    body = _require_raw_broker_success(
        raw_record=raw_record,
        raw_envelope=raw_envelope,
        raw_fact_id=request.raw_fact_id,
    )
    valuation_amount = parse_broker_amount(
        body.get(BROKER_FIELD_ACCOUNT_VALUATION),
        field_name=BROKER_FIELD_ACCOUNT_VALUATION,
        allow_missing=True,
    )
    facts = [
        _build_fact(
            binding=request.account_valuation,
            raw_record=raw_record,
            raw_envelope=raw_envelope,
            account_selector=request.account_selector,
            currency_code=DOMESTIC_CURRENCY_CODE,
            fact_kind=FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION,
            broker_field=BROKER_FIELD_ACCOUNT_VALUATION,
            amount=valuation_amount,
            extra={
                "sizing_authority": SIZING_AUTHORITY_NONE,
                "authority_note": (
                    "BROKER-REPORTED ACCOUNT VALUATION ONLY — "
                    "NOT sizing/weights/investable"
                ),
            },
        )
    ]
    rows = body.get("Record1")
    if type(rows) is not list:
        raise TypeError("Record1 must be list")
    binding_by_identity = {
        (
            item.account_selector,
            item.position_class,
            item.currency_code,
            item.provider_symbol,
        ): item
        for item in request.position_bindings
    }
    seen = set()
    exclusions: list[ExplicitDomesticCapitalRowExclusion] = []
    domestic_count = 0
    for row_index, row in enumerate(rows):
        if type(row) is not dict:
            raise TypeError("Record1 row must be dict")
        clsf = row.get("clsf")
        crncy_cd = row.get("crncy_cd")
        is_cd = row.get("is_cd")
        if type(clsf) is not str or type(is_cd) is not str:
            raise TypeError("Record1 identity fields must be str")
        if clsf.strip() == "" or is_cd.strip() == "":
            raise ValueError("Record1 identity fields must not be blank")
        if type(crncy_cd) is not str:
            raise TypeError("crncy_cd must be str")
        disposition = _row_projection_disposition(clsf, crncy_cd)
        if disposition == "exclude":
            exclusions.append(
                ExplicitDomesticCapitalRowExclusion(
                    row_index,
                    crncy_cd,
                    clsf,
                    is_cd,
                    _EXCLUSION_REASON_NON_DOMESTIC,
                )
            )
            continue
        currency = validate_domestic_currency_code(crncy_cd)
        # Bindings use operator currency_code (KRW); broker blank maps to KRW.
        binding_identity = (
            request.account_selector,
            clsf,
            DOMESTIC_CURRENCY_CODE,
            is_cd,
        )
        if binding_identity in seen:
            raise ValueError("duplicate canonical response identity")
        seen.add(binding_identity)
        binding = binding_by_identity.get(binding_identity)
        if binding is None:
            raise ValueError("missing explicit position MV binding")
        if binding.currency_code != currency:
            raise ValueError("position currency binding mismatch")
        quantity = parse_broker_amount(
            row.get("hld_q"),
            field_name="hld_q",
            allow_missing=False,
        )
        market_value = parse_broker_amount(
            row.get(BROKER_FIELD_POSITION_MARKET_VALUE),
            field_name=BROKER_FIELD_POSITION_MARKET_VALUE,
            allow_missing=False,
        )
        if market_value.presence != AMOUNT_PRESENCE_PRESENT:
            raise ValueError("val_amt must be present for bound rows")
        # Preserve unsettled: hld_q may be zero while val_amt > 0.
        facts.append(
            _build_fact(
                binding=ExplicitCapitalFactBinding(
                    binding.fact_id,
                    binding.envelope_id,
                    binding.superseded_fact_id,
                ),
                raw_record=raw_record,
                raw_envelope=raw_envelope,
                account_selector=request.account_selector,
                currency_code=currency,
                fact_kind=FACT_KIND_POSITION_MARKET_VALUE,
                broker_field=BROKER_FIELD_POSITION_MARKET_VALUE,
                amount=market_value,
                extra={
                    "position_class": binding.position_class,
                    "provider_symbol": binding.provider_symbol,
                    "raw_quantity": quantity.raw_text,
                    "quantity": quantity.canonical_text,
                    "quantity_presence": quantity.presence,
                    "valuation_method": "broker_val_amt",
                },
            )
        )
        domestic_count += 1
    if seen != set(binding_by_identity):
        raise ValueError("unused explicit position MV binding")
    exclusion_tuple = tuple(exclusions)
    provenance_request = None
    if len(exclusion_tuple) > 0:
        provenance_request = _build_capital_exclusion_provenance_request(
            request=request,
            raw_record=raw_record,
            raw_envelope=raw_envelope,
            exclusions=exclusion_tuple,
            domestic_projected_count=domestic_count,
            record1_observed_count=len(rows),
        )
    return ExplicitHoldingsCapitalNormalizationResult(
        raw_record.fact_id,
        raw_record.collected_at,
        tuple(facts),
        exclusion_tuple,
        provenance_request,
    )
