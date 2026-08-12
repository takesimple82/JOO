from MarketFactProvenanceReference.models import (
    ExplicitMarketFactProvenanceReference,
)


def validate_explicit_market_fact_provenance_reference(
    provenance: ExplicitMarketFactProvenanceReference,
) -> None:
    if (
        type(provenance)
        is not ExplicitMarketFactProvenanceReference
    ):
        raise TypeError(
            "provenance must be "
            "ExplicitMarketFactProvenanceReference"
        )
    if type(provenance.fact_id) is not str:
        raise TypeError("fact_id must be str")
    if provenance.fact_id.strip() == "":
        raise ValueError(
            "fact_id must not be blank"
        )
    if type(provenance.source_identity) is not str:
        raise TypeError(
            "source_identity must be str"
        )
    if provenance.source_identity.strip() == "":
        raise ValueError(
            "source_identity must not be blank"
        )
    if type(provenance.collected_at) is not str:
        raise TypeError(
            "collected_at must be str"
        )
    if provenance.collected_at.strip() == "":
        raise ValueError(
            "collected_at must not be blank"
        )
