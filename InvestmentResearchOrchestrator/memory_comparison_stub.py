from __future__ import annotations

import json

from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
)
from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
    MemoryDeltaClass,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDelta,
    MemoryDeltaSet,
)
from InvestmentResearchOrchestrator.validation.memory import (
    validate_memory_delta_set,
)


class MemoryComparisonStub:
    """M1 memory stub: presence/absence + exact statement identity."""

    def compare(
        self,
        *,
        run_id: str,
        current_store: EvidenceStore,
        prior_store: EvidenceStore | None,
        prior_run_id: str | None,
        subject_keys: tuple[str, ...],
    ) -> MemoryDeltaSet:
        if type(run_id) is not str or run_id.strip() == "":
            raise ValueError("run_id must be nonblank str")
        if type(current_store) is not EvidenceStore:
            raise TypeError(
                "current_store must be EvidenceStore"
            )
        if prior_store is not None and type(
            prior_store
        ) is not EvidenceStore:
            raise TypeError(
                "prior_store must be EvidenceStore or None"
            )
        if prior_run_id is not None and (
            type(prior_run_id) is not str
            or prior_run_id.strip() == ""
        ):
            raise ValueError(
                "prior_run_id must be nonblank str or None"
            )
        if type(subject_keys) is not tuple:
            raise TypeError("subject_keys must be tuple")
        for index, key in enumerate(subject_keys):
            if type(key) is not str or key.strip() == "":
                raise ValueError(
                    f"subject_keys[{index}] must be nonblank str"
                )

        current_by_key = self._findings_by_subject(
            current_store.list_for_run(run_id)
        )
        prior_available = (
            prior_store is not None and prior_run_id is not None
        )
        if prior_available:
            prior_by_key = self._findings_by_subject(
                prior_store.list_for_run(prior_run_id)
            )
        else:
            prior_by_key = {}

        keys: list[str] = list(subject_keys)
        for key in current_by_key:
            if key not in keys:
                keys.append(key)
        if prior_available:
            for key in prior_by_key:
                if key not in keys:
                    keys.append(key)

        deltas: list[MemoryDelta] = []
        for key in keys:
            if not prior_available:
                deltas.append(
                    MemoryDelta(
                        subject_key=key,
                        prior_present=False,
                        delta_class=MemoryDeltaClass.NO_PRIOR,
                    )
                )
                continue

            current_statements = current_by_key.get(key, ())
            prior_statements = prior_by_key.get(key, ())
            prior_present = len(prior_statements) > 0
            current_present = len(current_statements) > 0

            if not prior_present and not current_present:
                deltas.append(
                    MemoryDelta(
                        subject_key=key,
                        prior_present=False,
                        delta_class=MemoryDeltaClass.NO_PRIOR,
                    )
                )
            elif not prior_present and current_present:
                deltas.append(
                    MemoryDelta(
                        subject_key=key,
                        prior_present=False,
                        delta_class=MemoryDeltaClass.ADDED,
                    )
                )
            elif prior_present and not current_present:
                deltas.append(
                    MemoryDelta(
                        subject_key=key,
                        prior_present=True,
                        delta_class=MemoryDeltaClass.REMOVED,
                    )
                )
            elif current_statements == prior_statements:
                deltas.append(
                    MemoryDelta(
                        subject_key=key,
                        prior_present=True,
                        delta_class=MemoryDeltaClass.UNCHANGED,
                    )
                )
            else:
                deltas.append(
                    MemoryDelta(
                        subject_key=key,
                        prior_present=True,
                        delta_class=(
                            MemoryDeltaClass.STATEMENT_CHANGED
                        ),
                    )
                )

        result = MemoryDeltaSet(
            run_id=run_id,
            deltas=tuple(deltas),
        )
        validate_memory_delta_set(result)
        return result

    @staticmethod
    def _findings_by_subject(
        records: tuple,
    ) -> dict[str, tuple[str, ...]]:
        grouped: dict[str, list[str]] = {}
        for record in records:
            if (
                record.payload_kind
                is not EvidencePayloadKind.FINDING
            ):
                continue
            try:
                payload = json.loads(record.payload)
            except json.JSONDecodeError:
                continue
            subject_key = payload.get("subject_key")
            statement = payload.get("statement")
            if (
                type(subject_key) is not str
                or subject_key.strip() == ""
                or type(statement) is not str
            ):
                continue
            grouped.setdefault(subject_key, []).append(statement)
        return {
            key: tuple(statements)
            for key, statements in grouped.items()
        }
