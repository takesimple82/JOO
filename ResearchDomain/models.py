from dataclasses import dataclass

from PipelineRuntime.models import PipelineExecution


@dataclass
class ResearchTask:
    research_id: str
    title: str
    objective: str
    priority: str
    pipeline: PipelineExecution


@dataclass
class ResearchFinding:
    finding_id: str
    research_id: str
    committee_id: str
    category: str
    statement: str
    source: str
    event_date: str
    publication_date: str
    verification_status: str


@dataclass
class ResearchReport:
    research_id: str
    title: str
    findings: list[ResearchFinding]
    status: str
    error: str
