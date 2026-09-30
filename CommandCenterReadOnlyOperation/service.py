"""One bounded KB READ producer observation; never an application writer."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from FactStore.models import ExplicitFactAppendRequest
from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from FactStore.storage import InMemoryAppendOnlyFactEngine
from FactStore.store import FactStore
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from KbCapitalFactAuthority.models import (
    ExplicitBalancesNormalizationRequest,
    ExplicitCapitalFactBinding,
    ExplicitCapitalFactPolicy,
    ExplicitCapitalPortfolioBinding,
    ExplicitCapitalSnapshotIdentity,
    ExplicitHoldingsCapitalNormalizationRequest,
    ExplicitPositionMarketValueBinding,
)
from KbCapitalFactAuthority.service import run_kb_capital_fact_plane
from KbPortfolioVerticalSlice.change_detection import classify_snapshot_change
from KbPortfolioVerticalSlice.models import (
    ExplicitKbNormalizationRequest,
    ExplicitKbPositionBinding,
)
from KbPortfolioVerticalSlice.normalization import normalize_ssqm2952
from PortfolioSnapshotProducer.models import (
    ExplicitPortfolioFactSelectionCriteria,
    ExplicitPortfolioHoldingFactBinding,
    ExplicitPortfolioSnapshotProductionPolicy,
    ExplicitPortfolioSnapshotProductionRequest,
)
from PortfolioSnapshotProducer.production import PortfolioSnapshotProducer
from ProductionIntegration.journal import ProductionJournal
from ProviderGateway.models import ExplicitBrokerCollectRequest
from ProviderGateway.validation.validators import validate_explicit_collect_outcome

from CommandCenterReadOnlyOperation.models import (
    ReadOnlyObservation,
    ReadOnlyOperationConfig,
    ReadOnlyOperationResult,
)
from CommandCenterReadOnlyOperation.validation import (
    validate_read_only_observation,
)


_FOREIGN_CLASSES = frozenset({"외화증권", "외화증권(M)"})


class _CapturedBalancesAdapter:
    def __init__(self, outcome):
        self.outcome = outcome

    def collect(self, request):
        if request.request_kind != "balances":
            raise ValueError("captured adapter permits balances only")
        return self.outcome


def _require_success(outcome, label):
    validate_explicit_collect_outcome(outcome)
    if outcome.result_kind != "success" or outcome.envelope is None:
        code = "UNAVAILABLE" if outcome.failure is None else outcome.failure.failure_class
        raise ValueError(f"{label} READ failed closed: {code}")
    return outcome.envelope


def _rows(envelope):
    payload = envelope.payload
    if type(payload) is not dict or type(payload.get("dataBody")) is not dict:
        raise ValueError("SSQM2952 response body malformed")
    rows = payload["dataBody"].get("Record1")
    if type(rows) is not list:
        raise ValueError("SSQM2952 Record1 malformed")
    return rows


def _observed_domestic_bindings(config, envelope):
    configured = {
        (x.position_class, x.provider_symbol): x
        for x in config.domestic_bindings
    }
    observed = []
    seen = set()
    for row in _rows(envelope):
        if type(row) is not dict:
            raise ValueError("SSQM2952 row malformed")
        clsf = row.get("clsf")
        symbol = row.get("is_cd")
        currency = row.get("crncy_cd")
        if type(clsf) is not str or type(symbol) is not str or type(currency) is not str:
            raise ValueError("SSQM2952 identity fields malformed")
        if clsf.strip() == "" or symbol.strip() == "":
            raise ValueError("SSQM2952 identity fields blank")
        if clsf in _FOREIGN_CLASSES or (currency.strip() != "" and currency != "KRW"):
            continue
        identity = (clsf, symbol)
        binding = configured.get(identity)
        if binding is None:
            raise ValueError("verified domestic binding required")
        if identity in seen:
            raise ValueError("duplicate response identity")
        seen.add(identity)
        observed.append(binding)
    return tuple(observed)


def _active_records(records):
    superseded = {x.superseded_fact_id for x in records if x.superseded_fact_id}
    return tuple(x for x in records if x.fact_id not in superseded)


def _predecessor(records, kind, symbol=None):
    candidates = []
    for record in _active_records(records):
        payload = record.payload
        if type(payload) is not dict or payload.get("fact_kind") != kind:
            continue
        if symbol is not None and payload.get("provider_symbol") != symbol:
            continue
        candidates.append(record)
    if not candidates:
        return None
    return max(candidates, key=lambda x: (x.collected_at, x.appended_at)).fact_id


def _id(observation_id, category, suffix):
    return f"{category}:{observation_id}:{suffix}"


def _fact_binding(observation_id, suffix, prior):
    return ExplicitCapitalFactBinding(
        _id(observation_id, "fact", suffix),
        _id(observation_id, "envelope", suffix),
        prior,
    )


def run_real_read_only_observation(
    *, adapter, binding, config, fact_store_path, journal_path, observation_id, now,
):
    if type(config) is not ReadOnlyOperationConfig:
        raise TypeError("ReadOnlyOperationConfig required")
    if type(now) is not datetime or now.tzinfo is not timezone.utc:
        raise ValueError("now must be UTC")
    for label, path in (("FactStore", fact_store_path), ("DecisionJournal", journal_path)):
        if not isinstance(path, (str, Path)):
            raise TypeError(f"{label} path required")
        Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

    holdings_request = ExplicitBrokerCollectRequest(
        _id(observation_id, "raw-envelope", "holdings"),
        _id(observation_id, "correlation", "holdings"),
        binding,
        "holdings",
        None,
    )
    balances_request = ExplicitBrokerCollectRequest(
        _id(observation_id, "raw-envelope", "balances"),
        _id(observation_id, "correlation", "balances"),
        binding,
        "balances",
        None,
    )
    holdings_outcome = adapter.collect(holdings_request)
    holdings_envelope = _require_success(holdings_outcome, "SSQM2952")
    observed_bindings = _observed_domestic_bindings(config, holdings_envelope)
    balances_outcome = adapter.collect(balances_request)
    balances_envelope = _require_success(balances_outcome, "SSQM0004")
    now = max(now, holdings_envelope.collected_at, balances_envelope.collected_at)

    journal = DecisionJournal(journal_path)
    durable_journal = ProductionJournal(journal)
    prior_rows = durable_journal.load(JournalRecordKind.READ_ONLY_OBSERVATION)
    already_published = tuple(
        prior for _record, prior in prior_rows
        if prior.observation_id == observation_id
    )
    prior_observation = None if not prior_rows else prior_rows[-1][1]

    durable_engine = SQLiteAppendOnlyFactEngine(fact_store_path)
    try:
        existing = durable_engine.list_in_append_order()
        if already_published:
            prior = already_published[0]
            validate_read_only_observation(prior)
            by_id = {x.fact_id: x for x in existing}
            if not set(prior.application_fact_ids).issubset(by_id):
                raise ValueError("published observation facts missing")
            for fact_id in prior.application_fact_ids:
                durable_engine.get_by_fact_id(fact_id)
            return ReadOnlyOperationResult(
                prior, str(Path(fact_store_path).resolve()),
                str(Path(journal_path).resolve()), 0,
            )
        memory_engine = InMemoryAppendOnlyFactEngine()
        if existing:
            memory_engine.append_batch(existing)
        store = FactStore(lambda: now, memory_engine)
        holdings_raw_id = _id(observation_id, "raw-fact", "holdings")
        holdings_raw = store.append(ExplicitFactAppendRequest(
            holdings_raw_id, holdings_envelope, None,
        ))
        position_bindings = tuple(ExplicitKbPositionBinding(
            config.account_selector,
            item.position_class,
            "KRW",
            item.provider_symbol,
            _id(observation_id, "fact-position", str(index)),
            _id(observation_id, "envelope-position", str(index)),
            item.position_id,
            item.portfolio_subject_id,
            _predecessor(existing, "kb_ssqm2952_position", item.provider_symbol),
        ) for index, item in enumerate(observed_bindings))
        normalized = normalize_ssqm2952(
            raw_record=holdings_raw,
            raw_envelope=holdings_envelope,
            request=ExplicitKbNormalizationRequest(
                holdings_raw_id,
                config.account_selector,
                position_bindings,
                _id(observation_id, "fact", "portfolio-exclusions"),
                _id(observation_id, "envelope", "portfolio-exclusions"),
            ),
        )
        if normalized.exclusion_provenance_append_request is not None:
            store.append(normalized.exclusion_provenance_append_request)
        if normalized.positions:
            store.append_batch(tuple(x.append_request for x in normalized.positions))

        portfolio_result = PortfolioSnapshotProducer(store, lambda: now).produce(
            ExplicitPortfolioSnapshotProductionRequest(
                _id(observation_id, "portfolio-snapshot", "current"),
                _id(observation_id, "observation-context", "current"),
                config.portfolio_id,
                tuple(ExplicitPortfolioHoldingFactBinding(
                    x.append_request.fact_id, x.position_id,
                    x.portfolio_subject_id, "quantity",
                ) for x in normalized.positions if x.is_active_holding),
                (),
                ExplicitPortfolioFactSelectionCriteria(
                    "broker_fact", "kb_open_api",
                    holdings_envelope.collected_at, holdings_envelope.collected_at,
                ),
                ExplicitPortfolioSnapshotProductionPolicy(
                    timedelta(seconds=config.freshness_max_age_seconds)
                ),
            )
        )
        if portfolio_result.result_kind != "success":
            raise ValueError("PortfolioSnapshot production failed closed")
        prior_snapshot = None if prior_observation is None else prior_observation.portfolio_snapshot
        change = classify_snapshot_change(
            run_id=_id(observation_id, "scan", "current"),
            current_snapshot=portfolio_result.snapshot,
            prior_snapshot=prior_snapshot,
        )
        if change == "CHANGED":
            change = "CHANGE_DETECTED"

        balance_kinds = (
            ("orderable-cash", "kb_ssqm0004_orderable_cash"),
            ("deposit-today", "kb_ssqm0004_deposit_today"),
            ("deposit-d1", "kb_ssqm0004_deposit_d1"),
            ("deposit-d2", "kb_ssqm0004_deposit_d2"),
            ("withdrawable", "kb_ssqm0004_withdrawable_cash"),
            ("orderable-total", "kb_ssqm0004_orderable_total"),
        )
        balance_bindings = tuple(
            _fact_binding(observation_id, suffix, _predecessor(existing, kind))
            for suffix, kind in balance_kinds
        )
        balances_raw_id = _id(observation_id, "raw-fact", "balances")
        balances_normalization = ExplicitBalancesNormalizationRequest(
            balances_raw_id, config.account_selector, "KRW", *balance_bindings,
        )
        holdings_capital = ExplicitHoldingsCapitalNormalizationRequest(
            holdings_raw_id,
            config.account_selector,
            _fact_binding(
                observation_id, "account-valuation",
                _predecessor(existing, "kb_ssqm2952_broker_reported_account_valuation"),
            ),
            tuple(ExplicitPositionMarketValueBinding(
                config.account_selector, item.position_class, "KRW",
                item.provider_symbol,
                _id(observation_id, "fact-position-value", str(index)),
                _id(observation_id, "envelope-position-value", str(index)),
                _predecessor(existing, "kb_ssqm2952_position_market_value", item.provider_symbol),
            ) for index, item in enumerate(observed_bindings)),
            _id(observation_id, "fact", "capital-exclusions"),
            _id(observation_id, "envelope", "capital-exclusions"),
        )
        capital_result = run_kb_capital_fact_plane(
            adapter=_CapturedBalancesAdapter(balances_outcome),
            balances_collect_request=balances_request,
            balances_raw_fact_id=balances_raw_id,
            balances_normalization_request=balances_normalization,
            fact_store=store,
            snapshot_identity=ExplicitCapitalSnapshotIdentity(
                _id(observation_id, "capital-snapshot", "current"),
                config.account_selector,
            ),
            portfolio_binding=ExplicitCapitalPortfolioBinding(
                portfolio_result.snapshot.portfolio_snapshot_id,
                config.portfolio_id,
                portfolio_result.snapshot.observation_context.observation_context_id,
            ),
            policy=ExplicitCapitalFactPolicy(
                timedelta(seconds=config.freshness_max_age_seconds)
            ),
            now=now,
            holdings_raw_fact_id=holdings_raw_id,
            holdings_raw_envelope=holdings_envelope,
            holdings_capital_normalization_request=holdings_capital,
        )
        if capital_result.result_kind != "success":
            raise ValueError(
                f"CapitalSnapshot failed closed: {capital_result.failure_code}"
            )
        all_records = memory_engine.list_in_append_order()
        new_records = all_records[len(existing):]
        application_ids = tuple(
            record.fact_id for record in new_records
            if type(record.payload) is dict and record.payload.get("fact_kind") in {
                "kb_ssqm2952_position",
                "kb_ssqm2952_position_market_value",
                "kb_ssqm0004_orderable_cash",
                "kb_ssqm2952_broker_reported_account_valuation",
                "kb_ssqm2952_domestic_projection_exclusions",
                "kb_ssqm2952_capital_domestic_projection_exclusions",
            }
        )
        observation = ReadOnlyObservation(
            observation_id,
            now,
            portfolio_result.snapshot,
            portfolio_result.provenance,
            capital_result.capital_snapshot,
            change,
            application_ids,
            (holdings_raw_id, balances_raw_id),
            False,
        )
        validate_read_only_observation(observation)
        durable_engine.append_batch(new_records)
        durable_journal.append_artifact(
            JournalRecordKind.READ_ONLY_OBSERVATION,
            observation_id,
            observation,
            now,
            observation_id,
        )
        return ReadOnlyOperationResult(
            observation,
            str(Path(fact_store_path).resolve()),
            str(Path(journal_path).resolve()),
            len(new_records),
        )
    finally:
        durable_engine.close()
        journal.close()
