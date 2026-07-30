import ast
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from BaselineCurrentPropositionPair.models import (
    ExplicitBaselineCurrentPropositionPair,
)
from BaselineCurrentPropositionPairApplicability.classification import (
    classify_baseline_current_proposition_pair_applicability,
)
from BaselineCurrentPropositionPairApplicability.models import (
    BaselineCurrentPropositionPairApplicabilityStatus,
)
from EffectiveContextObservedDate.models import (
    ExplicitEffectiveContextObservedDate,
)
from EffectiveContextTemporalOrdering.models import (
    EffectiveContextTemporalOrderingStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)


def make_pair(**overrides):
    values = {
        "baseline_proposition_id": "proposition-baseline",
        "current_proposition_id": "proposition-current",
    }
    values.update(overrides)
    return ExplicitBaselineCurrentPropositionPair(**values)


def make_proposition(role, **overrides):
    values = {
        "proposition_id": f"proposition-{role}",
        "finding_id": f"finding-{role}",
        "subject_id": "subject-001",
        "predicate_id": "predicate-001",
        "value": Decimal("1.00"),
        "unit_id": "USD",
        "effective_context_id": f"context-{role}",
    }
    values.update(overrides)
    return ExactObservedNumericProposition(**values)


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
        "baseline": make_proposition("baseline"),
        "current": make_proposition("current"),
        "baseline_context_date": make_context_date("baseline"),
        "current_context_date": make_context_date("current"),
    }
    values.update(overrides)
    return classify_baseline_current_proposition_pair_applicability(
        values["pair"],
        values["baseline"],
        values["current"],
        values["baseline_context_date"],
        values["current_context_date"],
    )


class BaselineCurrentPropositionPairApplicabilityTests(
    unittest.TestCase
):
    def test_exact_enum_contract(self):
        expected_names = [
            "BASELINE_PROPOSITION_ENDPOINT_MISMATCH",
            "CURRENT_PROPOSITION_ENDPOINT_MISMATCH",
            "BASELINE_CONTEXT_ENDPOINT_MISMATCH",
            "CURRENT_CONTEXT_ENDPOINT_MISMATCH",
            "CONTEXT_DATE_CONFLICT",
            "SAME_DATE",
            "BASELINE_AFTER_CURRENT",
            "APPLICABLE",
        ]
        self.assertEqual(
            list(
                BaselineCurrentPropositionPairApplicabilityStatus
                .__members__
            ),
            expected_names,
        )
        self.assertEqual(
            [
                status.value
                for status in
                BaselineCurrentPropositionPairApplicabilityStatus
            ],
            [
                "baseline_proposition_endpoint_mismatch",
                "current_proposition_endpoint_mismatch",
                "baseline_context_endpoint_mismatch",
                "current_context_endpoint_mismatch",
                "context_date_conflict",
                "same_date",
                "baseline_after_current",
                "applicable",
            ],
        )

    def test_before_is_applicable(self):
        self.assertIs(
            classify(),
            BaselineCurrentPropositionPairApplicabilityStatus.APPLICABLE,
        )

    def test_endpoint_statuses_and_precedence(self):
        cases = (
            (
                {
                    "pair": make_pair(
                        baseline_proposition_id="other-baseline",
                        current_proposition_id="other-current",
                    ),
                    "baseline": make_proposition(
                        "baseline",
                        effective_context_id="other-context",
                    ),
                    "current": make_proposition(
                        "current",
                        effective_context_id="other-context",
                    ),
                },
                BaselineCurrentPropositionPairApplicabilityStatus
                .BASELINE_PROPOSITION_ENDPOINT_MISMATCH,
            ),
            (
                {
                    "pair": make_pair(
                        current_proposition_id="other-current"
                    ),
                    "baseline": make_proposition(
                        "baseline",
                        effective_context_id="other-context",
                    ),
                },
                BaselineCurrentPropositionPairApplicabilityStatus
                .CURRENT_PROPOSITION_ENDPOINT_MISMATCH,
            ),
            (
                {
                    "baseline": make_proposition(
                        "baseline",
                        effective_context_id="other-context",
                    ),
                    "current": make_proposition(
                        "current",
                        effective_context_id="other-context",
                    ),
                },
                BaselineCurrentPropositionPairApplicabilityStatus
                .BASELINE_CONTEXT_ENDPOINT_MISMATCH,
            ),
            (
                {
                    "current": make_proposition(
                        "current",
                        effective_context_id="other-context",
                    ),
                },
                BaselineCurrentPropositionPairApplicabilityStatus
                .CURRENT_CONTEXT_ENDPOINT_MISMATCH,
            ),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(classify(**overrides), expected)

    def test_temporal_status_mapping(self):
        cases = (
            (
                EffectiveContextTemporalOrderingStatus.BEFORE,
                BaselineCurrentPropositionPairApplicabilityStatus
                .APPLICABLE,
            ),
            (
                EffectiveContextTemporalOrderingStatus.SAME_DATE,
                BaselineCurrentPropositionPairApplicabilityStatus
                .SAME_DATE,
            ),
            (
                EffectiveContextTemporalOrderingStatus.AFTER,
                BaselineCurrentPropositionPairApplicabilityStatus
                .BASELINE_AFTER_CURRENT,
            ),
            (
                (
                    EffectiveContextTemporalOrderingStatus
                    .CONTEXT_DATE_CONFLICT
                ),
                (
                    BaselineCurrentPropositionPairApplicabilityStatus
                    .CONTEXT_DATE_CONFLICT
                ),
            ),
        )
        for temporal, expected in cases:
            with self.subTest(temporal=temporal):
                with patch(
                    "BaselineCurrentPropositionPairApplicability"
                    ".classification"
                    ".classify_effective_context_temporal_ordering",
                    return_value=temporal,
                ):
                    self.assertIs(classify(), expected)

    def test_integrated_same_and_conflicting_context_dates(self):
        cases = (
            (
                make_context_date(
                    "current",
                    effective_context_id="context-baseline",
                    observed_on="2026-07-29",
                ),
                make_proposition(
                    "current",
                    effective_context_id="context-baseline",
                ),
                BaselineCurrentPropositionPairApplicabilityStatus
                .SAME_DATE,
            ),
            (
                make_context_date(
                    "current",
                    effective_context_id="context-baseline",
                ),
                make_proposition(
                    "current",
                    effective_context_id="context-baseline",
                ),
                BaselineCurrentPropositionPairApplicabilityStatus
                .CONTEXT_DATE_CONFLICT,
            ),
            (
                make_context_date(
                    "current",
                    observed_on="2026-07-29",
                ),
                make_proposition("current"),
                BaselineCurrentPropositionPairApplicabilityStatus
                .SAME_DATE,
            ),
        )
        for current_date, current, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(
                    classify(
                        current=current,
                        current_context_date=current_date,
                    ),
                    expected,
                )

    def test_validation_order_and_identity(self):
        values = [
            make_pair(),
            make_proposition("baseline"),
            make_proposition("current"),
            make_context_date("baseline"),
            make_context_date("current"),
        ]
        calls = []
        with patch(
            "BaselineCurrentPropositionPairApplicability"
            ".classification"
            ".validate_explicit_baseline_current_proposition_pair",
            side_effect=lambda value: calls.append(("pair", value)),
        ), patch(
            "BaselineCurrentPropositionPairApplicability"
            ".classification"
            ".validate_exact_observed_numeric_proposition",
            side_effect=lambda value: calls.append(
                ("proposition", value)
            ),
        ), patch(
            "BaselineCurrentPropositionPairApplicability"
            ".classification"
            ".validate_explicit_effective_context_observed_date",
            side_effect=lambda value: calls.append(
                ("context_date", value)
            ),
        ):
            result = (
                classify_baseline_current_proposition_pair_applicability(
                    *values
                )
            )
        self.assertIs(
            result,
            BaselineCurrentPropositionPairApplicabilityStatus.APPLICABLE,
        )
        self.assertEqual(
            calls,
            [
                ("pair", values[0]),
                ("proposition", values[1]),
                ("proposition", values[2]),
                ("context_date", values[3]),
                ("context_date", values[4]),
            ],
        )

    def test_each_validation_failure_stops_later_work(self):
        values = [
            make_pair(),
            make_proposition("baseline"),
            make_proposition("current"),
            make_context_date("baseline"),
            make_context_date("current"),
        ]
        for failure_index in range(5):
            with self.subTest(failure_index=failure_index):
                error = ValueError(f"failure-{failure_index}")
                calls = []

                def record(value):
                    calls.append(value)
                    if value is values[failure_index]:
                        raise error

                with patch(
                    "BaselineCurrentPropositionPairApplicability"
                    ".classification"
                    ".validate_explicit_baseline_current_proposition_pair",
                    side_effect=record,
                ), patch(
                    "BaselineCurrentPropositionPairApplicability"
                    ".classification"
                    ".validate_exact_observed_numeric_proposition",
                    side_effect=record,
                ), patch(
                    "BaselineCurrentPropositionPairApplicability"
                    ".classification"
                    ".validate_explicit_effective_context_observed_date",
                    side_effect=record,
                ), patch(
                    "BaselineCurrentPropositionPairApplicability"
                    ".classification"
                    ".classify_effective_context_temporal_ordering",
                ) as temporal_classifier:
                    with self.assertRaises(ValueError) as context:
                        classify_baseline_current_proposition_pair_applicability(
                            *values
                        )
                self.assertIs(context.exception, error)
                self.assertEqual(
                    calls,
                    values[: failure_index + 1],
                )
                temporal_classifier.assert_not_called()

    def test_endpoint_mismatch_skips_temporal_classifier(self):
        with patch(
            "BaselineCurrentPropositionPairApplicability"
            ".classification"
            ".classify_effective_context_temporal_ordering",
        ) as temporal_classifier:
            result = classify(
                pair=make_pair(
                    baseline_proposition_id="other"
                )
            )
        self.assertIs(
            result,
            BaselineCurrentPropositionPairApplicabilityStatus
            .BASELINE_PROPOSITION_ENDPOINT_MISMATCH,
        )
        temporal_classifier.assert_not_called()

    def test_temporal_classifier_receives_original_associations(self):
        baseline_date = make_context_date("baseline")
        current_date = make_context_date("current")
        with patch(
            "BaselineCurrentPropositionPairApplicability"
            ".classification"
            ".classify_effective_context_temporal_ordering",
            return_value=EffectiveContextTemporalOrderingStatus.BEFORE,
        ) as temporal_classifier:
            result = classify(
                baseline_context_date=baseline_date,
                current_context_date=current_date,
            )
        self.assertIs(
            result,
            BaselineCurrentPropositionPairApplicabilityStatus.APPLICABLE,
        )
        temporal_classifier.assert_called_once_with(
            baseline_date,
            current_date,
        )

    def test_values_units_inputs_and_fields_are_preserved(self):
        baseline_id = " proposition-\u00e9 "
        current_id = " proposition-e\u0301 "
        baseline_context_id = " context-\u00e9 "
        current_context_id = " context-e\u0301 "
        pair = make_pair(
            baseline_proposition_id=baseline_id,
            current_proposition_id=current_id,
        )
        baseline = make_proposition(
            "baseline",
            proposition_id=baseline_id,
            effective_context_id=baseline_context_id,
            value=Decimal("1"),
            unit_id="USD",
        )
        current = make_proposition(
            "current",
            proposition_id=current_id,
            effective_context_id=current_context_id,
            value=Decimal("999"),
            unit_id="shares",
        )
        baseline_date = make_context_date(
            "baseline",
            effective_context_id=baseline_context_id,
        )
        current_date = make_context_date(
            "current",
            effective_context_id=current_context_id,
        )
        objects = (
            pair,
            baseline,
            current,
            baseline_date,
            current_date,
        )
        object_ids = tuple(map(id, objects))

        self.assertIs(
            classify_baseline_current_proposition_pair_applicability(
                *objects
            ),
            BaselineCurrentPropositionPairApplicabilityStatus.APPLICABLE,
        )
        self.assertEqual(tuple(map(id, objects)), object_ids)
        self.assertIs(pair.baseline_proposition_id, baseline_id)
        self.assertIs(pair.current_proposition_id, current_id)
        self.assertIs(
            baseline.effective_context_id,
            baseline_context_id,
        )
        self.assertIs(
            current.effective_context_id,
            current_context_id,
        )
        self.assertEqual(baseline.value, Decimal("1"))
        self.assertEqual(current.value, Decimal("999"))
        self.assertEqual(baseline.unit_id, "USD")
        self.assertEqual(current.unit_id, "shares")

    def test_production_structure_and_dependency_direction(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse((root / "models.py").read_text())
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
                "BaselineCurrentPropositionPair.models",
                "BaselineCurrentPropositionPair.validation",
                (
                    "BaselineCurrentPropositionPairApplicability"
                    ".models"
                ),
                "EffectiveContextObservedDate.models",
                "EffectiveContextObservedDate.validation",
                "EffectiveContextTemporalOrdering.classification",
                "EffectiveContextTemporalOrdering.models",
                "EvidenceProposition.models",
                "EvidenceProposition.validation",
            },
        )
        repository_root = root.parent
        for package_name in (
            "BaselineCurrentPropositionPair",
            "EffectiveContextObservedDate",
            "EffectiveContextTemporalOrdering",
            "EvidenceProposition",
        ):
            for path in (
                repository_root / package_name
            ).glob("*.py"):
                self.assertNotIn(
                    "BaselineCurrentPropositionPairApplicability",
                    path.read_text(),
                )


if __name__ == "__main__":
    unittest.main()
