from __future__ import annotations
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from ExpectedValueAssumptionSet.models import ExplicitExpectedValueAssumptionSet, ExplicitExpectedValueOutcomeAssumption
from ExplicitHypothesis.models import ExplicitHypothesis
from ExplicitPortfolioImpact.models import ExplicitPortfolioImpact
from ExplicitThesis.models import ExplicitThesis
from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactInterpretationPolicy.models import PortfolioImpactDirection, PortfolioImpactInterpretationPolicy
from SemanticHypothesisProduction.models import SemanticallyProducedHypothesis
from SemanticPortfolioImpactProduction.models import SemanticallyProducedPortfolioImpact
from SemanticThesisProduction.models import SemanticallyProducedThesis
from ThesisPortfolioSubjectLink.models import ExplicitThesisPortfolioSubjectLink

from InvestmentDecisionVerticalSlice.cio_synthesis import synthesize_cio_decision
from InvestmentDecisionVerticalSlice.ev_integration import calculate_admitted_ev, replay_exact_ev
from InvestmentDecisionVerticalSlice.models import *
from InvestmentDecisionVerticalSlice.opportunity_comparison import compare_opportunities, replay_comparison
from InvestmentDecisionVerticalSlice.semantic_admission import produce_and_admit_semantics
from InvestmentDecisionVerticalSlice.validation import validate_cio_decision, validate_semantic_output

NOW=datetime(2026,9,22,tzinfo=timezone.utc)
PROV=SemanticProducerProvenance("committee-synth","model-1","probability-v1","prompt-v1")

def bundle(**kw):
    vals=dict(bundle_id="bundle-1",iro_run_id="run-1",portfolio_snapshot_id="snap-1",evidence=(ResearchEvidenceReference("e1","r1","c1","s1",TruthClass.RESEARCH_AI,"changed"),ResearchEvidenceReference("e2","r1","c2","s1",TruthClass.RESEARCH_AI,"confirmed")),required_committees=("c1","c2"),completed_committees=("c1","c2"),unresolved_contradiction_ids=(),fresh=True); vals.update(kw); return ResearchEvidenceBundle(**vals)

def impact():
    thesis=SemanticallyProducedThesis(ExplicitThesis("t1","thesis"))
    subject=PortfolioSubject("s1","Subject")
    return ExplicitPortfolioImpact("i1",thesis,ExplicitThesisPortfolioSubjectLink("t1","s1"),subject,PortfolioImpactInterpretationPolicy("p","1",(PortfolioImpactDirection.BENEFICIAL,),("1Y","3Y"),True),PortfolioImpactDirection.BENEFICIAL,"1Y","evidence supports")

def output(**kw):
    imp=impact(); aset=ExplicitExpectedValueAssumptionSet("a1",SemanticallyProducedPortfolioImpact(imp),"return",(ExplicitExpectedValueOutcomeAssumption("up","up",Decimal("0.6"),Decimal("20")),ExplicitExpectedValueOutcomeAssumption("down","down",Decimal("0.4"),Decimal("-10"))))
    vals=dict(output_id="o1",request_id="q1",qualitative_signals=(QualitativeEvidenceSignal("qs1","s1",("e1","e2"),"material change",PROV),),consumed_numeric_signal_ids=(),hypothesis=SemanticallyProducedHypothesis(ExplicitHypothesis("h1","hypothesis")),thesis=imp.semantic_thesis,thesis_state=ThesisState.STRENGTHENED,impact=imp,assumption_set=aset,consumed_evidence_ids=("e1","e2"),uncertainty_status=UncertaintyStatus.COMPLETE,provenance=PROV); vals.update(kw); return SemanticProductionOutput(**vals)

def request(b=None): return SemanticProductionRequest("q1",b or bundle(),("e1","e2"),(),("1Y","3Y"))

class Producer:
    def __init__(self,value): self.value=value
    def produce(self,request): return self.value

class DecisionPathTests(unittest.TestCase):
    def test_semantic_allowlist_and_provenance(self):
        self.assertEqual(produce_and_admit_semantics(Producer(output()),request()).output_id,"o1")
        bad=replace(output(),consumed_evidence_ids=("invented",))
        with self.assertRaisesRegex(ValueError,"hallucinated evidence"):
            validate_semantic_output(request(),bad)

    def test_missing_committee_and_contradiction_block_assumptions(self):
        for b in (bundle(completed_committees=("c1",)),bundle(unresolved_contradiction_ids=("cx",))):
            with self.assertRaises(ValueError):
                validate_semantic_output(request(b),output())

    def test_float_probability_rejected_and_no_residual_fill(self):
        aset=output().assumption_set
        bad=replace(aset,outcomes=(replace(aset.outcomes[0],probability=0.6),aset.outcomes[1]))
        with self.assertRaises(TypeError): validate_semantic_output(request(),replace(output(),assumption_set=bad))
        mismatch=replace(aset,outcomes=(replace(aset.outcomes[0],probability=Decimal("0.5")),aset.outcomes[1]))
        with self.assertRaisesRegex(ValueError,"probability total"):
            validate_semantic_output(request(),replace(output(),assumption_set=mismatch))

    def test_exact_ev_and_replay(self):
        source=EvAssumptionProvenance("ep",output().assumption_set,"1Y",("e1","e2"),"tr","ir","o1",PROV,UncertaintyStatus.COMPLETE)
        record=calculate_admitted_ev("ev",source)
        self.assertEqual(record.calculation.expected_value.value,Decimal("8.0"))
        self.assertEqual(replay_exact_ev(record),record)

    def _opp(self,ident,role,value,horizon="1Y"):
        aset=output().assumption_set
        aset=replace(aset,outcomes=(ExplicitExpectedValueOutcomeAssumption("only","only",Decimal("1"),Decimal(value)),))
        src=EvAssumptionProvenance("ep"+ident,aset,horizon,("e1",),"tr","ir","o1",PROV,UncertaintyStatus.COMPLETE)
        ev=calculate_admitted_ev("ev"+ident,src)
        return OpportunityEvaluation(ident,"s1",role,"strict-v1","probability-v1",horizon,"return",ev)

    def test_strict_symmetric_comparison_no_incumbent_bias(self):
        holding=self._opp("hold",OpportunityRole.CURRENT_HOLDING,"8")
        candidate=self._opp("candidate",OpportunityRole.CANDIDATE,"9")
        first=compare_opportunities("c1",holding,candidate)
        second=compare_opportunities("c2",candidate,holding)
        self.assertIs(first.status,ComparisonStatus.RIGHT_SUPERIOR)
        self.assertIs(second.status,ComparisonStatus.LEFT_SUPERIOR)
        self.assertEqual(replay_comparison(first),first)

    def test_equal_incomparable_and_missing(self):
        a=self._opp("a",OpportunityRole.CURRENT_HOLDING,"8")
        b=self._opp("b",OpportunityRole.CANDIDATE,"8")
        self.assertIs(compare_opportunities("x",a,b).status,ComparisonStatus.EQUAL)
        self.assertIs(compare_opportunities("x",a,replace(b,horizon_id="3Y")).status,ComparisonStatus.INCOMPARABLE)
        self.assertIs(compare_opportunities("x",a,replace(b,ev_record=None)).status,ComparisonStatus.UNRESOLVED)

    def test_cio_posture_is_non_executable(self):
        hold=self._opp("hold",OpportunityRole.CURRENT_HOLDING,"8")
        cand=self._opp("cand",OpportunityRole.CANDIDATE,"9")
        comparison=compare_opportunities("cmp",hold,cand)
        transition=ThesisTransition("tr","s1",None,"t1",ThesisState.STRENGTHENED,("e1",),("qs1",),"o1",NOW)
        decision=synthesize_cio_decision(decision_id="d",snapshot_id="snap-1",bundle=bundle(),output=output(),transitions=(transition,),impacts=(),ev_records=(hold.ev_record,cand.ev_record),comparisons=(comparison,),what_changed="facts changed",why_it_matters="EV changed",narrative_reference_ids=("e1","cmp"))
        self.assertIs(decision.posture,CioActionPosture.CONSIDER_ROTATION)
        self.assertFalse(decision.executable)

    def test_cio_rejects_executable_true(self):
        forged = CioDecisionRecord(
            "d", "snap-1", "bundle-1", "o1", (), (), (), (), (),
            CioActionPosture.MAINTAIN, "facts changed", "EV changed", None, (), (), True,
        )
        with self.assertRaisesRegex(ValueError, "must not be executable"):
            validate_cio_decision(forged)

    def test_numeric_signal_requires_exact_object(self):
        from InvestmentDecisionVerticalSlice.validation import validate_semantic_request
        with self.assertRaisesRegex(TypeError, "ExactNumericDeltaSignalClassification"):
            validate_semantic_request(
                SemanticProductionRequest(
                    "q1", bundle(), ("e1", "e2"),
                    (NumericSignalReference("ns1", object()),),
                    ("1Y", "3Y"),
                )
            )

if __name__ == "__main__": unittest.main()
