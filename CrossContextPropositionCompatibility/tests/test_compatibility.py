import ast
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from CrossContextPropositionCompatibility.classification import (
    classify_cross_context_proposition_compatibility,
)
from CrossContextPropositionCompatibility.models import (
    CrossContextPropositionCompatibilityStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)


def make_production(role, **overrides):
    values = {
        "proposition_id": f"proposition-{role}",
        "finding_id": f"finding-{role}",
        "subject_id": "subject-001",
        "predicate_id": "predicate-001",
        "value": (
            Decimal("1.00")
            if role == "baseline"
            else Decimal("2.00")
        ),
        "unit_id": "USD",
        "effective_context_id": f"context-{role}",
    }
    values.update(overrides)
    return SemanticallyProducedNumericProposition(
        ExactObservedNumericProposition(**values)
    )


class CrossContextPropositionCompatibilityTests(
    unittest.TestCase
):
    def test_exact_enum_contract(self):
        self.assertEqual(
            list(
                CrossContextPropositionCompatibilityStatus
                .__members__
            ),
            [
                "SUBJECT_MISMATCH",
                "PREDICATE_MISMATCH",
                "UNIT_MISMATCH",
                "COMPATIBLE",
            ],
        )
        self.assertEqual(
            [
                status.value
                for status in
                CrossContextPropositionCompatibilityStatus
            ],
            [
                "subject_mismatch",
                "predicate_mismatch",
                "unit_mismatch",
                "compatible",
            ],
        )

    def test_different_contexts_are_compatible(self):
        self.assertIs(
            classify_cross_context_proposition_compatibility(
                make_production(
                    "baseline",
                    effective_context_id="context-earlier",
                ),
                make_production(
                    "current",
                    effective_context_id="context-later",
                ),
            ),
            CrossContextPropositionCompatibilityStatus.COMPATIBLE,
        )

    def test_same_context_is_not_rejected(self):
        self.assertIs(
            classify_cross_context_proposition_compatibility(
                make_production(
                    "baseline",
                    effective_context_id="same-context",
                ),
                make_production(
                    "current",
                    effective_context_id="same-context",
                ),
            ),
            CrossContextPropositionCompatibilityStatus.COMPATIBLE,
        )

    def test_mismatch_statuses_and_precedence(self):
        cases = (
            (
                {
                    "subject_id": "other-subject",
                    "predicate_id": "other-predicate",
                    "unit_id": "shares",
                },
                (
                    CrossContextPropositionCompatibilityStatus
                    .SUBJECT_MISMATCH
                ),
            ),
            (
                {
                    "predicate_id": "other-predicate",
                    "unit_id": "shares",
                },
                (
                    CrossContextPropositionCompatibilityStatus
                    .PREDICATE_MISMATCH
                ),
            ),
            (
                {"unit_id": "shares"},
                (
                    CrossContextPropositionCompatibilityStatus
                    .UNIT_MISMATCH
                ),
            ),
        )
        baseline = make_production("baseline")
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(
                    classify_cross_context_proposition_compatibility(
                        baseline,
                        make_production("current", **overrides),
                    ),
                    expected,
                )

    def test_identifiers_and_values_do_not_participate(self):
        baseline = make_production(
            "baseline",
            proposition_id="proposition-a",
            finding_id="finding-a",
            value=Decimal("-999.5"),
        )
        current = make_production(
            "current",
            proposition_id="proposition-b",
            finding_id="finding-b",
            value=Decimal("1000000.25"),
        )
        self.assertIs(
            classify_cross_context_proposition_compatibility(
                baseline,
                current,
            ),
            CrossContextPropositionCompatibilityStatus.COMPATIBLE,
        )

    def test_exact_stored_string_equality_without_normalization(self):
        cases = (
            (
                {"subject_id": "SUBJECT-001"},
                (
                    CrossContextPropositionCompatibilityStatus
                    .SUBJECT_MISMATCH
                ),
            ),
            (
                {"predicate_id": " predicate-001 "},
                (
                    CrossContextPropositionCompatibilityStatus
                    .PREDICATE_MISMATCH
                ),
            ),
            (
                {"unit_id": "usd"},
                (
                    CrossContextPropositionCompatibilityStatus
                    .UNIT_MISMATCH
                ),
            ),
            (
                {"subject_id": "e\u0301"},
                (
                    CrossContextPropositionCompatibilityStatus
                    .SUBJECT_MISMATCH
                ),
            ),
        )
        for overrides, expected in cases:
            baseline_overrides = (
                {"subject_id": "\u00e9"}
                if "subject_id" in overrides
                and overrides["subject_id"] == "e\u0301"
                else {}
            )
            with self.subTest(overrides=overrides):
                self.assertIs(
                    classify_cross_context_proposition_compatibility(
                        make_production(
                            "baseline",
                            **baseline_overrides,
                        ),
                        make_production("current", **overrides),
                    ),
                    expected,
                )

    def test_upstream_validation_order_and_identity(self):
        baseline = make_production("baseline")
        current = make_production("current")
        calls = []
        with patch(
            "CrossContextPropositionCompatibility"
            ".classification"
            ".validate_semantically_produced_numeric_proposition",
            side_effect=lambda value: calls.append(value),
        ) as validator:
            result = (
                classify_cross_context_proposition_compatibility(
                    baseline,
                    current,
                )
            )
        self.assertIs(
            result,
            CrossContextPropositionCompatibilityStatus.COMPATIBLE,
        )
        self.assertEqual(calls, [baseline, current])
        self.assertEqual(validator.call_count, 2)
        self.assertIs(validator.call_args_list[0].args[0], baseline)
        self.assertIs(validator.call_args_list[1].args[0], current)

    def test_baseline_failure_stops_current_validation(self):
        baseline = make_production("baseline")
        current = make_production("current")
        error = TypeError("baseline failure")
        calls = []

        def validate(value):
            calls.append(value)
            if value is baseline:
                raise error

        with patch(
            "CrossContextPropositionCompatibility"
            ".classification"
            ".validate_semantically_produced_numeric_proposition",
            side_effect=validate,
        ):
            with self.assertRaises(TypeError) as context:
                classify_cross_context_proposition_compatibility(
                    baseline,
                    current,
                )
        self.assertIs(context.exception, error)
        self.assertEqual(calls, [baseline])

    def test_current_failure_propagates_unchanged(self):
        baseline = make_production("baseline")
        current = make_production("current")
        error = ValueError("current failure")
        calls = []

        def validate(value):
            calls.append(value)
            if value is current:
                raise error

        with patch(
            "CrossContextPropositionCompatibility"
            ".classification"
            ".validate_semantically_produced_numeric_proposition",
            side_effect=validate,
        ):
            with self.assertRaises(ValueError) as context:
                classify_cross_context_proposition_compatibility(
                    baseline,
                    current,
                )
        self.assertIs(context.exception, error)
        self.assertEqual(calls, [baseline, current])

    def test_inputs_propositions_and_fields_are_preserved(self):
        subject_id = " subject-\u00e9 "
        predicate_id = " predicate-e\u0301 "
        unit_id = " USD "
        baseline = make_production(
            "baseline",
            subject_id=subject_id,
            predicate_id=predicate_id,
            unit_id=unit_id,
        )
        current = make_production(
            "current",
            subject_id=subject_id,
            predicate_id=predicate_id,
            unit_id=unit_id,
        )
        objects = (
            baseline,
            current,
            baseline.proposition,
            current.proposition,
        )
        object_ids = tuple(map(id, objects))

        self.assertIs(
            classify_cross_context_proposition_compatibility(
                baseline,
                current,
            ),
            CrossContextPropositionCompatibilityStatus.COMPATIBLE,
        )
        self.assertEqual(tuple(map(id, objects)), object_ids)
        self.assertIs(
            baseline.proposition.subject_id,
            subject_id,
        )
        self.assertIs(
            current.proposition.subject_id,
            subject_id,
        )
        self.assertIs(
            baseline.proposition.predicate_id,
            predicate_id,
        )
        self.assertIs(
            current.proposition.predicate_id,
            predicate_id,
        )
        self.assertIs(baseline.proposition.unit_id, unit_id)
        self.assertIs(current.proposition.unit_id, unit_id)

    def test_production_structure_and_dependency_direction(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        classification_tree = ast.parse(
            (root / "classification.py").read_text()
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(model_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"enum"},
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(classification_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "CrossContextPropositionCompatibility.models",
                "SemanticPropositionProduction.models",
                "SemanticPropositionProduction.validation",
            },
        )
        repository_root = root.parent
        for path in (
            repository_root / "SemanticPropositionProduction"
        ).glob("*.py"):
            self.assertNotIn(
                "CrossContextPropositionCompatibility",
                path.read_text(),
            )


if __name__ == "__main__":
    unittest.main()
