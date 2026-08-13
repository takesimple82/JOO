from __future__ import annotations

import hashlib
import json

from ProviderGateway.models import ExplicitProviderPayloadEnvelope
from ProviderGateway.validation.validators import (
    validate_explicit_provider_payload_envelope,
)

from FactStore.models.types import (
    ExplicitFactAppendRequest,
    ExplicitStoredFactRecord,
)
from FactStore.models.vocabularies import (
    ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES,
    FORBIDDEN_PAYLOAD_SECRET_FIELD_NAMES,
)
from FactStore.validation.common import (
    require_exact_type,
    require_membership,
    require_nonblank_string,
    require_optional_nonblank_string,
    require_utc_datetime,
)


def validate_explicit_fact_append_request(
    request: ExplicitFactAppendRequest,
) -> None:
    require_exact_type(
        "request",
        request,
        ExplicitFactAppendRequest,
    )
    require_nonblank_string("fact_id", request.fact_id)
    require_exact_type(
        "envelope",
        request.envelope,
        ExplicitProviderPayloadEnvelope,
    )
    validate_explicit_provider_payload_envelope(
        request.envelope
    )
    require_optional_nonblank_string(
        "superseded_fact_id",
        request.superseded_fact_id,
    )
    if (
        request.superseded_fact_id is not None
        and request.superseded_fact_id == request.fact_id
    ):
        raise ValueError(
            "superseded_fact_id must not equal fact_id"
        )


def validate_primary_fact_append_eligibility(
    request: ExplicitFactAppendRequest,
) -> None:
    envelope = request.envelope
    if envelope.status != "success":
        raise ValueError("status must be success")
    require_membership(
        "source_class",
        envelope.source_class,
        ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES,
        "ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES",
    )
    require_exact_type("payload", envelope.payload, dict)
    for key in envelope.payload:
        if key in FORBIDDEN_PAYLOAD_SECRET_FIELD_NAMES:
            raise ValueError(
                "payload must not contain forbidden "
                "secret field names"
            )


def validate_explicit_stored_fact_record(
    record: ExplicitStoredFactRecord,
) -> None:
    require_exact_type(
        "record",
        record,
        ExplicitStoredFactRecord,
    )
    require_nonblank_string("fact_id", record.fact_id)
    require_nonblank_string(
        "envelope_id",
        record.envelope_id,
    )
    require_nonblank_string(
        "provider_id",
        record.provider_id,
    )
    require_membership(
        "source_class",
        record.source_class,
        ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES,
        "ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES",
    )
    require_utc_datetime(
        "collected_at",
        record.collected_at,
    )
    require_utc_datetime(
        "appended_at",
        record.appended_at,
    )
    if record.status != "success":
        raise ValueError("status must be success")
    require_exact_type("payload", record.payload, dict)
    require_optional_nonblank_string(
        "superseded_fact_id",
        record.superseded_fact_id,
    )
    if (
        record.superseded_fact_id is not None
        and record.superseded_fact_id == record.fact_id
    ):
        raise ValueError(
            "superseded_fact_id must not equal fact_id"
        )
    require_optional_nonblank_string(
        "integrity_seal",
        record.integrity_seal,
    )


def validate_collected_at_window(
    collected_at_start,
    collected_at_end,
) -> None:
    require_utc_datetime(
        "collected_at_start",
        collected_at_start,
    )
    require_utc_datetime(
        "collected_at_end",
        collected_at_end,
    )
    if collected_at_start > collected_at_end:
        raise ValueError(
            "collected_at_start must not be after "
            "collected_at_end"
        )


def compute_stored_fact_integrity_seal(
    record: ExplicitStoredFactRecord,
) -> str:
    payload_text = json.dumps(
        record.payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    if record.superseded_fact_id is None:
        superseded_text = ""
    else:
        superseded_text = record.superseded_fact_id
    canonical = "\n".join(
        (
            record.fact_id,
            record.envelope_id,
            record.provider_id,
            record.source_class,
            record.collected_at.isoformat(),
            record.appended_at.isoformat(),
            record.status,
            payload_text,
            superseded_text,
        )
    )
    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def verify_stored_fact_integrity(
    record: ExplicitStoredFactRecord,
) -> None:
    validate_explicit_stored_fact_record(record)
    require_membership(
        "source_class",
        record.source_class,
        ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES,
        "ELIGIBLE_PRIMARY_FACT_SOURCE_CLASS_VALUES",
    )
    expected = compute_stored_fact_integrity_seal(record)
    if record.integrity_seal != expected:
        raise ValueError("integrity_seal mismatch")
