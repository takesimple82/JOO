from __future__ import annotations

from dataclasses import dataclass

from InvestmentResearchOrchestrator.models.enums import (
    MemoryDeltaClass,
)


@dataclass(frozen=True)
class MemoryProvenanceIdentity:
    committee_id: str | None
    provider_id: str | None
    prompt_hash: str | None
    source_reference: str | None


@dataclass(frozen=True)
class MemoryDeltaDetail:
    prior_statements: tuple[str, ...]
    current_statements: tuple[str, ...]
    prior_provenance: tuple[MemoryProvenanceIdentity, ...]
    current_provenance: tuple[MemoryProvenanceIdentity, ...]


@dataclass(frozen=True)
class MemoryDelta:
    subject_key: str
    prior_present: bool
    delta_class: MemoryDeltaClass
    detail: MemoryDeltaDetail | None = None


@dataclass(frozen=True)
class MemoryDeltaSet:
    run_id: str
    deltas: tuple[MemoryDelta, ...]
