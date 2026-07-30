import ast
import unittest
from decimal import (
    Decimal,
    Inexact,
    InvalidOperation,
    Rounded,
    localcontext,
)
from fractions import Fraction
from pathlib import Path

from ExactDecimalArithmetic.arithmetic import (
    add_exact_decimal,
    multiply_exact_decimal,
    subtract_exact_decimal,
)


class DecimalSubclass(Decimal):
    pass


class ExactDecimalArithmeticTests(unittest.TestCase):
    def test_basic_exact_addition(self):
        cases = (
            ("5", "2", "7"),
            ("-5", "-2", "-7"),
            ("5", "-2", "3"),
            ("-5", "2", "-3"),
            ("1.25", "0.20", "1.45"),
        )
        for augend, addend, expected in cases:
            with self.subTest(augend=augend, addend=addend):
                self.assertEqual(
                    add_exact_decimal(
                        Decimal(augend),
                        Decimal(addend),
                    ),
                    Decimal(expected),
                )

    def test_addition_exponent_and_trailing_zero_contract(self):
        cases = (
            ("2.00", "1.0", "3.00", -2),
            ("1E+2", "1", "101", 0),
            ("0.0100", "0.009", "0.0190", -4),
        )
        for augend, addend, expected, exponent in cases:
            with self.subTest(augend=augend, addend=addend):
                result = add_exact_decimal(
                    Decimal(augend),
                    Decimal(addend),
                )
                self.assertEqual(result, Decimal(expected))
                self.assertEqual(
                    result.as_tuple().exponent,
                    exponent,
                )

    def test_addition_zero_is_positive_at_finer_exponent(self):
        for augend, addend, exponent in (
            ("1.0", "-1.00", -2),
            ("-0", "-0.000", -3),
            ("0.00", "-0.0", -2),
        ):
            with self.subTest(augend=augend, addend=addend):
                result = add_exact_decimal(
                    Decimal(augend),
                    Decimal(addend),
                )
                self.assertEqual(result, Decimal("0"))
                self.assertEqual(result.as_tuple().sign, 0)
                self.assertEqual(
                    result.as_tuple().exponent,
                    exponent,
                )

    def test_basic_exact_multiplication(self):
        cases = (
            ("5", "2", "10"),
            ("-5", "-2", "10"),
            ("5", "-2", "-10"),
            ("-5", "2", "-10"),
            ("1.25", "0.20", "0.2500"),
        )
        for multiplicand, multiplier, expected in cases:
            with self.subTest(
                multiplicand=multiplicand,
                multiplier=multiplier,
            ):
                self.assertEqual(
                    multiply_exact_decimal(
                        Decimal(multiplicand),
                        Decimal(multiplier),
                    ),
                    Decimal(expected),
                )

    def test_multiplication_exponent_and_trailing_zero_contract(self):
        result = multiply_exact_decimal(
            Decimal("1.20"),
            Decimal("3.0"),
        )
        self.assertEqual(result, Decimal("3.600"))
        self.assertEqual(result.as_tuple().exponent, -3)

        large_exponents = multiply_exact_decimal(
            Decimal("2E+1000"),
            Decimal("3E-900"),
        )
        self.assertEqual(large_exponents, Decimal("6E+100"))
        self.assertEqual(
            large_exponents.as_tuple().exponent,
            100,
        )

    def test_multiplication_zero_is_positive_at_exponent_sum(self):
        for multiplicand, multiplier, exponent in (
            ("-0.00", "2.0", -3),
            ("0E+4", "-3E+2", 6),
            ("-0E-5", "-0E+2", -3),
        ):
            with self.subTest(
                multiplicand=multiplicand,
                multiplier=multiplier,
            ):
                result = multiply_exact_decimal(
                    Decimal(multiplicand),
                    Decimal(multiplier),
                )
                self.assertEqual(result, Decimal("0"))
                self.assertEqual(result.as_tuple().sign, 0)
                self.assertEqual(
                    result.as_tuple().exponent,
                    exponent,
                )

    def test_large_coefficients_are_exact(self):
        left = Decimal("9" * 120)
        right = Decimal("8" * 100)
        added = add_exact_decimal(left, right)
        multiplied = multiply_exact_decimal(left, right)
        self.assertEqual(
            added.as_tuple(),
            Decimal(
                int(str(left)) + int(str(right))
            ).as_tuple(),
        )
        self.assertEqual(
            multiplied.as_tuple(),
            Decimal(
                int(str(left)) * int(str(right))
            ).as_tuple(),
        )

    def test_addition_and_multiplication_ignore_context(self):
        with localcontext() as context:
            context.prec = 1
            context.rounding = "ROUND_DOWN"
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            context.traps[InvalidOperation] = False
            before = context.copy()

            added = add_exact_decimal(
                Decimal("9" * 80),
                Decimal("1"),
            )
            multiplied = multiply_exact_decimal(
                Decimal("9" * 80),
                Decimal("8" * 60),
            )

            self.assertEqual(added, Decimal("1" + "0" * 80))
            self.assertEqual(len(multiplied.as_tuple().digits), 140)
            self.assertEqual(context.prec, before.prec)
            self.assertEqual(context.rounding, before.rounding)
            self.assertEqual(context.traps, before.traps)
            self.assertEqual(context.flags, before.flags)

    def test_addition_validation_order_and_exact_types(self):
        invalid = (
            None,
            1,
            1.0,
            Fraction(1, 2),
            DecimalSubclass("1"),
        )
        for value in invalid:
            with self.subTest(position="augend", value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^augend must be Decimal$",
                ):
                    add_exact_decimal(value, Decimal("1"))
            with self.subTest(position="addend", value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^addend must be Decimal$",
                ):
                    add_exact_decimal(Decimal("1"), value)
        with self.assertRaisesRegex(
            TypeError,
            "^augend must be Decimal$",
        ):
            add_exact_decimal(None, Decimal("NaN"))

    def test_multiplication_validation_order_and_exact_types(self):
        invalid = (
            None,
            1,
            1.0,
            Fraction(1, 2),
            DecimalSubclass("1"),
        )
        for value in invalid:
            with self.subTest(position="multiplicand", value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^multiplicand must be Decimal$",
                ):
                    multiply_exact_decimal(
                        value,
                        Decimal("1"),
                    )
            with self.subTest(position="multiplier", value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^multiplier must be Decimal$",
                ):
                    multiply_exact_decimal(
                        Decimal("1"),
                        value,
                    )
        with self.assertRaisesRegex(
            TypeError,
            "^multiplicand must be Decimal$",
        ):
            multiply_exact_decimal(None, Decimal("NaN"))

    def test_addition_and_multiplication_reject_non_finite(self):
        non_finite = (
            Decimal("NaN"),
            Decimal("sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )
        functions = (
            (
                add_exact_decimal,
                "augend",
                "addend",
            ),
            (
                multiply_exact_decimal,
                "multiplicand",
                "multiplier",
            ),
        )
        for function, first_name, second_name in functions:
            for value in non_finite:
                with self.subTest(
                    function=function.__name__,
                    position=first_name,
                    value=value,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{first_name} must be finite$",
                    ):
                        function(value, Decimal("1"))
                with self.subTest(
                    function=function.__name__,
                    position=second_name,
                    value=value,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{second_name} must be finite$",
                    ):
                        function(Decimal("1"), value)

    def test_addition_and_multiplication_preserve_inputs(self):
        left = Decimal("-123.4500")
        right = Decimal("0.005")
        left_tuple = left.as_tuple()
        right_tuple = right.as_tuple()
        add_exact_decimal(left, right)
        multiply_exact_decimal(left, right)
        self.assertEqual(left.as_tuple(), left_tuple)
        self.assertEqual(right.as_tuple(), right_tuple)

    def test_basic_exact_subtraction(self):
        cases = (
            ("5", "2", "3"),
            ("2", "5", "-3"),
            ("-2", "-5", "3"),
            ("-5", "2", "-7"),
            ("0", "0", "0"),
            ("1.25", "0.20", "1.05"),
        )
        for minuend, subtrahend, expected in cases:
            with self.subTest(
                minuend=minuend,
                subtrahend=subtrahend,
            ):
                self.assertEqual(
                    subtract_exact_decimal(
                        Decimal(minuend),
                        Decimal(subtrahend),
                    ),
                    Decimal(expected),
                )

    def test_large_exponent_gap_is_exact(self):
        result = subtract_exact_decimal(
            Decimal("1e40"),
            Decimal("1"),
        )
        self.assertEqual(
            result,
            Decimal(
                "9999999999999999999999999999999999999999"
            ),
        )
        self.assertEqual(
            result.as_tuple().digits,
            (9,) * 40,
        )
        self.assertEqual(result.as_tuple().exponent, 0)

    def test_low_context_precision_does_not_round(self):
        expected = Decimal(
            "9999999999999999999999999999999999999999"
        )
        with localcontext() as context:
            context.prec = 1
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            result = subtract_exact_decimal(
                Decimal("1e40"),
                Decimal("1"),
            )
            self.assertEqual(result, expected)
            self.assertFalse(context.flags[Inexact])
            self.assertFalse(context.flags[Rounded])

    def test_active_context_is_not_changed(self):
        with localcontext() as context:
            context.prec = 7
            context.rounding = "ROUND_DOWN"
            context.traps[InvalidOperation] = False
            before = context.copy()

            subtract_exact_decimal(
                Decimal("123.4500"),
                Decimal("0.0001"),
            )

            self.assertEqual(context.prec, before.prec)
            self.assertEqual(context.rounding, before.rounding)
            self.assertEqual(context.traps, before.traps)
            self.assertEqual(context.flags, before.flags)

    def test_finer_input_exponent_is_preserved(self):
        cases = (
            ("2.00", "1.0", "1.00", -2),
            ("2", "1.000", "1.000", -3),
            ("1E+2", "1", "99", 0),
            ("0.0100", "0.009", "0.0010", -4),
        )
        for minuend, subtrahend, expected, exponent in cases:
            with self.subTest(
                minuend=minuend,
                subtrahend=subtrahend,
            ):
                result = subtract_exact_decimal(
                    Decimal(minuend),
                    Decimal(subtrahend),
                )
                self.assertEqual(result, Decimal(expected))
                self.assertEqual(
                    result.as_tuple().exponent,
                    exponent,
                )

    def test_zero_result_is_positive_at_finer_exponent(self):
        cases = (
            ("1.0", "1.00", -2),
            ("-0", "0.000", -3),
            ("0.00", "-0.0", -2),
        )
        for minuend, subtrahend, exponent in cases:
            with self.subTest(
                minuend=minuend,
                subtrahend=subtrahend,
            ):
                result = subtract_exact_decimal(
                    Decimal(minuend),
                    Decimal(subtrahend),
                )
                self.assertEqual(result, Decimal("0"))
                self.assertEqual(result.as_tuple().sign, 0)
                self.assertEqual(
                    result.as_tuple().exponent,
                    exponent,
                )

    def test_exact_decimal_type_required_in_argument_order(self):
        cases = (
            (
                None,
                None,
                TypeError,
                "minuend must be Decimal",
            ),
            (
                DecimalSubclass("1"),
                Decimal("1"),
                TypeError,
                "minuend must be Decimal",
            ),
            (
                Decimal("1"),
                DecimalSubclass("1"),
                TypeError,
                "subtrahend must be Decimal",
            ),
        )
        for minuend, subtrahend, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    subtract_exact_decimal(
                        minuend,
                        subtrahend,
                    )

    def test_non_finite_values_rejected_in_argument_order(self):
        non_finite = (
            Decimal("NaN"),
            Decimal("sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )
        for value in non_finite:
            with self.subTest(position="minuend", value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "^minuend must be finite$",
                ):
                    subtract_exact_decimal(
                        value,
                        Decimal("1"),
                    )
            with self.subTest(
                position="subtrahend",
                value=value,
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "^subtrahend must be finite$",
                ):
                    subtract_exact_decimal(
                        Decimal("1"),
                        value,
                    )

    def test_first_failure_stops_before_second_validation(self):
        with self.assertRaisesRegex(
            TypeError,
            "^minuend must be Decimal$",
        ):
            subtract_exact_decimal(
                None,
                Decimal("NaN"),
            )
        with self.assertRaisesRegex(
            ValueError,
            "^minuend must be finite$",
        ):
            subtract_exact_decimal(
                Decimal("NaN"),
                None,
            )

    def test_inputs_and_tuple_representation_are_preserved(self):
        minuend = Decimal("-123.4500")
        subtrahend = Decimal("0.005")
        minuend_tuple = minuend.as_tuple()
        subtrahend_tuple = subtrahend.as_tuple()

        result = subtract_exact_decimal(
            minuend,
            subtrahend,
        )

        self.assertEqual(result, Decimal("-123.4550"))
        self.assertEqual(minuend.as_tuple(), minuend_tuple)
        self.assertEqual(
            subtrahend.as_tuple(),
            subtrahend_tuple,
        )

    def test_production_structure_is_domain_independent(self):
        root = Path(__file__).resolve().parents[1]
        tree = ast.parse(
            (root / "arithmetic.py").read_text()
        )
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(imported_modules, {"decimal"})
        imported_symbols = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertEqual(imported_symbols, {"Decimal"})
        forbidden = {
            "float",
            "Fraction",
            "getcontext",
            "localcontext",
        }
        self.assertTrue(
            forbidden.isdisjoint(imported_symbols)
        )


if __name__ == "__main__":
    unittest.main()
