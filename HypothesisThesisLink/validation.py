from HypothesisThesisLink.models import (
    ExplicitHypothesisThesisLink,
)
from SemanticHypothesisProduction.models import (
    SemanticallyProducedHypothesis,
)
from SemanticHypothesisProduction.validation import (
    validate_semantically_produced_hypothesis,
)
from SemanticThesisProduction.models import (
    SemanticallyProducedThesis,
)
from SemanticThesisProduction.validation import (
    validate_semantically_produced_thesis,
)


def validate_explicit_hypothesis_thesis_link(
    link: ExplicitHypothesisThesisLink,
) -> None:
    if type(link) is not ExplicitHypothesisThesisLink:
        raise TypeError(
            "link must be ExplicitHypothesisThesisLink"
        )
    if type(link.hypothesis) is not SemanticallyProducedHypothesis:
        raise TypeError(
            "hypothesis must be SemanticallyProducedHypothesis"
        )
    if type(link.thesis) is not SemanticallyProducedThesis:
        raise TypeError(
            "thesis must be SemanticallyProducedThesis"
        )
    validate_semantically_produced_hypothesis(
        link.hypothesis
    )
    validate_semantically_produced_thesis(link.thesis)
