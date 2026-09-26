from __future__ import annotations

import ast
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def production_paths(package: Path):
    return tuple(p for p in package.rglob("*.py") if "tests" not in p.parts)


class BoundaryTests(unittest.TestCase):
    def test_no_joo_automation_dependency(self):
        imported = set()
        for path in production_paths(ROOT):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
        self.assertNotIn("joo_auto", imported)
        self.assertNotIn("JOOAutomation", imported)

    def test_cancel_modify_deferred_no_auto(self):
        from BrokerExecutionCycle.cancel_modify import (
            CANCEL_MODIFY_POLICY,
            assert_no_auto_cancel_modify,
        )

        self.assertEqual(CANCEL_MODIFY_POLICY, "DEFERRED_NO_AUTO_POLICY")
        with self.assertRaises(RuntimeError):
            assert_no_auto_cancel_modify()

    def test_preserved_docs_hashes_unchanged(self):
        expected = {
            "docs/JOO_PRODUCT_ARCHITECTURE.md": (
                "bb745ebb8f1ca21a114cbe980aa67fa5b97a41423a9c7d0233921fd4e4b3bfa3"
            ),
            "docs/automation/AUTOMATION_M3_HUMAN_GATED_GIT_EXECUTOR_ARCHITECTURE.md": (
                "fd32ae81147cdcc8156dd277cccd0fa4193dd8ffd6775249bd0ef2f8da9f16cf"
            ),
        }
        for rel, digest in expected.items():
            data = (REPO / rel).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_block_b_does_not_import_broker_execution(self):
        for package in ("CapitalAllocationCycle", "KbCapitalFactAuthority"):
            for path in production_paths(REPO / package):
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    modules = []
                    if isinstance(node, ast.Import):
                        modules = [a.name for a in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        modules = [node.module or ""]
                    for module in modules:
                        self.assertFalse(
                            module.startswith("BrokerExecutionCycle"),
                            (package, path, module),
                        )


if __name__ == "__main__":
    unittest.main()
