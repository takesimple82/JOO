import ast, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class BoundaryTests(unittest.TestCase):
    def test_no_automation_allocation_execution_dependencies(self):
        imports=set(); source=""
        for p in ROOT.glob("*.py"):
            source+=p.read_text(); tree=ast.parse(p.read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.Import): imports.update(x.name.split('.')[0] for x in n.names)
                elif isinstance(n,ast.ImportFrom) and n.module: imports.add(n.module.split('.')[0])
        self.assertTrue(imports.isdisjoint({"joo_auto","PortfolioAllocationLeg","PortfolioCapitalBucket","PortfolioRiskBudget"}))
        for text in ("place_order","execute_trade","allocation_quantity","position_size"):
            self.assertNotIn(text,source)
    def test_existing_core_does_not_import_slice(self):
        repo=ROOT.parent
        for name in ("InvestmentResearchOrchestrator","ExactExpectedValue","KbPortfolioVerticalSlice"):
            source="\n".join(p.read_text() for p in (repo/name).rglob("*.py") if "tests" not in p.parts)
            self.assertNotIn("InvestmentDecisionVerticalSlice",source)
if __name__ == "__main__": unittest.main()
