from decimal import Decimal

from PortfolioAllocationLegProposedAbsoluteQuantity.models import (
    ExplicitPortfolioAllocationLegProposedAbsoluteQuantity,
)


def validate_explicit_portfolio_allocation_leg_proposed_absolute_quantity(
    content: ExplicitPortfolioAllocationLegProposedAbsoluteQuantity,
) -> None:
    if type(content) is not ExplicitPortfolioAllocationLegProposedAbsoluteQuantity:
        raise TypeError(
            "content must be ExplicitPortfolioAllocationLegProposedAbsoluteQuantity"
        )
    if type(content.allocation_leg_id) is not str:
        raise TypeError("allocation_leg_id must be str")
    if content.allocation_leg_id.strip() == "":
        raise ValueError("allocation_leg_id must not be blank")
    if type(content.unit_id) is not str:
        raise TypeError("unit_id must be str")
    if content.unit_id.strip() == "":
        raise ValueError("unit_id must not be blank")
    if type(content.value) is not Decimal:
        raise TypeError("value must be Decimal")
    if not content.value.is_finite():
        raise ValueError("value must be finite")
