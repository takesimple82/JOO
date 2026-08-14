from __future__ import annotations

import ast
import inspect
import unittest
from pathlib import Path

from PortfolioSnapshotProducer.production import (
    PortfolioSnapshotProducer,
)


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


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
            "ProviderGateway",
            "InvestmentResearchOrchestrator",
            "joo_auto",
            "EvidenceProvenance",
            "EvidenceAggregation",
            "AIAdapter",
            "Committee",
            "ResearchOrchestrator",
            "MarketSnapshotProducer",
            "MarketEndpoint",
            "MarketVenue",
            "MarketInstrument",
            "MarketSessionContext",
            "MarketFactProvenanceReference",
            "MarketInstrumentObservation",
            "MarketSnapshot",
            "Automation",
            "PortfolioComposer",
            "HoldingsComposer",
            "PortfolioValuator",
            "PortfolioFactStore",
            "CashSnapshotProducer",
            "WatchlistProducer",
            "PositionResolver",
            "WatchlistStore",
            "WatchlistComposer",
            "SnapshotFactory",
            "ExactDecimalArithmetic",
        }
        imported = set()
        factstore_modules = set()
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
                        if root == "FactStore":
                            factstore_modules.add(node.module)
        self.assertTrue(
            imported.issubset(
                {
                    "__future__",
                    "dataclasses",
                    "datetime",
                    "decimal",
                    "PortfolioObservationContext",
                    "PortfolioMembership",
                    "PortfolioPosition",
                    "PortfolioHoldingObservation",
                    "PortfolioHoldingSnapshot",
                    "PortfolioWatchlistEntry",
                    "PortfolioSnapshot",
                    "FactStore",
                    "PortfolioSnapshotProducer",
                }
            ),
            imported,
        )
        self.assertTrue(imported.isdisjoint(forbidden_modules))
        self.assertTrue(
            factstore_modules.issubset(
                {
                    "FactStore.models",
                    "FactStore.store",
                }
            ),
            factstore_modules,
        )

    def test_no_gateway_runtime_or_http_refetch(self):
        production = _production_source()
        for forbidden in (
            "ProviderGateway",
            "ProviderGateway.adapters",
            "ProviderGateway.auth",
            "ProviderGateway.ingress",
            "ProviderGateway.health",
            "ProviderGateway.signaling",
            "ProviderGateway.provider_interface",
            "ExplicitProviderPayloadEnvelope",
            "ExplicitCollectRequest",
            "BROKER_REQUEST_KIND_VALUES",
            "datetime.now",
            "datetime.utcnow",
            "urllib",
            "requests",
            "http.client",
        ):
            self.assertNotIn(forbidden, production)

    def test_no_factstore_append_or_discovery(self):
        production = _production_source()
        for forbidden in (
            "ExplicitFactAppendRequest",
            "FactStore.append",
            "get_predecessor",
            "get_successor",
            "list_by_source_identity",
            "list_by_source_class",
            "list_by_collected_at_window",
        ):
            self.assertNotIn(forbidden, production)

    def test_retrieval_uses_only_get_and_verify(self):
        source = (
            ROOT / "retrieval" / "boundary.py"
        ).read_text()
        self.assertIn("get_by_fact_id", source)
        self.assertIn("verify_integrity", source)
        self.assertNotIn("append", source)

    def test_no_automatic_id_generation(self):
        production = _production_source()
        for forbidden in (
            "uuid",
            "token_hex",
            "token_urlsafe",
            "uuid4",
            "secrets.token",
            "hashlib",
        ):
            self.assertNotIn(forbidden, production)
        public = {
            name
            for name, value in PortfolioSnapshotProducer.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public, {"produce"})

    def test_no_market_snapshot_producer_or_market_construction(
        self,
    ):
        production = _production_source()
        for forbidden in (
            "MarketSnapshotProducer",
            "ExplicitMarketSnapshot",
            "ExplicitMarketInstrument",
            "build_explicit_market",
        ):
            self.assertNotIn(forbidden, production)

    def test_no_valuation_or_cash_fields(self):
        production = _production_source()
        for forbidden in (
            "allow_partial_emission",
            "require_all_bound_subjects",
            "EMPTY_REQUIRED_EMISSION",
        ):
            self.assertNotIn(forbidden, production)

    def test_rejected_package_names_are_absent(self):
        for name in (
            "PortfolioComposer",
            "HoldingsComposer",
            "PortfolioValuator",
            "PortfolioFactStore",
            "CashSnapshotProducer",
            "WatchlistProducer",
            "PositionResolver",
            "WatchlistStore",
            "WatchlistComposer",
            "SnapshotFactory",
        ):
            self.assertFalse((REPO / name).exists())
        self.assertTrue(ROOT.is_dir())
        self.assertFalse((ROOT / "__init__.py").exists())

    def test_no_gateway_modules_inside_producer(self):
        for name in (
            "adapters",
            "auth",
            "ingress.py",
            "health.py",
            "signaling.py",
            "provider_interface.py",
        ):
            self.assertFalse((ROOT / name).exists())

    def test_secrets_are_not_logged_or_dumped(self):
        production = _production_source()
        for forbidden in (
            "print(",
            "logging",
            "payload dump",
            "api_key",
            "password",
            "access_token",
        ):
            self.assertNotIn(forbidden, production)

    def test_oob_docs_remain_present(self):
        self.assertTrue(
            (REPO / "docs" / "JOO_PRODUCT_ARCHITECTURE.md").is_file()
        )
        self.assertTrue(
            (
                REPO
                / "docs"
                / "automation"
                / "AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md"
            ).is_file()
        )

    def test_readme_states_identity_and_non_responsibilities(
        self,
    ):
        readme = (ROOT / "README.md").read_text()
        for fragment in (
            "PortfolioSnapshotProducer",
            "first-slice operational production",
            "Non-responsibilities",
            "Portfolio\\* structure ownership",
            "ProviderGateway",
            "KB Open API",
            "FactStore append",
            "never-stored envelopes",
            "request_kind",
            "payload-shape classification",
            "intra-payload batched holdings",
            "cash / balances",
            "account_state",
            "valuation / marks / NAV / PnL / FX",
            "MarketSnapshotProducer",
            "snapshot timestamps",
            "automatic identity generation",
            "WatchlistStore / WatchlistProducer",
            "sibling composer packages",
            "IRO ownership",
            "Human Approval",
            "broker orders",
            "PF-M5 / Market Watch",
            "committed PF-M3 architecture",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, readme)

    def test_producer_does_not_import_append(self):
        source = inspect.getsource(PortfolioSnapshotProducer)
        self.assertNotIn("ExplicitFactAppendRequest", source)
        self.assertNotIn("store.append", source)
        self.assertIn("retrieve_by_fact_id", source)
        self.assertIn("verify_retrieved_fact_integrity", source)


if __name__ == "__main__":
    unittest.main()
