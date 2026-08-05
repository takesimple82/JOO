import ast
import inspect
import unittest
import unicodedata
from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, patch

from PortfolioAllocationLeg.models import ExplicitPortfolioAllocationLeg
from PortfolioAllocationLegCapitalBucketLink.models import (
    ExplicitPortfolioAllocationLegCapitalBucketLink,
)
from PortfolioAllocationLegCapitalBucketLinkApplicability.classification import (
    classify_portfolio_allocation_leg_capital_bucket_link_applicability,
)
from PortfolioAllocationLegCapitalBucketLinkApplicability.models import (
    PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus,
)
from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)
from PortfolioCapitalBucket.models import ExplicitPortfolioCapitalBucket
from PortfolioMembership.models import ExplicitPortfolioMembership
from PortfolioPosition.models import ExplicitPortfolioPosition


Status = PortfolioAllocationLegCapitalBucketLinkApplicabilityStatus


def make_set(**overrides):
    leg_id = overrides.get("leg_id", "leg-001")
    bucket_id = overrides.get("bucket_id", "bucket-001")
    position_id = overrides.get("position_id", "position-001")
    portfolio_id = overrides.get("portfolio_id", "portfolio-001")
    proposal_link = overrides.get(
        "proposal_link",
        ExplicitPortfolioAllocationProposalPositionLink(
            "proposal-001",
            overrides.get("leg_position_id", position_id),
        ),
    )
    membership = overrides.get(
        "membership",
        ExplicitPortfolioMembership(
            overrides.get("position_portfolio_id", portfolio_id),
            "subject-001",
        ),
    )
    return (
        ExplicitPortfolioAllocationLegCapitalBucketLink(
            overrides.get("link_leg_id", leg_id),
            overrides.get("link_bucket_id", bucket_id),
        ),
        ExplicitPortfolioAllocationLeg(leg_id, proposal_link),
        ExplicitPortfolioCapitalBucket(bucket_id, portfolio_id),
        ExplicitPortfolioPosition(position_id, membership),
    )


def classify(items):
    return classify_portfolio_allocation_leg_capital_bucket_link_applicability(
        *items
    )


class ApplicabilityTests(unittest.TestCase):
    def test_exact_enum_contract(self):
        names = [
            "ALLOCATION_LEG_ENDPOINT_MISMATCH",
            "CAPITAL_BUCKET_ENDPOINT_MISMATCH",
            "POSITION_ENDPOINT_MISMATCH",
            "PORTFOLIO_ENDPOINT_MISMATCH",
            "APPLICABLE",
        ]
        self.assertIs(Status.__bases__[0], Enum)
        self.assertEqual(list(Status.__members__), names)
        self.assertEqual([member.name for member in Status], names)
        self.assertEqual([member.value for member in Status], names)
        self.assertEqual(len(Status.__members__), len(Status))
        public_custom = {
            name
            for name in Status.__dict__
            if not name.startswith("_") and name not in names
        }
        self.assertEqual(public_custom, set())

    def test_exact_classifier_signature(self):
        function = (
            classify_portfolio_allocation_leg_capital_bucket_link_applicability
        )
        signature = inspect.signature(function)
        self.assertEqual(
            list(signature.parameters),
            ["capital_bucket_link", "leg", "capital_bucket", "position"],
        )
        annotations = (
            ExplicitPortfolioAllocationLegCapitalBucketLink,
            ExplicitPortfolioAllocationLeg,
            ExplicitPortfolioCapitalBucket,
            ExplicitPortfolioPosition,
        )
        for parameter, annotation in zip(
            signature.parameters.values(), annotations
        ):
            self.assertIs(
                parameter.kind,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            self.assertIs(parameter.default, inspect.Parameter.empty)
            self.assertIs(parameter.annotation, annotation)
        self.assertIs(signature.return_annotation, Status)

    def test_fully_aligned_set_is_applicable(self):
        self.assertIs(classify(make_set()), Status.APPLICABLE)

    def test_each_mismatch_returns_exact_status(self):
        cases = (
            ({"link_leg_id": "other"}, Status.ALLOCATION_LEG_ENDPOINT_MISMATCH),
            ({"link_bucket_id": "other"}, Status.CAPITAL_BUCKET_ENDPOINT_MISMATCH),
            ({"leg_position_id": "other"}, Status.POSITION_ENDPOINT_MISMATCH),
            ({"position_portfolio_id": "other"}, Status.PORTFOLIO_ENDPOINT_MISMATCH),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(classify(make_set(**overrides)), expected)

    def test_first_mismatch_wins_for_every_precedence_pair(self):
        mismatches = (
            ("link_leg_id", Status.ALLOCATION_LEG_ENDPOINT_MISMATCH),
            ("link_bucket_id", Status.CAPITAL_BUCKET_ENDPOINT_MISMATCH),
            ("leg_position_id", Status.POSITION_ENDPOINT_MISMATCH),
            ("position_portfolio_id", Status.PORTFOLIO_ENDPOINT_MISMATCH),
        )
        for first_index, (first_key, expected) in enumerate(mismatches):
            for later_key, _ in mismatches[first_index + 1 :]:
                with self.subTest(first=first_key, later=later_key):
                    self.assertIs(
                        classify(
                            make_set(
                                **{first_key: "first", later_key: "later"}
                            )
                        ),
                        expected,
                    )

    def test_exact_string_equality_preserves_case_whitespace_and_unicode(self):
        composed = unicodedata.normalize("NFC", "e\u0301")
        decomposed = unicodedata.normalize("NFD", "\u00e9")
        cases = (
            ({"link_leg_id": "LEG-001"}, Status.ALLOCATION_LEG_ENDPOINT_MISMATCH),
            ({"link_bucket_id": " bucket-001 "}, Status.CAPITAL_BUCKET_ENDPOINT_MISMATCH),
            (
                {"position_id": composed, "leg_position_id": decomposed},
                Status.POSITION_ENDPOINT_MISMATCH,
            ),
            ({"position_portfolio_id": "PORTFOLIO-001"}, Status.PORTFOLIO_ENDPOINT_MISMATCH),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(classify(make_set(**overrides)), expected)

    def test_validators_called_once_in_exact_order_with_exact_objects(self):
        items = make_set()
        calls = []
        targets = (
            ("validate_explicit_portfolio_allocation_leg_capital_bucket_link", "link"),
            ("validate_explicit_portfolio_allocation_leg", "leg"),
            ("validate_explicit_portfolio_capital_bucket", "bucket"),
            ("validate_explicit_portfolio_position", "position"),
        )
        patchers = []
        mocks = []
        for target, label in targets:
            patcher = patch(
                "PortfolioAllocationLegCapitalBucketLinkApplicability."
                "classification." + target,
                side_effect=lambda value, label=label: calls.append(
                    (label, value)
                ),
            )
            patchers.append(patcher)
            mocks.append(patcher.start())
        try:
            self.assertIs(classify(items), Status.APPLICABLE)
        finally:
            for patcher in reversed(patchers):
                patcher.stop()
        self.assertEqual(
            calls,
            [(label, item) for (_, label), item in zip(targets, items)],
        )
        for mock, item in zip(mocks, items):
            mock.assert_called_once_with(item)

    def test_each_validator_failure_stops_later_work_and_propagates_identity(self):
        targets = (
            "validate_explicit_portfolio_allocation_leg_capital_bucket_link",
            "validate_explicit_portfolio_allocation_leg",
            "validate_explicit_portfolio_capital_bucket",
            "validate_explicit_portfolio_position",
        )
        for failure_index, failing_target in enumerate(targets):
            with self.subTest(failing_target=failing_target):
                error = RuntimeError(failing_target)
                mocks = [MagicMock() for _ in targets]
                mocks[failure_index].side_effect = error
                patchers = [
                    patch(
                        "PortfolioAllocationLegCapitalBucketLinkApplicability."
                        "classification." + target,
                        mock,
                    )
                    for target, mock in zip(targets, mocks)
                ]
                for patcher in patchers:
                    patcher.start()
                try:
                    with self.assertRaises(RuntimeError) as caught:
                        classify(make_set())
                finally:
                    for patcher in reversed(patchers):
                        patcher.stop()
                self.assertIs(caught.exception, error)
                for index, mock in enumerate(mocks):
                    if index <= failure_index:
                        mock.assert_called_once()
                    else:
                        mock.assert_not_called()

    def test_no_comparison_occurs_until_all_validation_succeeds(self):
        class ComparisonProbe(str):
            def __eq__(self, other):
                raise AssertionError("comparison occurred")

            def __ne__(self, other):
                raise AssertionError("comparison occurred")

        items = make_set(link_leg_id=ComparisonProbe("leg-001"))
        error = RuntimeError("fourth validation failure")
        with patch(
            "PortfolioAllocationLegCapitalBucketLinkApplicability."
            "classification."
            "validate_explicit_portfolio_allocation_leg_capital_bucket_link"
        ), patch(
            "PortfolioAllocationLegCapitalBucketLinkApplicability."
            "classification.validate_explicit_portfolio_allocation_leg"
        ), patch(
            "PortfolioAllocationLegCapitalBucketLinkApplicability."
            "classification.validate_explicit_portfolio_capital_bucket"
        ), patch(
            "PortfolioAllocationLegCapitalBucketLinkApplicability."
            "classification.validate_explicit_portfolio_position",
            side_effect=error,
        ):
            with self.assertRaises(RuntimeError) as caught:
                classify(items)
        self.assertIs(caught.exception, error)

    def test_real_upstream_validation_and_no_local_duplicate_validation(self):
        cases = (
            (
                0,
                TypeError,
                "link must be "
                "ExplicitPortfolioAllocationLegCapitalBucketLink",
            ),
            (1, TypeError, "leg must be ExplicitPortfolioAllocationLeg"),
            (
                2,
                TypeError,
                "bucket must be ExplicitPortfolioCapitalBucket",
            ),
            (3, TypeError, "position must be ExplicitPortfolioPosition"),
        )
        base = list(make_set())
        for item_index, error_type, message in cases:
            malformed = list(base)
            malformed[item_index] = None
            with self.subTest(index=item_index):
                with self.assertRaisesRegex(error_type, f"^{message}$"):
                    classify(tuple(malformed))

        root = Path(__file__).resolve().parents[1]
        tree = ast.parse((root / "classification.py").read_text())
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertEqual(
            called_names,
            {
                "validate_explicit_portfolio_allocation_leg_capital_bucket_link",
                "validate_explicit_portfolio_allocation_leg",
                "validate_explicit_portfolio_capital_bucket",
                "validate_explicit_portfolio_position",
            },
        )

    def test_inputs_retained_objects_and_fields_are_not_mutated_or_replaced(self):
        leg_id = " leg-\u00e9 "
        bucket_id = " bucket-e\u0301 "
        position_id = " position-001 "
        portfolio_id = " portfolio-001 "
        items = make_set(
            leg_id=leg_id,
            bucket_id=bucket_id,
            position_id=position_id,
            portfolio_id=portfolio_id,
        )
        retained = (items[1].link, items[3].membership)
        identities = tuple(map(id, items + retained))
        fields = (
            items[0].allocation_leg_id,
            items[0].capital_bucket_id,
            items[1].allocation_leg_id,
            items[1].link.position_id,
            items[2].capital_bucket_id,
            items[2].portfolio_id,
            items[3].position_id,
            items[3].membership.portfolio_id,
        )
        field_identities = tuple(map(id, fields))
        self.assertIs(classify(items), Status.APPLICABLE)
        self.assertEqual(tuple(map(id, items + retained)), identities)
        self.assertEqual(tuple(map(id, fields)), field_identities)

    def test_shared_endpoints_and_duplicates_are_independently_classifiable(self):
        first = make_set()
        duplicate = make_set()
        shared_leg = make_set(link_bucket_id="other-bucket")
        self.assertEqual(first[0], duplicate[0])
        self.assertIs(classify(first), Status.APPLICABLE)
        self.assertIs(classify(duplicate), Status.APPLICABLE)
        self.assertIs(
            classify(shared_leg),
            Status.CAPITAL_BUCKET_ENDPOINT_MISMATCH,
        )

    def test_no_m50_or_m51_dependency_and_exact_package_boundary(self):
        root = Path(__file__).resolve().parents[1]
        files = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(
            files,
            {
                "README.md",
                "models.py",
                "classification.py",
                "tests/__init__.py",
                "tests/test_applicability.py",
            },
        )
        self.assertFalse((root / "__init__.py").exists())
        self.assertFalse((root / "validation.py").exists())
        modules = set()
        for name in ("models.py", "classification.py"):
            tree = ast.parse((root / name).read_text())
            modules.update(
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            )
        self.assertFalse(
            any(
                module.startswith(
                    (
                        "PortfolioAllocationLegRiskBudgetLink",
                        "PortfolioAllocationLegAssociationConsistencyApplicability",
                    )
                )
                for module in modules
            )
        )


if __name__ == "__main__":
    unittest.main()
