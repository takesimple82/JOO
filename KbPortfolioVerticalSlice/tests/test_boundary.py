from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent


def production_paths(root):
    return tuple(
        path
        for path in root.rglob("*.py")
        if "tests" not in path.parts
    )


def imported_roots(root):
    imported = set()
    for path in production_paths(root):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(
                    alias.name.split(".")[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
    return imported


class BoundaryTests(unittest.TestCase):
    def test_existing_components_do_not_import_vertical_slice(self):
        for package in (
            "ProviderGateway",
            "PortfolioSnapshotProducer",
            "PortfolioSnapshot",
            "InvestmentResearchOrchestrator",
        ):
            with self.subTest(package=package):
                self.assertNotIn(
                    "KbPortfolioVerticalSlice",
                    imported_roots(REPOSITORY / package),
                )

    def test_iro_core_still_excludes_factual_runtime_dependencies(self):
        imported = imported_roots(
            REPOSITORY / "InvestmentResearchOrchestrator"
        )
        self.assertTrue(
            imported.isdisjoint(
                {
                    "ProviderGateway",
                    "FactStore",
                    "PortfolioSnapshotProducer",
                    "KbPortfolioVerticalSlice",
                    "joo_auto",
                }
            ),
            imported,
        )

    def test_vertical_slice_has_no_automation_or_investment_authority(self):
        imported = imported_roots(ROOT)
        self.assertTrue(
            imported.isdisjoint(
                {
                    "joo_auto",
                    "CIOEngine",
                    "ExactExpectedValue",
                    "PortfolioAllocationProposal",
                    "BrokerExecution",
                }
            ),
            imported,
        )
        source = "\n".join(
            path.read_text() for path in production_paths(ROOT)
        )
        for forbidden in (
            "Controller",
            "Bridge",
            "scheduler",
            "place_order",
            "execute_trade",
        ):
            self.assertNotIn(forbidden, source)

    def test_decimal_and_identifiers_are_not_generated_by_float_or_uuid(self):
        source = "\n".join(
            path.read_text() for path in production_paths(ROOT)
        )
        for forbidden in ("float(", "uuid", "uuid4", "token_hex"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
