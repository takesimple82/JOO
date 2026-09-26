from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import WakeEvent
from CommandCenterRuntime.vocabularies import (
    FAILURE_AI_WAKE_WITHOUT_EVIDENCE,
    WAKE_TYPES,
)


def _utc(value: datetime) -> datetime:
    if type(value) is not datetime or value.tzinfo is not timezone.utc:
        raise ValueError("observed_at must be UTC datetime")
    return value


def _nonblank(label: str, value: str) -> str:
    if type(value) is not str or value.strip() == "":
        raise ValueError(f"{label} must be nonblank str")
    return value


def seal_wake_event(
    *,
    wake_event_id: str,
    wake_type: str,
    source: str,
    fact_or_evidence_id: str,
    observed_at: datetime,
    subject_ids: tuple[str, ...],
    provenance: str,
) -> WakeEvent:
    """Seal an evidence-bound wake. AI cannot invent wakes without evidence."""
    _nonblank("wake_event_id", wake_event_id)
    _nonblank("wake_type", wake_type)
    _nonblank("source", source)
    _nonblank("fact_or_evidence_id", fact_or_evidence_id)
    _nonblank("provenance", provenance)
    _utc(observed_at)
    if wake_type not in WAKE_TYPES:
        raise ValueError(f"unknown wake_type: {wake_type}")
    if type(subject_ids) is not tuple or any(
        type(x) is not str or x.strip() == "" for x in subject_ids
    ):
        raise ValueError("subject_ids must be tuple[str, ...]")
    # Evidence binding: fact/evidence id + provenance required; reject AI-only.
    if source.strip().upper() in {"AI", "AI_INVENTED", "MODEL", "LLM"}:
        raise ValueError(FAILURE_AI_WAKE_WITHOUT_EVIDENCE)
    if fact_or_evidence_id.strip().upper().startswith("AI_INVENTED"):
        raise ValueError(FAILURE_AI_WAKE_WITHOUT_EVIDENCE)
    payload = {
        "wake_event_id": wake_event_id,
        "wake_type": wake_type,
        "source": source,
        "fact_or_evidence_id": fact_or_evidence_id,
        "observed_at": observed_at,
        "subject_ids": subject_ids,
        "provenance": provenance,
    }
    return WakeEvent(
        wake_event_id,
        wake_type,
        source,
        fact_or_evidence_id,
        observed_at,
        subject_ids,
        provenance,
        integrity_seal(payload),
    )


def verify_wake_event(event: WakeEvent) -> None:
    if type(event) is not WakeEvent:
        raise TypeError("WakeEvent required")
    rebuilt = seal_wake_event(
        wake_event_id=event.wake_event_id,
        wake_type=event.wake_type,
        source=event.source,
        fact_or_evidence_id=event.fact_or_evidence_id,
        observed_at=event.observed_at,
        subject_ids=event.subject_ids,
        provenance=event.provenance,
    )
    if rebuilt.integrity_seal != event.integrity_seal:
        raise ValueError("wake event integrity mismatch")
