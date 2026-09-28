"""F — Credential-managed runtime account allowlist (FAIL CLOSED on mismatch).

No secrets are accepted or logged. Only exact digit account IDs may be listed.
Future mutation transport callers must pass through require_account_on_allowlist.
"""
from __future__ import annotations

from dataclasses import dataclass

from BrokerExecutionCycle.models import VerifiedExecutionAccountBinding
from BrokerExecutionCycle.account_binding import require_mutation_eligible_account
from BrokerExecutionCycle.vocabularies import (
    ACCOUNT_ALLOWLIST_MISMATCH,
)


@dataclass(frozen=True)
class ExecutionAccountAllowlist:
    """Immutable allowlist of gnl_ac_no1 values eligible for future mutation."""

    allowlist_id: str
    allowed_gnl_ac_no1: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.allowlist_id) is not str or self.allowlist_id.strip() == "":
            raise ValueError("allowlist_id required")
        if type(self.allowed_gnl_ac_no1) is not tuple:
            raise TypeError("allowed_gnl_ac_no1 must be tuple")
        cleaned: list[str] = []
        for acct in self.allowed_gnl_ac_no1:
            if type(acct) is not str or acct.strip() == "":
                raise ValueError(ACCOUNT_ALLOWLIST_MISMATCH)
            if any(ch.isspace() for ch in acct) or not acct.isdigit():
                raise ValueError(ACCOUNT_ALLOWLIST_MISMATCH)
            cleaned.append(acct)
        object.__setattr__(self, "allowed_gnl_ac_no1", tuple(cleaned))


def seal_execution_account_allowlist(
    *,
    allowlist_id: str,
    allowed_gnl_ac_no1: tuple[str, ...],
) -> ExecutionAccountAllowlist:
    return ExecutionAccountAllowlist(allowlist_id, allowed_gnl_ac_no1)


def require_account_on_allowlist(
    binding: VerifiedExecutionAccountBinding,
    allowlist: ExecutionAccountAllowlist,
) -> None:
    if type(binding) is not VerifiedExecutionAccountBinding:
        raise TypeError("account binding required")
    if type(allowlist) is not ExecutionAccountAllowlist:
        raise TypeError("allowlist required")
    require_mutation_eligible_account(binding)
    if binding.gnl_ac_no1 not in allowlist.allowed_gnl_ac_no1:
        raise ValueError(ACCOUNT_ALLOWLIST_MISMATCH)


def assert_no_secret_in_text(text: str, *, forbidden_substrings: tuple[str, ...]) -> None:
    """Fail closed if any forbidden secret substring appears in operator-visible text."""
    if type(text) is not str:
        raise TypeError("text must be str")
    lowered = text.casefold()
    for item in forbidden_substrings:
        if type(item) is str and item and item.casefold() in lowered:
            raise ValueError("SECRET_LEAK_FORBIDDEN")
