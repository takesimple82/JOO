"""Phase 2 broker authority evidence registry (Evidence First; no invented semantics).

Provenance tiers (strict):
  EXCEL_OFFICIAL — KB Excel artifact fields/enums
  SAMPLE_OBSERVED — official sample ZIP request/response observations
  REPO_CONTRACT — JOO fail-closed / frozen safety contracts
  NONE_DOCUMENTED — searched Excel+samples; absent; never claim present
"""
from __future__ import annotations

from dataclasses import dataclass


PROVENANCE_EXCEL_OFFICIAL = "EXCEL_OFFICIAL"
PROVENANCE_SAMPLE_OBSERVED = "SAMPLE_OBSERVED"
PROVENANCE_REPO_CONTRACT = "REPO_CONTRACT"
PROVENANCE_NONE_DOCUMENTED = "NONE_DOCUMENTED"

# Official local artifacts used for Phase 2 closure (hashes recorded at verify time).
KB_EXCEL_PATH = "/Users/takesimple/Downloads/all_kbstock_excel-20260812-101425.xlsx"
KB_SAMPLE_ZIP_PATH = "/Users/takesimple/Downloads/all_kbstock_sample (1).zip"
KB_EXCEL_SHA256 = "f9d723f90b916466debfc6dc325261a52929bd133cdc9c19c69ced7965616799"
KB_SAMPLE_ZIP_SHA256 = "36eef9fe734d4a3f083e49fd4a8ec5641ea6541063ec0ebdf4f4b580ccb241df"


@dataclass(frozen=True)
class AuthorityClaim:
    authority_id: str  # A..G
    claim: str
    provenance: str
    evidence: str
    fail_closed_when_unknown: bool


# A — SSAM account-field authority
#
# Excel SSAM1801/1802 INPUT lists: mkt_tm_clsf, is_cd, ordr_q, ordr_uprc, ordr_ccd
# (+ optional sor_ordr_ccd). Excel does NOT list gnl_ac_no1 as INPUT.
# Sample SSAM1802 successful buy request/response observes gnl_ac_no1="400277078".
# JOO binds OrderIntent/TEA to VerifiedExecutionAccountBinding.gnl_ac_no1 exactly;
# blank/mismatched/heuristic account → FAIL CLOSED. Never invent acct_cd/hts_pwd.
SSAM_EXCEL_REQUIRED_INPUT_FIELDS = (
    "mkt_tm_clsf",
    "is_cd",
    "ordr_q",
    "ordr_uprc",
    "ordr_ccd",
)
SSAM_ACCOUNT_BINDING_FIELD = "gnl_ac_no1"
SSAM_ACCOUNT_FIELD_PROVENANCE = PROVENANCE_SAMPLE_OBSERVED

# Phase 4 FOURTH GATE — gnl_ac_no1 authority investigation (READ-ONLY).
# Outcome: AUTHORITY_NOT_CLOSED → LIVE_BLOCKER (do not weaken).
#
# Exhaustive evidence (Excel SHA f9d723f9… / sample ZIP SHA 36eef9fe…):
# - Excel SSAM1801/1802/1805/1806 INPUT tables omit gnl_ac_no1 entirely.
# - Excel OUTPUT lists acct_cd (계정코드) but not gnl_ac_no1.
# - Sample SSAM1802 successful buy observes input+output gnl_ac_no1="400277078".
# - Sample SSAM1806 successful cancel observes input gnl_ac_no1="" (blank) yet
#   processFlag=A — so sample success does NOT prove the field is required.
# - Sample SSAM1801/1805 failures also omit/blank the field.
# - READ APIs SSQM0004/SSQM2952/SSQM1801 take no account field (OAuth-bound).
# - SSQM2442 sample uses gnl_ac_no (no trailing 1); SSQM0005 returns ac_no
#   "40027707801" (gnl + product suffix) — related identity, not SSAM INPUT authority.
# - Public portal guide does not document SSAM mutation account-field binding.
# - Third-party wrappers are not official KB authority.
#
# Therefore: meaning/requiredness/acceptedness of gnl_ac_no1 for SSAM mutation
# cannot be closed without heuristics or inventing broker semantics.
GNL_AC_NO1_AUTHORITY_STATUS = "AUTHORITY_NOT_CLOSED"
GNL_AC_NO1_LIVE_BLOCKER = True
GNL_AC_NO1_AUTHORITY_DETAIL = (
    "Excel omits gnl_ac_no1 from SSAM INPUT; samples conflict (buy populated / "
    "cancel blank+success); OAuth may bind READ; no official mutation-binding "
    "field proven. LIVE_BLOCKER until AUTHORITY_CLOSED."
)


# B — SSQM2341 positive fill semantics (Excel Record1 field names; no enum tables)
SSQM2341_QTY_ORDERED_FIELD = "ordr_q"
SSQM2341_QTY_FILLED_FIELD = "tl_ccls_q"
SSQM2341_QTY_REMAINING_FIELD = "nccls_q"
SSQM2341_ORDER_NO_FIELD = "ordr_no"
SSQM2341_ORGN_ORDER_NO_FIELD = "orgn_ordr_no"
SSQM2341_CCLS_NTC_CCD_FIELD = "ccls_ntc_ccd"  # String(1); NO Excel enum values
SSQM2341_CRCT_CNCL_CCD_FIELD = "crct_cncl_ccd"  # String(15); NO Excel enum values
SSQM2341_EXECUTION_ID_FIELD = None  # NONE_DOCUMENTED on SSQM2341 Record1

# C — KB native idempotency
KB_NATIVE_IDEMPOTENCY = PROVENANCE_NONE_DOCUMENTED
KB_NATIVE_IDEMPOTENCY_DETAIL = (
    "No idempotency-key / client-order-id / duplicate-submit header appears in "
    "Excel SSAM1801/1802/1805/1806 INPUT/OUTPUT or sample envelopes. "
    "JOO must not claim KB-native idempotency; rely on durable pre-send + TEA one-shot."
)

# D — Cancel/modify endpoints (Excel) — no auto policy
CANCEL_API = "/api/v1/ssam1806"
MODIFY_API = "/api/v1/ssam1805"
CRCT_CLSF_PARTIAL = "1"  # Excel: 1:일부정정
CRCT_CLSF_FULL = "2"  # Excel: 2:전부정정
CANCEL_MODIFY_AUTO_POLICY = "DEFERRED_NO_AUTO_POLICY"

# E — UNKNOWN recovery
UNKNOWN_RECOVERY_POLICY = "QUERY_RECOVER_THEN_HUMAN_IF_AMBIGUOUS"
UNKNOWN_MAY_AUTORESUBMIT = False

# F — Credential / allowlist
SECRET_MUST_NOT_LOG = True
ACCOUNT_ALLOWLIST_MISMATCH = "ACCOUNT_ALLOWLIST_MISMATCH_FAIL_CLOSED"

# G — Shadow dry-run
SHADOW_DRY_RUN_TRANSPORT = "LIVE_DISABLED_BOUNDARY"
SHADOW_MUST_NOT_SUBMIT_REAL = True


AUTHORITY_CLAIMS: tuple[AuthorityClaim, ...] = (
    AuthorityClaim(
        "A",
        "OrderIntent/TEA bind exact VerifiedExecutionAccountBinding.gnl_ac_no1; "
        "Excel-required SSAM INPUT fields enforced; unknown account FAIL CLOSED",
        SSAM_ACCOUNT_FIELD_PROVENANCE,
        "Excel SSAM1802 INPUT omits gnl_ac_no1; sample SSAM1802 input/output observes gnl_ac_no1",
        True,
    ),
    AuthorityClaim(
        "B",
        "SSQM2341 fill claims only from Excel qty fields (ordr_q/tl_ccls_q/nccls_q) "
        "when processFlag=A and matched Record1; HTTP success alone never fills; "
        "ccls_ntc_ccd/crct_cncl_ccd enums undocumented → raw only / UNKNOWN axis",
        PROVENANCE_EXCEL_OFFICIAL,
        "Excel SSQM2341 Record1 field table; sample Record1 empty/processFlag B",
        True,
    ),
    AuthorityClaim(
        "C",
        "KB native idempotency: NONE_DOCUMENTED",
        PROVENANCE_NONE_DOCUMENTED,
        KB_NATIVE_IDEMPOTENCY_DETAIL,
        True,
    ),
    AuthorityClaim(
        "D",
        "Cancel=SSAM1806 Modify=SSAM1805; crct_clsf 1/2 from Excel; "
        "orgn_ordr_no required; no auto-retry/cancel/modify policy",
        PROVENANCE_EXCEL_OFFICIAL,
        "Excel SSAM1805/1806 INPUT; samples ordr_jb_clsf 3/4",
        True,
    ),
    AuthorityClaim(
        "E",
        "UNKNOWN → QUERY_RECOVER_THEN_HUMAN_IF_AMBIGUOUS; never auto-resubmit",
        PROVENANCE_REPO_CONTRACT,
        "C0-D5 + CommandCenter HumanAttention SUBMISSION_OUTCOME_UNKNOWN",
        True,
    ),
    AuthorityClaim(
        "F",
        "Runtime credentials never logged; only allowlisted accounts reach future "
        "mutation transport; mismatch FAIL CLOSED",
        PROVENANCE_REPO_CONTRACT,
        "ProviderGateway credential sanitize + account allowlist contract",
        True,
    ),
    AuthorityClaim(
        "G",
        "Shadow dry-run completes intent→binding→qty→SSAM body→LiveMutationTransportDisabled "
        "boundary→simulated ack/recon→HumanAttention without real SSAM submit",
        PROVENANCE_REPO_CONTRACT,
        "shadow_dry_run + LiveMutationTransportDisabled",
        True,
    ),
)


def authority_claim_map() -> dict[str, AuthorityClaim]:
    return {c.authority_id: c for c in AUTHORITY_CLAIMS}


def assert_phase2_authorities_registered() -> None:
    ids = {c.authority_id for c in AUTHORITY_CLAIMS}
    missing = {"A", "B", "C", "D", "E", "F", "G"} - ids
    if missing:
        raise RuntimeError(f"missing Phase 2 authorities: {sorted(missing)}")
