from __future__ import annotations

import unittest
from decimal import Decimal

from CapitalAllocationCycle.hip import (
    HIP_V1_EXPLICIT_RESERVE_KRW,
    HIP_V1_MAX_POSITION_MARKET_VALUE_KRW,
    build_frozen_hip_v1,
    verify_hip_integrity,
)
from CapitalAllocationCycle.models import HumanInvestmentPolicy
from CapitalAllocationCycle.validation import validate_human_investment_policy
from CapitalAllocationCycle.vocabularies import (
    CAPITAL_SOURCING_MODE_ROTATION_ALLOWED,
    CURRENCY_KRW,
    DEPLOYABLE_CAPITAL_MODE_ORDERABLE_CASH_FULL,
    HIP_V1_POLICY_ID,
    HIP_V1_VERSION,
    ON_INVALIDATE_THESIS_BLOCK_AND_ALLOW_REDUCE_LEGS,
    PROFIT_REALIZATION_MODE_DEFER,
)


class HipTests(unittest.TestCase):
    def test_frozen_hip_v1_encodes_exact_policy(self):
        hip = build_frozen_hip_v1()
        self.assertEqual(hip.policy_id, HIP_V1_POLICY_ID)
        self.assertEqual(hip.version, HIP_V1_VERSION)
        self.assertEqual(hip.currency_code, CURRENCY_KRW)
        self.assertEqual(
            hip.deployable_capital_mode,
            DEPLOYABLE_CAPITAL_MODE_ORDERABLE_CASH_FULL,
        )
        self.assertEqual(hip.explicit_reserve_krw, Decimal("0"))
        self.assertIs(type(hip.explicit_reserve_krw), Decimal)
        self.assertEqual(hip.max_position_market_value_krw, Decimal("100000000"))
        self.assertEqual(
            hip.capital_sourcing_mode,
            CAPITAL_SOURCING_MODE_ROTATION_ALLOWED,
        )
        self.assertEqual(
            hip.on_invalidate_thesis,
            ON_INVALIDATE_THESIS_BLOCK_AND_ALLOW_REDUCE_LEGS,
        )
        self.assertIs(hip.leverage_allowed, False)
        self.assertIs(hip.approval_required, True)
        self.assertEqual(hip.profit_realization_mode, PROFIT_REALIZATION_MODE_DEFER)
        validate_human_investment_policy(hip)
        verify_hip_integrity(hip)

    def test_explicit_zero_reserve_constants(self):
        self.assertEqual(HIP_V1_EXPLICIT_RESERVE_KRW, Decimal("0"))
        self.assertEqual(HIP_V1_MAX_POSITION_MARKET_VALUE_KRW, Decimal("100000000"))

    def test_tampered_seal_fails(self):
        hip = build_frozen_hip_v1()
        tampered = HumanInvestmentPolicy(
            hip.policy_id,
            hip.version,
            hip.effective_at,
            hip.currency_code,
            hip.deployable_capital_mode,
            hip.explicit_reserve_krw,
            hip.max_position_market_value_krw,
            hip.capital_sourcing_mode,
            hip.on_invalidate_thesis,
            hip.leverage_allowed,
            hip.approval_required,
            hip.profit_realization_mode,
            "0" * 64,
        )
        with self.assertRaises(ValueError):
            validate_human_investment_policy(tampered)

    def test_leverage_allowed_true_rejected(self):
        hip = build_frozen_hip_v1()
        bad = HumanInvestmentPolicy(
            hip.policy_id,
            hip.version,
            hip.effective_at,
            hip.currency_code,
            hip.deployable_capital_mode,
            hip.explicit_reserve_krw,
            hip.max_position_market_value_krw,
            hip.capital_sourcing_mode,
            hip.on_invalidate_thesis,
            True,
            True,
            hip.profit_realization_mode,
            hip.integrity_seal,
        )
        with self.assertRaises(ValueError):
            validate_human_investment_policy(bad)
