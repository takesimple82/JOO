from __future__ import annotations

from FactStore.models.types import ExplicitStoredFactRecord
from FactStore.validation.validators import (
    validate_explicit_stored_fact_record,
)


class InMemoryAppendOnlyFactEngine:
    def __init__(self) -> None:
        self._records = []
        self._by_fact_id = {}
        self._envelope_ids = set()
        self._successor_of = {}

    def append(self, record: ExplicitStoredFactRecord) -> None:
        self.append_batch((record,))

    def append_batch(
        self,
        records: tuple[ExplicitStoredFactRecord, ...],
    ) -> None:
        if type(records) is not tuple:
            raise TypeError("records must be tuple")
        candidate_records = list(self._records)
        candidate_by_fact_id = dict(self._by_fact_id)
        candidate_envelope_ids = set(self._envelope_ids)
        candidate_successor_of = dict(self._successor_of)
        for record in records:
            validate_explicit_stored_fact_record(record)
            if record.fact_id in candidate_by_fact_id:
                raise ValueError("fact_id already accepted")
            if record.envelope_id in candidate_envelope_ids:
                raise ValueError("envelope_id already accepted")
            if (
                record.superseded_fact_id is not None
                and record.superseded_fact_id
                in candidate_successor_of
            ):
                raise ValueError(
                    "superseded_fact_id already superseded"
                )
            candidate_records.append(record)
            candidate_by_fact_id[record.fact_id] = record
            candidate_envelope_ids.add(record.envelope_id)
            if record.superseded_fact_id is not None:
                candidate_successor_of[
                    record.superseded_fact_id
                ] = record.fact_id
        self._records = candidate_records
        self._by_fact_id = candidate_by_fact_id
        self._envelope_ids = candidate_envelope_ids
        self._successor_of = candidate_successor_of

    def get_by_fact_id(
        self,
        fact_id: str,
    ) -> ExplicitStoredFactRecord:
        if fact_id not in self._by_fact_id:
            raise ValueError("fact_id not found")
        return self._by_fact_id[fact_id]

    def contains_fact_id(self, fact_id: str) -> bool:
        return fact_id in self._by_fact_id

    def contains_envelope_id(self, envelope_id: str) -> bool:
        return envelope_id in self._envelope_ids

    def list_in_append_order(
        self,
    ) -> tuple[ExplicitStoredFactRecord, ...]:
        return tuple(self._records)

    def successor_of(self, fact_id: str) -> str | None:
        return self._successor_of.get(fact_id)
