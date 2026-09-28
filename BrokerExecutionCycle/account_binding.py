from __future__ import annotations

from datetime import datetime

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import VerifiedExecutionAccountBinding
from BrokerExecutionCycle.vocabularies import (
    ACCOUNT_BINDING_UNVERIFIED,
    ACCOUNT_BINDING_VERIFIED,
    FAILURE_ACCOUNT_UNVERIFIED,
)


_FORBIDDEN_SECRET_KEYS = frozenset(
    {
        "hts_pwd",
        "appKey",
        "appSecret",
        "access_token",
        "token",
        "password",
        "secret",
        "Authorization",
    }
)


def seal_unverified_account_binding(
    *,
    binding_id: str,
    account_selector: str,
) -> VerifiedExecutionAccountBinding:
    """Token-only / selector-only is NOT mutation-eligible."""
    payload = {
        "binding_id": binding_id,
        "account_selector": account_selector,
        "gnl_ac_no1": "",
        "status": ACCOUNT_BINDING_UNVERIFIED,
        "verified_at": None,
        "verification_method": "none",
        "mutation_eligible": False,
    }
    return VerifiedExecutionAccountBinding(
        binding_id,
        account_selector,
        "",
        ACCOUNT_BINDING_UNVERIFIED,
        None,
        "none",
        False,
        integrity_seal(payload),
    )


def seal_verified_execution_account_binding(
    *,
    binding_id: str,
    account_selector: str,
    gnl_ac_no1: str,
    verified_at: datetime,
    verification_method: str,
) -> VerifiedExecutionAccountBinding:
    """C0-D4: verified gnl_ac_no1 required. No inventing. No secrets."""
    if type(gnl_ac_no1) is not str or gnl_ac_no1.strip() == "":
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if any(ch.isspace() for ch in gnl_ac_no1):
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if not gnl_ac_no1.isdigit():
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if type(verification_method) is not str or verification_method.strip() == "":
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    lowered = verification_method.casefold()
    for key in _FORBIDDEN_SECRET_KEYS:
        if key.casefold() in lowered:
            raise ValueError("verification_method must not carry secrets")
    payload = {
        "binding_id": binding_id,
        "account_selector": account_selector,
        "gnl_ac_no1": gnl_ac_no1,
        "status": ACCOUNT_BINDING_VERIFIED,
        "verified_at": verified_at,
        "verification_method": verification_method,
        "mutation_eligible": True,
    }
    return VerifiedExecutionAccountBinding(
        binding_id,
        account_selector,
        gnl_ac_no1,
        ACCOUNT_BINDING_VERIFIED,
        verified_at,
        verification_method,
        True,
        integrity_seal(payload),
    )


def require_mutation_eligible_account(
    binding: VerifiedExecutionAccountBinding,
) -> None:
    if type(binding) is not VerifiedExecutionAccountBinding:
        raise TypeError("account binding required")
    if binding.mutation_eligible is not True:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if binding.status != ACCOUNT_BINDING_VERIFIED:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if type(binding.gnl_ac_no1) is not str or binding.gnl_ac_no1.strip() == "":
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if not binding.gnl_ac_no1.isdigit():
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if binding.verified_at is None:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    if type(binding.verification_method) is not str or binding.verification_method.strip() == "":
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
    payload = {
        "binding_id": binding.binding_id,
        "account_selector": binding.account_selector,
        "gnl_ac_no1": binding.gnl_ac_no1,
        "status": binding.status,
        "verified_at": binding.verified_at,
        "verification_method": binding.verification_method,
        "mutation_eligible": binding.mutation_eligible,
    }
    if integrity_seal(payload) != binding.integrity_seal:
        raise ValueError(FAILURE_ACCOUNT_UNVERIFIED)
