import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EffectiveContextTemporalOrdering.classification import (
    classify_effective_context_temporal_ordering,
)
from EffectiveContextTemporalOrdering.models import (
    EffectiveContextTemporalOrderingStatus,
)


def make_context_date(
    **overrides,
) -> ExplicitEffectiveContextObservedDate:
    values = {
        "effective_context_id": "context-001",
        "observed_on": "2026-07-30",
    }
    values.update(overrides)
    return ExplicitEffectiveContextObservedDate(**values)


class EffectiveContextTemporalOrderingTests(
    unittest.TestCase
):
    def test_exact_enum_contract(self):
        self.assertEqual(
            EffectiveContextTemporalOrderingStatus.__members__,
            {
                "CONTEXT_DATE_CONFLICT": (
                    EffectiveContextTemporalOrderingStatus
                    .CONTEXT_DATE_CONFLICT
                ),
                "BEFORE": (
                    EffectiveContextTemporalOrderingStatus.BEFORE
                ),
                "SAME_DATE": (
                    EffectiveContextTemporalOrderingStatus
                    .SAME_DATE
                ),
                "AFTER": (
                    EffectiveContextTemporalOrderingStatus.AFTER
                ),
            },
        )
        self.assertEqual(
            [
                status.value
                for status in
                EffectiveContextTemporalOrderingStatus
            ],
            [
                "context_date_conflict",
                "before",
                "same_date",
                "after",
            ],
        )

    def test_same_context_with_different_dates_is_conflict(self):
        cases = (
            ("2026-07-29", "2026-07-30"),
            ("2026-07-30", "2026-07-29"),
        )

        for left_date, right_date in cases:
            with self.subTest(
                left_date=left_date,
                right_date=right_date,
            ):
                self.assertIs(
                    classify_effective_context_temporal_ordering(
                        make_context_date(
                            observed_on=left_date
                        ),
                        make_context_date(
                            observed_on=right_date
                        ),
                    ),
                    (
                        EffectiveContextTemporalOrderingStatus
                        .CONTEXT_DATE_CONFLICT
                    ),
                )

    def test_left_date_before_right_date(self):
        self.assertIs(
            classify_effective_context_temporal_ordering(
                make_context_date(observed_on="2026-07-29"),
                make_context_date(
                    effective_context_id="context-002",
                    observed_on="2026-07-30",
                ),
            ),
            EffectiveContextTemporalOrderingStatus.BEFORE,
        )

    def test_same_context_and_date_is_same_date(self):
        context_date = make_context_date()

        self.assertIs(
            classify_effective_context_temporal_ordering(
                context_date,
                context_date,
            ),
            EffectiveContextTemporalOrderingStatus.SAME_DATE,
        )

    def test_different_contexts_with_same_date_are_same_date(self):
        self.assertIs(
            classify_effective_context_temporal_ordering(
                make_context_date(
                    effective_context_id="context-001"
                ),
                make_context_date(
                    effective_context_id="context-002"
                ),
            ),
            EffectiveContextTemporalOrderingStatus.SAME_DATE,
        )

    def test_left_date_after_right_date(self):
        self.assertIs(
            classify_effective_context_temporal_ordering(
                make_context_date(observed_on="2026-07-31"),
                make_context_date(
                    effective_context_id="context-002",
                    observed_on="2026-07-30",
                ),
            ),
            EffectiveContextTemporalOrderingStatus.AFTER,
        )

    def test_argument_order_reverses_before_and_after(self):
        earlier = make_context_date(
            effective_context_id="earlier",
            observed_on="2026-07-29",
        )
        later = make_context_date(
            effective_context_id="later",
            observed_on="2026-07-30",
        )

        self.assertIs(
            classify_effective_context_temporal_ordering(
                earlier,
                later,
            ),
            EffectiveContextTemporalOrderingStatus.BEFORE,
        )
        self.assertIs(
            classify_effective_context_temporal_ordering(
                later,
                earlier,
            ),
            EffectiveContextTemporalOrderingStatus.AFTER,
        )

    def test_context_ids_are_compared_exactly_without_ordering(self):
        cases = (
            ("context", "CONTEXT"),
            ("context", " context "),
            ("\u00e9", "e\u0301"),
        )

        for left_id, right_id in cases:
            with self.subTest(
                left_id=repr(left_id),
                right_id=repr(right_id),
            ):
                self.assertIs(
                    classify_effective_context_temporal_ordering(
                        make_context_date(
                            effective_context_id=left_id,
                            observed_on="2026-07-29",
                        ),
                        make_context_date(
                            effective_context_id=right_id,
                            observed_on="2026-07-30",
                        ),
                    ),
                    EffectiveContextTemporalOrderingStatus.BEFORE,
                )

    def test_upstream_validators_run_once_left_then_right(self):
        left = make_context_date(
            effective_context_id="left",
            observed_on="2026-07-29",
        )
        right = make_context_date(
            effective_context_id="right",
            observed_on="2026-07-30",
        )
        calls = []

        with patch(
            "EffectiveContextTemporalOrdering"
            ".classification"
            ".validate_explicit_effective_context_observed_date",
            side_effect=lambda value: calls.append(value),
        ) as validator:
            result = classify_effective_context_temporal_ordering(
                left,
                right,
            )

        self.assertIs(
            result,
            EffectiveContextTemporalOrderingStatus.BEFORE,
        )
        self.assertEqual(calls, [left, right])
        self.assertEqual(validator.call_count, 2)
        self.assertIs(validator.call_args_list[0].args[0], left)
        self.assertIs(validator.call_args_list[1].args[0], right)

    def test_left_failure_stops_before_right_validation(self):
        left = make_context_date()
        right = make_context_date(
            effective_context_id="right"
        )
        error = TypeError("left failure")
        calls = []

        def validate(value):
            calls.append(value)
            if value is left:
                raise error

        with patch(
            "EffectiveContextTemporalOrdering"
            ".classification"
            ".validate_explicit_effective_context_observed_date",
            side_effect=validate,
        ):
            with self.assertRaises(TypeError) as context:
                classify_effective_context_temporal_ordering(
                    left,
                    right,
                )

        self.assertIs(context.exception, error)
        self.assertEqual(calls, [left])

    def test_right_failure_propagates_after_left_validation(self):
        left = make_context_date()
        right = make_context_date(
            effective_context_id="right"
        )
        error = ValueError("right failure")
        calls = []

        def validate(value):
            calls.append(value)
            if value is right:
                raise error

        with patch(
            "EffectiveContextTemporalOrdering"
            ".classification"
            ".validate_explicit_effective_context_observed_date",
            side_effect=validate,
        ):
            with self.assertRaises(ValueError) as context:
                classify_effective_context_temporal_ordering(
                    left,
                    right,
                )

        self.assertIs(context.exception, error)
        self.assertEqual(calls, [left, right])

    def test_inputs_and_field_objects_are_preserved(self):
        left_id = " left-\u00e9 "
        right_id = " right-e\u0301 "
        left_date = "2026-07-29"
        right_date = "2026-07-30"
        left = ExplicitEffectiveContextObservedDate(
            left_id,
            left_date,
        )
        right = ExplicitEffectiveContextObservedDate(
            right_id,
            right_date,
        )
        input_ids = (id(left), id(right))

        result = classify_effective_context_temporal_ordering(
            left,
            right,
        )

        self.assertIs(
            result,
            EffectiveContextTemporalOrderingStatus.BEFORE,
        )
        self.assertEqual((id(left), id(right)), input_ids)
        self.assertIs(left.effective_context_id, left_id)
        self.assertIs(right.effective_context_id, right_id)
        self.assertIs(left.observed_on, left_date)
        self.assertIs(right.observed_on, right_date)

    def test_production_structure_and_dependency_direction(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        classification_tree = ast.parse(
            (root / "classification.py").read_text()
        )

        model_imports = [
            node
            for node in ast.walk(model_tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        self.assertEqual(len(model_imports), 1)
        self.assertEqual(model_imports[0].module, "enum")

        imported_modules = {
            node.module
            for node in ast.walk(classification_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "EffectiveContextObservedDate.models",
                "EffectiveContextObservedDate.validation",
                "EffectiveContextTemporalOrdering.models",
            },
        )

        functions = [
            node
            for node in classification_tree.body
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
        ]
        self.assertEqual(
            [function.name for function in functions],
            ["classify_effective_context_temporal_ordering"],
        )
        self.assertFalse(
            any(
                isinstance(node, (ast.For, ast.While))
                for node in ast.walk(classification_tree)
            )
        )

        repository_root = root.parent
        for path in (
            repository_root / "EffectiveContextObservedDate"
        ).glob("*.py"):
            self.assertNotIn(
                "EffectiveContextTemporalOrdering",
                path.read_text(),
            )


if __name__ == "__main__":
    unittest.main()
