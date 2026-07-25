from dataclasses import dataclass


@dataclass
class QueueTask:
    task_id: str
    priority: int
    portfolio_entity: str
    portfolio_relevance: str
    committee_required: list[str]
    prompt_id: str
    prompt_version: str
    status: str
    created_at: str
    updated_at: str


@dataclass
class QueueResult:
    task_id: str
    status: str
    message: str
