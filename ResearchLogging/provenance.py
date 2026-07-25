from dataclasses import dataclass


@dataclass
class SourceReference:
    source_id: str
    source_type: str
    source_uri: str
    title: str
    publisher: str
    event_date: str
    publication_date: str
    retrieved_at: str
    verification_status: str
