from dataclasses import dataclass


@dataclass
class ResearchSnapshot:
    snapshot_id: str
    task_id: str
    execution_id: str
    portfolio_version: str
    prompt_id: str
    prompt_version: str
    committee_version: str
    event_manifest: str
    created_at: str
    status: str


@dataclass
class VersionManifest:
    snapshot_id: str
    portfolio_version: str
    prompt_id: str
    prompt_version: str
    committee_version: str
    created_at: str
