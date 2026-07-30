from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


@dataclass(frozen=True)
class ExactNumericDeltaMaterialityPolicy:
    unit_id: str
    threshold: Decimal


class ExactNumericDeltaMaterialityStatus(Enum):
    UNIT_MISMATCH = "unit_mismatch"
    IMMATERIAL = "immaterial"
    MATERIAL = "material"
