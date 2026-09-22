from __future__ import annotations

from datetime import datetime, timezone

from FactStore.models.types import (
    ExplicitFactAppendRequest,
    ExplicitStoredFactRecord,
)
from FactStore.models.vocabularies import SOURCE_CLASS_VALUES
from FactStore.storage import InMemoryAppendOnlyFactEngine
from FactStore.validation.common import (
    require_membership,
    require_nonblank_string,
)
from FactStore.validation.validators import (
    compute_stored_fact_integrity_seal,
    validate_collected_at_window,
    validate_explicit_fact_append_request,
    validate_explicit_stored_fact_record,
    validate_primary_fact_append_eligibility,
    verify_stored_fact_integrity,
)


class FactStore:
    def __init__(self, utc_clock, storage_engine=None) -> None:
        if storage_engine is None:
            storage_engine = InMemoryAppendOnlyFactEngine()
        self._utc_clock = utc_clock
        self._engine = storage_engine

    def append(
        self,
        request: ExplicitFactAppendRequest,
    ) -> ExplicitStoredFactRecord:
        return self.append_batch((request,))[0]

    def append_batch(
        self,
        batch: tuple[ExplicitFactAppendRequest, ...],
    ) -> tuple[ExplicitStoredFactRecord, ...]:
        if type(batch) is not tuple:
            raise TypeError("batch must be tuple")
        if len(batch) == 0:
            raise ValueError("batch must not be empty")
        records = []
        by_fact_id = {
            record.fact_id: record
            for record in self._engine.list_in_append_order()
        }
        envelope_ids = {
            record.envelope_id for record in by_fact_id.values()
        }
        successor_of = {
            record.superseded_fact_id: record.fact_id
            for record in by_fact_id.values()
            if record.superseded_fact_id is not None
        }
        for request in batch:
            validate_explicit_fact_append_request(request)
            validate_primary_fact_append_eligibility(request)
            envelope = request.envelope
            if request.fact_id in by_fact_id:
                raise ValueError("fact_id already accepted")
            if envelope.envelope_id in envelope_ids:
                raise ValueError("envelope_id already accepted")
            if request.superseded_fact_id is not None:
                if request.superseded_fact_id not in by_fact_id:
                    raise ValueError("superseded_fact_id not found")
                predecessor = by_fact_id[
                    request.superseded_fact_id
                ]
                if request.superseded_fact_id in successor_of:
                    raise ValueError(
                        "superseded_fact_id already superseded"
                    )
                if predecessor.source_class != envelope.source_class:
                    raise ValueError(
                        "supersession source_class must match"
                    )
            record = self._build_record(
                request,
                self._read_appended_at(),
            )
            records.append(record)
            by_fact_id[record.fact_id] = record
            envelope_ids.add(record.envelope_id)
            if record.superseded_fact_id is not None:
                successor_of[record.superseded_fact_id] = (
                    record.fact_id
                )
        accepted = tuple(records)
        self._engine.append_batch(accepted)
        return accepted

    @staticmethod
    def _build_record(
        request: ExplicitFactAppendRequest,
        appended_at: datetime,
    ) -> ExplicitStoredFactRecord:
        envelope = request.envelope
        draft = ExplicitStoredFactRecord(
            request.fact_id,
            envelope.envelope_id,
            envelope.provider_id,
            envelope.source_class,
            envelope.collected_at,
            appended_at,
            envelope.status,
            envelope.payload,
            request.superseded_fact_id,
            None,
        )
        record = ExplicitStoredFactRecord(
            draft.fact_id,
            draft.envelope_id,
            draft.provider_id,
            draft.source_class,
            draft.collected_at,
            draft.appended_at,
            draft.status,
            draft.payload,
            draft.superseded_fact_id,
            compute_stored_fact_integrity_seal(draft),
        )
        validate_explicit_stored_fact_record(record)
        return record

    def get_by_fact_id(
        self,
        fact_id: str,
    ) -> ExplicitStoredFactRecord:
        require_nonblank_string("fact_id", fact_id)
        return self._engine.get_by_fact_id(fact_id)

    def list_by_source_identity(
        self,
        source_identity: str,
    ) -> tuple[ExplicitStoredFactRecord, ...]:
        require_nonblank_string(
            "source_identity",
            source_identity,
        )
        return tuple(
            record
            for record in self._engine.list_in_append_order()
            if record.provider_id == source_identity
        )

    def list_by_source_class(
        self,
        source_class: str,
    ) -> tuple[ExplicitStoredFactRecord, ...]:
        require_membership(
            "source_class",
            source_class,
            SOURCE_CLASS_VALUES,
            "SOURCE_CLASS_VALUES",
        )
        return tuple(
            record
            for record in self._engine.list_in_append_order()
            if record.source_class == source_class
        )

    def list_by_collected_at_window(
        self,
        collected_at_start: datetime,
        collected_at_end: datetime,
    ) -> tuple[ExplicitStoredFactRecord, ...]:
        validate_collected_at_window(
            collected_at_start,
            collected_at_end,
        )
        return tuple(
            record
            for record in self._engine.list_in_append_order()
            if (
                collected_at_start
                <= record.collected_at
                <= collected_at_end
            )
        )

    def get_predecessor(
        self,
        fact_id: str,
    ) -> ExplicitStoredFactRecord | None:
        record = self.get_by_fact_id(fact_id)
        if record.superseded_fact_id is None:
            return None
        return self._engine.get_by_fact_id(
            record.superseded_fact_id
        )

    def get_successor(
        self,
        fact_id: str,
    ) -> ExplicitStoredFactRecord | None:
        record = self.get_by_fact_id(fact_id)
        successor_id = self._engine.successor_of(record.fact_id)
        if successor_id is None:
            return None
        return self._engine.get_by_fact_id(successor_id)

    def verify_integrity(self, fact_id: str) -> None:
        record = self.get_by_fact_id(fact_id)
        verify_stored_fact_integrity(record)

    def _read_appended_at(self) -> datetime:
        appended_at = self._utc_clock()
        if type(appended_at) is not datetime:
            raise TypeError("appended_at must be datetime")
        if appended_at.tzinfo is not timezone.utc:
            raise ValueError(
                "appended_at tzinfo must be "
                "datetime.timezone.utc"
            )
        return appended_at
