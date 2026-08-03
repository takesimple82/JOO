import ast
import inspect
import unittest
from pathlib import Path
from unittest.mock import patch

from PortfolioAllocationProposalEndpoint.models import (
    ExplicitPortfolioAllocationProposalEndpoint,
)
from PortfolioAllocationProposalPositionLink.models import (
    ExplicitPortfolioAllocationProposalPositionLink,
)
from PortfolioAllocationProposalPositionLinkApplicability.classification import (
    classify_portfolio_allocation_proposal_position_link_applicability,
)
from PortfolioAllocationProposalPositionLinkApplicability.models import (
    PortfolioAllocationProposalPositionLinkApplicabilityStatus,
)
from PortfolioHoldingSnapshot.models import (
    ExplicitPortfolioHoldingSnapshot,
)
from PortfolioMembership.models import ExplicitPortfolioMembership
from PortfolioObservationContext.models import (
    ExplicitPortfolioObservationContext,
)
from PortfolioPosition.models import ExplicitPortfolioPosition
from PortfolioRecommendationEndpoint.models import (
    ExplicitPortfolioRecommendationEndpoint,
)
from PortfolioSnapshot.models import ExplicitPortfolioSnapshot


Status = PortfolioAllocationProposalPositionLinkApplicabilityStatus


def make_chain(**overrides):
    proposal_id = overrides.get("proposal_id", "proposal-001")
    recommendation_id = overrides.get(
        "recommendation_id", "recommendation-001"
    )
    snapshot_id = overrides.get("snapshot_id", "snapshot-001")
    position_id = overrides.get("position_id", "position-001")
    portfolio_id = overrides.get("portfolio_id", "portfolio-001")
    context = ExplicitPortfolioObservationContext(
        "context-001", portfolio_id
    )
    return (
        ExplicitPortfolioAllocationProposalPositionLink(
            overrides.get("link_proposal_id", proposal_id),
            overrides.get("link_position_id", position_id),
        ),
        ExplicitPortfolioAllocationProposalEndpoint(
            proposal_id,
            overrides.get("proposal_recommendation_id", recommendation_id),
        ),
        ExplicitPortfolioRecommendationEndpoint(
            recommendation_id,
            overrides.get("recommendation_snapshot_id", snapshot_id),
        ),
        ExplicitPortfolioSnapshot(
            snapshot_id,
            context,
            ExplicitPortfolioHoldingSnapshot(context, ()),
            (),
        ),
        ExplicitPortfolioPosition(
            position_id,
            ExplicitPortfolioMembership(
                overrides.get("position_portfolio_id", portfolio_id),
                "subject-001",
            ),
        ),
    )


def classify(chain):
    return classify_portfolio_allocation_proposal_position_link_applicability(
        *chain
    )


class ApplicabilityTests(unittest.TestCase):
    def test_exact_enum_contract(self):
        names = [
            "ALLOCATION_PROPOSAL_ENDPOINT_MISMATCH",
            "POSITION_ENDPOINT_MISMATCH",
            "RECOMMENDATION_ENDPOINT_MISMATCH",
            "PORTFOLIO_SNAPSHOT_ENDPOINT_MISMATCH",
            "PORTFOLIO_ENDPOINT_MISMATCH",
            "APPLICABLE",
        ]
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

    def test_exact_classifier_name_signature_and_annotations(self):
        function = (
            classify_portfolio_allocation_proposal_position_link_applicability
        )
        self.assertEqual(
            function.__name__,
            "classify_portfolio_allocation_proposal_position_link_applicability",
        )
        signature = inspect.signature(function)
        self.assertEqual(
            list(signature.parameters),
            ["link", "proposal", "recommendation", "snapshot", "position"],
        )
        self.assertEqual(
            [parameter.annotation for parameter in signature.parameters.values()],
            [
                ExplicitPortfolioAllocationProposalPositionLink,
                ExplicitPortfolioAllocationProposalEndpoint,
                ExplicitPortfolioRecommendationEndpoint,
                ExplicitPortfolioSnapshot,
                ExplicitPortfolioPosition,
            ],
        )
        self.assertIs(signature.return_annotation, Status)

    def test_valid_chain_is_applicable_and_repeatable(self):
        chain = make_chain()
        self.assertIs(classify(chain), Status.APPLICABLE)
        self.assertIs(classify(chain), Status.APPLICABLE)
        self.assertIs(classify(make_chain()), Status.APPLICABLE)

    def test_each_mismatch_has_exact_status(self):
        cases = (
            ({"link_proposal_id": "other"}, Status.ALLOCATION_PROPOSAL_ENDPOINT_MISMATCH),
            ({"link_position_id": "other"}, Status.POSITION_ENDPOINT_MISMATCH),
            ({"proposal_recommendation_id": "other"}, Status.RECOMMENDATION_ENDPOINT_MISMATCH),
            ({"recommendation_snapshot_id": "other"}, Status.PORTFOLIO_SNAPSHOT_ENDPOINT_MISMATCH),
            ({"position_portfolio_id": "other"}, Status.PORTFOLIO_ENDPOINT_MISMATCH),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                self.assertIs(classify(make_chain(**overrides)), expected)

    def test_first_mismatch_wins(self):
        all_mismatched = make_chain(
            link_proposal_id="wrong-proposal",
            link_position_id="wrong-position",
            proposal_recommendation_id="wrong-recommendation",
            recommendation_snapshot_id="wrong-snapshot",
            position_portfolio_id="wrong-portfolio",
        )
        self.assertIs(
            classify(all_mismatched),
            Status.ALLOCATION_PROPOSAL_ENDPOINT_MISMATCH,
        )

    def test_validators_once_in_frozen_order_before_comparison(self):
        chain = make_chain()
        calls = []
        targets = (
            ("validate_explicit_portfolio_allocation_proposal_position_link", "link"),
            ("validate_explicit_portfolio_allocation_proposal_endpoint", "proposal"),
            ("validate_explicit_portfolio_recommendation_endpoint", "recommendation"),
            ("validate_explicit_portfolio_snapshot", "snapshot"),
            ("validate_explicit_portfolio_position", "position"),
        )
        patches = []
        mocks = []
        for index, (target, label) in enumerate(targets):
            patcher = patch(
                "PortfolioAllocationProposalPositionLinkApplicability.classification."
                + target,
                side_effect=lambda value, label=label: calls.append((label, value)),
            )
            patches.append(patcher)
            mocks.append(patcher.start())
        try:
            self.assertIs(classify(chain), Status.APPLICABLE)
        finally:
            for patcher in reversed(patches):
                patcher.stop()
        self.assertEqual(calls, list(zip((label for _, label in targets), chain)))
        for mock, value in zip(mocks, chain):
            mock.assert_called_once_with(value)

    def test_no_comparison_before_all_validation_succeeds(self):
        chain = make_chain(link_proposal_id="wrong")
        error = RuntimeError("position validation failed")
        with patch(
            "PortfolioAllocationProposalPositionLinkApplicability.classification."
            "validate_explicit_portfolio_position",
            side_effect=error,
        ):
            with self.assertRaises(RuntimeError) as caught:
                classify(chain)
        self.assertIs(caught.exception, error)

    def test_first_upstream_exception_propagates_and_stops_validation(self):
        error = ValueError("proposal validation failed")
        with patch(
            "PortfolioAllocationProposalPositionLinkApplicability.classification."
            "validate_explicit_portfolio_allocation_proposal_endpoint",
            side_effect=error,
        ), patch(
            "PortfolioAllocationProposalPositionLinkApplicability.classification."
            "validate_explicit_portfolio_recommendation_endpoint",
        ) as recommendation_validator, patch(
            "PortfolioAllocationProposalPositionLinkApplicability.classification."
            "validate_explicit_portfolio_snapshot",
        ) as snapshot_validator, patch(
            "PortfolioAllocationProposalPositionLinkApplicability.classification."
            "validate_explicit_portfolio_position",
        ) as position_validator:
            with self.assertRaises(ValueError) as caught:
                classify(make_chain())
        self.assertIs(caught.exception, error)
        recommendation_validator.assert_not_called()
        snapshot_validator.assert_not_called()
        position_validator.assert_not_called()

    def test_exact_value_semantics(self):
        cases = (
            make_chain(link_proposal_id=" proposal-001 "),
            make_chain(link_proposal_id="PROPOSAL-001"),
            make_chain(proposal_id="\u00e9", link_proposal_id="e\u0301"),
        )
        for chain in cases:
            with self.subTest(value=chain[0].allocation_proposal_id):
                self.assertIs(
                    classify(chain),
                    Status.ALLOCATION_PROPOSAL_ENDPOINT_MISMATCH,
                )

    def test_objects_fields_and_state_are_preserved(self):
        proposal_id = " proposal-\u00e9 "
        position_id = " position-e\u0301 "
        chain = make_chain(
            proposal_id=proposal_id,
            position_id=position_id,
        )
        identities = tuple(id(value) for value in chain)
        fields = (
            chain[0].allocation_proposal_id,
            chain[0].position_id,
            chain[1].allocation_proposal_id,
            chain[4].position_id,
            chain[4].membership,
            chain[3].observation_context,
            chain[3].holding_snapshot,
            chain[3].watchlist_entries,
        )
        field_identities = tuple(id(value) for value in fields)
        self.assertIs(classify(chain), Status.APPLICABLE)
        self.assertEqual(tuple(id(value) for value in chain), identities)
        self.assertEqual(tuple(id(value) for value in fields), field_identities)
        self.assertIs(chain[0].allocation_proposal_id, proposal_id)
        self.assertIs(chain[4].position_id, position_id)

    def test_position_need_not_be_held_or_watchlisted(self):
        chain = make_chain()
        self.assertEqual(chain[3].holding_snapshot.holding_observations, ())
        self.assertEqual(chain[3].watchlist_entries, ())
        self.assertIs(classify(chain), Status.APPLICABLE)

    def test_production_imports_and_forbidden_behavior(self):
        root = Path(__file__).resolve().parents[1]
        models_tree = ast.parse((root / "models.py").read_text())
        classifier_tree = ast.parse((root / "classification.py").read_text())
        self.assertEqual(
            {
                node.module
                for node in ast.walk(models_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"enum"},
        )
        modules = {
            node.module
            for node in ast.walk(classifier_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            modules,
            {
                "PortfolioAllocationProposalEndpoint.models",
                "PortfolioAllocationProposalEndpoint.validation",
                "PortfolioAllocationProposalPositionLink.models",
                "PortfolioAllocationProposalPositionLink.validation",
                "PortfolioAllocationProposalPositionLinkApplicability.models",
                "PortfolioPosition.models",
                "PortfolioPosition.validation",
                "PortfolioRecommendationEndpoint.models",
                "PortfolioRecommendationEndpoint.validation",
                "PortfolioSnapshot.models",
                "PortfolioSnapshot.validation",
            },
        )
        functions = [
            node.name
            for node in classifier_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(
            functions,
            ["classify_portfolio_allocation_proposal_position_link_applicability"],
        )
        forbidden_nodes = (ast.For, ast.While, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
        self.assertFalse(any(isinstance(node, forbidden_nodes) for node in ast.walk(classifier_tree)))
        source = (root / "classification.py").read_text().lower()
        for forbidden in (
            "holding_observations",
            "watchlist_entries",
            "repository",
            "registry",
            "resolver",
            "persistence",
            "runtime",
            "constraint",
            "approval",
            "execution",
        ):
            self.assertNotIn(forbidden, source)

    def test_readme_matches_the_frozen_contract(self):
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text()
        normalized_readme = " ".join(readme.split())
        required_fragments = (
            "PortfolioAllocationProposalPositionLinkApplicabilityStatus",
            "classify_portfolio_allocation_proposal_position_link_applicability()",
            "ALLOCATION_PROPOSAL_ENDPOINT_MISMATCH",
            "POSITION_ENDPOINT_MISMATCH",
            "RECOMMENDATION_ENDPOINT_MISMATCH",
            "PORTFOLIO_SNAPSHOT_ENDPOINT_MISMATCH",
            "PORTFOLIO_ENDPOINT_MISMATCH",
            "APPLICABLE",
            "the first mismatch wins",
            "position.membership.portfolio_id",
            "snapshot.observation_context.portfolio_id",
            "does not inspect or search Snapshot holding observations",
            "pure and stateless",
            "does not enforce uniqueness",
            "runtime, orchestration, CLI, automation",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, normalized_readme)


if __name__ == "__main__":
    unittest.main()
