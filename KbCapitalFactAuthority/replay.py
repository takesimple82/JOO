from __future__ import annotations

from FactStore.models import ExplicitStoredFactRecord
from FactStore.store import FactStore

from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot
from KbCapitalFactAuthority.validation import (
    validate_capital_snapshot_consistency,
)


def replay_capital_snapshot_from_store(
    *,
    fact_store: FactStore,
    snapshot: ExplicitCapitalSnapshot,
) -> ExplicitCapitalSnapshot:
    """Rebuild consistency view from stored facts without KB or AI."""
    if type(fact_store) is not FactStore:
        raise TypeError("fact_store must be FactStore")
    if type(snapshot) is not ExplicitCapitalSnapshot:
        raise TypeError("snapshot must be ExplicitCapitalSnapshot")
    fact_ids = [
        snapshot.raw_balances_fact_id,
        snapshot.orderable_cash_fact_id,
        snapshot.deposit_today_fact_id,
        snapshot.deposit_d1_fact_id,
        snapshot.deposit_d2_fact_id,
        snapshot.withdrawable_cash_fact_id,
        snapshot.orderable_total_fact_id,
    ]
    if snapshot.raw_holdings_fact_id is not None:
        fact_ids.append(snapshot.raw_holdings_fact_id)
    if snapshot.broker_reported_account_valuation_fact_id is not None:
        fact_ids.append(
            snapshot.broker_reported_account_valuation_fact_id
        )
    fact_ids.extend(snapshot.position_market_value_fact_ids)
    records_by_id: dict[str, ExplicitStoredFactRecord] = {}
    for fact_id in fact_ids:
        record = fact_store.get_by_fact_id(fact_id)
        fact_store.verify_integrity(record.fact_id)
        records_by_id[fact_id] = record
    validate_capital_snapshot_consistency(
        snapshot,
        records_by_id=records_by_id,
    )
    return ExplicitCapitalSnapshot(
        snapshot.capital_snapshot_id,
        snapshot.account_selector,
        snapshot.provider_id,
        snapshot.currency_code,
        snapshot.collected_at,
        snapshot.freshness_max_age,
        snapshot.portfolio_snapshot_id,
        snapshot.portfolio_id,
        snapshot.observation_context_id,
        snapshot.raw_balances_fact_id,
        snapshot.raw_holdings_fact_id,
        snapshot.orderable_cash_fact_id,
        snapshot.deposit_today_fact_id,
        snapshot.deposit_d1_fact_id,
        snapshot.deposit_d2_fact_id,
        snapshot.withdrawable_cash_fact_id,
        snapshot.orderable_total_fact_id,
        snapshot.broker_reported_account_valuation_fact_id,
        snapshot.position_market_value_fact_ids,
        snapshot.sizing_authority,
    )
