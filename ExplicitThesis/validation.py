from ExplicitThesis.models import ExplicitThesis


def validate_explicit_thesis(
    thesis: ExplicitThesis,
) -> None:
    if type(thesis) is not ExplicitThesis:
        raise TypeError("thesis must be ExplicitThesis")
    if type(thesis.thesis_id) is not str:
        raise TypeError("thesis_id must be str")
    if thesis.thesis_id.strip() == "":
        raise ValueError("thesis_id must not be blank")
    if type(thesis.statement) is not str:
        raise TypeError("statement must be str")
    if thesis.statement.strip() == "":
        raise ValueError("statement must not be blank")
