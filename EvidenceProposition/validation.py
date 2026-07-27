from decimal import Decimal

from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)


def validate_exact_observed_numeric_proposition(
    proposition: ExactObservedNumericProposition,
) -> None:
    if type(proposition) is not ExactObservedNumericProposition:
        raise TypeError(
            "proposition must be ExactObservedNumericProposition"
        )

    _validate_identifier(
        "proposition_id",
        proposition.proposition_id,
    )
    _validate_identifier(
        "finding_id",
        proposition.finding_id,
    )
    _validate_identifier(
        "subject_id",
        proposition.subject_id,
    )
    _validate_identifier(
        "predicate_id",
        proposition.predicate_id,
    )

    if type(proposition.value) is not Decimal:
        raise TypeError("value must be Decimal")
    if not proposition.value.is_finite():
        raise ValueError("value must be finite")

    _validate_identifier(
        "unit_id",
        proposition.unit_id,
    )
    _validate_identifier(
        "effective_context_id",
        proposition.effective_context_id,
    )


def _validate_identifier(name: str, value: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be str")
    if value.strip() == "":
        raise ValueError(f"{name} must not be blank")
