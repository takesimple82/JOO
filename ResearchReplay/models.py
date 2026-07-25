from dataclasses import dataclass


@dataclass
class ReplayRequest:
    snapshot_id: str
    task_id: str
    execution_id: str
    requested_at: str
    requested_by: str


@dataclass
class ReplayResult:
    snapshot_id: str
    execution_id: str
    status: str
    replayed_events: str
    committee_results: str
    summary: str
