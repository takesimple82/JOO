from PipelineRuntime.models import PipelineExecution
from ResearchDomain.models import (
    ResearchFinding,
    ResearchReport,
    ResearchTask,
)


PRIORITIES = {"P0", "P1", "P2"}
VERIFICATION_STATUSES = {
    "verified",
    "partially_verified",
    "unverified",
}
REPORT_STATUSES = {"completed", "failed"}


def validate_research_task(task: ResearchTask) -> None:
    if not isinstance(task, ResearchTask):
        raise TypeError("task must be ResearchTask")

    _require_nonblank_string("research_id", task.research_id)
    _require_nonblank_string("title", task.title)
    _require_nonblank_string("objective", task.objective)
    _require_string("priority", task.priority)
    if task.priority not in PRIORITIES:
        raise ValueError("priority must be P0, P1, or P2")
    if not isinstance(task.pipeline, PipelineExecution):
        raise TypeError("pipeline must be PipelineExecution")


def validate_research_finding(
    finding: ResearchFinding,
) -> None:
    if not isinstance(finding, ResearchFinding):
        raise TypeError("finding must be ResearchFinding")

    string_fields = (
        ("finding_id", finding.finding_id),
        ("research_id", finding.research_id),
        ("committee_id", finding.committee_id),
        ("category", finding.category),
        ("statement", finding.statement),
        ("source", finding.source),
        ("event_date", finding.event_date),
        ("publication_date", finding.publication_date),
        ("verification_status", finding.verification_status),
    )
    for name, value in string_fields:
        _require_nonblank_string(name, value)

    if finding.verification_status not in VERIFICATION_STATUSES:
        raise ValueError(
            "verification_status must be verified, "
            "partially_verified, or unverified"
        )


def validate_research_report(report: ResearchReport) -> None:
    if not isinstance(report, ResearchReport):
        raise TypeError("report must be ResearchReport")

    _require_nonblank_string("research_id", report.research_id)
    _require_nonblank_string("title", report.title)
    if not isinstance(report.findings, list):
        raise TypeError("findings must be list[ResearchFinding]")
    if not all(
        isinstance(finding, ResearchFinding)
        for finding in report.findings
    ):
        raise TypeError(
            "findings must contain only ResearchFinding"
        )

    _require_string("status", report.status)
    if report.status not in REPORT_STATUSES:
        raise ValueError("status must be completed or failed")
    _require_string("error", report.error)

    if report.status == "completed" and report.error != "":
        raise ValueError("completed report error must be empty")
    if report.status == "failed" and not report.error.strip():
        raise ValueError("failed report error must be nonblank")


def _require_string(name: str, value: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be str")


def _require_nonblank_string(name: str, value: str) -> None:
    _require_string(name, value)
    if not value.strip():
        raise ValueError(f"{name} must not be blank")
