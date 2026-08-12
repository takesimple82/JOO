from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitMarketFactProvenanceReference:
    fact_id: str
    source_identity: str
    collected_at: str
