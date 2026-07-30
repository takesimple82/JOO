from dataclasses import dataclass
from enum import Enum


class PortfolioImpactDirection(Enum):
    BENEFICIAL = "beneficial"
    NEUTRAL = "neutral"
    ADVERSE = "adverse"


@dataclass(frozen=True)
class PortfolioImpactInterpretationPolicy:
    policy_id: str
    policy_version: str
    allowed_directions: tuple[PortfolioImpactDirection, ...]
    allowed_horizon_ids: tuple[str, ...]
    rationale_required: bool


class PortfolioImpactInterpretationPolicyApplicabilityStatus(
    Enum
):
    APPLICABLE = "applicable"
    DIRECTION_NOT_ALLOWED = "direction_not_allowed"
    HORIZON_NOT_ALLOWED = "horizon_not_allowed"
    RATIONALE_REQUIRED = "rationale_required"
