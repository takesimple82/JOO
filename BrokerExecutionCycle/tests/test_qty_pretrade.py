from __future__ import annotations

import unittest
from decimal import Decimal

from BrokerExecutionCycle.pretrade import validate_pretrade
from BrokerExecutionCycle.qty import derive_limit_quantity
from BrokerExecutionCycle.tests.helpers import NOW, make_pretrade_bundle
from BrokerExecutionCycle.vocabularies import (
    FAILURE_BUY_CASH_INSUFFICIENT,
    FAILURE_EXPOSURE_CAP,
    FAILURE_MISSING_TRADE_UNIT,
    FAILURE_SELL_EXCEEDS_SELLABLE,
    SIDE_BUY,
    SIDE_SELL,
)


class QtyDerivationTests(unittest.TestCase):
    def test_floor_to_trade_unit(self):
        raw, derived, notional = derive_limit_quantity(
            approved_notional=Decimal("1000000"),
            limit_price=Decimal("360000"),
            trade_quantity_unit=Decimal("1"),
        )
        self.assertEqual(raw, Decimal("2"))
        self.assertEqual(derived, Decimal("2"))
        self.assertEqual(notional, Decimal("720000"))

    def test_floor_with_unit_greater_than_one(self):
        raw, derived, notional = derive_limit_quantity(
            approved_notional=Decimal("10000000"),
            limit_price=Decimal("360000"),
            trade_quantity_unit=Decimal("5"),
        )
        # raw = floor(10000000/360000)=27; derived=floor(27/5)*5=25
        self.assertEqual(raw, Decimal("27"))
        self.assertEqual(derived, Decimal("25"))
        self.assertEqual(notional, Decimal("9000000"))

    def test_missing_trade_unit_fail_closed(self):
        with self.assertRaisesRegex(ValueError, FAILURE_MISSING_TRADE_UNIT):
            derive_limit_quantity(
                approved_notional=Decimal("1000000"),
                limit_price=Decimal("360000"),
                trade_quantity_unit=None,
            )

    def test_invalid_trade_unit_zero_fail_closed(self):
        with self.assertRaisesRegex(ValueError, FAILURE_MISSING_TRADE_UNIT):
            derive_limit_quantity(
                approved_notional=Decimal("1000000"),
                limit_price=Decimal("360000"),
                trade_quantity_unit=Decimal("0"),
            )

    def test_no_float_in_qty_module(self):
        from pathlib import Path

        src = (Path(__file__).resolve().parents[1] / "qty.py").read_text()
        self.assertNotIn("float(", src)


class PreTradeMatrixTests(unittest.TestCase):
    def test_buy_happy_path(self):
        bundle = make_pretrade_bundle(limit_price="360000", cash_amount="50000000")
        result = validate_pretrade(
            validation_id="v1",
            bundle=bundle,
            side=SIDE_BUY,
            approved_notional_krw=Decimal("10000000"),
            validated_at=NOW,
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.derived_qty, Decimal("27"))

    def test_buy_insufficient_cash(self):
        bundle = make_pretrade_bundle(cash_amount="1000")
        result = validate_pretrade(
            validation_id="v2",
            bundle=bundle,
            side=SIDE_BUY,
            approved_notional_krw=Decimal("10000000"),
            validated_at=NOW,
        )
        self.assertFalse(result.passed)
        self.assertIn(FAILURE_BUY_CASH_INSUFFICIENT, [f.code for f in result.findings])

    def test_sell_exceeds_sellable(self):
        bundle = make_pretrade_bundle(side=SIDE_SELL, sellable_qty="1", cash_amount="0")
        result = validate_pretrade(
            validation_id="v3",
            bundle=bundle,
            side=SIDE_SELL,
            approved_notional_krw=Decimal("10000000"),
            validated_at=NOW,
        )
        self.assertFalse(result.passed)
        self.assertIn(FAILURE_SELL_EXCEEDS_SELLABLE, [f.code for f in result.findings])

    def test_exposure_cap(self):
        bundle = make_pretrade_bundle(cash_amount="200000000")
        result = validate_pretrade(
            validation_id="v4",
            bundle=bundle,
            side=SIDE_BUY,
            approved_notional_krw=Decimal("150000000"),
            validated_at=NOW,
        )
        self.assertFalse(result.passed)
        self.assertIn(FAILURE_EXPOSURE_CAP, [f.code for f in result.findings])

    def test_unverified_account_blocks(self):
        from BrokerExecutionCycle.tests.helpers import unverified_account
        from BrokerExecutionCycle.vocabularies import FAILURE_ACCOUNT_UNVERIFIED

        bundle = make_pretrade_bundle(account=unverified_account())
        result = validate_pretrade(
            validation_id="v5",
            bundle=bundle,
            side=SIDE_BUY,
            approved_notional_krw=Decimal("10000000"),
            validated_at=NOW,
        )
        self.assertFalse(result.passed)
        self.assertIn(FAILURE_ACCOUNT_UNVERIFIED, [f.code for f in result.findings])


if __name__ == "__main__":
    unittest.main()
