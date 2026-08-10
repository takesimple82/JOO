from __future__ import annotations

from InvestmentResearchOrchestrator.models.enums import (
    ScanChangeClass,
    SubjectClass,
)
from InvestmentResearchOrchestrator.models.scan import (
    ScanDelta,
    ScanDeltaSet,
)
from InvestmentResearchOrchestrator.validation.common import (
    require_enum,
    require_nonblank_string,
    require_tuple_of,
)


def validate_scan_delta(delta: ScanDelta) -> None:
    if type(delta) is not ScanDelta:
        raise TypeError("delta must be ScanDelta")
    require_nonblank_string("subject_id", delta.subject_id)
    require_enum(
        "change_class",
        delta.change_class,
        ScanChangeClass,
    )
    require_enum(
        "materiality_basis",
        delta.materiality_basis,
        ScanChangeClass,
    )
    if delta.materiality_basis is not delta.change_class:
        raise ValueError(
            "materiality_basis must equal change_class"
        )
    require_enum(
        "subject_class",
        delta.subject_class,
        SubjectClass,
    )


def validate_scan_delta_set(delta_set: ScanDeltaSet) -> None:
    if type(delta_set) is not ScanDeltaSet:
        raise TypeError("delta_set must be ScanDeltaSet")
    require_nonblank_string("run_id", delta_set.run_id)
    require_tuple_of("deltas", delta_set.deltas, ScanDelta)
    for delta in delta_set.deltas:
        validate_scan_delta(delta)
