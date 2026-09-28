"""G — Read-only live rehearsal / shadow dry-run (NO real SSAM mutation).

Completes: approved intent → binding → qty → SSAM request construction →
LiveMutationTransportDisabled boundary → simulated/shadow ack+recon →
HumanAttention signal. MUST NOT submit a real order.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from CapitalAllocationCycle.models import (
    InvestmentHumanApproval,
    SealedApprovedAllocationArtifact,
)

from BrokerExecutionCycle.acceptance import classify_submission_outcome
from BrokerExecutionCycle.account_allowlist import (
    ExecutionAccountAllowlist,
    require_account_on_allowlist,
)
from BrokerExecutionCycle.authorization import (
    initial_mutation_authority,
    issue_trade_execution_authorization,
)
from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.intent import seal_limit_order_intent
from BrokerExecutionCycle.models import (
    BrokerAcceptanceClassification,
    OrderIntent,
    PreTradeFactBundle,
    ReconciliationResult,
    SsamRequestTranslation,
    SubmissionRecoveryPlan,
    TradeExecutionAuthorization,
    VerifiedExecutionAccountBinding,
)
from BrokerExecutionCycle.mutation_transport import (
    LiveMutationTransportDisabled,
    MockMutationTransport,
    MutationTransportResponse,
)
from BrokerExecutionCycle.pretrade import validate_pretrade
from BrokerExecutionCycle.reconciliation import reconcile_acceptance_and_fill
from BrokerExecutionCycle.recovery import plan_submission_unknown_recovery
from BrokerExecutionCycle.translation import translate_order_intent_to_ssam
from BrokerExecutionCycle.vocabularies import (
    FAILURE_LIVE_MUTATION_DISABLED,
    MUTATION_TRANSPORT_LIVE_DISABLED,
    SHADOW_DRY_RUN_KIND,
)


@dataclass(frozen=True)
class ShadowDryRunResult:
    kind: str
    order_intent: OrderIntent
    tea: TradeExecutionAuthorization
    translation: SsamRequestTranslation
    live_boundary_error: str
    transport_mode_at_boundary: str
    shadow_acceptance: BrokerAcceptanceClassification
    shadow_reconciliation: ReconciliationResult
    human_attention_required: bool
    human_attention_detail: str
    recovery: SubmissionRecoveryPlan | None
    real_mutation_submitted: bool
    integrity_seal: str


def run_read_only_shadow_dry_run(
    *,
    intent_id: str,
    authorization_id: str,
    classification_id: str,
    recon_id: str,
    side: str,
    portfolio_subject_id: str,
    approved_notional_krw: Decimal,
    bundle: PreTradeFactBundle,
    artifact: SealedApprovedAllocationArtifact,
    approval: InvestmentHumanApproval,
    account: VerifiedExecutionAccountBinding,
    allowlist: ExecutionAccountAllowlist,
    now: datetime,
    principal: str,
    shadow_ack: MutationTransportResponse | None = None,
) -> ShadowDryRunResult:
    """Full construction path; live transport raises; shadow ack is local only."""
    require_account_on_allowlist(account, allowlist)

    validation = validate_pretrade(
        validation_id=f"shadow-pretrade-{intent_id}",
        bundle=bundle,
        side=side,
        approved_notional_krw=approved_notional_krw,
        validated_at=now,
    )
    if not validation.passed:
        codes = tuple(f.code for f in validation.findings if f.status == "FAIL")
        raise ValueError(f"SHADOW_PRETRADE_FAILED:{','.join(codes)}")

    intent = seal_limit_order_intent(
        intent_id=intent_id,
        side=side,
        portfolio_subject_id=portfolio_subject_id,
        bundle=bundle,
        validation=validation,
        artifact=artifact,
        approval=approval,
        sealed_at=now,
    )
    tea = issue_trade_execution_authorization(
        authorization_id=authorization_id,
        order_intent=intent,
        artifact=artifact,
        approval=approval,
        authorized_at=now,
        principal=principal,
    )
    _authority = initial_mutation_authority(tea)
    translation = translate_order_intent_to_ssam(
        translation_id=f"shadow-xlat-{intent_id}",
        order_intent=intent,
        account=account,
    )
    if not translation.ready:
        raise ValueError(f"SHADOW_TRANSLATION_NOT_READY:{translation.unresolved_fields}")

    live = LiveMutationTransportDisabled()
    live_error = FAILURE_LIVE_MUTATION_DISABLED
    try:
        live.submit(translation.api_path, translation.data_body)
        raise RuntimeError("SHADOW_INVARIANT_BROKEN_LIVE_SUBMITTED")
    except RuntimeError as exc:
        if str(exc) != FAILURE_LIVE_MUTATION_DISABLED:
            raise
        live_error = str(exc)

    # Simulated/shadow ack only — MockMutationTransport is local; not real SSAM.
    if shadow_ack is None:
        mock = MockMutationTransport()
        shadow_ack = mock.submit(translation.api_path, dict(translation.data_body))
    acceptance = classify_submission_outcome(
        classification_id=classification_id,
        attempt_id=f"shadow-attempt-{intent_id}",
        response=shadow_ack,
        classified_at=now,
    )
    recovery = None
    human_required = False
    human_detail = "shadow dry-run complete; live mutation disabled; no real submit"
    if acceptance.outcome == "SUBMISSION_OUTCOME_UNKNOWN":
        recovery = plan_submission_unknown_recovery(
            plan_id=f"shadow-recovery-{intent_id}",
            acceptance=acceptance,
            status_fact=None,
        )
        human_required = True
        human_detail = recovery.detail
    recon = reconcile_acceptance_and_fill(
        result_id=recon_id,
        attempt_id=acceptance.attempt_id,
        acceptance=acceptance,
        fill=None,
        cash_corroborated=None,
        holdings_corroborated=None,
        reconciled_at=now,
    )
    payload = {
        "kind": SHADOW_DRY_RUN_KIND,
        "order_intent_seal": intent.integrity_seal,
        "tea_seal": tea.integrity_seal,
        "translation_payload_hash": translation.payload_hash,
        "live_boundary_error": live_error,
        "transport_mode_at_boundary": MUTATION_TRANSPORT_LIVE_DISABLED,
        "shadow_acceptance_outcome": acceptance.outcome,
        "human_attention_required": human_required,
        "real_mutation_submitted": False,
    }
    return ShadowDryRunResult(
        SHADOW_DRY_RUN_KIND,
        intent,
        tea,
        translation,
        live_error,
        MUTATION_TRANSPORT_LIVE_DISABLED,
        acceptance,
        recon,
        human_required,
        human_detail,
        recovery,
        False,
        integrity_seal(payload),
    )
