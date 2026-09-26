import ast
from pathlib import Path
import unittest


class BoundaryTests(unittest.TestCase):
    def test_no_investment_authority_or_automation_dependencies(self):
        forbidden = ("CapitalAllocation", "AllocationProposal", "HumanApproval", "OrderIntent", "BrokerExecution", "JOOAutomation", "joo_", "CapitalBucket", "RiskBudget")
        for path in Path(__file__).resolve().parents[1].glob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [x.name for x in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                for module in modules:
                    self.assertFalse(module.startswith(forbidden), (path, module))

    def test_replay_has_no_provider_refresh_calls(self):
        from OperationalCioCycle import service
        import inspect
        source = inspect.getsource(service.replay_cycle)
        for forbidden in ("execute(", "collect(", "run_kb_portfolio_vertical_slice(", "produce("):
            self.assertNotIn(forbidden, source)
