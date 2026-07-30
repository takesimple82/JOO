import ast
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)
from BaselineCurrentPropositionPairApplicability.models import (
    BaselineCurrentPropositionPairApplicabilityStatus,
)
from CrossContextPropositionCompatibility.models import (
    CrossContextPropositionCompatibilityStatus,
)
from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from ExactCrossContextNumericDeltaApplicability.classification import (
    classify_exact_cross_context_numeric_delta_applicability,
)
from ExactCrossContextNumericDeltaApplicability.models import (
    ExactCrossContextNumericDeltaApplicabilityStatus,
)
from SemanticPropositionProduction.models import (
    SemanticallyProducedNumericProposition,
)


def make_pair(**overrides):
    values = {
        "baseline_proposition_id": "proposition-baseline",
        "current_proposition_id": "proposition-current",
    }
    values.update(overrides)
    return ExplicitBaselineCurrentPropositionPair(**values)


def make_production(role, **overrides):
    values = {
        "proposition_id": f"proposition-{role}",
        "finding_id": f"finding-{role}",
        "subject_id": "subject-001",
        "predicate_id": "predicate-001",
        "value": (
            Decimal("-999")
            if role == "baseline"
            else Decimal("1000000")
        ),
        "unit_id": "USD",
        "effective_context_id": f"context-{role}",
    }
    values.update(overrides)
    return SemanticallyProducedNumericProposition(
        ExactObservedNumericProposition(**values)
    )


def make_context_date(role, **overrides):
    values = {
        "effective_context_id": f"context-{role}",
        "observed_on": (
            "2026-07-29"
            if role == "baseline"
            else "2026-07-30"
        ),
    }
    values.update(overrides)
    return ExplicitEffectiveContextObservedDate(**values)


def classify(**overrides):
    values = {
        "pair": make_pair(),
        "baseline": make_production("baseline"),
        "current": make_production("current"),
        "baseline_context_date": make_context_date("baseline"),
        "current_context_date": make_context_date("current"),
    }
    values.update(overrides)
    return classify_exact_cross_context_numeric_delta_applicability(
        values["pair"],
        values["baseline"],
        values["current"],
        values["baseline_context_date"],
        values["current_context_date"],
    )


class ExactCrossContextNumericDeltaApplicabilityTests(
    unittest.TestCase
):
    def test_exact_enum_contract(self):
        self.assertEqual(
            list(
                ExactCrossContextNumericDeltaApplicabilityStatus
                .__members__
            ),
            [
                "BASELINE_PROPOSITION_ENDPOINT_MISMATCH",
                "CURRENT_PROPOSITION_ENDPOINT_MISMATCH",
                "BASELINE_CONTEXT_ENDPOINT_MISMATCH",
                "CURRENT_CONTEXT_ENDPOINT_MISMATCH",
                "CONTEXT_DATE_CONFLICT",
                "SAME_DATE",
                "BASELINE_AFTER_CURRENT",
                "SUBJECT_MISMATCH",
                "PREDICATE_MISMATCH",
                "UNIT_MISMATCH",
                "CALCULABLE",
            ],
        )
        self.assertEqual(
            [
                status.value
                for status in
                ExactCrossContextNumericDeltaApplicabilityStatus
            ],
            [
                "baseline_proposition_endpoint_mismatch",
                "current_proposition_endpoint_mismatch",
                "baseline_context_endpoint_mismatch",
                "current_context_endpoint_mismatch",
                "context_date_conflict",
                "same_date",
                "baseline_after_current",
                "subject_mismatch",
                "predicate_mismatch",
                "unit_mismatch",
                "calculable",
            ],
        )

    def test_integrated_calculable(self):
        self.assertIs(
            classify(),
            (
                ExactCrossContextNumericDeltaApplicabilityStatus
                .CALCULABLE
            ),
        )

    def test_integrated_pair_and_temporal_statuses(self):
        cases = (
            (
                {
                    "pair": make_pair(
                        baseline_proposition_id="other"
                    )
                },
                "BASELINE_PROPOSITION_ENDPOINT_MISMATCH",
            ),
            (
                {
                    "pair": make_pair(
                        current_proposition_id="other"
                    )
                },
                "CURRENT_PROPOSITION_ENDPOINT_MISMATCH",
            ),
            (
                {
                    "baseline": make_production(
                        "baseline",
                        effective_context_id="other",
                    )
                },
                "BASELINE_CONTEXT_ENDPOINT_MISMATCH",
            ),
            (
                {
                    "current": make_production(
                        "current",
                        effective_context_id="other",
                    )
                },
                "CURRENT_CONTEXT_ENDPOINT_MISMATCH",
            ),
            (
                {
                    "current": make_production(
                        "current",
                        effective_context_id="context-baseline",
                    ),
                    "current_context_date": make_context_date(
                        "current",
                        effective_context_id="context-baseline",
                    ),
                },
                "CONTEXT_DATE_CONFLICT",
            ),
            (
                {
                    "current_context_date": make_context_date(
                        "current",
                        observed_on="2026-07-29",
                    )
                },
                "SAME_DATE",
            ),
            (
                {
                    "baseline_context_date": make_context_date(
                        "baseline",
                        observed_on="2026-07-31",
                    )
                },
                "BASELINE_AFTER_CURRENT",
            ),
        )
        for overrides, expected_name in cases:
            with self.subTest(expected=expected_name):
                self.assertIs(
                    classify(**overrides),
                    (
                        ExactCrossContextNumericDeltaApplicabilityStatus
                        .__members__[expected_name]
                    ),
                )

    def test_integrated_compatibility_statuses(self):
        cases = (
            ("subject_id", "other", "SUBJECT_MISMATCH"),
            ("predicate_id", "other", "PREDICATE_MISMATCH"),
            ("unit_id", "shares", "UNIT_MISMATCH"),
        )
        for field_name, value, expected_name in cases:
            with self.subTest(field=field_name):
                self.assertIs(
                    classify(
                        current=make_production(
                            "current",
                            **{field_name: value},
                        )
                    ),
                    (
                        ExactCrossContextNumericDeltaApplicabilityStatus
                        .__members__[expected_name]
                    ),
                )

    def test_validation_runs_once_in_exact_order(self):
        values = [
            make_pair(),
            make_production("baseline"),
            make_production("current"),
            make_context_date("baseline"),
            make_context_date("current"),
        ]
        calls = []
        with patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            ".validate_explicit_baseline_current_proposition_pair",
            side_effect=lambda value: calls.append(("pair", value)),
        ) as pair_validator, patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            ".validate_semantically_produced_numeric_proposition",
            side_effect=lambda value: calls.append(
                ("production", value)
            ),
        ) as production_validator, patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            ".validate_explicit_effective_context_observed_date",
            side_effect=lambda value: calls.append(
                ("context_date", value)
            ),
        ) as context_validator:
            result = (
                classify_exact_cross_context_numeric_delta_applicability(
                    *values
                )
            )

        self.assertIs(
            result,
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE,
        )
        self.assertEqual(
            calls,
            [
                ("pair", values[0]),
                ("production", values[1]),
                ("production", values[2]),
                ("context_date", values[3]),
                ("context_date", values[4]),
            ],
        )
        pair_validator.assert_called_once_with(values[0])
        self.assertEqual(production_validator.call_count, 2)
        self.assertEqual(context_validator.call_count, 2)

    def test_each_validation_failure_stops_later_work(self):
        values = [
            make_pair(),
            make_production("baseline"),
            make_production("current"),
            make_context_date("baseline"),
            make_context_date("current"),
        ]
        for failure_index in range(5):
            with self.subTest(failure_index=failure_index):
                error = ValueError(f"failure-{failure_index}")
                calls = []

                def validate(value):
                    calls.append(value)
                    if value is values[failure_index]:
                        raise error

                with patch(
                    "ExactCrossContextNumericDeltaApplicability"
                    ".classification"
                    ".validate_explicit_baseline_current_proposition_pair",
                    side_effect=validate,
                ), patch(
                    "ExactCrossContextNumericDeltaApplicability"
                    ".classification"
                    ".validate_semantically_produced_numeric_proposition",
                    side_effect=validate,
                ), patch(
                    "ExactCrossContextNumericDeltaApplicability"
                    ".classification"
                    ".validate_explicit_effective_context_observed_date",
                    side_effect=validate,
                ), patch(
                    "ExactCrossContextNumericDeltaApplicability"
                    ".classification"
                    "._classify_baseline_current_proposition_pair_applicability_unchecked",
                ) as pair_classifier:
                    with self.assertRaises(ValueError) as context:
                        classify_exact_cross_context_numeric_delta_applicability(
                            *values
                        )
                self.assertIs(context.exception, error)
                self.assertEqual(
                    calls,
                    values[: failure_index + 1],
                )
                pair_classifier.assert_not_called()

    def test_pair_helper_receives_original_actual_endpoints(self):
        pair = make_pair()
        baseline = make_production("baseline")
        current = make_production("current")
        baseline_date = make_context_date("baseline")
        current_date = make_context_date("current")
        with patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            "._classify_baseline_current_proposition_pair_applicability_unchecked",
            return_value=(
                BaselineCurrentPropositionPairApplicabilityStatus
                .APPLICABLE
            ),
        ) as pair_classifier:
            result = (
                classify_exact_cross_context_numeric_delta_applicability(
                    pair,
                    baseline,
                    current,
                    baseline_date,
                    current_date,
                )
            )

        self.assertIs(
            result,
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE,
        )
        args = pair_classifier.call_args.args
        self.assertIs(args[0], pair)
        self.assertIs(args[1], baseline.proposition)
        self.assertIs(args[2], current.proposition)
        self.assertIs(args[3], baseline_date)
        self.assertIs(args[4], current_date)
        self.assertTrue(callable(args[5]))

    def test_nonapplicable_pair_skips_compatibility(self):
        with patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            "._classify_baseline_current_proposition_pair_applicability_unchecked",
            return_value=(
                BaselineCurrentPropositionPairApplicabilityStatus
                .SAME_DATE
            ),
        ), patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            "._classify_cross_context_proposition_compatibility_unchecked",
        ) as compatibility_classifier:
            result = classify()
        self.assertIs(
            result,
            ExactCrossContextNumericDeltaApplicabilityStatus
            .SAME_DATE,
        )
        compatibility_classifier.assert_not_called()

    def test_compatible_pair_delegates_original_wrappers(self):
        baseline = make_production("baseline")
        current = make_production("current")
        with patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            "._classify_cross_context_proposition_compatibility_unchecked",
            return_value=(
                CrossContextPropositionCompatibilityStatus.COMPATIBLE
            ),
        ) as compatibility_classifier:
            result = classify(
                baseline=baseline,
                current=current,
            )
        self.assertIs(
            result,
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE,
        )
        compatibility_classifier.assert_called_once_with(
            baseline,
            current,
        )

    def test_values_are_not_compared_or_subtracted(self):
        self.assertIs(
            classify(
                baseline=make_production(
                    "baseline",
                    value=Decimal("1E+100"),
                ),
                current=make_production(
                    "current",
                    value=Decimal("-1E-100"),
                ),
            ),
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE,
        )

    def test_inputs_and_internal_field_objects_are_preserved(self):
        pair = make_pair()
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
        baseline_date = make_context_date("baseline")
        current_date = make_context_date("current")
        objects = (
            pair,
            baseline,
            current,
            baseline.proposition,
            current.proposition,
            baseline_date,
            current_date,
        )
        identities = tuple(map(id, objects))

        self.assertIs(
            classify_exact_cross_context_numeric_delta_applicability(
                pair,
                baseline,
                current,
                baseline_date,
                current_date,
            ),
            ExactCrossContextNumericDeltaApplicabilityStatus
            .CALCULABLE,
        )
        self.assertEqual(tuple(map(id, objects)), identities)
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

    def test_unsupported_delegated_statuses_raise(self):
        with patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            "._classify_baseline_current_proposition_pair_applicability_unchecked",
            return_value=object(),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "^unsupported baseline/current pair "
                "applicability status$",
            ):
                classify()

        with patch(
            "ExactCrossContextNumericDeltaApplicability"
            ".classification"
            "._classify_cross_context_proposition_compatibility_unchecked",
            return_value=object(),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "^unsupported cross-context compatibility status$",
            ):
                classify()

    def test_production_dependency_direction_and_no_arithmetic(self):
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
        imported_modules = {
            node.module
            for node in ast.walk(classification_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertNotIn("decimal", imported_modules)
        self.assertNotIn(
            "ExactDecimalArithmetic.arithmetic",
            imported_modules,
        )
        repository_root = root.parent
        for package_name in (
            "BaselineCurrentPropositionPair",
            "BaselineCurrentPropositionPairApplicability",
            "CrossContextPropositionCompatibility",
            "EffectiveContextObservedDate",
            "EffectiveContextTemporalOrdering",
            "EvidenceProposition",
            "SemanticPropositionProduction",
        ):
            for path in (
                repository_root / package_name
            ).glob("*.py"):
                self.assertNotIn(
                    "ExactCrossContextNumericDeltaApplicability",
                    path.read_text(),
                )


if __name__ == "__main__":
    unittest.main()
