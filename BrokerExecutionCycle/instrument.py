from __future__ import annotations

from BrokerExecutionCycle.integrity import integrity_seal
from BrokerExecutionCycle.models import InstrumentIdentityBinding
from BrokerExecutionCycle.vocabularies import (
    FAILURE_INSTRUMENT_UNPROVEN,
    HOLDINGS_IS_CD_PREFIX,
    SSAM_IS_CD_PATTERN_LEN,
)


def _is_digits(value: str) -> bool:
    return type(value) is str and value.isdigit() and value != ""


def holdings_is_cd_to_ssam_is_cd(holdings_is_cd: str) -> str | None:
    """Deterministic bridge: A005930 → 005930. Unproven → None."""
    if type(holdings_is_cd) is not str:
        return None
    code = holdings_is_cd.strip()
    if len(code) == SSAM_IS_CD_PATTERN_LEN + 1 and code.startswith(
        HOLDINGS_IS_CD_PREFIX
    ):
        body = code[1:]
        if _is_digits(body) and len(body) == SSAM_IS_CD_PATTERN_LEN:
            return body
        return None
    if _is_digits(code) and len(code) == SSAM_IS_CD_PATTERN_LEN:
        # Already SSAM form — only accept when caller proves via holdings match.
        return None
    return None


def seal_instrument_identity_binding(
    *,
    binding_id: str,
    portfolio_subject_id: str,
    holdings_is_cd: str,
    expected_ssam_is_cd: str | None = None,
) -> InstrumentIdentityBinding:
    derived = holdings_is_cd_to_ssam_is_cd(holdings_is_cd)
    proven = derived is not None
    ssam = derived if derived is not None else ""
    if (
        expected_ssam_is_cd is not None
        and proven
        and expected_ssam_is_cd != derived
    ):
        proven = False
        ssam = ""
    payload = {
        "binding_id": binding_id,
        "portfolio_subject_id": portfolio_subject_id,
        "holdings_is_cd": holdings_is_cd,
        "ssam_is_cd": ssam,
        "proven": proven,
    }
    return InstrumentIdentityBinding(
        binding_id,
        portfolio_subject_id,
        holdings_is_cd,
        ssam,
        proven,
        integrity_seal(payload),
    )


def require_proven_instrument(binding: InstrumentIdentityBinding) -> str:
    if type(binding) is not InstrumentIdentityBinding:
        raise TypeError("instrument binding required")
    if not binding.proven or binding.ssam_is_cd == "":
        raise ValueError(FAILURE_INSTRUMENT_UNPROVEN)
    return binding.ssam_is_cd
