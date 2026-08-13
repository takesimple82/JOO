from __future__ import annotations

import ast
import inspect
import unittest
from pathlib import Path

from ProviderGateway.adapters.market_api import MarketApiAdapter
from ProviderGateway.models import (
    RESERVED_KB_OPEN_API_PROVIDER_ID,
)
from ProviderGateway.provider_interface import ProviderInterface


ROOT = Path(__file__).resolve().parents[1]


def _production_paths():
    paths = []
    for path in ROOT.rglob("*.py"):
        if "tests" in path.parts:
            continue
        paths.append(path)
    return paths


def _production_source():
    return "\n".join(
        path.read_text() for path in _production_paths()
    )


class PackageBoundaryTests(unittest.TestCase):
    def test_reserved_kb_constant(self):
        self.assertEqual(
            RESERVED_KB_OPEN_API_PROVIDER_ID,
            "kb_open_api",
        )

    def test_kb_open_api_adapter_file_is_absent(self):
        self.assertFalse(
            (ROOT / "adapters" / "kb_open_api.py").exists()
        )

    def test_no_forbidden_package_imports(self):
        forbidden_modules = {
            "MarketEndpoint",
            "MarketVenue",
            "MarketInstrument",
            "MarketSessionContext",
            "MarketFactProvenanceReference",
            "MarketInstrumentObservation",
            "MarketSnapshot",
            "FactStore",
            "MarketSnapshotProducer",
            "InvestmentResearchOrchestrator",
            "joo_auto",
            "EvidenceProvenance",
            "EvidenceAggregation",
            "AIAdapter",
            "Committee",
            "ResearchOrchestrator",
            "PortfolioSnapshot",
            "PortfolioHoldingSnapshot",
        }
        imported = set()
        for path in _production_paths():
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported.add(node.module.split(".")[0])
        self.assertTrue(
            imported.issubset(
                {
                    "__future__",
                    "abc",
                    "dataclasses",
                    "datetime",
                    "typing",
                    "ProviderGateway",
                }
            ),
            imported,
        )
        self.assertTrue(imported.isdisjoint(forbidden_modules))

    def test_success_path_does_not_name_market_domain_types(self):
        production = _production_source()
        for forbidden in (
            "ExplicitMarketVenue",
            "ExplicitMarketInstrument",
            "ExplicitMarketSessionContext",
            "ExplicitMarketFactProvenanceReference",
            "ExplicitMarketInstrumentObservation",
            "ExplicitMarketSnapshot",
            "MarketEndpoint",
            "FactStore",
            "MarketSnapshotProducer",
            "InvestmentResearchOrchestrator",
        ):
            self.assertNotIn(forbidden, production)

    def test_collect_is_not_korea_else_us(self):
        collect_source = (
            (ROOT / "ingress.py").read_text()
            + (ROOT / "adapters" / "market_api.py").read_text()
            + (ROOT / "health.py").read_text()
        )
        lowered = collect_source.casefold()
        for token in (
            "korea",
            "krx",
            "nyse",
            "nasdaq",
            "if korea",
            "else us",
        ):
            self.assertNotIn(token, lowered)
        tree = ast.parse((ROOT / "ingress.py").read_text())
        literals = [
            node.value.casefold()
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and type(node.value) is str
        ]
        for literal in literals:
            self.assertNotIn("korea", literal)
            self.assertNotIn("krx", literal)
            self.assertNotIn("nyse", literal)
            self.assertNotIn("nasdaq", literal)

    def test_no_automatic_id_generation(self):
        production = _production_source()
        for forbidden in (
            "uuid",
            "token_hex",
            "token_urlsafe",
            "uuid4",
            "secrets.token",
        ):
            self.assertNotIn(forbidden, production)

    def test_no_evidence_provenance_taxonomy(self):
        production = _production_source()
        self.assertNotIn("primary | secondary | unknown", production)
        self.assertNotIn('"primary"', production)
        self.assertNotIn('"secondary"', production)
        self.assertNotIn('"unknown"', production)

    def test_adapter_source_declares_market_fact_literally(self):
        source = inspect.getsource(MarketApiAdapter)
        self.assertIn('return "market_fact"', source)
        self.assertNotIn("broker_fact", source)
        self.assertNotIn("research_ai", source)

    def test_provider_interface_surface(self):
        self.assertTrue(
            issubclass(MarketApiAdapter, ProviderInterface)
        )
        self.assertTrue(
            inspect.isabstract(ProviderInterface)
        )

    def test_readme_states_identity_and_non_responsibilities(self):
        readme = (ROOT / "README.md").read_text()
        for fragment in (
            "ProviderGateway",
            "additive market-adapter path",
            "RESERVED_KB_OPEN_API_PROVIDER_ID",
            "MarketApiAdapter",
            "ProviderInterface",
            "Non-responsibilities",
            "FactStore",
            "Market Snapshot",
            "ticker / entity / alias resolution",
            "research_ai",
            "broker orders",
            "OHLC",
            "EvidenceProvenance",
            "PF-M4",
            "kb_open_api.py",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, readme)

    def test_rejected_package_names_are_absent(self):
        parent = ROOT.parent
        for name in (
            "MarketAdapter",
            "MarketGateway",
            "QuoteIngress",
            "MarketFactStore",
        ):
            self.assertFalse((parent / name).exists())


if __name__ == "__main__":
    unittest.main()
