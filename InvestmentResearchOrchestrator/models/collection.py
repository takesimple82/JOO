from __future__ import annotations

from dataclasses import dataclass

from ResearchDomain.models import ResearchFinding, ResearchReport


@dataclass(frozen=True)
class CollectionBinding:
    category: str
    event_date: str
    publication_date: str
    verification_status: str


@dataclass(frozen=True)
class CollectionFailureMarker:
    research_id: str
    committee_id: str
    reason: str


@dataclass(frozen=True)
class CollectedEvidence:
    research_id: str
    findings: tuple[ResearchFinding, ...]
    failure_markers: tuple[CollectionFailureMarker, ...]
    report: ResearchReport | None
