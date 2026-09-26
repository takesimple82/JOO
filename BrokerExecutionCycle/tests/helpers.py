from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from CapitalAllocationCycle.approval import record_investment_human_approval
from CapitalAllocationCycle.artifact import seal_approved_allocation_artifact
from CapitalAllocationCycle.hip import build_frozen_hip_v1
from CapitalAllocationCycle.models import (
    AllocationLegProposal,
    CapitalAllocationProposal,
    CapitalFundingProvenance,
    InvestmentHumanApproval,
    SealedApprovedAllocationArtifact,
)
from CapitalAllocationCycle.vocabularies import (
    ALLOCATION_ACTION_INCREASE,
    APPROVAL_DECISION_APPROVED,
    CURRENCY_KRW,
)
from CapitalAllocationCycle.integrity import integrity_seal as cac_seal
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot

from BrokerExecutionCycle.account_binding import (
    seal_unverified_account_binding,
    seal_verified_execution_account_binding,
)
from BrokerExecutionCycle.instrument import seal_instrument_identity_binding
from BrokerExecutionCycle.pretrade import (
    seal_pretrade_fact_bundle,
    seal_proposed_limit_price,
)
from BrokerExecutionCycle.provider_read import (
    normalize_ivu10140_quote,
    normalize_orderable_cash,
    normalize_sellable_quantity,
    normalize_ssqm2341_status,
    seal_session_context,
)
from BrokerExecutionCycle.vocabularies import SIDE_BUY

UTC = timezone.utc
NOW = datetime(2026, 9, 26, 10, 0, tzinfo=UTC)
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def capital_snapshot():
    from datetime import timedelta

    return ExplicitCapitalSnapshot(
        "capital-snapshot-001",
        "account-primary",
        "kb_open_api",
        CURRENCY_KRW,
        NOW,
        timedelta(seconds=3600),
        "portfolio-snapshot-001",
        "portfolio-001",
        "observation-001",
        "balances-raw-001",
        "holdings-raw-001",
        "orderable-cash-fact-001",
        "deposit-today-fact-001",
        "deposit-d1-fact-001",
        "deposit-d2-fact-001",
        "withdrawable-fact-001",
        "orderable-total-fact-001",
        "account-valuation-fact-001",
        ("position-mv-fact-a",),
        "NOT_SIZING_AUTHORITY",
    )


def _proposal(hip, snapshot):
    leg = AllocationLegProposal(
        "leg-cand",
        "CAND-B",
        ALLOCATION_ACTION_INCREASE,
        Decimal("0"),
        Decimal("10000000"),
        Decimal("10000000"),
        None,
        None,
        (),
        Decimal("10000000"),
        Decimal("0"),
        False,
    )
    funding = CapitalFundingProvenance(
        Decimal("50000000"),
        Decimal("0"),
        Decimal("50000000"),
        Decimal("0"),
        Decimal("10000000"),
        Decimal("0"),
        Decimal("40000000"),
    )
    payload = {
        "proposal_id": "proposal-001",
        "request_id": "req-001",
        "created_at": NOW,
        "hip_policy_id": hip.policy_id,
        "hip_version": hip.version,
        "hip_integrity_seal": hip.integrity_seal,
        "capital_snapshot_id": snapshot.capital_snapshot_id,
        "orderable_cash_fact_id": snapshot.orderable_cash_fact_id,
        "currency_code": CURRENCY_KRW,
        "legs": (
            (
                leg.allocation_leg_id,
                leg.portfolio_subject_id,
                leg.action,
                leg.current_market_value_krw,
                leg.proposed_market_value_krw,
                leg.delta_market_value_krw,
                leg.cash_funding_krw,
                leg.rotation_funding_krw,
                leg.executable,
            ),
        ),
        "funding": (
            funding.deployable_orderable_cash_krw,
            funding.explicit_reserve_krw,
            funding.deployable_after_reserve_krw,
            funding.rotation_proceeds_krw,
            funding.cash_funded_increases_krw,
            funding.rotation_funded_increases_krw,
            funding.unused_deployable_krw,
        ),
        "constraint_findings": (),
        "cio_decision_ids": ("cio-001",),
        "comparison_ids": (),
        "universe_id": "universe-001",
        "executable": False,
    }
    return CapitalAllocationProposal(
        "proposal-001",
        "req-001",
        NOW,
        hip.policy_id,
        hip.version,
        hip.integrity_seal,
        snapshot.capital_snapshot_id,
        snapshot.orderable_cash_fact_id,
        CURRENCY_KRW,
        (leg,),
        funding,
        (),
        ("cio-001",),
        (),
        "universe-001",
        False,
        cac_seal(payload),
    )


def sealed_chain():
    hip = build_frozen_hip_v1(effective_at=NOW)
    snapshot = capital_snapshot()
    proposal = _proposal(hip, snapshot)
    approval = record_investment_human_approval(
        approval_id="approval-001",
        decision=APPROVAL_DECISION_APPROVED,
        proposal=proposal,
        hip=hip,
        capital_snapshot=snapshot,
        principal="human-operator",
        decided_at=NOW,
        rationale="approve increase",
    )
    artifact = seal_approved_allocation_artifact(
        artifact_id="artifact-001",
        approval=approval,
        proposal=proposal,
        hip=hip,
        capital_snapshot=snapshot,
        sealed_at=NOW,
    )
    return hip, snapshot, proposal, approval, artifact


def verified_account():
    return seal_verified_execution_account_binding(
        binding_id="acct-bind-001",
        account_selector="account-primary",
        gnl_ac_no1="400277078",
        verified_at=NOW,
        verification_method="human_verified_account_binding_v1",
    )


def unverified_account():
    return seal_unverified_account_binding(
        binding_id="acct-bind-unverified",
        account_selector="account-primary",
    )


def instrument_binding(holdings_is_cd="A005930"):
    return seal_instrument_identity_binding(
        binding_id="inst-001",
        portfolio_subject_id="CAND-B",
        holdings_is_cd=holdings_is_cd,
    )


def make_pretrade_bundle(
    *,
    side=SIDE_BUY,
    limit_price="360000",
    cash_amount="50000000",
    trade_unit="1",
    sellable_qty="10",
    holdings_is_cd="A005930",
    account=None,
):
    quote_payload = load_fixture("IVU10140.json")["output"]
    # Override trade unit / price via body mutation for tests when needed
    body = dict(quote_payload["dataBody"])
    body["trd_q_unt"] = f"{int(trade_unit):05d}" if trade_unit.isdigit() else trade_unit
    body["now_prc"] = str(int(Decimal(limit_price)))  # quote observation; limit is separate
    quote_payload = {
        "dataHeader": quote_payload["dataHeader"],
        "dataBody": body,
    }
    instrument = instrument_binding(holdings_is_cd)
    quote = normalize_ivu10140_quote(
        fact_id="quote-001",
        payload=quote_payload,
        instrument_ssam_is_cd=instrument.ssam_is_cd if instrument.proven else "005930",
        collected_at=NOW,
        raw_envelope_id="env-quote-001",
    )
    # Force trade unit from arg after normalize if needed
    if quote.trade_quantity_unit != Decimal(trade_unit):
        from BrokerExecutionCycle.models import QuoteFact
        from BrokerExecutionCycle.integrity import integrity_seal

        q_payload = {
            "fact_id": "quote-001",
            "instrument_ssam_is_cd": quote.instrument_ssam_is_cd,
            "now_price": quote.now_price,
            "trade_quantity_unit": Decimal(trade_unit),
            "currency_code": quote.currency_code,
            "collected_at": NOW,
            "raw_envelope_id": quote.raw_envelope_id,
        }
        quote = QuoteFact(
            quote.fact_id,
            quote.instrument_ssam_is_cd,
            quote.now_price,
            Decimal(trade_unit),
            quote.currency_code,
            NOW,
            quote.raw_envelope_id,
            integrity_seal(q_payload),
        )

    cash_payload = {
        "dataHeader": {"processFlag": "A"},
        "dataBody": {"ordr_psbl_csh": cash_amount},
    }
    cash = normalize_orderable_cash(
        fact_id="cash-001",
        payload=cash_payload,
        collected_at=NOW,
        raw_envelope_id="env-cash-001",
    )
    sellable = None
    if side != SIDE_BUY or sellable_qty is not None:
        sell_payload = {
            "dataHeader": {"processFlag": "A"},
            "dataBody": {
                "Record1": [
                    {
                        "is_no": holdings_is_cd,
                        "ordr_psbl_q": sellable_qty,
                    }
                ]
            },
        }
        sellable = normalize_sellable_quantity(
            fact_id="sell-001",
            payload=sell_payload,
            instrument_ssam_is_cd=instrument.ssam_is_cd if instrument.proven else "005930",
            collected_at=NOW,
            raw_envelope_id="env-sell-001",
        )
    proposed = seal_proposed_limit_price(
        proposal_id="plp-001",
        instrument_ssam_is_cd=instrument.ssam_is_cd if instrument.proven else "005930",
        limit_price=Decimal(limit_price),
        bound_at=NOW,
        principal="human-operator",
    )
    session = seal_session_context(session_id="session-001", collected_at=NOW)
    acct = account if account is not None else verified_account()
    return seal_pretrade_fact_bundle(
        bundle_id="bundle-001",
        quote=quote,
        orderable_cash=cash,
        sellable=sellable,
        instrument=instrument,
        account=acct,
        session=session,
        proposed_limit_price=proposed,
        collected_at=NOW,
    )
