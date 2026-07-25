from dataclasses import dataclass


@dataclass
class ResearchEvent:
    event_id: str
    execution_id: str
    task_id: str
    event_type: str
    status: str
    occurred_at: str
    provider: str
    committee: str
    prompt_id: str
    prompt_version: str
    payload: str
    error: str


@dataclass
class ExecutionManifest:
    execution_id: str
    task_id: str
    started_at: str
    completed_at: str
    status: str
    provider: str
    committee: str
    prompt_id: str
    prompt_version: str
