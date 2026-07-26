from dataclasses import dataclass

from AIAdapter.models import AIRequest, AIResponse


@dataclass
class CommitteeExecution:
    committee_id: str
    name: str
    requests: list[AIRequest]


@dataclass
class CommitteeRequest:
    committee: str
    task_id: str
    provider: str
    prompt_id: str
    prompt_version: str


@dataclass
class CommitteeResult:
    committee: str
    task_id: str
    provider: str
    prompt_id: str
    prompt_version: str
    status: str
    summary: str
    error: str


@dataclass
class CommitteeExecutionResult:
    committee_id: str
    responses: list[AIResponse]


@dataclass
class CommitteeAggregate:
    task_id: str
    committee: str
    required_providers: list[str]
    completed_providers: list[str]
    failed_providers: list[str]
    missing_providers: list[str]
    status: str
