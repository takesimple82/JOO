import ast
import unittest
from dataclasses import fields, replace
from decimal import Decimal
from enum import Enum
from pathlib import Path
from unittest.mock import patch

from EvidenceComparison.comparison import (
    compare_exact_observed_numeric_propositions,
)
from EvidenceComparison.models import EvidenceComparisonStatus
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)


def make_proposition(
    **overrides,
) -> ExactObservedNumericProposition:
    values = {
        "proposition_id": "proposition-001",
        "finding_id": "finding-001",
        "subject_id": "subject-001",
        "predicate_id": "predicate-001",
        "value": Decimal("100"),
        "unit_id": "USD",
        "effective_context_id": "context-001",
    }
    values.update(overrides)
    return ExactObservedNumericProposition(**values)


class EvidenceComparisonTests(unittest.TestCase):
    def test_exact_enum_contract(self):
        self.assertEqual(
            EvidenceComparisonStatus.__bases__,
            (Enum,),
        )
        self.assertEqual(
            list(EvidenceComparisonStatus),
            [
                EvidenceComparisonStatus.NOT_COMPARABLE,
                EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE,
                EvidenceComparisonStatus.NUMERICALLY_INCOMPATIBLE,
            ],
        )
        self.assertEqual(
            [
                (member.name, member.value)
                for member in EvidenceComparisonStatus
            ],
            [
                ("NOT_COMPARABLE", "not_comparable"),
                (
                    "NUMERICALLY_COMPATIBLE",
                    "numerically_compatible",
                ),
                (
                    "NUMERICALLY_INCOMPATIBLE",
                    "numerically_incompatible",
                ),
            ],
        )
        self.assertEqual(
            len(EvidenceComparisonStatus.__members__),
            3,
        )
        self.assertIsInstance(
            hash(EvidenceComparisonStatus.NOT_COMPARABLE),
            int,
        )
        with self.assertRaises(AttributeError):
            EvidenceComparisonStatus.NOT_COMPARABLE.value = "changed"

    def test_compatible_decimal_values(self):
        pairs = (
            (Decimal("100"), Decimal("100")),
            (Decimal("1.25"), Decimal("1.25")),
            (Decimal("1.0"), Decimal("1.00")),
            (Decimal("0"), Decimal("-0")),
            (Decimal("1E+2"), Decimal("100")),
            (Decimal("-5.50"), Decimal("-5.500")),
        )

        for left_value, right_value in pairs:
            with self.subTest(
                left=str(left_value),
                right=str(right_value),
            ):
                self.assertIs(
                    compare_exact_observed_numeric_propositions(
                        make_proposition(value=left_value),
                        make_proposition(value=right_value),
                    ),
                    EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE,
                )

    def test_self_comparison_is_compatible(self):
        proposition = make_proposition()

        self.assertIs(
            compare_exact_observed_numeric_propositions(
                proposition,
                proposition,
            ),
            EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE,
        )

    def test_incompatible_decimal_values(self):
        pairs = (
            (Decimal("1"), Decimal("2")),
            (Decimal("-1"), Decimal("-2")),
            (Decimal("0"), Decimal("1")),
        )

        for left_value, right_value in pairs:
            with self.subTest(
                left=str(left_value),
                right=str(right_value),
            ):
                self.assertIs(
                    compare_exact_observed_numeric_propositions(
                        make_proposition(value=left_value),
                        make_proposition(value=right_value),
                    ),
                    EvidenceComparisonStatus.NUMERICALLY_INCOMPATIBLE,
                )

    def test_each_comparison_identity_mismatch_is_not_comparable(self):
        cases = (
            ("subject_id", "subject-002"),
            ("predicate_id", "predicate-002"),
            ("unit_id", "EUR"),
            ("effective_context_id", "context-002"),
        )

        for field_name, value in cases:
            with self.subTest(field=field_name):
                self.assertIs(
                    compare_exact_observed_numeric_propositions(
                        make_proposition(),
                        make_proposition(
                            **{field_name: value}
                        ),
                    ),
                    EvidenceComparisonStatus.NOT_COMPARABLE,
                )

    def test_multiple_identity_mismatches_are_not_comparable(self):
        left = make_proposition()
        right = make_proposition(
            subject_id="subject-002",
            predicate_id="predicate-002",
            unit_id="EUR",
            effective_context_id="context-002",
        )

        self.assertIs(
            compare_exact_observed_numeric_propositions(
                left,
                right,
            ),
            EvidenceComparisonStatus.NOT_COMPARABLE,
        )

    def test_value_and_other_ids_do_not_override_identity_mismatch(self):
        left = make_proposition()
        right = make_proposition(
            proposition_id=left.proposition_id,
            finding_id=left.finding_id,
            subject_id="subject-002",
            value=left.value,
        )

        self.assertIs(
            compare_exact_observed_numeric_propositions(
                left,
                right,
            ),
            EvidenceComparisonStatus.NOT_COMPARABLE,
        )

    def test_proposition_and_finding_ids_are_ignored(self):
        compatible = make_proposition(
            proposition_id="proposition-002",
            finding_id="finding-002",
        )
        incompatible = make_proposition(
            proposition_id="proposition-003",
            finding_id="finding-003",
            value=Decimal("101"),
        )
        left = make_proposition()

        self.assertIs(
            compare_exact_observed_numeric_propositions(
                left,
                compatible,
            ),
            EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE,
        )
        self.assertIs(
            compare_exact_observed_numeric_propositions(
                left,
                incompatible,
            ),
            EvidenceComparisonStatus.NUMERICALLY_INCOMPATIBLE,
        )

    def test_same_proposition_id_does_not_override_value_inequality(self):
        left = make_proposition()
        right = make_proposition(
            proposition_id=left.proposition_id,
            value=Decimal("101"),
        )

        self.assertIs(
            compare_exact_observed_numeric_propositions(
                left,
                right,
            ),
            EvidenceComparisonStatus.NUMERICALLY_INCOMPATIBLE,
        )

    def test_status_is_symmetric_for_valid_inputs(self):
        pairs = (
            (
                make_proposition(),
                make_proposition(value=Decimal("100.00")),
            ),
            (
                make_proposition(),
                make_proposition(value=Decimal("101")),
            ),
            (
                make_proposition(),
                make_proposition(subject_id="subject-002"),
            ),
        )

        for left, right in pairs:
            with self.subTest(
                right_subject=right.subject_id,
                right_value=str(right.value),
            ):
                self.assertIs(
                    compare_exact_observed_numeric_propositions(
                        left,
                        right,
                    ),
                    compare_exact_observed_numeric_propositions(
                        right,
                        left,
                    ),
                )

    def test_validator_is_called_once_per_position_in_order(self):
        left = make_proposition(proposition_id="left")
        right = make_proposition(proposition_id="right")
        calls = []

        with patch(
            "EvidenceComparison.comparison."
            "validate_exact_observed_numeric_proposition",
            side_effect=lambda value: calls.append(value),
        ) as validator:
            result = compare_exact_observed_numeric_propositions(
                left,
                right,
            )

        self.assertIs(
            result,
            EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE,
        )
        self.assertEqual(calls, [left, right])
        self.assertEqual(validator.call_count, 2)

    def test_invalid_left_stops_before_right_validation(self):
        left = make_proposition(proposition_id="left")
        right = make_proposition(proposition_id="right")
        error = TypeError("accepted left failure")
        calls = []

        def validate(value):
            calls.append(value)
            raise error

        with patch(
            "EvidenceComparison.comparison."
            "validate_exact_observed_numeric_proposition",
            side_effect=validate,
        ):
            try:
                compare_exact_observed_numeric_propositions(
                    left,
                    right,
                )
            except TypeError as caught:
                self.assertIs(caught, error)
            else:
                self.fail("validation exception did not propagate")

        self.assertEqual(calls, [left])

    def test_invalid_right_follows_valid_left_and_propagates(self):
        left = make_proposition(proposition_id="left")
        right = make_proposition(proposition_id="right")
        error = ValueError("accepted right failure")
        calls = []

        def validate(value):
            calls.append(value)
            if value is right:
                raise error

        with patch(
            "EvidenceComparison.comparison."
            "validate_exact_observed_numeric_proposition",
            side_effect=validate,
        ):
            try:
                compare_exact_observed_numeric_propositions(
                    left,
                    right,
                )
            except ValueError as caught:
                self.assertIs(caught, error)
            else:
                self.fail("validation exception did not propagate")

        self.assertEqual(calls, [left, right])

    def test_real_upstream_type_errors_propagate(self):
        with self.assertRaisesRegex(
            TypeError,
            "^proposition must be "
            "ExactObservedNumericProposition$",
        ):
            compare_exact_observed_numeric_propositions(
                object(),
                make_proposition(),
            )

    def test_comparison_preserves_inputs_and_representations(self):
        left_value = Decimal("1.0")
        right_value = Decimal("1.00")
        left = make_proposition(
            proposition_id=" left ",
            value=left_value,
        )
        right = make_proposition(
            proposition_id=" right ",
            value=right_value,
        )
        left_values = {
            field.name: getattr(left, field.name)
            for field in fields(left)
        }
        right_values = {
            field.name: getattr(right, field.name)
            for field in fields(right)
        }

        compare_exact_observed_numeric_propositions(left, right)

        for name, value in left_values.items():
            self.assertIs(getattr(left, name), value)
        for name, value in right_values.items():
            self.assertIs(getattr(right, name), value)
        self.assertEqual(left.value.as_tuple().exponent, -1)
        self.assertEqual(right.value.as_tuple().exponent, -2)

    def test_signed_zero_representation_is_preserved(self):
        positive = make_proposition(value=Decimal("0"))
        negative = make_proposition(value=Decimal("-0"))

        compare_exact_observed_numeric_propositions(
            positive,
            negative,
        )

        self.assertEqual(positive.value.as_tuple().sign, 0)
        self.assertEqual(negative.value.as_tuple().sign, 1)

    def test_production_structure_and_import_boundaries(self):
        package_root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (package_root / "models.py").read_text()
        )
        comparison_tree = ast.parse(
            (package_root / "comparison.py").read_text()
        )

        self.assertEqual(
            self._import_roots(model_tree),
            {"enum"},
        )
        self.assertEqual(
            self._import_roots(comparison_tree),
            {"EvidenceComparison", "EvidenceProposition"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["EvidenceComparisonStatus"],
        )
        self.assertEqual(
            [
                node.name
                for node in comparison_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            ["compare_exact_observed_numeric_propositions"],
        )

        all_names = {
            node.id
            for tree in (model_tree, comparison_tree)
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        }
        self.assertNotIn("dataclass", all_names)
        self.assertNotIn("round", all_names)
        self.assertNotIn("quantize", all_names)

    def test_upstream_package_has_no_reverse_dependency(self):
        upstream_root = Path(__file__).resolve().parents[2] / (
            "Evidence" + "Proposition"
        )
        prohibited_root = "Evidence" + "Comparison"

        for path in upstream_root.glob("*.py"):
            with self.subTest(path=path.name):
                self.assertNotIn(
                    prohibited_root,
                    self._import_roots(
                        ast.parse(path.read_text())
                    ),
                )

    @staticmethod
    def _import_roots(tree):
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(
                    alias.name.split(".", 1)[0]
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                roots.add(node.module.split(".", 1)[0])
        return roots


if __name__ == "__main__":
    unittest.main()
