from __future__ import annotations

import json
from dataclasses import dataclass, replace

from EvidenceContradiction.classification import (
    classify_exact_observed_numeric_contradiction_candidate,
)
from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)

from InvestmentResearchOrchestrator.evidence_store import (
    EvidenceStore,
)
from InvestmentResearchOrchestrator.models.contradiction import (
    ContradictionCase,
    ContradictionEvaluation,
    ContradictionEvidenceRef,
)
from InvestmentResearchOrchestrator.models.enums import (
    ContradictionCaseClass,
    ContradictionCaseStatus,
    ContradictionNotesCode,
    EvidencePayloadKind,
    MemoryDeltaClass,
    NumericPathStatus,
    ReResearchReasonCode,
    SubjectClass,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDeltaSet,
)
from InvestmentResearchOrchestrator.models.re_research import (
    ReResearchRequest,
    ReResearchRequestSet,
)
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)
from InvestmentResearchOrchestrator.validation.contradiction import (
    validate_contradiction_evaluation,
)
from InvestmentResearchOrchestrator.validation.memory import (
    validate_memory_delta_set,
)

_HOLDING_TASK_TYPE = "HOLDING_STRUCTURAL"
_WATCHLIST_TASK_TYPE = "WATCHLIST_STRUCTURAL"
_PRIOR_CONFLICT_CLASSES = frozenset(
    {
        MemoryDeltaClass.STATEMENT_CHANGED,
        MemoryDeltaClass.MULTI_FINDING_SET_CHANGED,
    }
)
_REASON_BY_CLASS = {
    ContradictionCaseClass.NUMERIC_CANDIDATE: (
        ReResearchReasonCode.NUMERIC_CANDIDATE
    ),
    ContradictionCaseClass.MULTI_COMMITTEE_STATEMENT_CONFLICT: (
        ReResearchReasonCode.MULTI_COMMITTEE_STATEMENT_CONFLICT
    ),
    ContradictionCaseClass.PRIOR_VS_CURRENT_STATEMENT_CONFLICT: (
        ReResearchReasonCode.PRIOR_VS_CURRENT_STATEMENT_CONFLICT
    ),
    ContradictionCaseClass.CONFIDENCE_INSUFFICIENT: (
        ReResearchReasonCode.CONFIDENCE_INSUFFICIENT
    ),
}


@dataclass(frozen=True)
class _FindingView:
    subject_key: str
    statement: str
    research_id: str | None
    committee_id: str | None
    prompt_hash: str | None


class ContradictionEngine:
    """Operational contradiction detection (IRO-M2)."""

    def evaluate(
        self,
        *,
        run_id: str,
        attempt: int,
        current_store: EvidenceStore,
        memory: MemoryDeltaSet,
        subject_keys: tuple[str, ...],
        numeric_pairs: (
            tuple[
                tuple[
                    ExactObservedNumericProposition,
                    ExactObservedNumericProposition,
                ],
                ...,
            ]
            | None
        ) = None,
        previous_evaluation: ContradictionEvaluation | None = None,
        subject_class_by_key: dict[str, SubjectClass] | None = None,
    ) -> ContradictionEvaluation:
        self._validate_inputs(
            run_id=run_id,
            attempt=attempt,
            current_store=current_store,
            memory=memory,
            subject_keys=subject_keys,
            numeric_pairs=numeric_pairs,
            previous_evaluation=previous_evaluation,
            subject_class_by_key=subject_class_by_key,
        )

        records = current_store.list_for_run(run_id)
        findings = self._current_wave_findings(
            records,
            run_id=run_id,
            attempt=attempt,
        )
        completeness = self._current_wave_completeness(
            records,
            run_id=run_id,
            attempt=attempt,
        )
        memory_by_key = {
            delta.subject_key: delta for delta in memory.deltas
        }
        scope = list(subject_keys)
        for key in findings:
            if key not in scope:
                scope.append(key)
        for key in completeness:
            if key not in scope:
                scope.append(key)

        cases: list[ContradictionCase] = []
        for subject_key in scope:
            subject_findings = findings.get(subject_key, ())
            refs = tuple(
                ContradictionEvidenceRef(
                    research_id=item.research_id,
                    committee_id=item.committee_id,
                    store_identity=None,
                    prompt_hash=item.prompt_hash,
                )
                for item in subject_findings
            )
            if self._has_multi_committee_conflict(
                subject_findings
            ):
                cases.append(
                    self._case(
                        run_id=run_id,
                        subject_key=subject_key,
                        case_class=(
                            ContradictionCaseClass
                            .MULTI_COMMITTEE_STATEMENT_CONFLICT
                        ),
                        status=ContradictionCaseStatus.UNRESOLVED,
                        evidence_refs=refs,
                    )
                )
            delta = memory_by_key.get(subject_key)
            if (
                delta is not None
                and delta.delta_class in _PRIOR_CONFLICT_CLASSES
                and subject_key in subject_keys
            ):
                cases.append(
                    self._case(
                        run_id=run_id,
                        subject_key=subject_key,
                        case_class=(
                            ContradictionCaseClass
                            .PRIOR_VS_CURRENT_STATEMENT_CONFLICT
                        ),
                        status=ContradictionCaseStatus.UNRESOLVED,
                        evidence_refs=refs,
                    )
                )
            gap = self._has_completeness_gap(
                completeness.get(subject_key)
            )
            has_conflict = any(
                case.subject_key == subject_key
                and case.case_class
                in {
                    ContradictionCaseClass
                    .MULTI_COMMITTEE_STATEMENT_CONFLICT,
                    ContradictionCaseClass
                    .PRIOR_VS_CURRENT_STATEMENT_CONFLICT,
                }
                for case in cases
            )
            if gap and (
                has_conflict or subject_key in subject_keys
            ):
                cases.append(
                    self._case(
                        run_id=run_id,
                        subject_key=subject_key,
                        case_class=(
                            ContradictionCaseClass
                            .CONFIDENCE_INSUFFICIENT
                        ),
                        status=ContradictionCaseStatus.UNRESOLVED,
                        evidence_refs=refs,
                    )
                )

        numeric_status = NumericPathStatus.NOT_APPLICABLE
        if numeric_pairs:
            numeric_status = NumericPathStatus.APPLIED
            for index, pair in enumerate(numeric_pairs):
                left, right = pair
                domain_status = (
                    classify_exact_observed_numeric_contradiction_candidate(
                        left,
                        right,
                    )
                )
                subject_key = left.subject_id
                if (
                    domain_status
                    is EvidenceContradictionStatus.CONTRADICTION_CANDIDATE
                ):
                    cases.append(
                        self._case(
                            run_id=run_id,
                            subject_key=subject_key,
                            case_class=(
                                ContradictionCaseClass.NUMERIC_CANDIDATE
                            ),
                            status=ContradictionCaseStatus.UNRESOLVED,
                            evidence_refs=(),
                            domain_status=domain_status,
                            case_suffix=str(index),
                        )
                    )
                elif (
                    domain_status
                    is EvidenceContradictionStatus.NOT_ELIGIBLE
                ):
                    cases.append(
                        self._case(
                            run_id=run_id,
                            subject_key=subject_key,
                            case_class=(
                                ContradictionCaseClass.NUMERIC_CANDIDATE
                            ),
                            status=ContradictionCaseStatus.INELIGIBLE,
                            evidence_refs=(),
                            domain_status=domain_status,
                            notes_code=(
                                ContradictionNotesCode.DOMAIN_NOT_ELIGIBLE
                            ),
                            case_suffix=str(index),
                        )
                    )

        if previous_evaluation is not None:
            triggered = {case.case_id for case in cases}
            for previous in previous_evaluation.cases:
                if (
                    previous.status
                    is not ContradictionCaseStatus.UNRESOLVED
                ):
                    continue
                if previous.case_id in triggered:
                    continue
                if (
                    previous.case_class
                    is ContradictionCaseClass.NUMERIC_CANDIDATE
                    and not numeric_pairs
                ):
                    continue
                cases.append(
                    replace(
                        previous,
                        status=(
                            ContradictionCaseStatus.STRUCTURALLY_CLEARED
                        ),
                    )
                )

        requests = self._requests_from_cases(
            run_id=run_id,
            attempt=attempt,
            cases=cases,
            subject_class_by_key=subject_class_by_key or {},
        )
        unresolved = tuple(
            case.case_id
            for case in cases
            if case.status is ContradictionCaseStatus.UNRESOLVED
        )
        evaluation = ContradictionEvaluation(
            run_id=run_id,
            attempt=attempt,
            cases=tuple(cases),
            unresolved=unresolved,
            re_research_requests=requests,
            numeric_path_status=numeric_status,
        )
        validate_contradiction_evaluation(evaluation)
        return evaluation

    @staticmethod
    def _validate_inputs(
        *,
        run_id: str,
        attempt: int,
        current_store: EvidenceStore,
        memory: MemoryDeltaSet,
        subject_keys: tuple[str, ...],
        numeric_pairs: object,
        previous_evaluation: ContradictionEvaluation | None,
        subject_class_by_key: dict[str, SubjectClass] | None,
    ) -> None:
        if type(run_id) is not str or run_id.strip() == "":
            raise ValueError("run_id must be nonblank str")
        if type(attempt) is not int:
            raise TypeError("attempt must be int")
        if attempt < 0:
            raise ValueError("attempt must be >= 0")
        if type(current_store) is not EvidenceStore:
            raise TypeError(
                "current_store must be EvidenceStore"
            )
        validate_memory_delta_set(memory)
        if memory.run_id != run_id:
            raise ValueError("memory.run_id must match run_id")
        if type(subject_keys) is not tuple:
            raise TypeError("subject_keys must be tuple")
        for index, key in enumerate(subject_keys):
            if type(key) is not str or key.strip() == "":
                raise ValueError(
                    f"subject_keys[{index}] must be nonblank str"
                )
        if numeric_pairs is not None:
            if type(numeric_pairs) is not tuple:
                raise TypeError("numeric_pairs must be tuple")
            for index, pair in enumerate(numeric_pairs):
                if type(pair) is not tuple or len(pair) != 2:
                    raise TypeError(
                        f"numeric_pairs[{index}] must be "
                        "a 2-tuple"
                    )
        if previous_evaluation is not None:
            validate_contradiction_evaluation(
                previous_evaluation
            )
        if subject_class_by_key is not None:
            if type(subject_class_by_key) is not dict:
                raise TypeError(
                    "subject_class_by_key must be dict"
                )

    @staticmethod
    def _case(
        *,
        run_id: str,
        subject_key: str,
        case_class: ContradictionCaseClass,
        status: ContradictionCaseStatus,
        evidence_refs: tuple[ContradictionEvidenceRef, ...],
        domain_status: EvidenceContradictionStatus | None = None,
        notes_code: ContradictionNotesCode | None = None,
        case_suffix: str | None = None,
    ) -> ContradictionCase:
        case_id = f"{run_id}:case:{subject_key}:{case_class.value}"
        if case_suffix is not None:
            case_id = f"{case_id}:{case_suffix}"
        return ContradictionCase(
            case_id=case_id,
            subject_key=subject_key,
            case_class=case_class,
            status=status,
            evidence_refs=evidence_refs,
            domain_status=domain_status,
            notes_code=notes_code,
        )

    @staticmethod
    def _has_multi_committee_conflict(
        findings: tuple[_FindingView, ...],
    ) -> bool:
        if len(findings) < 2:
            return False
        committee_ids = {
            item.committee_id
            for item in findings
            if item.committee_id is not None
        }
        if len(committee_ids) < 2:
            return False
        statements = {
            item.statement
            for item in findings
            if item.committee_id is not None
        }
        return len(statements) > 1

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

    def _requests_from_cases(
        self,
        *,
        run_id: str,
        attempt: int,
        cases: list[ContradictionCase],
        subject_class_by_key: dict[str, SubjectClass],
    ) -> ReResearchRequestSet:
        grouped: dict[
            tuple[str, ReResearchReasonCode],
            list[str],
        ] = {}
        order: list[tuple[str, ReResearchReasonCode]] = []
        for case in cases:
            if case.status is not ContradictionCaseStatus.UNRESOLVED:
                continue
            reason = _REASON_BY_CLASS[case.case_class]
            key = (case.subject_key, reason)
            if key not in grouped:
                grouped[key] = []
                order.append(key)
            grouped[key].append(case.case_id)

        requests: list[ReResearchRequest] = []
        for subject_key, reason in order:
            task_type, priority = self._route_for_subject(
                subject_key,
                subject_class_by_key,
            )
            requests.append(
                ReResearchRequest(
                    request_id=(
                        f"{run_id}:request:{subject_key}:"
                        f"{reason.value}"
                    ),
                    subject_key=subject_key,
                    reason_code=reason,
                    task_type=task_type,
                    source_case_ids=tuple(grouped[(subject_key, reason)]),
                    priority=priority,
                )
            )
        return ReResearchRequestSet(
            run_id=run_id,
            attempt=attempt,
            requests=tuple(requests),
        )

    @staticmethod
    def _route_for_subject(
        subject_key: str,
        subject_class_by_key: dict[str, SubjectClass],
    ) -> tuple[str, str]:
        subject_class = subject_class_by_key.get(subject_key)
        if subject_class is SubjectClass.WATCHLIST:
            return _WATCHLIST_TASK_TYPE, "P1"
        return _HOLDING_TASK_TYPE, "P0"

    def _current_wave_findings(
        self,
        records: tuple[EvidenceStoreRecord, ...],
        *,
        run_id: str,
        attempt: int,
    ) -> dict[str, tuple[_FindingView, ...]]:
        grouped: dict[str, list[_FindingView]] = {}
        for record in records:
            if record.payload_kind is not EvidencePayloadKind.FINDING:
                continue
            record_attempt = self._attempt_from_research_id(
                run_id,
                record.research_id,
            )
            if record_attempt is None:
                if attempt != 0:
                    continue
            elif record_attempt != attempt:
                continue
            view = self._parse_finding(record)
            grouped.setdefault(view.subject_key, []).append(view)
        return {
            key: tuple(items) for key, items in grouped.items()
        }

    def _current_wave_completeness(
        self,
        records: tuple[EvidenceStoreRecord, ...],
        *,
        run_id: str,
        attempt: int,
    ) -> dict[str, dict]:
        latest: dict[str, dict] = {}
        for record in records:
            if (
                record.payload_kind
                is not EvidencePayloadKind.COMPLETENESS
            ):
                continue
            record_attempt = self._attempt_from_research_id(
                run_id,
                record.research_id,
            )
            if record_attempt is None:
                if attempt != 0:
                    continue
            elif record_attempt != attempt:
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
        return _FindingView(
            subject_key=subject_key,
            statement=statement,
            research_id=record.research_id,
            committee_id=record.committee_id,
            prompt_hash=record.prompt_hash,
        )

    @staticmethod
    def _attempt_from_research_id(
        run_id: str,
        research_id: str | None,
    ) -> int | None:
        if type(research_id) is not str:
            return None
        attempt_prefix = f"{run_id}:attempt:"
        initial_prefix = f"{run_id}:unit:"
        if research_id.startswith(attempt_prefix):
            rest = research_id[len(attempt_prefix):]
            attempt_text = rest.split(":", 1)[0]
            if type(attempt_text) is not str:
                return None
            try:
                return int(attempt_text)
            except ValueError:
                return None
        if research_id.startswith(initial_prefix):
            return 0
        return None

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
