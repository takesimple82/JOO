from __future__ import annotations

from FactStore.models import ExplicitStoredFactRecord
from FactStore.store import FactStore


def retrieve_by_fact_id(
    fact_store: FactStore,
    fact_id: str,
) -> ExplicitStoredFactRecord:
    return fact_store.get_by_fact_id(fact_id)


def verify_retrieved_fact_integrity(
    fact_store: FactStore,
    fact_id: str,
) -> None:
    fact_store.verify_integrity(fact_id)
