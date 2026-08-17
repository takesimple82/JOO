from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    MemoryDeltaClass,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDelta,
    MemoryDeltaDetail,
    MemoryDeltaSet,
    MemoryProvenanceIdentity,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_bool,
    require_enum,
    require_nonblank_string,
    require_optional_nonblank_string,
    require_tuple_of,
)

_REQUIRES_PRIOR = frozenset(
    {
        MemoryDeltaClass.UNCHANGED,
        MemoryDeltaClass.STATEMENT_CHANGED,
        MemoryDeltaClass.REMOVED,
        MemoryDeltaClass.PROVENANCE_CHANGED,
        MemoryDeltaClass.MULTI_FINDING_SET_CHANGED,
    }
)


def validate_memory_provenance_identity(
    identity: MemoryProvenanceIdentity,
) -> None:
    if type(identity) is not MemoryProvenanceIdentity:
        raise TypeError(
            "identity must be MemoryProvenanceIdentity"
        )
    require_optional_nonblank_string(
        "committee_id",
        identity.committee_id,
    )
    require_optional_nonblank_string(
        "provider_id",
        identity.provider_id,
    )
    require_optional_nonblank_string(
        "prompt_hash",
        identity.prompt_hash,
    )
    require_optional_nonblank_string(
        "source_reference",
        identity.source_reference,
    )


def validate_memory_delta_detail(
    detail: MemoryDeltaDetail,
) -> None:
    if type(detail) is not MemoryDeltaDetail:
        raise TypeError(
            "detail must be MemoryDeltaDetail"
        )
    require_tuple_of(
        "prior_statements",
        detail.prior_statements,
        str,
    )
    require_tuple_of(
        "current_statements",
        detail.current_statements,
        str,
    )
    require_tuple_of(
        "prior_provenance",
        detail.prior_provenance,
        MemoryProvenanceIdentity,
    )
    require_tuple_of(
        "current_provenance",
        detail.current_provenance,
        MemoryProvenanceIdentity,
    )
    for item in detail.prior_statements:
        if type(item) is not str:
            raise TypeError("prior_statements must be str")
    for item in detail.current_statements:
        if type(item) is not str:
            raise TypeError("current_statements must be str")
    for identity in detail.prior_provenance:
        validate_memory_provenance_identity(identity)
    for identity in detail.current_provenance:
        validate_memory_provenance_identity(identity)


def validate_memory_delta(delta: MemoryDelta) -> None:
    if type(delta) is not MemoryDelta:
        raise TypeError("delta must be MemoryDelta")
    require_nonblank_string("subject_key", delta.subject_key)
    require_bool("prior_present", delta.prior_present)
    require_enum(
        "delta_class",
        delta.delta_class,
        MemoryDeltaClass,
    )
    if (
        delta.delta_class is MemoryDeltaClass.NO_PRIOR
        and delta.prior_present
    ):
        raise ValueError(
            "NO_PRIOR requires prior_present False"
        )
    if (
        delta.delta_class in _REQUIRES_PRIOR
        and not delta.prior_present
    ):
        raise ValueError(
            f"{delta.delta_class.value} requires "
            "prior_present True"
        )
    if delta.detail is not None:
        validate_memory_delta_detail(delta.detail)


def validate_memory_delta_set(
    delta_set: MemoryDeltaSet,
) -> None:
    if type(delta_set) is not MemoryDeltaSet:
        raise TypeError(
            "delta_set must be MemoryDeltaSet"
        )
    require_nonblank_string("run_id", delta_set.run_id)
    require_tuple_of("deltas", delta_set.deltas, MemoryDelta)
    for delta in delta_set.deltas:
        validate_memory_delta(delta)
