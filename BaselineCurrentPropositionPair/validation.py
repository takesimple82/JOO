from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)


def validate_explicit_baseline_current_proposition_pair(
    pair: ExplicitBaselineCurrentPropositionPair,
) -> None:
    if type(pair) is not ExplicitBaselineCurrentPropositionPair:
        raise TypeError(
            "pair must be ExplicitBaselineCurrentPropositionPair"
        )

    if type(pair.baseline_proposition_id) is not str:
        raise TypeError(
            "baseline_proposition_id must be str"
        )
    if pair.baseline_proposition_id.strip() == "":
        raise ValueError(
            "baseline_proposition_id must not be blank"
        )

    if type(pair.current_proposition_id) is not str:
        raise TypeError(
            "current_proposition_id must be str"
        )
    if pair.current_proposition_id.strip() == "":
        raise ValueError(
            "current_proposition_id must not be blank"
        )

    if (
        pair.current_proposition_id
        == pair.baseline_proposition_id
    ):
        raise ValueError(
            "current_proposition_id must differ from "
            "baseline_proposition_id"
        )
