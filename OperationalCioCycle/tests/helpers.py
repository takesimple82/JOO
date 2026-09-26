import json
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from AIAdapter.providers.grok import GrokAdapter
from AIAdapter.providers.claude import ClaudeAdapter
from types import SimpleNamespace
from Committee.runtime import CommitteeRuntime
from ExecutionEngine.base import ExecutionEngine
from PipelineRuntime.runtime import PipelineRuntime
from ResearchOrchestrator.orchestrator import ResearchOrchestrator
from FactStore.store import FactStore
from FactStore.sqlite_storage import SQLiteAppendOnlyFactEngine
from InvestmentResearchOrchestrator.committee_manager import StaticCommitteeRouter
from InvestmentResearchOrchestrator.models.assignment import StaticRoutingTable
from InvestmentResearchOrchestrator.models.collection import CollectionBinding
from InvestmentResearchOrchestrator.models.prompt import PromptTemplate
from InvestmentResearchOrchestrator.evidence_store import EvidenceStore
from InvestmentResearchOrchestrator.evidence_collector import EvidenceCollector
from InvestmentResearchOrchestrator.execution_adapter import M22Adapter
from InvestmentResearchOrchestrator.prompt_planner import PromptFreeze
from InvestmentResearchOrchestrator.planner import ResearchPlanner
from InvestmentResearchOrchestrator.scanner import PortfolioScanner
from InvestmentResearchOrchestrator.memory_comparison import MemoryComparison
from InvestmentResearchOrchestrator.contradiction_engine import ContradictionEngine
from InvestmentResearchOrchestrator.re_research import make_re_research_budget
from InvestmentResearchOrchestrator.run_coordinator import RunCoordinator
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from InvestmentDecisionVerticalSlice.models import SemanticProducerProvenance
from PortfolioDomain.models import PortfolioSubject
from PortfolioImpactInterpretationPolicy.models import PortfolioImpactInterpretationPolicy, PortfolioImpactDirection
from PortfolioSnapshotProducer.production import PortfolioSnapshotProducer
from PortfolioSnapshotProducer.models import ExplicitPortfolioWatchlistMembershipDeclaration
from ProviderGateway.adapters.kb_open_api import KbOpenApiAdapter
from ProviderGateway.tests.test_kb_openapi_live_broker_transport import make_transport, RecordingHttp, http_json, oauth_success_payload, FAKE_CREDENTIAL
from KbPortfolioVerticalSlice.tests.test_vertical_slice import COLLECTED, collect_request, normalization_request, payload, run_model
from KbPortfolioVerticalSlice.models import ExplicitSnapshotIdentity, ExplicitVerticalSlicePolicy
from OperationalCioCycle.models import CandidateAdmission, CycleConfig, SemanticBinding, SubjectPlan
from OperationalCioCycle.codec import decode
from OperationalCioCycle.service import run_operational_cio_cycle

NOW = COLLECTED


def semantic_payload(subject, horizon, evidence, payoff="9"):
    return dict(subject_id=subject, horizon_id=horizon, evidence_ids=list(evidence), numeric_signal_ids=[],
        hypothesis="Research hypothesis", thesis="Research thesis", thesis_state="STRENGTHENED",
        material_change="Committee evidence changed", rationale="Explicit assumptions support this interpretation",
        direction="beneficial", uncertainty="COMPLETE",
        outcomes=[dict(statement="scenario", probability="1", payoff=payoff)])


class ProviderHttp:
    """Only external HTTP is replaced; provider, engine, pipeline and IRO are real."""
    def __init__(self):
        self.calls = []
        self.mutate = None
        self.research_content = "Verified input merits research; this is interpretation."

    def post(self, **kwargs):
        self.calls.append(kwargs)
        prompt = kwargs["payload"]["messages"][0]["content"]
        if prompt.startswith("Return ONLY"):
            context = json.loads(prompt.split("\n", 1)[1])
            req, plan = decode(context["request"]), decode(context["plan"])
            value = semantic_payload(plan.subject.subject_id, plan.horizon_id, req.allowed_evidence_ids,
                "8" if plan.subject.subject_id == "subject-samsung" else "9")
            if self.mutate:
                value = self.mutate(value)
            content = json.dumps(value) if type(value) is dict else value
        else:
            content = self.research_content
        return {"choices": [{"message": {"content": content}}]}


class Fixture:
    def __init__(self, directory):
        self.path = Path(directory)
        self.engine = SQLiteAppendOnlyFactEngine(self.path / "facts.sqlite3")
        self.store = FactStore(lambda: NOW, self.engine)
        self.journal = DecisionJournal(self.path / "decisions.sqlite3")
        self.http = ProviderHttp()
        self.grok = GrokAdapter(self.http, api_key="offline-test", model="configured-model")
        def create(**kwargs):
            value = self.http.post(payload=kwargs)
            return SimpleNamespace(content=[SimpleNamespace(text=value["choices"][0]["message"]["content"])])
        self.chatgpt = ClaudeAdapter(client=SimpleNamespace(messages=SimpleNamespace(create=create)), model="other-model")
        self.evidence_store = EvidenceStore(self.path / "evidence")
        self.coordinator = RunCoordinator(scanner=PortfolioScanner(), planner=ResearchPlanner(),
            committee_router=StaticCommitteeRouter(StaticRoutingTable((("HOLDING_STRUCTURAL", ("a", "b")), ("WATCHLIST_STRUCTURAL", ("a", "b")), ("CANDIDATE_RESEARCH", ("a", "b"))))),
            prompt_freeze=PromptFreeze(), execution_adapter=M22Adapter(ResearchOrchestrator(PipelineRuntime(CommitteeRuntime(ExecutionEngine((self.grok, self.chatgpt)))))),
            evidence_collector=EvidenceCollector(), evidence_store=self.evidence_store, memory_comparison=MemoryComparison(),
            contradiction_engine=ContradictionEngine(), re_research_budget=make_re_research_budget(max_attempts=1))
        self.kb_http = RecordingHttp([http_json(oauth_success_payload()), http_json(payload())])
        request = collect_request()
        broker = KbOpenApiAdapter(request.binding, make_transport(self.kb_http, clock=lambda: NOW), lambda _: FAKE_CREDENTIAL, lambda: NOW)
        self.arguments = dict(adapter=broker, collect_request=request, raw_fact_id="raw-fact-001", normalization_request=normalization_request(),
            fact_store=self.store, snapshot_producer=PortfolioSnapshotProducer(self.store, lambda: NOW),
            snapshot_identity=ExplicitSnapshotIdentity("snapshot-001", "context-001", "portfolio-main"),
            watchlist_memberships=(ExplicitPortfolioWatchlistMembershipDeclaration("candidate"), ExplicitPortfolioWatchlistMembershipDeclaration("watch-only")),
            policy=ExplicitVerticalSlicePolicy(timedelta(minutes=5)), run=run_model("snapshot-001"), prior_snapshot=None,
            ingress_id="ingress-001", coordinator=self.coordinator,
            iro_run_arguments=dict(templates_by_committee={x: PromptTemplate("research", "1", b"Research {subject_id}") for x in ("a", "b")},
                bindings_by_committee={x: {"subject_id": "wrong-caller-subject"} for x in ("a", "b")},
                provider_by_committee={"a": "grok", "b": "claude"}, collection_binding=CollectionBinding("market", "2026-09-22", "2026-09-22", "unverified")))
        self.subjects = tuple(PortfolioSubject(x, x) for x in ("subject-samsung", "candidate", "watch-only"))
        self.admissions = (CandidateAdmission(self.subjects[1], "explicit-admission", "human-config-v1"),)
        policy = PortfolioImpactInterpretationPolicy("impact", "1", tuple(PortfolioImpactDirection), ("1Y", "3Y"), True)
        binding = SemanticBinding("synthesis", "grok", SemanticProducerProvenance("semantic-adapter", "configured-model", "probability-v1", "prompt-v1"), "semantic-adapter", "probability-v1")
        self.plans = tuple(SubjectPlan(x, "1Y", "return", policy, binding) for x in self.subjects[:2])
        self.config = CycleConfig("cycle", "snapshot-001", "run-001", "universe", "eligibility-v1", "strict-v1", self.journal.journal_identity, timedelta(minutes=5))

    def run(self, **kwargs):
        args = dict(config=self.config, first_slice_arguments=self.arguments, subjects=self.subjects,
            admissions=self.admissions, plans=self.plans, providers={"grok": self.grok}, journal=self.journal, clock=lambda: NOW)
        args.update(kwargs)
        with patch("InvestmentResearchOrchestrator.run_coordinator.utc_now", return_value=NOW), patch("InvestmentResearchOrchestrator.run_coordinator.datetime") as clock:
            clock.now.return_value = NOW
            return run_operational_cio_cycle(**args)

    def close(self):
        self.journal.close()
        self.engine.close()
