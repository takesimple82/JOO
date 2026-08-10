from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
)
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)
from InvestmentResearchOrchestrator.validation.store import (
    validate_evidence_store_record,
)


class EvidenceStore:
    """Append-only run-local JSONL evidence store (IRO-M1)."""

    def __init__(self, root_path: str | Path) -> None:
        if not isinstance(root_path, (str, Path)):
            raise TypeError("root_path must be str or Path")
        self._root = Path(root_path)

    @property
    def root_path(self) -> Path:
        return self._root

    def append(self, record: EvidenceStoreRecord) -> None:
        validate_evidence_store_record(record)
        self._root.mkdir(parents=True, exist_ok=True)
        path = self._run_path(record.run_id)
        line = json.dumps(
            self._serialize(record),
            separators=(",", ":"),
            ensure_ascii=False,
        )
        try:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.write("\n")
        except OSError:
            raise

    def list_for_run(
        self,
        run_id: str,
    ) -> tuple[EvidenceStoreRecord, ...]:
        if type(run_id) is not str or run_id.strip() == "":
            raise ValueError("run_id must be nonblank str")
        path = self._run_path(run_id)
        if not path.exists():
            return ()
        records: list[EvidenceStoreRecord] = []
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    stripped = line.strip()
                    if stripped == "":
                        continue
                    records.append(
                        self._deserialize(json.loads(stripped))
                    )
        except OSError:
            raise
        return tuple(records)

    def list_by_research_id(
        self,
        run_id: str,
        research_id: str,
    ) -> tuple[EvidenceStoreRecord, ...]:
        if type(research_id) is not str or research_id.strip() == "":
            raise ValueError("research_id must be nonblank str")
        return tuple(
            record
            for record in self.list_for_run(run_id)
            if record.research_id == research_id
        )

    def _run_path(self, run_id: str) -> Path:
        return self._root / f"{run_id}.jsonl"

    @staticmethod
    def _serialize(record: EvidenceStoreRecord) -> dict:
        return {
            "run_id": record.run_id,
            "research_id": record.research_id,
            "committee_id": record.committee_id,
            "provider_id": record.provider_id,
            "prompt_id": record.prompt_id,
            "prompt_hash": record.prompt_hash,
            "source_reference": record.source_reference,
            "collected_at": (
                None
                if record.collected_at is None
                else record.collected_at.isoformat()
            ),
            "stored_at": record.stored_at.isoformat(),
            "payload_kind": record.payload_kind.value,
            "payload": record.payload,
        }

    @staticmethod
    def _deserialize(data: dict) -> EvidenceStoreRecord:
        collected_raw = data.get("collected_at")
        collected_at = (
            None
            if collected_raw is None
            else datetime.fromisoformat(collected_raw)
        )
        record = EvidenceStoreRecord(
            run_id=data["run_id"],
            research_id=data.get("research_id"),
            committee_id=data.get("committee_id"),
            provider_id=data.get("provider_id"),
            prompt_id=data.get("prompt_id"),
            prompt_hash=data.get("prompt_hash"),
            source_reference=data.get("source_reference"),
            collected_at=collected_at,
            stored_at=datetime.fromisoformat(data["stored_at"]),
            payload_kind=EvidencePayloadKind(
                data["payload_kind"]
            ),
            payload=data["payload"],
        )
        validate_evidence_store_record(record)
        return record


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
