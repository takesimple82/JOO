"""Fail-closed validation for durable read-only observations."""
from __future__ import annotations

from datetime import datetime, timezone

from CommandCenterReadOnlyOperation.models import ReadOnlyObservation


_CHANGE_CLASSES = frozenset({
    "BASELINE_ABSENT", "NO_CHANGE", "CHANGE_DETECTED",
})


def validate_read_only_observation(value):
    if type(value) is not ReadOnlyObservation:
        raise TypeError("ReadOnlyObservation required")
    if type(value.observation_id) is not str or value.observation_id.strip() == "":
        raise ValueError("observation_id required")
    if type(value.created_at) is not datetime or value.created_at.tzinfo is not timezone.utc:
        raise ValueError("created_at must be UTC")
    if value.change_class not in _CHANGE_CLASSES:
        raise ValueError("unsupported change_class")
    if type(value.application_fact_ids) is not tuple or not value.application_fact_ids:
        raise ValueError("application facts required")
    if len(set(value.application_fact_ids)) != len(value.application_fact_ids):
        raise ValueError("application fact identities must be unique")
    if type(value.raw_fact_ids) is not tuple or len(value.raw_fact_ids) != 2:
        raise ValueError("exact holdings and balances raw facts required")
    if value.live_mutation_enabled is not False:
        raise ValueError("live mutation must remain disabled")
