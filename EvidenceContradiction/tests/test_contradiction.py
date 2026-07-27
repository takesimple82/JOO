import ast
import unittest
from dataclasses import fields
from decimal import Decimal
from enum import Enum
from pathlib import Path
from unittest.mock import patch

from EvidenceComparison.models import EvidenceComparisonStatus
from EvidenceContradiction.classification import (
    classify_exact_observed_numeric_contradiction_candidate,
)
from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
)
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


class UnrelatedStatus(Enum):
    UNKNOWN = "unknown"


class EvidenceContradictionTests(unittest.TestCase):
    def test_exact_enum_contract(self):
        self.assertEqual(
            EvidenceContradictionStatus.__bases__,
            (Enum,),
        )
        self.assertEqual(
            list(EvidenceContradictionStatus),
            [
                EvidenceContradictionStatus.NOT_ELIGIBLE,
                (
                    EvidenceContradictionStatus
                    .NO_CONTRADICTION_CANDIDATE
                ),
                (
                    EvidenceContradictionStatus
                    .CONTRADICTION_CANDIDATE
                ),
            ],
        )
        self.assertEqual(
            [
                (member.name, member.value)
                for member in EvidenceContradictionStatus
            ],
            [
                ("NOT_ELIGIBLE", "not_eligible"),
                (
                    "NO_CONTRADICTION_CANDIDATE",
                    "no_contradiction_candidate",
                ),
                (
                    "CONTRADICTION_CANDIDATE",
                    "contradiction_candidate",
                ),
            ],
        )
        self.assertEqual(
            len(EvidenceContradictionStatus.__members__),
            3,
        )
        self.assertIsInstance(
            hash(EvidenceContradictionStatus.NOT_ELIGIBLE),
            int,
        )
        with self.assertRaises(AttributeError):
            EvidenceContradictionStatus.NOT_ELIGIBLE.value = "changed"

    def test_exact_comparison_status_mapping(self):
        cases = (
            (
                EvidenceComparisonStatus.NOT_COMPARABLE,
                EvidenceContradictionStatus.NOT_ELIGIBLE,
            ),
            (
                EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE,
                (
                    EvidenceContradictionStatus
                    .NO_CONTRADICTION_CANDIDATE
                ),
            ),
            (
                EvidenceComparisonStatus.NUMERICALLY_INCOMPATIBLE,
                (
                    EvidenceContradictionStatus
                    .CONTRADICTION_CANDIDATE
                ),
            ),
        )
        left = object()
        right = object()

        for comparison_status, expected in cases:
            with self.subTest(status=comparison_status):
                with patch(
                    "EvidenceContradiction.classification."
                    "compare_exact_observed_numeric_propositions",
                    return_value=comparison_status,
                ) as comparison:
                    result = (
                        classify_exact_observed_numeric_contradiction_candidate(
                            left,
                            right,
                        )
                    )

                self.assertIs(result, expected)
                comparison.assert_called_once_with(left, right)

    def test_exact_objects_and_order_are_forwarded_once(self):
        left = object()
        right = object()

        with patch(
            "EvidenceContradiction.classification."
            "compare_exact_observed_numeric_propositions",
            return_value=(
                EvidenceComparisonStatus.NUMERICALLY_COMPATIBLE
            ),
        ) as comparison:
            classify_exact_observed_numeric_contradiction_candidate(
                left,
                right,
            )

        comparison.assert_called_once()
        forwarded_left, forwarded_right = (
            comparison.call_args.args
        )
        self.assertIs(forwarded_left, left)
        self.assertIs(forwarded_right, right)

    def test_upstream_exceptions_propagate_unchanged(self):
        cases = (
            TypeError("accepted type failure"),
            ValueError("accepted value failure"),
        )

        for error in cases:
            with self.subTest(error_type=type(error)):
                with patch(
                    "EvidenceContradiction.classification."
                    "compare_exact_observed_numeric_propositions",
                    side_effect=error,
                ) as comparison:
                    try:
                        classify_exact_observed_numeric_contradiction_candidate(
                            object(),
                            object(),
                        )
                    except type(error) as caught:
                        self.assertIs(caught, error)
                    else:
                        self.fail(
                            "comparison exception did not propagate"
                        )

                self.assertEqual(comparison.call_count, 1)

    def test_unknown_comparison_status_raises_exact_error(self):
        unknown_values = (
            object(),
            None,
            UnrelatedStatus.UNKNOWN,
        )

        for value in unknown_values:
            with self.subTest(value=value):
                with patch(
                    "EvidenceContradiction.classification."
                    "compare_exact_observed_numeric_propositions",
                    return_value=value,
                ):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        "^unsupported evidence comparison status$",
                    ):
                        classify_exact_observed_numeric_contradiction_candidate(
                            object(),
                            object(),
                        )

    def test_integrated_identity_mismatch_is_not_eligible(self):
        self.assertIs(
            classify_exact_observed_numeric_contradiction_candidate(
                make_proposition(),
                make_proposition(subject_id="subject-002"),
            ),
            EvidenceContradictionStatus.NOT_ELIGIBLE,
        )

    def test_integrated_equal_values_have_no_candidate(self):
        pairs = (
            (Decimal("100"), Decimal("100")),
            (Decimal("1.0"), Decimal("1.00")),
            (Decimal("0"), Decimal("-0")),
        )

        for left_value, right_value in pairs:
            with self.subTest(
                left=str(left_value),
                right=str(right_value),
            ):
                self.assertIs(
                    classify_exact_observed_numeric_contradiction_candidate(
                        make_proposition(value=left_value),
                        make_proposition(value=right_value),
                    ),
                    (
                        EvidenceContradictionStatus
                        .NO_CONTRADICTION_CANDIDATE
                    ),
                )

    def test_integrated_unequal_values_form_candidate(self):
        self.assertIs(
            classify_exact_observed_numeric_contradiction_candidate(
                make_proposition(value=Decimal("100")),
                make_proposition(value=Decimal("101")),
            ),
            (
                EvidenceContradictionStatus
                .CONTRADICTION_CANDIDATE
            ),
        )

    def test_self_comparison_has_no_candidate(self):
        proposition = make_proposition()

        self.assertIs(
            classify_exact_observed_numeric_contradiction_candidate(
                proposition,
                proposition,
            ),
            (
                EvidenceContradictionStatus
                .NO_CONTRADICTION_CANDIDATE
            ),
        )

    def test_proposition_and_finding_ids_do_not_suppress_candidate(self):
        left = make_proposition()
        cases = (
            make_proposition(
                proposition_id="proposition-002",
                value=Decimal("101"),
            ),
            make_proposition(
                finding_id="finding-002",
                value=Decimal("101"),
            ),
            make_proposition(
                proposition_id=left.proposition_id,
                value=Decimal("101"),
            ),
            make_proposition(
                finding_id=left.finding_id,
                value=Decimal("101"),
            ),
        )

        for right in cases:
            with self.subTest(
                proposition_id=right.proposition_id,
                finding_id=right.finding_id,
            ):
                self.assertIs(
                    classify_exact_observed_numeric_contradiction_candidate(
                        left,
                        right,
                    ),
                    (
                        EvidenceContradictionStatus
                        .CONTRADICTION_CANDIDATE
                    ),
                )

    def test_status_is_symmetric_for_valid_pairs(self):
        pairs = (
            (
                make_proposition(),
                make_proposition(subject_id="subject-002"),
            ),
            (
                make_proposition(),
                make_proposition(value=Decimal("100.00")),
            ),
            (
                make_proposition(),
                make_proposition(value=Decimal("101")),
            ),
        )

        for left, right in pairs:
            with self.subTest(
                subject_id=right.subject_id,
                value=str(right.value),
            ):
                self.assertIs(
                    classify_exact_observed_numeric_contradiction_candidate(
                        left,
                        right,
                    ),
                    classify_exact_observed_numeric_contradiction_candidate(
                        right,
                        left,
                    ),
                )

    def test_classification_does_not_mutate_inputs(self):
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

        classify_exact_observed_numeric_contradiction_candidate(
            left,
            right,
        )

        for name, value in left_values.items():
            self.assertIs(getattr(left, name), value)
        for name, value in right_values.items():
            self.assertIs(getattr(right, name), value)
        self.assertEqual(left.value.as_tuple().exponent, -1)
        self.assertEqual(right.value.as_tuple().exponent, -2)

    def test_production_structure_and_import_boundaries(self):
        package_root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (package_root / "models.py").read_text()
        )
        classification_tree = ast.parse(
            (package_root / "classification.py").read_text()
        )

        self.assertEqual(
            self._import_roots(model_tree),
            {"enum"},
        )
        self.assertEqual(
            self._import_roots(classification_tree),
            {
                "EvidenceComparison",
                "EvidenceContradiction",
                "EvidenceProposition",
            },
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["EvidenceContradictionStatus"],
        )
        self.assertEqual(
            [
                node.name
                for node in classification_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "classify_exact_observed_numeric_"
                "contradiction_candidate"
            ],
        )

        imported_symbols = {
            alias.name
            for node in classification_tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertNotIn(
            "validate_exact_observed_numeric_proposition",
            imported_symbols,
        )
        self.assertNotIn("Decimal", imported_symbols)

        accessed_attributes = {
            node.attr
            for node in ast.walk(classification_tree)
            if isinstance(node, ast.Attribute)
        }
        for field_name in (
            "proposition_id",
            "finding_id",
            "subject_id",
            "predicate_id",
            "value",
            "unit_id",
            "effective_context_id",
        ):
            with self.subTest(field=field_name):
                self.assertNotIn(
                    field_name,
                    accessed_attributes,
                )

    def test_upstream_packages_have_no_reverse_dependency(self):
        repository_root = Path(__file__).resolve().parents[2]
        target_root = "Evidence" + "Contradiction"
        upstream_names = (
            "Evidence" + "Proposition",
            "Evidence" + "Comparison",
            "Evidence" + "Aggregation",
        )

        for package_name in upstream_names:
            for path in (
                repository_root / package_name
            ).glob("*.py"):
                with self.subTest(
                    package=package_name,
                    path=path.name,
                ):
                    self.assertNotIn(
                        target_root,
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
