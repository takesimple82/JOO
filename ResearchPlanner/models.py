from dataclasses import dataclass


@dataclass
class PortfolioItem:
    entity_id: str
    name: str
    category: str


@dataclass
class ResearchTask:
    task_id: str
    portfolio_entity: str
    portfolio_relevance: str
    status: str


@dataclass
class Priority:
    level: int
    rationale: str
