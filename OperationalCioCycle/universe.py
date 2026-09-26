from datetime import datetime, timezone, timedelta

from PortfolioDomain.models import PortfolioSubject
from PortfolioDomain.validation import validate_portfolio_subject
from PortfolioSnapshot.validation import validate_explicit_portfolio_snapshot
from InvestmentDecisionVerticalSlice.validation import nonblank
from OperationalCioCycle.models import CandidateAdmission, CycleConfig, OpportunityUniverse, UniverseMember


def utc(value):
    if type(value) is not datetime or value.tzinfo is not timezone.utc:
        raise ValueError("timestamp must be exact UTC datetime")


def validate_config(config):
    if type(config) is not CycleConfig:
        raise TypeError("config must be CycleConfig")
    for name in ("cycle_id", "snapshot_id", "iro_run_id", "universe_id", "universe_policy_version", "comparison_policy_id", "journal_id"):
        nonblank(name, getattr(config, name))
    if type(config.freshness_max_age) is not timedelta or config.freshness_max_age < timedelta(0):
        raise ValueError("explicit nonnegative freshness policy required")


def build_universe(config, snapshot, subjects, admissions, created_at):
    validate_config(config)
    utc(created_at)
    validate_explicit_portfolio_snapshot(snapshot)
    if snapshot.portfolio_snapshot_id != config.snapshot_id:
        raise ValueError("universe snapshot binding mismatch")
    if type(subjects) is not tuple or type(admissions) is not tuple:
        raise TypeError("subjects and admissions must be tuples")
    identities = {}
    for subject in subjects:
        validate_portfolio_subject(subject)
        if subject.subject_id in identities:
            raise ValueError("duplicate subject identity")
        identities[subject.subject_id] = subject
    holdings = [x.position.membership.portfolio_subject_id for x in snapshot.holding_snapshot.holding_observations]
    watchlist = [x.membership.portfolio_subject_id for x in snapshot.watchlist_entries]
    if len(set(holdings)) != len(holdings) or len(set(watchlist)) != len(watchlist):
        raise ValueError("duplicate snapshot subject identity")
    admitted = {}
    admission_ids = set()
    for item in admissions:
        if type(item) is not CandidateAdmission:
            raise TypeError("candidate must be explicit CandidateAdmission")
        validate_portfolio_subject(item.subject)
        nonblank("admission_id", item.admission_id)
        nonblank("admission provenance", item.provenance)
        key = item.subject.subject_id
        if key in admitted or key in holdings or item.admission_id in admission_ids:
            raise ValueError("duplicate/conflicting candidate admission")
        if identities.get(key) != item.subject:
            raise ValueError("candidate subject identity mismatch")
        admitted[key] = item
        admission_ids.add(item.admission_id)
    ordered = tuple(dict.fromkeys(holdings + watchlist + list(admitted)))
    if not ordered or set(ordered) != set(identities):
        raise ValueError("empty universe or identity coverage mismatch")
    members = []
    for key in ordered:
        sources, provenance = [], []
        if key in holdings:
            sources.append("holding")
            provenance.append(config.snapshot_id)
        if key in watchlist:
            sources.append("watchlist")
            provenance.append(config.snapshot_id)
        if key in admitted:
            sources.append("explicit_candidate")
            provenance.extend((admitted[key].admission_id, admitted[key].provenance))
        members.append(UniverseMember(identities[key], tuple(sources), tuple(provenance), key in holdings or key in admitted))
    if not any(x.eligible for x in members):
        raise ValueError("universe has no eligible evaluation subjects")
    return OpportunityUniverse(config.universe_id, config.cycle_id, config.snapshot_id, tuple(members), config.universe_policy_version, created_at)
