from __future__ import annotations

from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
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
    NumericPathStatus,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_enum,
    require_int,
    require_nonblank_string,
    require_optional_nonblank_string,
    require_tuple_of,
)
from InvestmentResearchOrchestrator.validation.re_research import (
    validate_re_research_request_set,
)


def validate_contradiction_evidence_ref(
    ref: ContradictionEvidenceRef,
) -> None:
    if type(ref) is not ContradictionEvidenceRef:
        raise TypeError(
            "ref must be ContradictionEvidenceRef"
        )
    require_optional_nonblank_string(
        "research_id",
        ref.research_id,
    )
    require_optional_nonblank_string(
        "committee_id",
        ref.committee_id,
    )
    require_optional_nonblank_string(
        "store_identity",
        ref.store_identity,
    )
    require_optional_nonblank_string(
        "prompt_hash",
        ref.prompt_hash,
    )


def validate_contradiction_case(
    case: ContradictionCase,
) -> None:
    if type(case) is not ContradictionCase:
        raise TypeError("case must be ContradictionCase")
    require_nonblank_string("case_id", case.case_id)
    require_nonblank_string("subject_key", case.subject_key)
    require_enum(
        "case_class",
        case.case_class,
        ContradictionCaseClass,
    )
    require_enum(
        "status",
        case.status,
        ContradictionCaseStatus,
    )
    require_tuple_of(
        "evidence_refs",
        case.evidence_refs,
        ContradictionEvidenceRef,
    )
    for ref in case.evidence_refs:
        validate_contradiction_evidence_ref(ref)
    if case.domain_status is not None:
        require_enum(
            "domain_status",
            case.domain_status,
            EvidenceContradictionStatus,
        )
    if case.notes_code is not None:
        require_enum(
            "notes_code",
            case.notes_code,
            ContradictionNotesCode,
        )


def validate_contradiction_evaluation(
    evaluation: ContradictionEvaluation,
) -> None:
    if type(evaluation) is not ContradictionEvaluation:
        raise TypeError(
            "evaluation must be ContradictionEvaluation"
        )
    require_nonblank_string("run_id", evaluation.run_id)
    require_int("attempt", evaluation.attempt)
    if evaluation.attempt < 0:
        raise ValueError("attempt must be >= 0")
    require_tuple_of(
        "cases",
        evaluation.cases,
        ContradictionCase,
    )
    for case in evaluation.cases:
        validate_contradiction_case(case)
    require_tuple_of(
        "unresolved",
        evaluation.unresolved,
        str,
    )
    expected_unresolved = tuple(
        case.case_id
        for case in evaluation.cases
        if case.status is ContradictionCaseStatus.UNRESOLVED
    )
    if evaluation.unresolved != expected_unresolved:
        raise ValueError(
            "unresolved must be the ordered UNRESOLVED "
            "case ids"
        )
    validate_re_research_request_set(
        evaluation.re_research_requests
    )
    if evaluation.re_research_requests.run_id != evaluation.run_id:
        raise ValueError(
            "re_research_requests.run_id must match run_id"
        )
    if evaluation.re_research_requests.attempt != evaluation.attempt:
        raise ValueError(
            "re_research_requests.attempt must match attempt"
        )
    require_enum(
        "numeric_path_status",
        evaluation.numeric_path_status,
        NumericPathStatus,
    )
