from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitResearchCandidate:
    """Caller admission to research only; not watchlist membership or investment approval."""
    subject_id: str
    admission_id: str
    provenance: str


@dataclass(frozen=True)
class PlannedUnit:
    research_id: str
    subject_id: str
    task_type: str
    priority: str
    title: str
    objective: str


@dataclass(frozen=True)
class PlanSkip:
    subject_id: str
    reason: str


@dataclass(frozen=True)
class ResearchPlan:
    run_id: str
    units: tuple[PlannedUnit, ...]
    skips: tuple[PlanSkip, ...]
