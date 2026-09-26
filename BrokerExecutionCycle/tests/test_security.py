from __future__ import annotations

import ast
import unittest
from pathlib import Path

from BrokerExecutionCycle.account_binding import seal_verified_execution_account_binding
from BrokerExecutionCycle.tests.helpers import NOW


ROOT = Path(__file__).resolve().parents[1]


def production_paths():
    return tuple(p for p in ROOT.rglob("*.py") if "tests" not in p.parts)


class SecurityTests(unittest.TestCase):
    def test_no_secrets_in_account_binding(self):
        with self.assertRaises(ValueError):
            seal_verified_execution_account_binding(
                binding_id="b",
                account_selector="a",
                gnl_ac_no1="400277078",
                verified_at=NOW,
                verification_method="hts_pwd_check",
            )

    def test_no_float_uuid_second_db_or_live_default(self):
        source = "\n".join(p.read_text() for p in production_paths())
        for forbidden in (
            "float(",
            "uuid4",
            "sqlite3.connect",
            "CREATE TABLE",
            "developer.kbsec.com",
        ):
            self.assertNotIn(forbidden, source)

    def test_mutation_transport_live_disabled_default(self):
        from BrokerExecutionCycle.mutation_transport import default_mutation_transport

        t = default_mutation_transport()
        self.assertEqual(t.mode, "LIVE_DISABLED")

    def test_no_automation_controller_bridge_imports(self):
        imported = set()
        for path in production_paths():
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(a.name.split(".")[0] for a in node.names)
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


if __name__ == "__main__":
    unittest.main()
