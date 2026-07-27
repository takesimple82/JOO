from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ExactObservedNumericProposition:
    proposition_id: str
    finding_id: str
    subject_id: str
    predicate_id: str
    value: Decimal
    unit_id: str
    effective_context_id: str
