from __future__ import annotations

from ResearchDomain.models import ResearchFinding, ResearchReport
from ResearchDomain.validation import (
    validate_research_finding,
    validate_research_report,
)

from InvestmentResearchOrchestrator.models.collection import (
    CollectedEvidence,
    CollectionBinding,
    CollectionFailureMarker,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_nonblank_string,
    require_tuple_of,
)


def validate_collection_binding(
    binding: CollectionBinding,
) -> None:
    if type(binding) is not CollectionBinding:
        raise TypeError("binding must be CollectionBinding")
    require_nonblank_string("category", binding.category)
    require_nonblank_string("event_date", binding.event_date)
    require_nonblank_string(
        "publication_date",
        binding.publication_date,
    )
    require_nonblank_string(
        "verification_status",
        binding.verification_status,
    )


def validate_collection_failure_marker(
    marker: CollectionFailureMarker,
) -> None:
    if type(marker) is not CollectionFailureMarker:
        raise TypeError(
            "marker must be CollectionFailureMarker"
        )
    require_nonblank_string(
        "research_id",
        marker.research_id,
    )
    require_nonblank_string(
        "committee_id",
        marker.committee_id,
    )
    require_nonblank_string("reason", marker.reason)


def validate_collected_evidence(
    evidence: CollectedEvidence,
) -> None:
    if type(evidence) is not CollectedEvidence:
        raise TypeError(
            "evidence must be CollectedEvidence"
        )
    require_nonblank_string(
        "research_id",
        evidence.research_id,
    )
    require_tuple_of(
        "findings",
        evidence.findings,
        ResearchFinding,
    )
    require_tuple_of(
        "failure_markers",
        evidence.failure_markers,
        CollectionFailureMarker,
    )
    for finding in evidence.findings:
        validate_research_finding(finding)
    for marker in evidence.failure_markers:
        validate_collection_failure_marker(marker)
    if evidence.report is not None:
        if type(evidence.report) is not ResearchReport:
            raise TypeError(
                "report must be ResearchReport or None"
            )
        validate_research_report(evidence.report)
