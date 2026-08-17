from __future__ import annotations

import ast
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
FORBIDDEN_PREFIXES = (
    "ProviderGateway",
    "FactStore",
    "PortfolioSnapshotProducer",
    "MarketSnapshotProducer",
    "MarketSnapshot",
    "MarketInstrument",
    "MarketVenue",
    "MarketSessionContext",
    "MarketInstrumentObservation",
    "MarketEndpoint",
    "MarketFactProvenanceReference",
    "Automation",
    "joo_auto",
)
PRODUCTION_SKIP = {"tests"}


def _module_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Import):
        return node.names[0].name
    if isinstance(node, ast.ImportFrom):
        return node.module
    return None


class M2DependencyDirectionTests(unittest.TestCase):
    def test_production_modules_forbid_neighbor_imports(self):
        offenders: list[str] = []
        for path in PACKAGE.rglob("*.py"):
            relative = path.relative_to(PACKAGE)
            if relative.parts and relative.parts[0] in PRODUCTION_SKIP:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                module = _module_name(node)
                if module is None:
                    continue
                for prefix in FORBIDDEN_PREFIXES:
                    if (
                        module == prefix
                        or module.startswith(prefix + ".")
                    ):
                        offenders.append(
                            f"{relative}: {module}"
                        )
        self.assertEqual(offenders, [])

    def test_contradiction_engine_does_not_import_planner(self):
        path = PACKAGE / "contradiction_engine.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            module = _module_name(node)
            if module is None:
                continue
            if (
                module == "InvestmentResearchOrchestrator.planner"
                or module.endswith(".planner")
            ):
                imported.append(module)
        self.assertEqual(imported, [])

    def test_re_research_does_not_import_planner_or_m22(self):
        path = PACKAGE / "re_research.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            module = _module_name(node)
            if module is None:
                continue
            if module in {
                "InvestmentResearchOrchestrator.planner",
                "ResearchOrchestrator",
                "ResearchOrchestrator.orchestrator",
            } or module.startswith("ResearchOrchestrator."):
                imported.append(module)
        self.assertEqual(imported, [])


if __name__ == "__main__":
    unittest.main()
