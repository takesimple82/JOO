"""C — KB native idempotency authority.

Excel + official samples document no client idempotency key for SSAM mutation.
JOO must never claim KB-native idempotency. Local durability is TEA one-shot +
durable pre-send append only.
"""
from __future__ import annotations

from BrokerExecutionCycle.authority_evidence import (
    KB_NATIVE_IDEMPOTENCY,
    KB_NATIVE_IDEMPOTENCY_DETAIL,
    PROVENANCE_NONE_DOCUMENTED,
)


def kb_native_idempotency_status() -> dict[str, str]:
    return {
        "status": KB_NATIVE_IDEMPOTENCY,
        "provenance": PROVENANCE_NONE_DOCUMENTED,
        "detail": KB_NATIVE_IDEMPOTENCY_DETAIL,
        "joo_substitute": "TEA_ONE_SHOT_PLUS_DURABLE_PRE_SEND",
    }


def assert_no_kb_native_idempotency_claim(claim: str | None) -> None:
    if claim is None:
        return
    text = claim.casefold()
    if "kb" in text and "idempot" in text and "native" in text and "none" not in text:
        raise ValueError("KB_NATIVE_IDEMPOTENCY_UNPROVEN")
