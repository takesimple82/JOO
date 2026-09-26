from __future__ import annotations

from datetime import datetime

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import BrokerAcceptanceClassification
from BrokerExecutionCycle.mutation_transport import MutationTransportResponse
from BrokerExecutionCycle.vocabularies import (
    ACCEPTANCE_ACCEPTED,
    ACCEPTANCE_REJECTED,
    ACCEPTANCE_UNKNOWN,
    FAILURE_HTTP200_NOT_ACCEPT,
    PROCESS_FLAG_ACCEPT,
    PROCESS_FLAG_REJECT,
)


def _nonzero_order_no(ordr_no: str | None) -> bool:
    if type(ordr_no) is not str:
        return False
    stripped = ordr_no.strip()
    if stripped == "":
        return False
    # all-zero / zero-padded zero is NOT accept
    if set(stripped) <= {"0"}:
        return False
    return True


def classify_submission_outcome(
    *,
    classification_id: str,
    attempt_id: str,
    response: MutationTransportResponse,
    classified_at: datetime,
) -> BrokerAcceptanceClassification:
    """§16 Acceptance: processFlag==A AND nonzero ordr_no. HTTP 200 alone ≠ accept."""
    outcome = ACCEPTANCE_UNKNOWN
    process_flag = response.process_flag
    ordr_no = response.ordr_no
    detail_msg = response.raw_message

    if response.transport_error is not None:
        outcome = ACCEPTANCE_UNKNOWN
    elif process_flag == PROCESS_FLAG_REJECT:
        outcome = ACCEPTANCE_REJECTED
    elif process_flag == PROCESS_FLAG_ACCEPT and _nonzero_order_no(ordr_no):
        outcome = ACCEPTANCE_ACCEPTED
    elif process_flag == PROCESS_FLAG_ACCEPT and not _nonzero_order_no(ordr_no):
        outcome = ACCEPTANCE_UNKNOWN
    elif response.http_status == 200 and process_flag is None:
        # Explicit: HTTP 200 alone is not acceptance.
        outcome = ACCEPTANCE_UNKNOWN
        detail_msg = FAILURE_HTTP200_NOT_ACCEPT
    else:
        outcome = ACCEPTANCE_UNKNOWN

    payload = {
        "classification_id": classification_id,
        "attempt_id": attempt_id,
        "outcome": outcome,
        "process_flag": process_flag,
        "broker_order_no": ordr_no if outcome == ACCEPTANCE_ACCEPTED else ordr_no,
        "http_status": response.http_status,
        "raw_message": detail_msg,
        "classified_at": classified_at,
    }
    return BrokerAcceptanceClassification(
        classification_id,
        attempt_id,
        outcome,
        process_flag,
        ordr_no,
        response.http_status,
        detail_msg,
        classified_at,
        integrity_seal(payload),
    )
