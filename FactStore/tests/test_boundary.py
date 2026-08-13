from __future__ import annotations

import ast
import unittest
from pathlib import Path

from FactStore.store import FactStore


ROOT = Path(__file__).resolve().parents[1]


def _production_paths():
    paths = []
    for path in ROOT.rglob("*.py"):
        if "tests" in path.parts:
            continue
        paths.append(path)
    return paths


def _production_source():
    return "\n".join(path.read_text() for path in _production_paths())


class PackageBoundaryTests(unittest.TestCase):
    def test_no_forbidden_package_imports(self):
        forbidden_modules = {
            "MarketEndpoint",
            "MarketVenue",
            "MarketInstrument",
            "MarketSessionContext",
            "MarketFactProvenanceReference",
            "MarketInstrumentObservation",
            "MarketSnapshot",
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
            "Automation",
        }
        imported = set()
        gateway_modules = set()
        validator_names = set()
        for path in _production_paths():
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        root = node.module.split(".")[0]
                        imported.add(root)
                        if root == "ProviderGateway":
                            gateway_modules.add(node.module)
                            if (
                                node.module
                                == "ProviderGateway.validation.validators"
                            ):
                                for alias in node.names:
                                    validator_names.add(alias.name)
        self.assertTrue(
            imported.issubset(
                {
                    "__future__",
                    "dataclasses",
                    "datetime",
                    "hashlib",
                    "json",
                    "typing",
                    "ProviderGateway",
                    "FactStore",
                }
            ),
            imported,
        )
        self.assertTrue(imported.isdisjoint(forbidden_modules))
        self.assertTrue(
            gateway_modules.issubset(
                {
                    "ProviderGateway.models",
                    "ProviderGateway.validation.validators",
                }
            ),
            gateway_modules,
        )
        self.assertEqual(
            validator_names,
            {"validate_explicit_provider_payload_envelope"},
        )

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
            "MarketSnapshotProducer",
            "InvestmentResearchOrchestrator",
            "validate_market_fact_success_envelope",
        ):
            self.assertNotIn(forbidden, production)

    def test_no_gateway_runtime_or_http_refetch(self):
        production = _production_source()
        for forbidden in (
            "ProviderGateway.adapters",
            "ProviderGateway.auth",
            "ProviderGateway.ingress",
            "ProviderGateway.health",
            "ProviderGateway.signaling",
            "ProviderGateway.provider_interface",
            "datetime.now",
            "datetime.utcnow",
            "urllib",
            "requests",
            "http.client",
        ):
            self.assertNotIn(forbidden, production)

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

    def test_no_get_by_envelope_id_public_method(self):
        self.assertFalse(
            hasattr(FactStore, "get_by_envelope_id")
        )
        public = {
            name
            for name, value in FactStore.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(
            public,
            {
                "append",
                "get_by_fact_id",
                "list_by_source_identity",
                "list_by_source_class",
                "list_by_collected_at_window",
                "get_predecessor",
                "get_successor",
                "verify_integrity",
            },
        )

    def test_readme_states_identity_and_non_responsibilities(self):
        readme = (ROOT / "README.md").read_text()
        for fragment in (
            "FactStore",
            "package-identity reuse",
            "broker_fact",
            "market_fact",
            "Non-responsibilities",
            "MarketSnapshotProducer",
            "PF-M4",
            "ProviderGateway",
            "ticker / entity / alias resolution",
            "research_ai",
            "execution_fact",
            "broker orders",
            "OHLC",
            "EvidenceProvenance",
            "auto-generated `fact_id`",
            "Market Watch",
            "IRO",
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
            "MarketHistory",
            "QuoteStore",
            "MarketSnapshotProducer",
        ):
            self.assertFalse((parent / name).exists())

    def test_factstore_does_not_contain_gateway_modules(self):
        for name in (
            "adapters",
            "auth",
            "ingress.py",
            "health.py",
            "signaling.py",
            "provider_interface.py",
        ):
            self.assertFalse((ROOT / name).exists())


if __name__ == "__main__":
    unittest.main()
