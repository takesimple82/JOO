from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    MemoryDeltaClass,
)
from InvestmentResearchOrchestrator.models.memory import (
    MemoryDelta,
    MemoryDeltaSet,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_bool,
    require_enum,
    require_nonblank_string,
    require_tuple_of,
)


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
        delta.delta_class
        in {
            MemoryDeltaClass.UNCHANGED,
            MemoryDeltaClass.STATEMENT_CHANGED,
            MemoryDeltaClass.REMOVED,
        }
        and not delta.prior_present
    ):
        raise ValueError(
            f"{delta.delta_class.value} requires "
            "prior_present True"
        )


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
