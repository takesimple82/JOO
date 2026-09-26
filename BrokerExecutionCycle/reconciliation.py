from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import (
    BrokerAcceptanceClassification,
    FillFact,
    OrderStatusFact,
    ReconciliationResult,
)
from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_ACCEPTED,
    ACCEPTANCE_REJECTED,
    ACCEPTANCE_UNKNOWN,
    FAILURE_ACCEPTANCE_AS_FILL,
    FILL_CLAIM_FULL,
    FILL_CLAIM_NONE,
    FILL_CLAIM_PARTIAL,
    FILL_CLAIM_UNKNOWN,
    RECON_INCONCLUSIVE,
    RECON_MATCH,
    RECON_MISMATCH,
)


def fill_fact_from_status(
    *,
    fact_id: str,
    status: OrderStatusFact,
    observed_at: datetime,
) -> FillFact:
    """§19 — do not overclaim. SSQM2341 samples often insufficient → UNKNOWN."""
    payload = {
        "fact_id": fact_id,
        "broker_order_no": status.broker_order_no,
        "fill_claim": status.fill_claim,
        "filled_qty": status.filled_qty,
        "filled_amount_krw": status.filled_amount_krw,
        "status_fact_id": status.fact_id,
        "observed_at": observed_at,
    }
    return FillFact(
        fact_id,
        status.broker_order_no,
        status.fill_claim,
        status.filled_qty,
        status.filled_amount_krw,
        status.fact_id,
        observed_at,
        integrity_seal(payload),
    )


def reconcile_acceptance_and_fill(
    *,
    result_id: str,
    attempt_id: str,
    acceptance: BrokerAcceptanceClassification,
    fill: FillFact | None,
    cash_corroborated: bool | None,
    holdings_corroborated: bool | None,
    reconciled_at: datetime,
) -> ReconciliationResult:
    """§20 acceptance ≠ fill."""
    if (
        acceptance.outcome == ACCEPTANCE_ACCEPTED
        and fill is not None
        and fill.fill_claim in (FILL_CLAIM_FULL, FILL_CLAIM_PARTIAL)
    ):
        status = RECON_MATCH
        detail = "accepted and fill observed"
    elif acceptance.outcome == ACCEPTANCE_ACCEPTED and (
        fill is None or fill.fill_claim in (FILL_CLAIM_NONE, FILL_CLAIM_UNKNOWN)
    ):
        # Acceptance without fill is valid open order — not a fill claim.
        status = RECON_INCONCLUSIVE
        detail = FAILURE_ACCEPTANCE_AS_FILL
    elif acceptance.outcome == ACCEPTANCE_REJECTED:
        if fill is not None and fill.fill_claim in (FILL_CLAIM_FULL, FILL_CLAIM_PARTIAL):
            status = RECON_MISMATCH
            detail = "rejected but fill claimed"
        else:
            status = RECON_MATCH
            detail = "rejected; no fill"
    elif acceptance.outcome == ACCEPTANCE_UNKNOWN:
        status = RECON_INCONCLUSIVE
        detail = "submission outcome unknown"
    else:
        status = RECON_INCONCLUSIVE
        detail = "inconclusive"

    payload = {
        "result_id": result_id,
        "attempt_id": attempt_id,
        "acceptance_outcome": acceptance.outcome,
        "fill_claim": None if fill is None else fill.fill_claim,
        "status": status,
        "cash_corroborated": cash_corroborated,
        "holdings_corroborated": holdings_corroborated,
        "detail": detail,
        "reconciled_at": reconciled_at,
    }
    return ReconciliationResult(
        result_id,
        attempt_id,
        acceptance.outcome,
        FILL_CLAIM_NONE if fill is None else fill.fill_claim,
        status,
        cash_corroborated,
        holdings_corroborated,
        detail,
        reconciled_at,
        integrity_seal(payload),
    )
