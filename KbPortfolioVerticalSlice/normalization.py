from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from FactStore.models import (
    ExplicitFactAppendRequest,
    ExplicitStoredFactRecord,
)
from ProviderGateway.models import ExplicitProviderPayloadEnvelope

from KbPortfolioVerticalSlice.models import (
    ExplicitKbNormalizationRequest,
    ExplicitKbNormalizationResult,
    ExplicitNormalizedPosition,
)
from KbPortfolioVerticalSlice.validation import (
    validate_normalization_request,
)


_DECIMAL_TEXT = re.compile(r"^(0|[0-9]+)(\.[0-9]+)?$")
_DOMESTIC_CURRENCY_CODE = "KRW"


def _required_text(row: dict, key: str) -> str:
    value = row.get(key)
    if type(value) is not str:
        raise TypeError(f"{key} must be str")
    if value.strip() == "":
        raise ValueError(f"{key} must not be blank")
    return value


def _raw_currency(row: dict) -> str:
    value = row.get("crncy_cd")
    if type(value) is not str:
        raise TypeError("crncy_cd must be str")
    if value != "" and value.strip() == "":
        raise ValueError("crncy_cd must be blank or KRW")
    if value not in ("", _DOMESTIC_CURRENCY_CODE):
        raise ValueError("unsupported SSQM2952 currency")
    return value


def _quantity(raw: object) -> tuple[str, bool]:
    if type(raw) is not str:
        raise TypeError("hld_q must be str")
    if _DECIMAL_TEXT.fullmatch(raw) is None:
        raise ValueError("hld_q must be unsigned decimal text")
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("hld_q must be finite Decimal") from exc
    if not value.is_finite() or value < Decimal(0):
        raise ValueError("hld_q must be finite and nonnegative")
    canonical = format(value, "f")
    return canonical, value != Decimal(0)


def normalize_ssqm2952(
    *,
    raw_record: ExplicitStoredFactRecord,
    raw_envelope: ExplicitProviderPayloadEnvelope,
    request: ExplicitKbNormalizationRequest,
) -> ExplicitKbNormalizationResult:
    if type(raw_record) is not ExplicitStoredFactRecord:
        raise TypeError("raw_record must be ExplicitStoredFactRecord")
    if type(raw_envelope) is not ExplicitProviderPayloadEnvelope:
        raise TypeError(
            "raw_envelope must be ExplicitProviderPayloadEnvelope"
        )
    validate_normalization_request(request)
    if raw_record.fact_id != request.raw_fact_id:
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
    binding_by_domestic_identity = {}
    for item in request.position_bindings:
        key = (
            item.account_selector,
            item.position_class,
            item.provider_symbol,
        )
        binding_by_domestic_identity.setdefault(key, []).append(item)
    seen = set()
    positions = []
    for row in rows:
        if type(row) is not dict:
            raise TypeError("Record1 row must be dict")
        position_class = _required_text(row, "clsf")
        provider_symbol = _required_text(row, "is_cd")
        raw_currency = _raw_currency(row)
        if raw_currency == "":
            candidates = binding_by_domestic_identity.get(
                (
                    request.account_selector,
                    position_class,
                    provider_symbol,
                ),
                (),
            )
            if len(candidates) != 1:
                raise ValueError(
                    "blank crncy_cd requires one explicit domestic binding"
                )
            binding = candidates[0]
            if binding.currency_code != _DOMESTIC_CURRENCY_CODE:
                raise ValueError(
                    "blank crncy_cd requires explicit KRW binding"
                )
        else:
            binding = binding_by_identity.get(
                (
                    request.account_selector,
                    position_class,
                    raw_currency,
                    provider_symbol,
                )
            )
        identity = (
            request.account_selector,
            position_class,
            _DOMESTIC_CURRENCY_CODE,
            provider_symbol,
        )
        if identity in seen:
            raise ValueError("duplicate canonical response identity")
        seen.add(identity)
        if binding is None:
            raise ValueError("missing explicit position binding")
        if binding.currency_code != _DOMESTIC_CURRENCY_CODE:
            raise ValueError("SSQM2952 binding currency must be KRW")
        quantity, active = _quantity(row.get("hld_q"))
        canonical_payload = {
            "fact_kind": "kb_ssqm2952_position",
            "raw_fact_id": raw_record.fact_id,
            "raw_envelope_id": raw_record.envelope_id,
            "account_selector": binding.account_selector,
            "position_class": binding.position_class,
            "currency_code": binding.currency_code,
            "raw_currency_code": raw_currency,
            "provider_symbol": binding.provider_symbol,
            "quantity": quantity,
            "raw_quantity": row["hld_q"],
        }
        envelope = ExplicitProviderPayloadEnvelope(
            binding.envelope_id,
            raw_record.provider_id,
            "broker_fact",
            raw_record.collected_at,
            "success",
            canonical_payload,
            None,
            raw_envelope.request_correlation_id,
        )
        append_request = ExplicitFactAppendRequest(
            binding.fact_id,
            envelope,
            binding.superseded_fact_id,
        )
        positions.append(
            ExplicitNormalizedPosition(
                append_request,
                binding.position_id,
                binding.portfolio_subject_id,
                quantity,
                active,
            )
        )
    if len(seen) != len(request.position_bindings):
        raise ValueError("unused explicit position binding")
    return ExplicitKbNormalizationResult(
        raw_record.fact_id,
        raw_record.collected_at,
        tuple(positions),
    )
