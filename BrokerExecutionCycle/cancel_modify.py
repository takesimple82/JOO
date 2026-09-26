from __future__ import annotations

"""§21 Cancel/Modify — modeled minimally; deferred auto policy.

KB contracts:
  MODIFY → SSAM1805 (ordr_jb_clsf=3, orgn_ordr_no required)
  CANCEL → SSAM1806 (ordr_jb_clsf=4, orgn_ordr_no required)

Block C does NOT auto-cancel/modify, does NOT place live SSAM1805/1806,
and does NOT invent a cancel/replace policy. Human-gated follow-up only.
"""

from BrokerExecutionCycle.vocabularies import (
    API_PATH_SSAM1805,
    API_PATH_SSAM1806,
    FAILURE_CANCEL_MODIFY_NOT_AUTO,
    ORDR_JB_CLSF_CANCEL,
    ORDR_JB_CLSF_MODIFY,
)


CANCEL_MODIFY_POLICY = "DEFERRED_NO_AUTO_POLICY"
MODIFY_API_PATH = API_PATH_SSAM1805
CANCEL_API_PATH = API_PATH_SSAM1806
MODIFY_JB_CLSF = ORDR_JB_CLSF_MODIFY
CANCEL_JB_CLSF = ORDR_JB_CLSF_CANCEL


def assert_no_auto_cancel_modify() -> None:
    raise RuntimeError(FAILURE_CANCEL_MODIFY_NOT_AUTO)
