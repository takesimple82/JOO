from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def production_paths(package: Path):
    return tuple(
        path
        for path in package.rglob("*.py")
        if "tests" not in path.parts
    )


class BoundaryTests(unittest.TestCase):
    def test_no_ssam_orders_automation_or_ai_arithmetic(self):
        source = "\n".join(path.read_text() for path in production_paths(ROOT))
        for forbidden in (
            "SSAM",
            "place_order",
            "execute_trade",
            "OrderIntent",
            "BrokerExecution",
            "joo_auto",
            "JOOAutomation",
            "Controller",
            "Bridge",
            "float(",
            "uuid4",
            "CREATE TABLE",
            "+50%",
            "profit_take_pct",
            "nt_asts_val_amt",
        ):
            self.assertNotIn(forbidden, source)

    def test_no_forbidden_package_imports(self):
        imported = set()
        for path in production_paths(ROOT):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
        forbidden = {
            "joo_auto",
            "JOOAutomation",
            "AIAdapter",
            "Committee",
            "ExecutionEngine",
        }
        self.assertTrue(imported.isdisjoint(forbidden), imported)

    def test_exact_expected_value_untouched_by_package(self):
        imported = set()
        for path in production_paths(ROOT):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
                elif isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
        self.assertNotIn("ExactExpectedValue", imported)

    def test_block_a_packages_do_not_statically_import_capital_allocation(self):
        for package in (
            "OperationalCioCycle",
            "InvestmentDecisionVerticalSlice",
            "KbCapitalFactAuthority",
            "ExactExpectedValue",
        ):
            for path in production_paths(REPO / package):
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    modules = []
                    if isinstance(node, ast.Import):
                        modules = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        modules = [node.module or ""]
                    for module in modules:
                        self.assertFalse(
                            module.startswith("CapitalAllocationCycle"),
                            (package, path, module),
                        )


if __name__ == "__main__":
    unittest.main()
