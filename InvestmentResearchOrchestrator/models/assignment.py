from dataclasses import dataclass


@dataclass(frozen=True)
class CompletenessBuckets:
    required: tuple[str, ...]
    completed: tuple[str, ...]
    failed: tuple[str, ...]
    missing: tuple[str, ...]


@dataclass(frozen=True)
class CommitteeAssignmentPlan:
    research_id: str
    required_committees: tuple[str, ...]
    completeness: CompletenessBuckets


@dataclass(frozen=True)
class StaticRoutingTable:
    routes: tuple[tuple[str, tuple[str, ...]], ...]
