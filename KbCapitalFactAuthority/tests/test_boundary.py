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
    def test_no_allocation_hip_approval_orders_or_automation(self):
        imported = imported_roots(ROOT)
        forbidden_packages = {
            "joo_auto",
            "JOOAutomation",
            "PortfolioAllocationLeg",
            "PortfolioCapitalBucket",
            "ExactExpectedValue",
            "CIOEngine",
            "BrokerExecution",
            "AIAdapter",
            "Committee",
        }
        self.assertTrue(imported.isdisjoint(forbidden_packages), imported)
        source = "\n".join(
            path.read_text() for path in production_paths(ROOT)
        )
        for forbidden in (
            "HumanApproval",
            "place_order",
            "execute_trade",
            "deployable_capital",
            "investable_capital",
            "HIP",
            "Controller",
            "Bridge",
            "allocation_weight",
        ):
            self.assertNotIn(forbidden, source)

    def test_no_float_uuid_or_second_fact_store(self):
        source = "\n".join(
            path.read_text() for path in production_paths(ROOT)
        )
        for forbidden in (
            "float(",
            "uuid4",
            "sqlite3.connect",
            "CREATE TABLE",
            "class FactStore",
        ):
            self.assertNotIn(forbidden, source)

    def test_existing_core_packages_do_not_import_capital_authority(self):
        for package in (
            "ProviderGateway",
            "FactStore",
            "PortfolioSnapshot",
            "PortfolioSnapshotProducer",
            "KbPortfolioVerticalSlice",
            "InvestmentResearchOrchestrator",
            "OperationalCioCycle",
            "InvestmentDecisionVerticalSlice",
        ):
            with self.subTest(package=package):
                self.assertNotIn(
                    "KbCapitalFactAuthority",
                    imported_roots(REPOSITORY / package),
                )


if __name__ == "__main__":
    unittest.main()
