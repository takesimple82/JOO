from __future__ import annotations

from datetime import datetime

from BrokerExecutionCycle.authorization import (
    assert_tea_binds_intent,
    consume_one_shot,
)
from BrokerExecutionCycle.account_allowlist import (
    ExecutionAccountAllowlist,
    require_account_on_allowlist,
)
from BrokerExecutionCycle.account_binding import require_mutation_eligible_account
from BrokerExecutionCycle.translation import verify_ssam_translation
from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import (
    BrokerSubmitAttempt,
    MutationAuthorityState,
    OrderIntent,
    SsamRequestTranslation,
    TradeExecutionAuthorization,
    VerifiedExecutionAccountBinding,
)
from BrokerExecutionCycle.mutation_transport import (
    MockMutationTransport,
    MutationTransport,
    MutationTransportResponse,
    default_mutation_transport,
)
from BrokerExecutionCycle.vocabularies import (
    FAILURE_ACCOUNT_UNVERIFIED,
    FAILURE_LIVE_MUTATION_DISABLED,
    FAILURE_TEA_CONSUMED,
    FAILURE_TEA_MISSING,
    FAILURE_UNRESOLVED_SSAM_FIELD,
    MUTATION_TRANSPORT_LIVE_DISABLED,
    MUTATION_TRANSPORT_MOCK,
)

DURABLE_PRE_SEND_APPENDER_REQUIRED = "DURABLE_PRE_SEND_APPENDER_REQUIRED"


def assert_mutation_eligible(
    *,
    tea: TradeExecutionAuthorization | None,
    order_intent: OrderIntent,
    translation: SsamRequestTranslation,
    account: VerifiedExecutionAccountBinding,
    account_allowlist: ExecutionAccountAllowlist,
    authority: MutationAuthorityState,
) -> None:
    if tea is None:
        raise ValueError(FAILURE_TEA_MISSING)
    assert_tea_binds_intent(tea, order_intent)
    require_mutation_eligible_account(account)
    require_account_on_allowlist(account, account_allowlist)
    if order_intent.account_binding_id != account.binding_id:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if order_intent.account_binding_seal != account.integrity_seal:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if not translation.ready:
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    verify_ssam_translation(
        translation=translation, order_intent=order_intent, account=account
    )
    if authority.consumed:
        raise ValueError(FAILURE_TEA_CONSUMED)


def record_pre_send_attempt(
    *,
    attempt_id: str,
    tea: TradeExecutionAuthorization,
    order_intent: OrderIntent,
    translation: SsamRequestTranslation,
    transport_mode: str,
    attempted_at: datetime,
) -> BrokerSubmitAttempt:
    payload = {
        "attempt_id": attempt_id,
        "authorization_id": tea.authorization_id,
        "tea_seal": tea.integrity_seal,
        "order_intent_id": order_intent.intent_id,
        "order_intent_seal": order_intent.integrity_seal,
        "translation_id": translation.translation_id,
        "payload_hash": translation.payload_hash,
        "transport_mode": transport_mode,
        "attempted_at": attempted_at,
        "durable_pre_send": True,
    }
    return BrokerSubmitAttempt(
        attempt_id,
        tea.authorization_id,
        tea.integrity_seal,
        order_intent.intent_id,
        order_intent.integrity_seal,
        translation.translation_id,
        translation.payload_hash,
        transport_mode,
        attempted_at,
        True,
        integrity_seal(payload),
    )


def execute_mutation_attempt(
    *,
    attempt_id: str,
    tea: TradeExecutionAuthorization,
    order_intent: OrderIntent,
    translation: SsamRequestTranslation,
    account: VerifiedExecutionAccountBinding,
    account_allowlist: ExecutionAccountAllowlist,
    authority: MutationAuthorityState,
    attempted_at: datetime,
    transport: MutationTransport | None = None,
    durable_pre_send_appender=None,
) -> tuple[BrokerSubmitAttempt, MutationAuthorityState, MutationTransportResponse]:
    """One-shot mutation. Durable pre-send record before transport call. Mock only by default."""
    assert_mutation_eligible(
        tea=tea,
        order_intent=order_intent,
        translation=translation,
        account=account,
        account_allowlist=account_allowlist,
        authority=authority,
    )
    active = transport if transport is not None else default_mutation_transport()
    mode = getattr(active, "mode", MUTATION_TRANSPORT_LIVE_DISABLED)
    if mode == MUTATION_TRANSPORT_LIVE_DISABLED:
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)
    if type(active) is not MockMutationTransport or mode != MUTATION_TRANSPORT_MOCK:
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)

    # Freeze the already-verified wire values before the persistence callback.
    # The dataclass is frozen, but its data_body dict is intentionally copied to
    # close a mutation/time-of-check-to-time-of-use seam.
    api_path = translation.api_path
    request_body = dict(translation.data_body)

    attempt = record_pre_send_attempt(
        attempt_id=attempt_id,
        tea=tea,
        order_intent=order_intent,
        translation=translation,
        transport_mode=mode,
        attempted_at=attempted_at,
    )
    new_authority = consume_one_shot(
        authority,
        tea=tea,
        attempt_id=attempt_id,
        payload_hash=translation.payload_hash,
        consumed_at=attempted_at,
    )
    if not callable(durable_pre_send_appender):
        raise RuntimeError(DURABLE_PRE_SEND_APPENDER_REQUIRED)
    durable_pre_send_appender(attempt, new_authority)
    response = active.submit(api_path, request_body)
    return attempt, new_authority, response
