import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

from PortfolioImpactInterpretationPolicy.classification import (
    classify_portfolio_impact_interpretation_policy_applicability,
)
from PortfolioImpactInterpretationPolicy.models import (
    PortfolioImpactDirection,
    PortfolioImpactInterpretationPolicy,
    PortfolioImpactInterpretationPolicyApplicabilityStatus,
)
from PortfolioImpactInterpretationPolicy.validation import (
    validate_portfolio_impact_interpretation_policy,
)


def make_policy(**overrides):
    values = {
        "policy_id": "policy-001",
        "policy_version": "version-001",
        "allowed_directions": (
            PortfolioImpactDirection.BENEFICIAL,
            PortfolioImpactDirection.NEUTRAL,
            PortfolioImpactDirection.ADVERSE,
        ),
        "allowed_horizon_ids": (
            "short-term",
            "long-term",
        ),
        "rationale_required": True,
    }
    values.update(overrides)
    return PortfolioImpactInterpretationPolicy(**values)


class StringSubclass(str):
    pass


class TupleSubclass(tuple):
    pass


class PolicySubclass(PortfolioImpactInterpretationPolicy):
    pass


class PortfolioImpactInterpretationPolicyTests(
    unittest.TestCase
):
    def test_exact_public_model_and_enum_contracts(self):
        model_fields = fields(
            PortfolioImpactInterpretationPolicy
        )
        self.assertEqual(
            [field.name for field in model_fields],
            [
                "policy_id",
                "policy_version",
                "allowed_directions",
                "allowed_horizon_ids",
                "rationale_required",
            ],
        )
        self.assertEqual(
            get_type_hints(
                PortfolioImpactInterpretationPolicy
            ),
            {
                "policy_id": str,
                "policy_version": str,
                "allowed_directions": tuple[
                    PortfolioImpactDirection,
                    ...,
                ],
                "allowed_horizon_ids": tuple[str, ...],
                "rationale_required": bool,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__slots__",
            PortfolioImpactInterpretationPolicy.__dict__,
        )
        self.assertEqual(
            [
                direction.value
                for direction in PortfolioImpactDirection
            ],
            ["beneficial", "neutral", "adverse"],
        )
        self.assertEqual(
            [
                status.value
                for status in
                PortfolioImpactInterpretationPolicyApplicabilityStatus
            ],
            [
                "applicable",
                "direction_not_allowed",
                "horizon_not_allowed",
                "rationale_required",
            ],
        )

    def test_policy_is_frozen_hashable_and_structural(self):
        first = make_policy()
        same = make_policy()
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        with self.assertRaises(FrozenInstanceError):
            first.policy_id = "replacement"

    def test_exact_policy_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "^policy must be "
            "PortfolioImpactInterpretationPolicy$",
        ):
            validate_portfolio_impact_interpretation_policy(
                PolicySubclass(
                    "policy",
                    "version",
                    (PortfolioImpactDirection.NEUTRAL,),
                    ("horizon",),
                    False,
                )
            )

    def test_policy_identity_fields_and_order(self):
        cases = (
            (
                make_policy(policy_id=None),
                TypeError,
                "policy_id must be str",
            ),
            (
                make_policy(policy_id=" "),
                ValueError,
                "policy_id must not be blank",
            ),
            (
                make_policy(policy_version=None),
                TypeError,
                "policy_version must be str",
            ),
            (
                make_policy(policy_version=" "),
                ValueError,
                "policy_version must not be blank",
            ),
            (
                make_policy(
                    policy_id=StringSubclass("policy")
                ),
                TypeError,
                "policy_id must be str",
            ),
            (
                make_policy(
                    policy_version=StringSubclass("version")
                ),
                TypeError,
                "policy_version must be str",
            ),
        )
        for policy, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_portfolio_impact_interpretation_policy(
                        policy
                    )

    def test_allowed_directions_collection_contract(self):
        invalid_collections = (
            None,
            [],
            set(),
            (item for item in ()),
            TupleSubclass(
                (PortfolioImpactDirection.NEUTRAL,)
            ),
        )
        for value in invalid_collections:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^allowed_directions must be tuple$",
                ):
                    validate_portfolio_impact_interpretation_policy(
                        make_policy(allowed_directions=value)
                    )
        with self.assertRaisesRegex(
            ValueError,
            "^allowed_directions must not be empty$",
        ):
            validate_portfolio_impact_interpretation_policy(
                make_policy(allowed_directions=())
            )

    def test_allowed_directions_elements_and_duplicates(self):
        invalid = (
            None,
            "beneficial",
            1,
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^allowed_directions must contain only "
                    "PortfolioImpactDirection$",
                ):
                    validate_portfolio_impact_interpretation_policy(
                        make_policy(
                            allowed_directions=(
                                PortfolioImpactDirection.NEUTRAL,
                                value,
                            )
                        )
                    )
        with self.assertRaisesRegex(
            ValueError,
            "^allowed_directions must not contain duplicates$",
        ):
            validate_portfolio_impact_interpretation_policy(
                make_policy(
                    allowed_directions=(
                        PortfolioImpactDirection.ADVERSE,
                        PortfolioImpactDirection.ADVERSE,
                    )
                )
            )

    def test_allowed_horizons_collection_contract(self):
        invalid_collections = (
            None,
            [],
            set(),
            (item for item in ()),
            TupleSubclass(("horizon",)),
        )
        for value in invalid_collections:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^allowed_horizon_ids must be tuple$",
                ):
                    validate_portfolio_impact_interpretation_policy(
                        make_policy(allowed_horizon_ids=value)
                    )
        with self.assertRaisesRegex(
            ValueError,
            "^allowed_horizon_ids must not be empty$",
        ):
            validate_portfolio_impact_interpretation_policy(
                make_policy(allowed_horizon_ids=())
            )

    def test_allowed_horizon_elements_and_duplicates(self):
        for value in (None, 1, StringSubclass("horizon")):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^allowed_horizon_ids must contain only str$",
                ):
                    validate_portfolio_impact_interpretation_policy(
                        make_policy(
                            allowed_horizon_ids=("valid", value)
                        )
                    )
        for value in ("", " ", "\t", "\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^allowed_horizon_ids must not contain "
                    "blank values$",
                ):
                    validate_portfolio_impact_interpretation_policy(
                        make_policy(
                            allowed_horizon_ids=("valid", value)
                        )
                    )
        with self.assertRaisesRegex(
            ValueError,
            "^allowed_horizon_ids must not contain duplicates$",
        ):
            validate_portfolio_impact_interpretation_policy(
                make_policy(
                    allowed_horizon_ids=(
                        "horizon",
                        "horizon",
                    )
                )
            )

    def test_rationale_required_requires_exact_bool(self):
        for value in (None, 0, 1, "true"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^rationale_required must be bool$",
                ):
                    validate_portfolio_impact_interpretation_policy(
                        make_policy(rationale_required=value)
                    )

    def test_validation_stops_at_first_invalid_field(self):
        policy = make_policy(
            policy_id=None,
            policy_version=None,
            allowed_directions=None,
            allowed_horizon_ids=None,
            rationale_required=None,
        )
        with self.assertRaisesRegex(
            TypeError,
            "^policy_id must be str$",
        ):
            validate_portfolio_impact_interpretation_policy(
                policy
            )

    def test_success_preserves_objects_and_order(self):
        policy_id = " policy-\u00e9 "
        policy_version = " version-e\u0301 "
        directions = (
            PortfolioImpactDirection.ADVERSE,
            PortfolioImpactDirection.BENEFICIAL,
        )
        horizon_a = " horizon-\u00e9 "
        horizon_b = " horizon-e\u0301 "
        horizons = (horizon_a, horizon_b)
        policy = PortfolioImpactInterpretationPolicy(
            policy_id,
            policy_version,
            directions,
            horizons,
            False,
        )
        self.assertIsNone(
            validate_portfolio_impact_interpretation_policy(
                policy
            )
        )
        self.assertIs(policy.policy_id, policy_id)
        self.assertIs(policy.policy_version, policy_version)
        self.assertIs(policy.allowed_directions, directions)
        self.assertIs(policy.allowed_horizon_ids, horizons)
        self.assertIs(
            policy.allowed_horizon_ids[0],
            horizon_a,
        )
        self.assertIs(
            policy.allowed_horizon_ids[1],
            horizon_b,
        )

    def test_classifier_input_validation(self):
        valid_policy = make_policy()
        cases = (
            (
                None,
                "short-term",
                "rationale",
                TypeError,
                "direction must be PortfolioImpactDirection",
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                None,
                "rationale",
                TypeError,
                "horizon_id must be str",
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                " ",
                "rationale",
                ValueError,
                "horizon_id must not be blank",
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                "short-term",
                None,
                TypeError,
                "rationale must be str",
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                StringSubclass("short-term"),
                "rationale",
                TypeError,
                "horizon_id must be str",
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                "short-term",
                StringSubclass("rationale"),
                TypeError,
                "rationale must be str",
            ),
        )
        for (
            direction,
            horizon,
            rationale,
            error_type,
            message,
        ) in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    classify_portfolio_impact_interpretation_policy_applicability(
                        valid_policy,
                        direction,
                        horizon,
                        rationale,
                    )

    def test_classifier_precedence(self):
        policy = make_policy(
            allowed_directions=(
                PortfolioImpactDirection.NEUTRAL,
            ),
            allowed_horizon_ids=("allowed",),
            rationale_required=True,
        )
        cases = (
            (
                PortfolioImpactDirection.ADVERSE,
                "other",
                "",
                PortfolioImpactInterpretationPolicyApplicabilityStatus
                .DIRECTION_NOT_ALLOWED,
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                "other",
                "",
                PortfolioImpactInterpretationPolicyApplicabilityStatus
                .HORIZON_NOT_ALLOWED,
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                "allowed",
                " \t ",
                PortfolioImpactInterpretationPolicyApplicabilityStatus
                .RATIONALE_REQUIRED,
            ),
            (
                PortfolioImpactDirection.NEUTRAL,
                "allowed",
                "rationale",
                PortfolioImpactInterpretationPolicyApplicabilityStatus
                .APPLICABLE,
            ),
        )
        for direction, horizon, rationale, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(
                    classify_portfolio_impact_interpretation_policy_applicability(
                        policy,
                        direction,
                        horizon,
                        rationale,
                    ),
                    expected,
                )

    def test_blank_rationale_allowed_when_not_required(self):
        policy = make_policy(rationale_required=False)
        for rationale in ("", " ", "\t", "\n"):
            with self.subTest(rationale=repr(rationale)):
                self.assertIs(
                    classify_portfolio_impact_interpretation_policy_applicability(
                        policy,
                        PortfolioImpactDirection.NEUTRAL,
                        "short-term",
                        rationale,
                    ),
                    PortfolioImpactInterpretationPolicyApplicabilityStatus
                    .APPLICABLE,
                )

    def test_policy_validation_once_and_exception_identity(self):
        policy = make_policy()
        with patch(
            "PortfolioImpactInterpretationPolicy.classification"
            ".validate_portfolio_impact_interpretation_policy",
        ) as validator:
            result = (
                classify_portfolio_impact_interpretation_policy_applicability(
                    policy,
                    PortfolioImpactDirection.NEUTRAL,
                    "short-term",
                    "rationale",
                )
            )
        self.assertIs(
            result,
            PortfolioImpactInterpretationPolicyApplicabilityStatus
            .APPLICABLE,
        )
        validator.assert_called_once_with(policy)

        error = ValueError("policy failure")
        with patch(
            "PortfolioImpactInterpretationPolicy.classification"
            ".validate_portfolio_impact_interpretation_policy",
            side_effect=error,
        ):
            with self.assertRaises(ValueError) as context:
                classify_portfolio_impact_interpretation_policy_applicability(
                    policy,
                    PortfolioImpactDirection.NEUTRAL,
                    "short-term",
                    "rationale",
                )
        self.assertIs(context.exception, error)

    def test_production_surface_and_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        trees = {
            path.name: ast.parse(path.read_text())
            for path in (
                root / "models.py",
                root / "validation.py",
                root / "classification.py",
            )
        }
        self.assertEqual(
            {
                node.module
                for tree in trees.values()
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            },
            {
                "dataclasses",
                "enum",
                "PortfolioImpactInterpretationPolicy.models",
                "PortfolioImpactInterpretationPolicy.validation",
            },
        )


if __name__ == "__main__":
    unittest.main()
