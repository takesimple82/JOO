from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from CapitalAllocationCycle.integrity import integrity_seal
from CapitalAllocationCycle.models import HumanInvestmentPolicy
from CapitalAllocationCycle.vocabularies import (
    CAPITAL_SOURCING_MODE_ROTATION_ALLOWED,
    CURRENCY_KRW,
    DEPLOYABLE_CAPITAL_MODE_ORDERABLE_CASH_FULL,
    HIP_V1_POLICY_ID,
    HIP_V1_VERSION,
    ON_INVALIDATE_THESIS_BLOCK_AND_ALLOW_REDUCE_LEGS,
    PROFIT_REALIZATION_MODE_DEFER,
)

# Frozen HIP V1 numeric policy — do not invent alternate ceilings here.
HIP_V1_EXPLICIT_RESERVE_KRW = Decimal("0")
HIP_V1_MAX_POSITION_MARKET_VALUE_KRW = Decimal("100000000")


def hip_seal_payload(
    *,
    policy_id: str,
    version: str,
    effective_at: datetime,
    currency_code: str,
    deployable_capital_mode: str,
    explicit_reserve_krw: Decimal,
    max_position_market_value_krw: Decimal,
    capital_sourcing_mode: str,
    on_invalidate_thesis: str,
    leverage_allowed: bool,
    approval_required: bool,
    profit_realization_mode: str,
) -> dict:
    return {
        "policy_id": policy_id,
        "version": version,
        "effective_at": effective_at,
        "currency_code": currency_code,
        "deployable_capital_mode": deployable_capital_mode,
        "explicit_reserve_krw": explicit_reserve_krw,
        "max_position_market_value_krw": max_position_market_value_krw,
        "capital_sourcing_mode": capital_sourcing_mode,
        "on_invalidate_thesis": on_invalidate_thesis,
        "leverage_allowed": leverage_allowed,
        "approval_required": approval_required,
        "profit_realization_mode": profit_realization_mode,
    }


def seal_human_investment_policy(
    *,
    policy_id: str,
    version: str,
    effective_at: datetime,
    currency_code: str,
    deployable_capital_mode: str,
    explicit_reserve_krw: Decimal,
    max_position_market_value_krw: Decimal,
    capital_sourcing_mode: str,
    on_invalidate_thesis: str,
    leverage_allowed: bool,
    approval_required: bool,
    profit_realization_mode: str,
) -> HumanInvestmentPolicy:
    payload = hip_seal_payload(
        policy_id=policy_id,
        version=version,
        effective_at=effective_at,
        currency_code=currency_code,
        deployable_capital_mode=deployable_capital_mode,
        explicit_reserve_krw=explicit_reserve_krw,
        max_position_market_value_krw=max_position_market_value_krw,
        capital_sourcing_mode=capital_sourcing_mode,
        on_invalidate_thesis=on_invalidate_thesis,
        leverage_allowed=leverage_allowed,
        approval_required=approval_required,
        profit_realization_mode=profit_realization_mode,
    )
    return HumanInvestmentPolicy(
        policy_id,
        version,
        effective_at,
        currency_code,
        deployable_capital_mode,
        explicit_reserve_krw,
        max_position_market_value_krw,
        capital_sourcing_mode,
        on_invalidate_thesis,
        leverage_allowed,
        approval_required,
        profit_realization_mode,
        integrity_seal(payload),
    )


def build_frozen_hip_v1(*, effective_at: datetime | None = None) -> HumanInvestmentPolicy:
    """Encode frozen HIP V1 exactly. Explicit reserve is present Decimal 0, never missing."""
    when = effective_at if effective_at is not None else datetime(2026, 9, 26, 0, 0, tzinfo=timezone.utc)
    return seal_human_investment_policy(
        policy_id=HIP_V1_POLICY_ID,
        version=HIP_V1_VERSION,
        effective_at=when,
        currency_code=CURRENCY_KRW,
        deployable_capital_mode=DEPLOYABLE_CAPITAL_MODE_ORDERABLE_CASH_FULL,
        explicit_reserve_krw=HIP_V1_EXPLICIT_RESERVE_KRW,
        max_position_market_value_krw=HIP_V1_MAX_POSITION_MARKET_VALUE_KRW,
        capital_sourcing_mode=CAPITAL_SOURCING_MODE_ROTATION_ALLOWED,
        on_invalidate_thesis=ON_INVALIDATE_THESIS_BLOCK_AND_ALLOW_REDUCE_LEGS,
        leverage_allowed=False,
        approval_required=True,
        profit_realization_mode=PROFIT_REALIZATION_MODE_DEFER,
    )


def verify_hip_integrity(hip: HumanInvestmentPolicy) -> None:
    expected = integrity_seal(
        hip_seal_payload(
            policy_id=hip.policy_id,
            version=hip.version,
            effective_at=hip.effective_at,
            currency_code=hip.currency_code,
            deployable_capital_mode=hip.deployable_capital_mode,
            explicit_reserve_krw=hip.explicit_reserve_krw,
            max_position_market_value_krw=hip.max_position_market_value_krw,
            capital_sourcing_mode=hip.capital_sourcing_mode,
            on_invalidate_thesis=hip.on_invalidate_thesis,
            leverage_allowed=hip.leverage_allowed,
            approval_required=hip.approval_required,
            profit_realization_mode=hip.profit_realization_mode,
        )
    )
    if hip.integrity_seal != expected:
        raise ValueError("HIP integrity seal mismatch")
