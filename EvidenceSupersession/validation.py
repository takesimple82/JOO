from EvidenceSupersession.models import (
    ExplicitPropositionSupersession,
)


def validate_explicit_proposition_supersession(
    relation: ExplicitPropositionSupersession,
) -> None:
    if type(relation) is not ExplicitPropositionSupersession:
        raise TypeError(
            "relation must be ExplicitPropositionSupersession"
        )

    if type(relation.superseded_proposition_id) is not str:
        raise TypeError(
            "superseded_proposition_id must be str"
        )
    if relation.superseded_proposition_id.strip() == "":
        raise ValueError(
            "superseded_proposition_id must not be blank"
        )

    if type(relation.superseding_proposition_id) is not str:
        raise TypeError(
            "superseding_proposition_id must be str"
        )
    if relation.superseding_proposition_id.strip() == "":
        raise ValueError(
            "superseding_proposition_id must not be blank"
        )

    if (
        relation.superseding_proposition_id
        == relation.superseded_proposition_id
    ):
        raise ValueError(
            "superseding_proposition_id must differ from "
            "superseded_proposition_id"
        )
