from __future__ import annotations

import json
from dataclasses import dataclass

from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
)
from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
    MemoryDeltaClass,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDelta,
    MemoryDeltaDetail,
    MemoryDeltaSet,
    MemoryProvenanceIdentity,
)
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)
from InvestmentResearchOrchestrator.validation.memory import (
    validate_memory_delta_set,
)


@dataclass(frozen=True)
class _FindingView:
    subject_key: str
    statement: str
    finding_id: str | None
    committee_id: str | None
    provider_id: str | None
    prompt_hash: str | None
    source_reference: str | None


class MemoryComparison:
    """Operational prior-vs-current store comparison (IRO-M2)."""

    def compare(
        self,
        *,
        run_id: str,
        current_store: EvidenceStore,
        prior_store: EvidenceStore | None,
        prior_run_id: str | None,
        subject_keys: tuple[str, ...],
    ) -> MemoryDeltaSet:
        self._validate_inputs(
            run_id=run_id,
            current_store=current_store,
            prior_store=prior_store,
            prior_run_id=prior_run_id,
            subject_keys=subject_keys,
        )

        current_records = current_store.list_for_run(run_id)
        current_findings = self._findings_by_subject(
            current_records
        )
        current_completeness = self._completeness_by_subject(
            current_records
        )
        prior_available = (
            prior_store is not None and prior_run_id is not None
        )
        if prior_available:
            prior_records = prior_store.list_for_run(
                prior_run_id
            )
            prior_findings = self._findings_by_subject(
                prior_records
            )
            prior_completeness = self._completeness_by_subject(
                prior_records
            )
        else:
            prior_findings = {}
            prior_completeness = {}

        keys = self._ordered_keys(
            subject_keys,
            current_findings,
            current_completeness,
            prior_findings if prior_available else {},
            prior_completeness if prior_available else {},
        )

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
            deltas.append(
                self._compare_subject(
                    key=key,
                    current_findings=current_findings.get(
                        key, ()
                    ),
                    prior_findings=prior_findings.get(key, ()),
                    current_gap=self._has_completeness_gap(
                        current_completeness.get(key)
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
    def _validate_inputs(
        *,
        run_id: str,
        current_store: EvidenceStore,
        prior_store: EvidenceStore | None,
        prior_run_id: str | None,
        subject_keys: tuple[str, ...],
    ) -> None:
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

    @staticmethod
    def _ordered_keys(
        subject_keys: tuple[str, ...],
        current_findings: dict[str, tuple[_FindingView, ...]],
        current_completeness: dict[str, dict],
        prior_findings: dict[str, tuple[_FindingView, ...]],
        prior_completeness: dict[str, dict],
    ) -> list[str]:
        keys: list[str] = list(subject_keys)
        for source in (
            current_findings,
            current_completeness,
            prior_findings,
            prior_completeness,
        ):
            for key in source:
                if key not in keys:
                    keys.append(key)
        return keys

    def _compare_subject(
        self,
        *,
        key: str,
        current_findings: tuple[_FindingView, ...],
        prior_findings: tuple[_FindingView, ...],
        current_gap: bool,
    ) -> MemoryDelta:
        prior_present = len(prior_findings) > 0
        current_present = len(current_findings) > 0
        if not prior_present and not current_present:
            return MemoryDelta(
                subject_key=key,
                prior_present=False,
                delta_class=MemoryDeltaClass.NO_PRIOR,
            )
        if not prior_present and current_present:
            return MemoryDelta(
                subject_key=key,
                prior_present=False,
                delta_class=MemoryDeltaClass.ADDED,
            )
        if prior_present and not current_present:
            return MemoryDelta(
                subject_key=key,
                prior_present=True,
                delta_class=MemoryDeltaClass.REMOVED,
            )

        prior_statements = tuple(
            item.statement for item in prior_findings
        )
        current_statements = tuple(
            item.statement for item in current_findings
        )
        prior_provenance = tuple(
            self._provenance_of(item) for item in prior_findings
        )
        current_provenance = tuple(
            self._provenance_of(item)
            for item in current_findings
        )
        detail = MemoryDeltaDetail(
            prior_statements=prior_statements,
            current_statements=current_statements,
            prior_provenance=prior_provenance,
            current_provenance=current_provenance,
        )

        if prior_statements != current_statements:
            if (
                max(
                    len(prior_statements),
                    len(current_statements),
                )
                > 1
            ):
                delta_class = (
                    MemoryDeltaClass.MULTI_FINDING_SET_CHANGED
                )
            else:
                delta_class = MemoryDeltaClass.STATEMENT_CHANGED
            return MemoryDelta(
                subject_key=key,
                prior_present=True,
                delta_class=delta_class,
                detail=detail,
            )

        prior_identity = frozenset(prior_provenance)
        current_identity = frozenset(current_provenance)
        if prior_identity != current_identity:
            return MemoryDelta(
                subject_key=key,
                prior_present=True,
                delta_class=MemoryDeltaClass.PROVENANCE_CHANGED,
                detail=detail,
            )
        if current_gap:
            return MemoryDelta(
                subject_key=key,
                prior_present=True,
                delta_class=MemoryDeltaClass.CONFIDENCE_GAP,
            )
        return MemoryDelta(
            subject_key=key,
            prior_present=True,
            delta_class=MemoryDeltaClass.UNCHANGED,
        )

    @staticmethod
    def _provenance_of(
        item: _FindingView,
    ) -> MemoryProvenanceIdentity:
        return MemoryProvenanceIdentity(
            committee_id=item.committee_id,
            provider_id=item.provider_id,
            prompt_hash=item.prompt_hash,
            source_reference=item.source_reference,
        )

    @staticmethod
    def _has_completeness_gap(payload: dict | None) -> bool:
        if payload is None:
            return False
        failed = payload.get("failed")
        missing = payload.get("missing")
        if type(failed) is list and len(failed) > 0:
            return True
        if type(missing) is list and len(missing) > 0:
            return True
        return False

    def _findings_by_subject(
        self,
        records: tuple[EvidenceStoreRecord, ...],
    ) -> dict[str, tuple[_FindingView, ...]]:
        grouped: dict[str, list[_FindingView]] = {}
        for record in records:
            if record.payload_kind is not EvidencePayloadKind.FINDING:
                continue
            view = self._parse_finding(record)
            grouped.setdefault(view.subject_key, []).append(view)
        return {
            key: tuple(items)
            for key, items in grouped.items()
        }

    def _parse_finding(
        self,
        record: EvidenceStoreRecord,
    ) -> _FindingView:
        try:
            payload = json.loads(record.payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "FINDING payload must be valid JSON"
            ) from exc
        if type(payload) is not dict:
            raise ValueError(
                "FINDING payload must be a JSON object"
            )
        subject_key = payload.get("subject_key")
        statement = payload.get("statement")
        if type(subject_key) is not str or subject_key.strip() == "":
            raise ValueError(
                "FINDING payload subject_key must be nonblank str"
            )
        if type(statement) is not str:
            raise ValueError(
                "FINDING payload statement must be str"
            )
        finding_id = payload.get("finding_id")
        if finding_id is not None and type(finding_id) is not str:
            raise ValueError(
                "FINDING payload finding_id must be str or absent"
            )
        return _FindingView(
            subject_key=subject_key,
            statement=statement,
            finding_id=finding_id,
            committee_id=record.committee_id,
            provider_id=record.provider_id,
            prompt_hash=record.prompt_hash,
            source_reference=record.source_reference,
        )

    def _completeness_by_subject(
        self,
        records: tuple[EvidenceStoreRecord, ...],
    ) -> dict[str, dict]:
        latest: dict[str, dict] = {}
        for record in records:
            if (
                record.payload_kind
                is not EvidencePayloadKind.COMPLETENESS
            ):
                continue
            subject_key = self._subject_from_research_id(
                record.research_id
            )
            if subject_key is None:
                continue
            try:
                payload = json.loads(record.payload)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "COMPLETENESS payload must be valid JSON"
                ) from exc
            if type(payload) is not dict:
                raise ValueError(
                    "COMPLETENESS payload must be a JSON object"
                )
            latest[subject_key] = payload
        return latest

    @staticmethod
    def _subject_from_research_id(
        research_id: str | None,
    ) -> str | None:
        if type(research_id) is not str:
            return None
        marker = ":unit:"
        if marker not in research_id:
            return None
        rest = research_id.split(marker, 1)[1]
        parts = rest.split(":", 1)
        if len(parts) != 2 or parts[1].strip() == "":
            return None
        return parts[1]
