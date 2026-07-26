from __future__ import annotations

import re
from datetime import date

from EvidenceValidation.models import (
    EvidenceValidationIssue,
    EvidenceValidationResult,
)
from ResearchDomain.models import ResearchFinding
from ResearchDomain.validation import validate_research_finding


_DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class EvidenceValidator:
    def validate(
        self,
        finding: ResearchFinding,
    ) -> EvidenceValidationResult:
        validate_research_finding(finding)
        issues = _collect_date_issues(finding)
        return EvidenceValidationResult(
            valid=len(issues) == 0,
            issues=issues,
        )


def _collect_date_issues(
    finding: ResearchFinding,
) -> tuple[EvidenceValidationIssue, ...]:
    issues = []
    event_date = _parse_strict_date(finding.event_date)
    publication_date = _parse_strict_date(
        finding.publication_date
    )

    if event_date is None:
        issues.append(
            EvidenceValidationIssue(
                code="INVALID_EVENT_DATE",
                message=(
                    "event_date must be a valid YYYY-MM-DD date"
                ),
            )
        )
    if publication_date is None:
        issues.append(
            EvidenceValidationIssue(
                code="INVALID_PUBLICATION_DATE",
                message=(
                    "publication_date must be a valid "
                    "YYYY-MM-DD date"
                ),
            )
        )
    if (
        event_date is not None
        and publication_date is not None
        and _publication_before_event(
            event_date,
            publication_date,
        )
    ):
        issues.append(
            EvidenceValidationIssue(
                code="PUBLICATION_BEFORE_EVENT",
                message=(
                    "publication_date must not be before event_date"
                ),
            )
        )

    return tuple(issues)


def _parse_strict_date(value: str) -> date | None:
    if _DATE_PATTERN.fullmatch(value) is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _publication_before_event(
    event_date: date,
    publication_date: date,
) -> bool:
    return publication_date < event_date
