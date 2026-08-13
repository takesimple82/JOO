from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ProviderGateway.models import ExplicitProviderPayloadEnvelope


@dataclass(frozen=True)
class ExplicitFactAppendRequest:
    fact_id: str
    envelope: ExplicitProviderPayloadEnvelope
    superseded_fact_id: str | None


@dataclass(frozen=True)
class ExplicitStoredFactRecord:
    fact_id: str
    envelope_id: str
    provider_id: str
    source_class: str
    collected_at: datetime
    appended_at: datetime
    status: str
    payload: dict
    superseded_fact_id: str | None
    integrity_seal: str | None
