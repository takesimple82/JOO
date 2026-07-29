from EvidenceContradiction.classification import (
    classify_exact_observed_numeric_contradiction_candidate,
)
from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from EvidenceSupersession.models import (
    ExplicitPropositionSupersession,
)
from EvidenceSupersession.validation import (
    validate_explicit_proposition_supersession,
)
from EvidenceSupersessionApplicability.models import (
    EvidenceSupersessionApplicabilityStatus,
)


def classify_explicit_supersession_applicability(
    left: ExactObservedNumericProposition,
    right: ExactObservedNumericProposition,
    relation: ExplicitPropositionSupersession,
) -> EvidenceSupersessionApplicabilityStatus:
    validate_explicit_proposition_supersession(relation)
    contradiction_status = (
        classify_exact_observed_numeric_contradiction_candidate(
            left,
            right,
        )
    )

    if contradiction_status is EvidenceContradictionStatus.NOT_ELIGIBLE:
        return (
            EvidenceSupersessionApplicabilityStatus
            .NOT_CONTRADICTION_CANDIDATE
        )
    if (
        contradiction_status
        is EvidenceContradictionStatus.NO_CONTRADICTION_CANDIDATE
    ):
        return (
            EvidenceSupersessionApplicabilityStatus
            .NOT_CONTRADICTION_CANDIDATE
        )
    if (
        contradiction_status
        is not EvidenceContradictionStatus.CONTRADICTION_CANDIDATE
    ):
        raise RuntimeError(
            "unsupported evidence contradiction status"
        )

    left_id = left.proposition_id
    right_id = right.proposition_id
    superseded_id = relation.superseded_proposition_id
    superseding_id = relation.superseding_proposition_id

    if (
        superseded_id == left_id
        and superseding_id == right_id
    ):
        return EvidenceSupersessionApplicabilityStatus.APPLICABLE
    if (
        superseded_id == right_id
        and superseding_id == left_id
    ):
        return EvidenceSupersessionApplicabilityStatus.APPLICABLE
    return (
        EvidenceSupersessionApplicabilityStatus
        .RELATION_ENDPOINT_MISMATCH
    )
