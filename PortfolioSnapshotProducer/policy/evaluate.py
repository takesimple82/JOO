from __future__ import annotations

from datetime import datetime, timedelta

from FactStore.models import ExplicitStoredFactRecord

from PortfolioSnapshotProducer.models.types import (
    ExplicitPortfolioFactSelectionCriteria,
)
from PortfolioSnapshotProducer.models.vocabularies import (
    COMPOSITION_SOURCE_CLASS,
)

MISSING_FACT_MESSAGE = "fact_id not found"


def is_missing_required_fact_error(exc: BaseException) -> bool:
    return (
        type(exc) is ValueError
        and str(exc) == MISSING_FACT_MESSAGE
    )


def classify_retrieved_fact(
    record: ExplicitStoredFactRecord,
    criteria: ExplicitPortfolioFactSelectionCriteria,
    evaluation_time: datetime | None,
    freshness_max_age: timedelta | None,
) -> str | None:
    if (
        record.source_class != COMPOSITION_SOURCE_CLASS
        or record.status != "success"
    ):
        return "INELIGIBLE_FACT"
    if record.source_class != criteria.required_source_class:
        return "CRITERIA_MISMATCH"
    if (
        criteria.required_source_identity is not None
        and record.provider_id
        != criteria.required_source_identity
    ):
        return "CRITERIA_MISMATCH"
    start = criteria.collected_at_start
    end = criteria.collected_at_end
    if start is not None and end is not None:
        collected_at = record.collected_at
        if collected_at < start or collected_at > end:
            return "CRITERIA_MISMATCH"
    if freshness_max_age is not None:
        age = evaluation_time - record.collected_at
        if age > freshness_max_age:
            return "STALE_REQUIRED_FACT"
    return None
