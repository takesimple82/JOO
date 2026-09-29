"""Phase 4 A — Just-in-time / single-transaction TEA freshness.

TEA is NOT long-lived stored trading permission. Immediately before a
theoretical/mock submission the caller must refresh authoritative broker
facts already used by JOO (account binding, SSQM0004.ordr_psbl_csh under
ORDERABLE_CASH_FULL, sellability when selling) and re-validate that the
*exact* sealed OrderIntent remains executable. Fresh facts that prevent
exact execution FAIL CLOSED. No auto-resize / reprice / market conversion.
No new broker authorities or arbitrary TTLs are invented here.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from BrokerExecutionCycle.account_binding import require_mutation_eligible_account
from BrokerExecutionCycle.authorization import assert_tea_binds_intent
from BrokerExecutionCycle.models import (
    OrderIntent,
    OrderableCashFact,
    SellableQuantityFact,
    TradeExecutionAuthorization,
    VerifiedExecutionAccountBinding,
)
from BrokerExecutionCycle.vocabularies import (
    AMOUNT_PRESENCE_PRESENT,
    BROKER_FIELD_ORDR_PSBL_CSH,
    CURRENCY_KRW,
    FAILURE_BUY_CASH_INSUFFICIENT,
    FAILURE_JIT_ACCOUNT_CHANGED,
    FAILURE_JIT_CASH_NOT_FULL,
    FAILURE_JIT_FACTS_INVALIDATE_EXECUTION,
    FAILURE_SELL_EXCEEDS_SELLABLE,
    ORDERABLE_CASH_FULL,
    ORDERABLE_CASH_RESERVE_KRW,
    SIDE_BUY,
    SIDE_SELL,
)


def _exact_notional(order_intent: OrderIntent) -> Decimal:
    return order_intent.limit_price * order_intent.quantity


def assert_jit_fresh_facts_permit_exact_execution(
    *,
    tea: TradeExecutionAuthorization,
    order_intent: OrderIntent,
    account: VerifiedExecutionAccountBinding,
    fresh_orderable_cash: OrderableCashFact,
    fresh_sellable: SellableQuantityFact | None,
    refreshed_at: datetime,
) -> None:
    """Fail closed if refreshed broker facts invalidate exact sealed execution."""
    del refreshed_at  # caller-supplied acquisition timestamp; no invented TTL.
    assert_tea_binds_intent(tea, order_intent)
    require_mutation_eligible_account(account)
    if (
        account.binding_id != order_intent.account_binding_id
        or account.integrity_seal != order_intent.account_binding_seal
        or account.binding_id != tea.account_binding_id
        or account.integrity_seal != tea.account_binding_seal
    ):
        raise ValueError(FAILURE_JIT_ACCOUNT_CHANGED)

    if order_intent.side == SIDE_BUY:
        if type(fresh_orderable_cash) is not OrderableCashFact:
            raise TypeError("fresh OrderableCashFact required")
        if fresh_orderable_cash.broker_field != BROKER_FIELD_ORDR_PSBL_CSH:
            raise ValueError(FAILURE_JIT_CASH_NOT_FULL)
        # Deployable cash authority: SSQM0004.ordr_psbl_csh under ORDERABLE_CASH_FULL.
        # Reserve is frozen at 0; no other cash field may substitute.
        if ORDERABLE_CASH_RESERVE_KRW != "0":
            raise RuntimeError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
        if fresh_orderable_cash.presence != AMOUNT_PRESENCE_PRESENT:
            raise ValueError(FAILURE_JIT_CASH_NOT_FULL)
        if fresh_orderable_cash.currency_code != CURRENCY_KRW:
            raise ValueError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
        if (
            fresh_orderable_cash.amount_krw is None
            or type(fresh_orderable_cash.amount_krw) is not Decimal
            or not fresh_orderable_cash.amount_krw.is_finite()
        ):
            raise ValueError(FAILURE_JIT_CASH_NOT_FULL)
        # Tag the authority class used for this check (documentation invariant).
        if ORDERABLE_CASH_FULL != "ORDERABLE_CASH_FULL":
            raise RuntimeError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
        needed = _exact_notional(order_intent)
        if fresh_orderable_cash.amount_krw < needed:
            raise ValueError(FAILURE_BUY_CASH_INSUFFICIENT)
        return

    if order_intent.side == SIDE_SELL:
        if fresh_sellable is None or type(fresh_sellable) is not SellableQuantityFact:
            raise ValueError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
        if fresh_sellable.instrument_ssam_is_cd != order_intent.ssam_is_cd:
            raise ValueError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
        if fresh_sellable.presence != AMOUNT_PRESENCE_PRESENT:
            raise ValueError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
        if (
            fresh_sellable.sellable_qty is None
            or type(fresh_sellable.sellable_qty) is not Decimal
            or not fresh_sellable.sellable_qty.is_finite()
        ):
            raise ValueError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
        if fresh_sellable.sellable_qty < order_intent.quantity:
            raise ValueError(FAILURE_SELL_EXCEEDS_SELLABLE)
        return

    raise ValueError(FAILURE_JIT_FACTS_INVALIDATE_EXECUTION)
