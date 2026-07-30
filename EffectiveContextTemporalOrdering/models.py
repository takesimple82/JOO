from enum import Enum


class EffectiveContextTemporalOrderingStatus(Enum):
    CONTEXT_DATE_CONFLICT = "context_date_conflict"
    BEFORE = "before"
    SAME_DATE = "same_date"
    AFTER = "after"
