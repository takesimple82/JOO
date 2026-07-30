import re
from datetime import date

from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)


_DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def validate_explicit_effective_context_observed_date(
    context_date: ExplicitEffectiveContextObservedDate,
) -> None:
    if type(context_date) is not ExplicitEffectiveContextObservedDate:
        raise TypeError(
            "context_date must be "
            "ExplicitEffectiveContextObservedDate"
        )

    if type(context_date.effective_context_id) is not str:
        raise TypeError("effective_context_id must be str")
    if context_date.effective_context_id.strip() == "":
        raise ValueError(
            "effective_context_id must not be blank"
        )

    if type(context_date.observed_on) is not str:
        raise TypeError("observed_on must be str")
    if not _is_strict_date(context_date.observed_on):
        raise ValueError(
            "observed_on must be a valid YYYY-MM-DD date"
        )


def _is_strict_date(value: str) -> bool:
    if _DATE_PATTERN.fullmatch(value) is None:
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True
