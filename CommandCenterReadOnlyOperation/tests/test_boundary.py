from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def production_imports(package):
    modules = []
    for path in (ROOT / package).glob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(x.name for x in node.names)
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module or "")
    return tuple(modules)


class ReadOnlyOperationBoundaryTests(unittest.TestCase):
    def test_application_never_imports_producer_service_or_http(self):
        imports = production_imports("CommandCenterApplication")
        self.assertNotIn("CommandCenterReadOnlyOperation.service", imports)
        self.assertNotIn("CommandCenterReadOnlyOperation.http", imports)
        self.assertNotIn("ProviderGateway.auth.kb_openapi_runtime", imports)

    def test_operation_has_no_broker_mutation_or_execution_authority(self):
        sources = "\n".join(
            path.read_text()
            for path in (ROOT / "CommandCenterReadOnlyOperation").glob("*.py")
        )
        for forbidden in (
            "SSAM1802", "SSAM1805", "SSAM1806",
            "execute_mutation_attempt", "TradeExecutionAuthorization",
            "InvestmentHumanApproval", "run_one_joo_command_center_cycle",
        ):
            self.assertNotIn(forbidden, sources)

    def test_documented_application_flag_matches_cli(self):
        readme = (ROOT / "CommandCenterApplication" / "README.md").read_text()
        cli = (ROOT / "CommandCenterApplication" / "__main__.py").read_text()
        self.assertIn("--journal", readme)
        self.assertNotIn("--decision-journal", readme)
        self.assertIn('parser.add_argument("--journal")', cli)

    def test_loopback_only_server_boundary_remains(self):
        source = (ROOT / "CommandCenterApplication" / "server.py").read_text()
        self.assertIn('{"127.0.0.1", "::1", "localhost"}', source)
        self.assertNotIn('"0.0.0.0"', source)


if __name__ == "__main__":
    unittest.main()
