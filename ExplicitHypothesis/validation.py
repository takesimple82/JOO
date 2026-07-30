from ExplicitHypothesis.models import ExplicitHypothesis


def validate_explicit_hypothesis(
    hypothesis: ExplicitHypothesis,
) -> None:
    if type(hypothesis) is not ExplicitHypothesis:
        raise TypeError(
            "hypothesis must be ExplicitHypothesis"
        )
    if type(hypothesis.hypothesis_id) is not str:
        raise TypeError("hypothesis_id must be str")
    if hypothesis.hypothesis_id.strip() == "":
        raise ValueError(
            "hypothesis_id must not be blank"
        )
    if type(hypothesis.statement) is not str:
        raise TypeError("statement must be str")
    if hypothesis.statement.strip() == "":
        raise ValueError("statement must not be blank")
