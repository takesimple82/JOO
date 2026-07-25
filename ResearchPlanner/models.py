from dataclasses import dataclass


@dataclass
class PortfolioItem:
    entity_id: str
    name: str
    category: str


@dataclass
class ResearchTask:
    task_id: str
    priority: int
    portfolio_entity: str
    portfolio_relevance: str
    committee_required: list[str]
    prompt_id: str
    prompt_version: str
    status: str


@dataclass
class Priority:
    level: int
    rationale: str
