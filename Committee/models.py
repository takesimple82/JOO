from dataclasses import dataclass


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
    status: str
    summary: str
