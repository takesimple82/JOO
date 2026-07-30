from ExplicitPortfolioImpact.models import (
    ExplicitPortfolioImpact,
)
from PortfolioDomain.models import PortfolioSubject
from PortfolioDomain.validation import validate_portfolio_subject
from PortfolioImpactApplicability._classification import (
    _classify_portfolio_impact_applicability_unchecked,
)
from PortfolioImpactApplicability.models import (
    PortfolioImpactApplicabilityStatus,
)
from PortfolioImpactInterpretationPolicy._classification import (
    _classify_portfolio_impact_interpretation_policy_applicability_unchecked,
)
from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
    PortfolioImpactInterpretationPolicyApplicabilityStatus,
)
from PortfolioImpactInterpretationPolicy.validation import (
    validate_portfolio_impact_interpretation_policy,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from SemanticThesisProduction.validation import (
    validate_semantically_produced_thesis,
)
from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)
from ThesisPortfolioSubjectLink.validation import (
    validate_explicit_thesis_portfolio_subject_link,
)


def validate_explicit_portfolio_impact(
    impact: ExplicitPortfolioImpact,
) -> None:
    if type(impact) is not ExplicitPortfolioImpact:
        raise TypeError(
            "impact must be ExplicitPortfolioImpact"
        )
    if type(impact.impact_id) is not str:
        raise TypeError("impact_id must be str")
    if impact.impact_id.strip() == "":
        raise ValueError("impact_id must not be blank")

    if type(impact.semantic_thesis) is not SemanticallyProducedThesis:
        raise TypeError(
            "semantic_thesis must be SemanticallyProducedThesis"
        )
    validate_semantically_produced_thesis(
        impact.semantic_thesis
    )

    if type(impact.link) is not ExplicitThesisPortfolioSubjectLink:
        raise TypeError(
            "link must be ExplicitThesisPortfolioSubjectLink"
        )
    validate_explicit_thesis_portfolio_subject_link(
        impact.link
    )

    if type(impact.portfolio_subject) is not PortfolioSubject:
        raise TypeError(
            "portfolio_subject must be PortfolioSubject"
        )
    validate_portfolio_subject(impact.portfolio_subject)

    if type(impact.policy) is not PortfolioImpactInterpretationPolicy:
        raise TypeError(
            "policy must be PortfolioImpactInterpretationPolicy"
        )
    validate_portfolio_impact_interpretation_policy(
        impact.policy
    )

    if type(impact.direction) is not PortfolioImpactDirection:
        raise TypeError(
            "direction must be PortfolioImpactDirection"
        )
    if type(impact.horizon_id) is not str:
        raise TypeError("horizon_id must be str")
    if impact.horizon_id.strip() == "":
        raise ValueError("horizon_id must not be blank")
    if type(impact.rationale) is not str:
        raise TypeError("rationale must be str")

    endpoint_status = (
        _classify_portfolio_impact_applicability_unchecked(
            impact.semantic_thesis,
            impact.link,
            impact.portfolio_subject,
        )
    )
    if (
        endpoint_status
        is PortfolioImpactApplicabilityStatus
        .THESIS_ENDPOINT_MISMATCH
    ):
        raise ValueError(
            "semantic_thesis thesis_id must match link thesis_id"
        )
    if (
        endpoint_status
        is PortfolioImpactApplicabilityStatus
        .PORTFOLIO_SUBJECT_ENDPOINT_MISMATCH
    ):
        raise ValueError(
            "portfolio_subject subject_id must match "
            "link portfolio_subject_id"
        )

    policy_status = (
        _classify_portfolio_impact_interpretation_policy_applicability_unchecked(
            impact.policy,
            impact.direction,
            impact.horizon_id,
            impact.rationale,
        )
    )
    if (
        policy_status
        is PortfolioImpactInterpretationPolicyApplicabilityStatus
        .DIRECTION_NOT_ALLOWED
    ):
        raise ValueError(
            "direction must be allowed by policy"
        )
    if (
        policy_status
        is PortfolioImpactInterpretationPolicyApplicabilityStatus
        .HORIZON_NOT_ALLOWED
    ):
        raise ValueError(
            "horizon_id must be allowed by policy"
        )
    if (
        policy_status
        is PortfolioImpactInterpretationPolicyApplicabilityStatus
        .RATIONALE_REQUIRED
    ):
        raise ValueError(
            "rationale must not be blank when policy "
            "requires rationale"
        )
