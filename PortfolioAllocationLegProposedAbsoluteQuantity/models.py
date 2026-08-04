from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ExplicitPortfolioAllocationLegProposedAbsoluteQuantity:
    allocation_leg_id: str
    unit_id: str
    value: Decimal
