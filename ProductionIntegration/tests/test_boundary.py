from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "ProductionIntegration"


class BoundaryTests(unittest.TestCase):
    def test_no_generic_orchestration_or_automation_dependency(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PACKAGE.glob("*.py")
        )
        for forbidden in (
            "JOO-Automation", "Controller", "LoopCore", "MilestoneSelectionEngine",
            "RecoveryCore", "Materializer", "WriteModelB",
        ):
            self.assertNotIn(forbidden, text)

    def test_no_second_database_or_ev_allocation_execution_engine(self):
        files = {path.name for path in PACKAGE.glob("*.py")}
        self.assertNotIn("sqlite_storage.py", files)
        self.assertNotIn("ev.py", files)
        self.assertNotIn("allocator.py", files)
        self.assertNotIn("execution.py", files)
        journal = (PACKAGE / "journal.py").read_text(encoding="utf-8")
        self.assertIn("DecisionJournal", journal)
        self.assertNotIn("sqlite3", journal)

    def test_production_entrypoint_has_no_mutation_transport_parameter(self):
        import inspect
        from BrokerExecutionCycle.mutation_transport import default_mutation_transport
        from ProductionIntegration.service import run_one_joo_command_center_cycle

        self.assertNotIn("transport", inspect.signature(run_one_joo_command_center_cycle).parameters)
        self.assertEqual(default_mutation_transport().mode, "LIVE_DISABLED")

    def test_no_float_and_exact_ev_not_reimplemented(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE.glob("*.py"))
        self.assertNotIn("float(", text)
        self.assertNotIn("expected_value =", text)
        self.assertNotIn("probability *", text)


if __name__ == "__main__":
    unittest.main()
