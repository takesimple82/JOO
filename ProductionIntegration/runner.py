"""Concrete Block E stage adapter over existing A/B0/B/C authorities."""
from __future__ import annotations

from decimal import Decimal

from BrokerExecutionCycle.authorization import assert_tea_binds_intent
from BrokerExecutionCycle.integrity import integrity_seal as broker_seal
from BrokerExecutionCycle.provider_read import normalize_ssqm2341_status
from BrokerExecutionCycle.reconciliation import fill_fact_from_status, reconcile_acceptance_and_fill
from BrokerExecutionCycle.recovery import plan_submission_unknown_recovery
from BrokerExecutionCycle.service import run_pretrade_validation, seal_order_intent_from_approval_chain
from BrokerExecutionCycle.vocabularies import SIDE_BUY, SIDE_SELL
from CapitalAllocationCycle.models import CapitalAllocationRequest, ResolvedExactAmount
from CapitalAllocationCycle.service import run_capital_allocation_cycle
from CapitalAllocationCycle.validation import validate_approval, validate_artifact
from CapitalAllocationCycle.vocabularies import APPROVAL_DECISION_APPROVED
from CommandCenterRuntime.vocabularies import *  # stage/wake closed vocabularies
from CommandCenterRuntime.integrity import integrity_seal as command_center_seal
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from KbCapitalFactAuthority.models import ExplicitCapitalSnapshot
from KbCapitalFactAuthority.replay import replay_capital_snapshot_from_store
from KbCapitalFactAuthority.service import run_kb_capital_fact_plane
from OperationalCioCycle.service import replay_cycle, run_operational_cio_cycle


class ProductionJooDomainRunner:
    """Stateful one-cycle adapter; all arithmetic and decisions stay in A/B0/B/C.

    The adapter never creates Human approval, TEA, or broker mutation. Every
    returned identifier names an authoritative artifact in the existing journal
    (or an immutable FactStore artifact referenced by a journaled snapshot).
    """

    def __init__(self, *, inputs, journal, source_event_id: str, now, wake_events):
        self.inputs = inputs
        self.production_journal = journal
        self.journal = journal.journal
        self.source_event_id = source_event_id
        self.now = now
        self.wake_events = wake_events
        self._occ = None
        self._capital = None
        self._proposal = None
        self._validation = None
        self._intent = None
        self._broker = {}
        self._refs: dict[str, str] = {}

    def retry_safe(self, _stage: str) -> bool:
        # Provider/AI/journal/Human/execution boundaries are not blanket-retried.
        return False

    @property
    def artifact_references(self):
        return tuple(sorted(self._refs.items()))

    def _ref(self, name, record_id):
        if type(record_id) is not str or not record_id:
            raise ValueError("authoritative artifact ID required")
        prior = self._refs.get(name)
        if prior is not None and prior != record_id:
            raise ValueError("artifact reference drift")
        self._refs[name] = record_id
        return record_id

    def _ref_nested(self, name, parent_record_id, child_id):
        return self._ref(name, f"{parent_record_id}#{name}={child_id}")

    def _load_one(self, kind, record_id):
        loaded = self.production_journal.load(kind, record_id)
        if len(loaded) != 1:
            raise ValueError(f"MISSING_DURABLE_{kind.value}")
        return loaded[0][1]

    def _ensure_occ(self):
        if self._occ is not None:
            return self._occ
        kwargs = self.inputs.operational_cio_kwargs
        if type(kwargs) is not dict:
            raise ValueError("OPERATIONAL_CIO_INPUT_REQUIRED")
        config = kwargs.get("config")
        if config is None or kwargs.get("journal") is not self.journal:
            raise ValueError("OPERATIONAL_CIO_JOURNAL_BINDING_REQUIRED")
        record_id = config.cycle_id + ":completed"
        existing = [r for r in self.journal.list_records() if r.record_id == record_id]
        if existing:
            self._occ = replay_cycle(self.journal, config.cycle_id, config.journal_id)
        else:
            self._occ = run_operational_cio_cycle(**kwargs)
        self._ref("operational_cio_cycle", self._occ.journal_record_id)
        self._ref_nested("portfolio_snapshot", self._occ.journal_record_id, self._occ.universe.snapshot_id)
        for index, decision in enumerate(self._occ.decisions):
            self._ref_nested(f"cio_decision:{index}", self._occ.journal_record_id, decision.decision_id)
        for index, evaluation in enumerate(self._occ.evaluations):
            self._ref_nested(f"exact_ev:{index}", self._occ.journal_record_id, evaluation.ev_record.record_id)
        return self._occ

    def _ensure_capital(self):
        if self._capital is not None:
            return self._capital
        kwargs = self.inputs.capital_fact_kwargs
        if type(kwargs) is not dict:
            raise ValueError("CAPITAL_FACT_INPUT_REQUIRED")
        identity = kwargs.get("snapshot_identity")
        if identity is None:
            raise ValueError("CAPITAL_SNAPSHOT_IDENTITY_REQUIRED")
        loaded = self.production_journal.load(JournalRecordKind.CAPITAL_SNAPSHOT, identity.capital_snapshot_id)
        if loaded:
            self._capital = loaded[0][1]
        else:
            self._capital = self._recover_capital_snapshot(kwargs)
            if self._capital is None:
                result = run_kb_capital_fact_plane(**kwargs)
                if result.result_kind != "success" or result.capital_snapshot is None:
                    raise ValueError(result.failure_code or "CAPITAL_FACT_PLANE_FAILED")
                self._capital = result.capital_snapshot
            self.production_journal.append_artifact(
                JournalRecordKind.CAPITAL_SNAPSHOT, self._capital.capital_snapshot_id,
                self._capital, self.now, self.source_event_id,
            )
        self._validate_capital_snapshot(self._capital, kwargs)
        self._ref("capital_snapshot", self._capital.capital_snapshot_id)
        self._ref("orderable_cash_fact", self._capital.orderable_cash_fact_id)
        return self._capital

    def _recover_capital_snapshot(self, kwargs):
        """Recover the deterministic B0 snapshot after FactStore-only crash."""
        store = kwargs["fact_store"]
        balances = kwargs["balances_normalization_request"]
        holdings = kwargs.get("holdings_capital_normalization_request")
        required = [
            kwargs["balances_raw_fact_id"], balances.orderable_cash.fact_id,
            balances.deposit_today.fact_id, balances.deposit_d1.fact_id,
            balances.deposit_d2.fact_id, balances.withdrawable_cash.fact_id,
            balances.orderable_total.fact_id,
        ]
        if holdings is not None:
            required.extend([kwargs["holdings_raw_fact_id"], holdings.account_valuation.fact_id])
            required.extend(x.fact_id for x in holdings.position_bindings)
        try:
            records = [store.get_by_fact_id(x) for x in required]
            for record in records:
                store.verify_integrity(record.fact_id)
        except ValueError:
            return None
        identity = kwargs["snapshot_identity"]
        binding = kwargs["portfolio_binding"]
        policy = kwargs["policy"]
        raw = records[0]
        snapshot = ExplicitCapitalSnapshot(
            identity.capital_snapshot_id, identity.account_selector, raw.provider_id,
            "KRW", raw.collected_at, policy.freshness_max_age,
            binding.portfolio_snapshot_id, binding.portfolio_id, binding.observation_context_id,
            kwargs["balances_raw_fact_id"], kwargs.get("holdings_raw_fact_id") if holdings else None,
            balances.orderable_cash.fact_id, balances.deposit_today.fact_id,
            balances.deposit_d1.fact_id, balances.deposit_d2.fact_id,
            balances.withdrawable_cash.fact_id, balances.orderable_total.fact_id,
            holdings.account_valuation.fact_id if holdings else None,
            tuple(x.fact_id for x in holdings.position_bindings) if holdings else (),
            "NOT_SIZING_AUTHORITY",
        )
        return replay_capital_snapshot_from_store(fact_store=store, snapshot=snapshot)

    def _validate_capital_snapshot(self, snapshot, kwargs):
        identity = kwargs["snapshot_identity"]
        binding = kwargs["portfolio_binding"]
        policy = kwargs["policy"]
        if (snapshot.capital_snapshot_id, snapshot.account_selector,
            snapshot.portfolio_snapshot_id, snapshot.portfolio_id,
            snapshot.observation_context_id, snapshot.freshness_max_age) != (
            identity.capital_snapshot_id, identity.account_selector,
            binding.portfolio_snapshot_id, binding.portfolio_id,
            binding.observation_context_id, policy.freshness_max_age,
        ):
            raise ValueError("CAPITAL_SNAPSHOT_CURRENT_BINDING_MISMATCH")
        if self.now < snapshot.collected_at or self.now - snapshot.collected_at > policy.freshness_max_age:
            raise ValueError("CAPITAL_SNAPSHOT_STALE")
        replay_capital_snapshot_from_store(fact_store=kwargs["fact_store"], snapshot=snapshot)

    def _resolved_cash(self, snapshot):
        store = self.inputs.capital_fact_kwargs["fact_store"]
        record = store.get_by_fact_id(snapshot.orderable_cash_fact_id)
        store.verify_integrity(record.fact_id)
        presence = record.payload.get("amount_presence")
        text = record.payload.get("amount")
        amount = None if text is None else Decimal(text)
        return ResolvedExactAmount(record.fact_id, presence, amount, record.payload.get("currency_code"))

    def _verify_position_values(self, snapshot, values):
        allowed = set(snapshot.position_market_value_fact_ids)
        store = self.inputs.capital_fact_kwargs["fact_store"]
        for view in values:
            if view.market_value_fact_id not in allowed:
                raise ValueError("POSITION_VALUE_NOT_IN_CAPITAL_SNAPSHOT")
            record = store.get_by_fact_id(view.market_value_fact_id)
            store.verify_integrity(record.fact_id)
            amount = record.payload.get("amount")
            exact = None if amount is None else Decimal(amount)
            if (record.payload.get("amount_presence"), exact, record.payload.get("currency_code")) != (
                view.presence, view.market_value_krw, view.currency_code
            ):
                raise ValueError("POSITION_VALUE_FACT_MISMATCH")

    def _ensure_proposal(self):
        if self._proposal is not None:
            return self._proposal
        composition = self.inputs.allocation
        if composition is None:
            raise ValueError("ALLOCATION_COMPOSITION_REQUIRED")
        record_id = "proposal:" + composition.request_id
        loaded = self.production_journal.load(JournalRecordKind.CAPITAL_ALLOCATION_PROPOSAL, record_id)
        occ = self._ensure_occ()
        capital = self._ensure_capital()
        if capital.portfolio_snapshot_id != occ.universe.snapshot_id:
            raise ValueError("CAPITAL_PORTFOLIO_SNAPSHOT_MISMATCH")
        self._verify_position_values(capital, composition.position_values)
        request = CapitalAllocationRequest(
            composition.request_id,
            loaded[0][1].created_at if loaded else self.now,
            composition.hip, capital,
            self._resolved_cash(capital), composition.position_values,
            occ.universe, occ.decisions, occ.evaluations, occ.comparisons,
            composition.proposed_notionals,
        )
        result = run_capital_allocation_cycle(request)
        if result.result_kind != "success" or result.proposal is None:
            raise ValueError("|".join(result.failure_codes) or "ALLOCATION_FAILED")
        expected = result.proposal
        if loaded:
            if loaded[0][1] != expected:
                raise ValueError("STALE_ALLOCATION_PROPOSAL_BINDING")
            self._proposal = loaded[0][1]
        else:
            self._proposal = expected
            self.production_journal.append_artifact(
                JournalRecordKind.HUMAN_INVESTMENT_POLICY, composition.hip.policy_id,
                composition.hip, self.now, self.source_event_id,
            )
            self.production_journal.append_artifact(
                JournalRecordKind.CAPITAL_ALLOCATION_PROPOSAL, record_id,
                self._proposal, self.now, self.source_event_id,
            )
        self._ref("capital_allocation_proposal", self._proposal.proposal_id)
        return self._proposal

    def _observe_iha(self):
        proposal = self._ensure_proposal()
        approval = self.inputs.investment_approval
        if approval is None:
            raise ValueError("INVESTMENT_HUMAN_APPROVAL_REQUIRED")
        validate_approval(approval)
        if not self.production_journal.contains_exact(
            JournalRecordKind.INVESTMENT_HUMAN_APPROVAL, approval.approval_id, approval
        ):
            raise ValueError("INVESTMENT_HUMAN_APPROVAL_NOT_DURABLE")
        composition = self.inputs.allocation
        capital = self._ensure_capital()
        if (approval.proposal_id, approval.proposal_integrity_seal,
            approval.capital_snapshot_id, approval.hip_integrity_seal) != (
            proposal.proposal_id, proposal.integrity_seal,
            capital.capital_snapshot_id, composition.hip.integrity_seal,
        ):
            raise ValueError("INVESTMENT_HUMAN_APPROVAL_BINDING_MISMATCH")
        if approval.decision != APPROVAL_DECISION_APPROVED:
            raise ValueError("INVESTMENT_HUMAN_APPROVAL_NOT_APPROVED")
        artifact = self.inputs.approved_artifact
        if artifact is None:
            raise ValueError("SEALED_APPROVED_ALLOCATION_REQUIRED")
        validate_artifact(artifact)
        if not self.production_journal.contains_exact(
            JournalRecordKind.SEALED_APPROVED_ALLOCATION, artifact.artifact_id, artifact
        ):
            raise ValueError("SEALED_APPROVED_ALLOCATION_NOT_DURABLE")
        if (artifact.approval_id, artifact.approval_integrity_seal,
            artifact.proposal_id, artifact.proposal_integrity_seal,
            artifact.hip_integrity_seal) != (
            approval.approval_id, approval.integrity_seal,
            proposal.proposal_id, proposal.integrity_seal,
            composition.hip.integrity_seal,
        ):
            raise ValueError("SEALED_APPROVED_ALLOCATION_BINDING_MISMATCH")
        self._ref("investment_human_approval", approval.approval_id)
        self._ref("sealed_approved_allocation", artifact.artifact_id)
        return approval, artifact

    def _ensure_pretrade(self, observed_chain=None):
        if self._intent is not None:
            return self._intent
        composition = self.inputs.pretrade
        if composition is None:
            raise ValueError("PRETRADE_INPUT_REQUIRED")
        loaded = self.production_journal.load(JournalRecordKind.ORDER_INTENT_SEALED, composition.intent_id)
        approval, artifact = observed_chain or self._observe_iha()
        bundle = composition.bundle
        max_age = composition.freshness_max_age
        if type(max_age).__name__ != "timedelta" or max_age.total_seconds() <= 0:
            raise ValueError("EXPLICIT_PRETRADE_FRESHNESS_POLICY_REQUIRED")
        capital_kwargs = self.inputs.capital_fact_kwargs
        capital_policy = None if type(capital_kwargs) is not dict else capital_kwargs.get("policy")
        if capital_policy is None or capital_policy.freshness_max_age != max_age:
            raise ValueError("PRETRADE_FRESHNESS_POLICY_BINDING_MISMATCH")
        observed_times = [
            bundle.collected_at, bundle.quote.collected_at,
            bundle.orderable_cash.collected_at, bundle.session.collected_at,
            bundle.proposed_limit_price.bound_at,
        ]
        if bundle.sellable is not None:
            observed_times.append(bundle.sellable.collected_at)
        if any(value > self.now or self.now - value > max_age for value in observed_times):
            raise ValueError("PRETRADE_STALE_OR_INVALID")
        legs = tuple(
            leg for leg in artifact.legs
            if leg.portfolio_subject_id == composition.portfolio_subject_id
        )
        if len(legs) != 1:
            raise ValueError("ORDER_INTENT_ALLOCATION_LEG_BINDING_MISSING")
        leg = legs[0]
        authorized_notional = (
            leg.delta_market_value_krw if composition.side == SIDE_BUY
            else -leg.delta_market_value_krw if composition.side == SIDE_SELL
            else None
        )
        if authorized_notional is None or authorized_notional <= Decimal("0") or composition.approved_notional_krw != authorized_notional:
            raise ValueError("ORDER_INTENT_NOTIONAL_NOT_APPROVED_ALLOCATION_DELTA")
        prior_validation = None
        validated_at = self.now
        sealed_at = self.now
        if loaded:
            prior_intent = loaded[0][1]
            validations = self.production_journal.load(
                JournalRecordKind.PRETRADE_REVALIDATION,
                prior_intent.pretrade_validation_id,
            )
            if len(validations) != 1:
                raise ValueError("PRETRADE_VALIDATION_NOT_DURABLE")
            prior_validation = validations[0][1]
            validated_at = prior_validation.validated_at
            sealed_at = prior_intent.sealed_at
        self._validation = run_pretrade_validation(
                validation_id="pretrade:" + composition.intent_id,
                bundle=bundle, side=composition.side,
                approved_notional_krw=composition.approved_notional_krw,
                validated_at=validated_at,
            )
        if not self._validation.passed:
            raise ValueError("PRETRADE_FAIL_CLOSED")
        if prior_validation is not None and prior_validation != self._validation:
            raise ValueError("STALE_PRETRADE_VALIDATION_BINDING")
        expected = seal_order_intent_from_approval_chain(
                intent_id=composition.intent_id, side=composition.side,
                portfolio_subject_id=composition.portfolio_subject_id,
                bundle=bundle, validation=self._validation,
                artifact=artifact, approval=approval, sealed_at=sealed_at,
            )
        if loaded:
            if loaded[0][1] != expected:
                raise ValueError("STALE_ORDER_INTENT_BINDING")
            self._intent = loaded[0][1]
        else:
            self._intent = expected
            self.production_journal.append_artifact(
                JournalRecordKind.PRETRADE_REVALIDATION, self._validation.validation_id,
                self._validation, self.now, self.source_event_id,
            )
            self.production_journal.append_artifact(
                JournalRecordKind.ORDER_INTENT_SEALED, self._intent.intent_id,
                self._intent, self.now, self.source_event_id,
            )
        self._ref("order_intent", self._intent.intent_id)
        return self._intent

    def _observe_tea(self):
        intent = self._ensure_pretrade()
        tea = self.inputs.trade_authorization
        if tea is None:
            raise ValueError("TRADE_EXECUTION_AUTHORIZATION_REQUIRED")
        if not self.production_journal.contains_exact(
            JournalRecordKind.TRADE_EXECUTION_AUTHORIZATION, tea.authorization_id, tea
        ):
            raise ValueError("TRADE_EXECUTION_AUTHORIZATION_NOT_DURABLE")
        assert_tea_binds_intent(tea, intent)
        if tea.account_binding_id != intent.account_binding_id or tea.account_binding_seal != intent.account_binding_seal:
            raise ValueError("TRADE_EXECUTION_ACCOUNT_BINDING_MISMATCH")
        if tea.one_shot is not True:
            raise ValueError("TRADE_EXECUTION_AUTHORIZATION_NOT_ONE_SHOT")
        self._ref("trade_execution_authorization", tea.authorization_id)
        return tea

    def _ensure_broker_read(self):
        recovery = self.inputs.broker_recovery
        if recovery is None:
            raise ValueError("BROKER_READ_RECOVERY_REQUIRED")
        acceptance = recovery.acceptance
        acceptance_payload = {
            "classification_id": acceptance.classification_id,
            "attempt_id": acceptance.attempt_id, "outcome": acceptance.outcome,
            "process_flag": acceptance.process_flag,
            "broker_order_no": acceptance.broker_order_no,
            "http_status": acceptance.http_status,
            "raw_message": acceptance.raw_message,
            "classified_at": acceptance.classified_at,
        }
        if broker_seal(acceptance_payload) != acceptance.integrity_seal:
            raise ValueError("BROKER_ACCEPTANCE_INTEGRITY_MISMATCH")
        acceptance_kinds = (
            JournalRecordKind.BROKER_ACCEPTANCE, JournalRecordKind.BROKER_REJECTION,
            JournalRecordKind.SUBMISSION_OUTCOME_UNKNOWN,
        )
        if not any(self.production_journal.contains_exact(kind, acceptance.classification_id, acceptance)
                   for kind in acceptance_kinds):
            raise ValueError("BROKER_ACCEPTANCE_NOT_DURABLE")
        attempts = self.production_journal.load(
            JournalRecordKind.BROKER_SUBMIT_ATTEMPT, acceptance.attempt_id
        )
        if len(attempts) != 1:
            raise ValueError("BROKER_ACCEPTANCE_ATTEMPT_MISSING")
        self._ref("broker_acceptance", acceptance.classification_id)
        status = None
        fill = None
        if recovery.status_fact is not None:
            if recovery.fact_store is None or recovery.raw_status_fact_id is None:
                raise ValueError("BROKER_STATUS_RAW_PROVENANCE_REQUIRED")
            raw = recovery.fact_store.get_by_fact_id(recovery.raw_status_fact_id)
            recovery.fact_store.verify_integrity(raw.fact_id)
            if (raw.provider_id != "kb_open_api" or raw.source_class != "broker_fact"
                    or raw.status != "success" or raw.collected_at != self.now):
                raise ValueError("BROKER_STATUS_RAW_AUTHORITY_INVALID")
            status = normalize_ssqm2341_status(
                fact_id=recovery.status_fact.fact_id, payload=raw.payload,
                query_order_no=recovery.status_fact.query_order_no,
                query_order_date=recovery.status_fact.query_order_date,
                collected_at=raw.collected_at, raw_envelope_id=raw.envelope_id,
            )
            if status != recovery.status_fact:
                raise ValueError("BROKER_STATUS_FACT_PROVENANCE_MISMATCH")
            fill = fill_fact_from_status(
                fact_id="fill:" + acceptance.attempt_id, status=status, observed_at=self.now,
            )
            self.production_journal.append_artifact(
                JournalRecordKind.ORDER_STATUS_FACT, status.fact_id, status, self.now, self.source_event_id,
            )
            self.production_journal.append_artifact(
                JournalRecordKind.FILL_FACT, fill.fact_id, fill, self.now, self.source_event_id,
            )
            self._ref("order_status_fact", status.fact_id)
            self._ref("fill_fact", fill.fact_id)
        if acceptance.outcome == "SUBMISSION_OUTCOME_UNKNOWN":
            plan = plan_submission_unknown_recovery(
                plan_id="recovery:" + acceptance.attempt_id, acceptance=acceptance, status_fact=status,
            )
            self.production_journal.append_artifact(
                JournalRecordKind.SUBMISSION_OUTCOME_UNKNOWN, plan.plan_id, plan, self.now, self.source_event_id,
            )
            self._ref("unknown_recovery", plan.plan_id)
        recon = reconcile_acceptance_and_fill(
            result_id="recon:" + acceptance.attempt_id, attempt_id=acceptance.attempt_id,
            acceptance=acceptance, fill=fill,
            cash_corroborated=recovery.cash_corroborated,
            holdings_corroborated=recovery.holdings_corroborated,
            reconciled_at=self.now,
        )
        self.production_journal.append_artifact(
            JournalRecordKind.RECONCILIATION_RESULT, recon.result_id, recon, self.now, self.source_event_id,
        )
        self._broker = {"status": status, "fill": fill, "reconciliation": recon}
        self._ref("reconciliation", recon.result_id)
        return self._broker

    def _approval_gate_for_wakes(self):
        transitions = {x.fact_id: x for x in self.inputs.approval_transitions}
        if len(transitions) != len(self.inputs.approval_transitions):
            raise ValueError("DUPLICATE_APPROVAL_TRANSITION_ID")
        for item in transitions.values():
            payload = {
                "fact_id": item.fact_id, "gate_kind": item.gate_kind,
                "approval_or_authorization_id": item.approval_or_authorization_id,
                "decision": item.decision, "bound_artifact_id": item.bound_artifact_id,
                "observed_at": item.observed_at,
            }
            if command_center_seal(payload) != item.integrity_seal:
                raise ValueError("APPROVAL_TRANSITION_INTEGRITY_MISMATCH")
        relevant = [transitions.get(w.fact_or_evidence_id) for w in self.wake_events if w.wake_type == WAKE_APPROVAL_TRANSITION]
        if any(x is None for x in relevant):
            raise ValueError("APPROVAL_TRANSITION_AUTHORITY_MISSING")
        return tuple(x for x in relevant if x is not None)

    def __call__(self, stage, _primary_wake):
        if stage == STAGE_FACT_REFRESH:
            return tuple(self._ref(f"wake_source:{i}", w.fact_or_evidence_id) for i, w in enumerate(self.wake_events))
        if stage in {STAGE_PORTFOLIO_SNAPSHOT, STAGE_RESEARCH, STAGE_SEMANTIC_ADMISSION,
                     STAGE_THESIS, STAGE_EXPECTED_VALUE, STAGE_CIO}:
            occ = self._ensure_occ()
            return tuple(value for _, value in self.artifact_references)
        if stage == STAGE_CAPITAL_SNAPSHOT:
            return (self._ensure_capital().capital_snapshot_id,)
        if stage == STAGE_CAPITAL_ALLOCATION:
            return (self._ensure_proposal().proposal_id,)
        if stage == STAGE_INVESTMENT_HUMAN_GATE:
            transitions = self._approval_gate_for_wakes()
            approval, artifact = self._observe_iha()
            matching = tuple(x for x in transitions if x.gate_kind == "INVESTMENT_HUMAN_APPROVAL")
            if matching and (len(matching) != 1 or
                    matching[0].approval_or_authorization_id != approval.approval_id or
                    matching[0].decision != approval.decision or
                    matching[0].bound_artifact_id not in {approval.proposal_id, artifact.artifact_id}):
                raise ValueError("INVESTMENT_APPROVAL_TRANSITION_BINDING_MISMATCH")
            ids = [approval.approval_id, artifact.artifact_id]
            # An APPROVED IHA permits preparation only. It still cannot create
            # TEA or mutate; the exact sealed intent is exposed to the TEA gate.
            if self.inputs.pretrade is not None:
                ids.append(self._ensure_pretrade((approval, artifact)).intent_id)
            return tuple(ids)
        if stage == STAGE_PRETRADE:
            return (self._ensure_pretrade().intent_id,)
        if stage == STAGE_TRADE_HUMAN_GATE:
            transitions = self._approval_gate_for_wakes()
            if transitions and all(x.gate_kind != "TRADE_EXECUTION_AUTHORIZATION" for x in transitions):
                raise ValueError("TRADE_EXECUTION_AUTHORIZATION_REQUIRED")
            tea = self._observe_tea()
            matching = tuple(x for x in transitions if x.gate_kind == "TRADE_EXECUTION_AUTHORIZATION")
            if matching and (len(matching) != 1 or
                    matching[0].approval_or_authorization_id != tea.authorization_id or
                    matching[0].decision != "AUTHORIZED" or
                    matching[0].bound_artifact_id != tea.order_intent_id):
                raise ValueError("TRADE_AUTHORIZATION_TRANSITION_BINDING_MISMATCH")
            return (tea.authorization_id,)
        if stage == STAGE_BROKER_STATUS:
            broker = self._ensure_broker_read()
            return tuple(x.fact_id for x in (broker.get("status"), broker.get("fill")) if x is not None)
        if stage == STAGE_RECONCILIATION:
            return (self._ensure_broker_read()["reconciliation"].result_id,)
        raise ValueError("UNSUPPORTED_PRODUCTION_STAGE")
