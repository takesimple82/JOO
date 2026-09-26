from __future__ import annotations

from datetime import datetime

from BrokerExecutionCycle.authorization import (
    assert_tea_binds_intent,
    consume_one_shot,
)
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
    MutationTransport,
    MutationTransportResponse,
    default_mutation_transport,
)
from BrokerExecutionCycle.vocabularies import (
    FAILURE_ACCOUNT_UNVERIFIED,
    FAILURE_LIVE_MUTATION_DISABLED,
    FAILURE_PAYLOAD_HASH_MISMATCH,
    FAILURE_TEA_CONSUMED,
    FAILURE_TEA_MISSING,
    FAILURE_UNRESOLVED_SSAM_FIELD,
    MUTATION_TRANSPORT_LIVE_DISABLED,
    MUTATION_TRANSPORT_MOCK,
)


def assert_mutation_eligible(
    *,
    tea: TradeExecutionAuthorization | None,
    order_intent: OrderIntent,
    translation: SsamRequestTranslation,
    account: VerifiedExecutionAccountBinding,
    authority: MutationAuthorityState,
) -> None:
    if tea is None:
        raise ValueError(FAILURE_TEA_MISSING)
    assert_tea_binds_intent(tea, order_intent)
    if account.mutation_eligible is not True:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if not translation.ready:
        raise ValueError(FAILURE_UNRESOLVED_SSAM_FIELD)
    if translation.payload_hash == "":
        raise ValueError(FAILURE_PAYLOAD_HASH_MISMATCH)
    if translation.order_intent_seal != order_intent.integrity_seal:
        raise ValueError(FAILURE_PAYLOAD_HASH_MISMATCH)
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
    authority: MutationAuthorityState,
    attempted_at: datetime,
    transport: MutationTransport | None = None,
) -> tuple[BrokerSubmitAttempt, MutationAuthorityState, MutationTransportResponse]:
    """One-shot mutation. Durable pre-send record before transport call. Mock only by default."""
    assert_mutation_eligible(
        tea=tea,
        order_intent=order_intent,
        translation=translation,
        account=account,
        authority=authority,
    )
    active = transport if transport is not None else default_mutation_transport()
    mode = getattr(active, "mode", MUTATION_TRANSPORT_LIVE_DISABLED)
    if mode == MUTATION_TRANSPORT_LIVE_DISABLED:
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)
    if mode != MUTATION_TRANSPORT_MOCK:
        raise RuntimeError(FAILURE_LIVE_MUTATION_DISABLED)

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
    response = active.submit(translation.api_path, translation.data_body)
    return attempt, new_authority, response
