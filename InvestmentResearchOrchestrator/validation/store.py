from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    EvidencePayloadKind,
)
from InvestmentResearchOrchestrator.models.store import (
    EvidenceStoreRecord,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_datetime,
    require_enum,
    require_nonblank_string,
    require_optional_datetime,
    require_optional_nonblank_string,
    require_string,
)


def validate_evidence_store_record(
    record: EvidenceStoreRecord,
) -> None:
    if type(record) is not EvidenceStoreRecord:
        raise TypeError(
            "record must be EvidenceStoreRecord"
        )
    require_nonblank_string("run_id", record.run_id)
    require_optional_nonblank_string(
        "research_id",
        record.research_id,
    )
    require_optional_nonblank_string(
        "committee_id",
        record.committee_id,
    )
    require_optional_nonblank_string(
        "provider_id",
        record.provider_id,
    )
    require_optional_nonblank_string(
        "prompt_id",
        record.prompt_id,
    )
    require_optional_nonblank_string(
        "prompt_hash",
        record.prompt_hash,
    )
    require_optional_nonblank_string(
        "source_reference",
        record.source_reference,
    )
    require_optional_datetime(
        "collected_at",
        record.collected_at,
    )
    require_datetime("stored_at", record.stored_at)
    require_enum(
        "payload_kind",
        record.payload_kind,
        EvidencePayloadKind,
    )
    require_string("payload", record.payload)
