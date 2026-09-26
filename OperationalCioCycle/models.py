"""Immutable application inputs. Eligibility is analytical, never allocation authority."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta

from InvestmentDecisionVerticalSlice.models import NumericSignalReference, SemanticProducerProvenance
from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactInterpretationPolicy.models import PortfolioImpactInterpretationPolicy


@dataclass(frozen=True)
class CandidateAdmission:
    subject: PortfolioSubject
    admission_id: str
    provenance: str


@dataclass(frozen=True)
class UniverseMember:
    subject: PortfolioSubject
    sources: tuple[str, ...]
    provenance: tuple[str, ...]
    eligible: bool


@dataclass(frozen=True)
class OpportunityUniverse:
    universe_id: str
    cycle_id: str
    snapshot_id: str
    members: tuple[UniverseMember, ...]
    policy_version: str
    created_at: datetime


@dataclass(frozen=True)
class SemanticBinding:
    committee_id: str
    provider_id: str
    provenance: SemanticProducerProvenance
    producer_id: str
    probability_policy_version: str


@dataclass(frozen=True)
class SubjectPlan:
    subject: PortfolioSubject
    horizon_id: str
    unit_id: str
    impact_policy: PortfolioImpactInterpretationPolicy
    binding: SemanticBinding
    numeric_signals: tuple[NumericSignalReference, ...] = ()
    prior_thesis_id: str | None = None


@dataclass(frozen=True)
class CycleConfig:
    cycle_id: str
    snapshot_id: str
    iro_run_id: str
    universe_id: str
    universe_policy_version: str
    comparison_policy_id: str
    journal_id: str
    freshness_max_age: timedelta


@dataclass(frozen=True)
class CycleResult:
    cycle_id: str
    universe: OpportunityUniverse
    evaluations: tuple
    comparisons: tuple
    decisions: tuple
    journal_record_id: str
