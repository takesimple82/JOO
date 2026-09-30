from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class AiDecisionBoundaryTests(unittest.TestCase):
    def test_operation_has_no_execution_or_broker_mutation_dependency(self):
        imports = []
        source = ""
        for path in (ROOT / "CommandCenterAiDecisionOperation").glob("*.py"):
            text = path.read_text()
            source += text
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
                elif isinstance(node, ast.Import):
                    imports.extend(item.name for item in node.names)
        for prefix in ("BrokerExecutionCycle", "TradeExecution", "ProviderGateway"):
            self.assertFalse(any(item.startswith(prefix) for item in imports))
        for forbidden in (
            "SSAM1802", "SSAM1805", "SSAM1806", "TradeExecutionAuthorization",
            "approve_capital_allocation", "seal_approved_allocation",
        ):
            self.assertNotIn(forbidden, source)

    def test_real_operation_cannot_accept_fixture_or_provider_content(self):
        source = (ROOT / "CommandCenterAiDecisionOperation" / "service.py").read_text()
        self.assertNotIn("content", source)
        self.assertNotIn("FIXTURE", source)
        self.assertNotIn("AIResponse", source)


if __name__ == "__main__":
    unittest.main()
