import tempfile
import unittest
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from InvestmentDecisionVerticalSlice.models import CioActionPosture, ComparisonStatus, NumericSignalReference
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from OperationalCioCycle.codec import decode, encode
from OperationalCioCycle.models import CandidateAdmission
from OperationalCioCycle.service import replay_cycle, _derive
from OperationalCioCycle.universe import build_universe
from OperationalCioCycle.tests.helpers import Fixture, NOW


class CycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = Fixture(self.tmp.name)

    def tearDown(self):
        self.f.close()
        self.tmp.cleanup()

    def test_real_full_composition_restart_and_replay_without_providers(self):
        result = self.f.run()
        self.assertEqual(len(self.f.kb_http.calls), 2)
        self.assertEqual(len(self.f.http.calls), 8)  # 3 subjects × 2 committees + 2 synthesis calls
        self.assertEqual([e.ev_record.calculation.expected_value.value for e in result.evaluations], [Decimal("8"), Decimal("9")])
        self.assertIs(result.comparisons[0].status, ComparisonStatus.RIGHT_SUPERIOR)
        self.assertIs(result.decisions[0].posture, CioActionPosture.CONSIDER_ROTATION)
        self.assertTrue(all(x.executable is False for x in result.decisions))
        self.assertEqual([m.eligible for m in result.universe.members], [True, True, False])
        self.assertEqual(result.universe.members[1].sources, ("watchlist", "explicit_candidate"))
        self.f.journal.close()
        self.f.journal = DecisionJournal(self.f.path / "decisions.sqlite3")
        with patch("OperationalCioCycle.service.run_kb_portfolio_vertical_slice", side_effect=AssertionError("broker replay")), patch("OperationalCioCycle.semantic.ExecutionEngine.execute", side_effect=AssertionError("AI replay")):
            self.assertEqual(replay_cycle(self.f.journal, "cycle", self.f.config.journal_id), result)
        self.assertEqual(len(self.f.journal.list_records()), 1)

    def test_first_to_iro_prompt_subject_and_snapshot_binding(self):
        self.f.run()
        prompts = [c["payload"]["messages"][0]["content"] for c in self.f.http.calls[:6]]
        self.assertTrue(all("wrong-caller-subject" not in p and "snapshot-001" in p for p in prompts))
        self.assertIn('"holding_quantities":["10"]', prompts[0])
        self.assertIn("Research candidate", prompts[2])

    def test_existing_exact_ev_is_called(self):
        from ExactExpectedValue.calculation import calculate_exact_expected_value
        with patch("InvestmentDecisionVerticalSlice.ev_integration.calculate_exact_expected_value", wraps=calculate_exact_expected_value) as calculate:
            self.f.run()
            self.assertEqual(calculate.call_count, 2)

    def test_duplicate_completion_fails_before_external_calls(self):
        self.f.run()
        calls = len(self.f.http.calls)
        with self.assertRaisesRegex(ValueError, "already completed"):
            self.f.run()
        self.assertEqual(len(self.f.http.calls), calls)

    def test_cross_horizon_incomparable_with_separate_decisions(self):
        result = self.f.run(plans=(self.f.plans[0], replace(self.f.plans[1], horizon_id="3Y")))
        self.assertIs(result.comparisons[0].status, ComparisonStatus.INCOMPARABLE)
        self.assertEqual(len(result.decisions), 2)
        self.assertTrue(all(x.superior_opportunity_id is None for x in result.decisions))

    def test_stale_before_semantic(self):
        with self.assertRaisesRegex(ValueError, "stale"):
            self.f.run(clock=lambda: NOW + timedelta(minutes=6))
        self.assertEqual(len(self.f.http.calls), 6)
        self.assertEqual(self.f.journal.list_records(), ())

    def test_latency_expiry_rolls_back_decision(self):
        moments = iter((NOW, NOW + timedelta(minutes=6)))
        with self.assertRaisesRegex(ValueError, "expired"):
            self.f.run(clock=lambda: next(moments))
        self.assertEqual(self.f.journal.list_records(), ())

    def test_provider_model_binding_rejected(self):
        self.f.grok.model = "wrong-model"
        with self.assertRaisesRegex(ValueError, "model mismatch"):
            self.f.run()
        self.assertEqual(self.f.journal.list_records(), ())

    def test_incomplete_iro_and_contradiction(self):
        self.f.http.research_content = ""
        with self.assertRaisesRegex(ValueError, "IRO incomplete"):
            self.f.run()
        self.assertEqual(self.f.journal.list_records(), ())

    def test_wrong_numeric_signal_object(self):
        bad = replace(self.f.plans[0], numeric_signals=(NumericSignalReference("n", object()),))
        with self.assertRaisesRegex(TypeError, "ExactNumericDeltaSignalClassification"):
            self.f.run(plans=(bad, self.f.plans[1]))

    def test_semantic_attack_table(self):
        # Run the real composition once, then attack its exact admitted context.
        self.f.run()
        payload = self.f.journal.list_records()[0].payload
        inputs, contents = decode(payload["inputs"]), decode(payload["contents"])
        import json
        base = json.loads(contents[0])
        attacks = [dict(base, evidence_ids=["hallucinated"]), dict(base, numeric_signal_ids=["invented"]),
            dict(base, subject_id="outside"), dict(base, horizon_id="wrong"), dict(base, ev="999"),
            dict(base, outcomes=[]), dict(base, uncertainty="UNRESOLVED"),
            dict(base, outcomes=[dict(statement="a", probability="0.9", payoff="10")]),
            dict(base, outcomes=[dict(statement="a", probability=1.0, payoff="10")]),
            dict(base, outcomes=[dict(statement="a", probability="1", payoff="NaN")])]
        for attack in attacks:
            with self.subTest(attack=attack), self.assertRaises((ValueError, TypeError)):
                _derive(inputs, stored_contents=(json.dumps(attack), contents[1]))
        for text in ("not JSON", '{"subject_id":"a","subject_id":"b"}'):
            with self.assertRaises(ValueError):
                _derive(inputs, stored_contents=(text, contents[1]))

    def test_universe_duplicate_empty_stale_ineligible_and_identity_attacks(self):
        self.f.run()
        inputs = decode(self.f.journal.list_records()[0].payload["inputs"])
        config, first = inputs[:2]
        for subjects, admissions in ((self.f.subjects + (self.f.subjects[0],), self.f.admissions),
                ((), ()), (self.f.subjects, self.f.admissions * 2),
                (self.f.subjects, (CandidateAdmission(replace(self.f.subjects[1], display_name="forged"), "a", "p"),))):
            with self.assertRaises(ValueError):
                build_universe(config, first.snapshot, subjects, admissions, NOW)
        with self.assertRaisesRegex(ValueError, "snapshot"):
            build_universe(replace(config, snapshot_id="old"), first.snapshot, self.f.subjects, self.f.admissions, NOW)
        bad_inputs = list(inputs)
        bad_inputs[6] = (self.f.plans[0], replace(self.f.plans[1], subject=self.f.subjects[2]))
        with self.assertRaisesRegex(ValueError, "ineligible"):
            _derive(tuple(bad_inputs), stored_contents=("", ""))

    def test_per_subject_evidence_and_completeness_attacks(self):
        self.f.run()
        payload = self.f.journal.list_records()[0].payload
        inputs, contents = decode(payload["inputs"]), decode(payload["contents"])
        from InvestmentResearchOrchestrator.models.enums import EvidencePayloadKind as K
        for kind in (K.FINDING, K.COMPLETENESS, K.CONTRADICTION_EVALUATION):
            bad = list(inputs)
            bad[2] = tuple(r for r in inputs[2] if r.payload_kind is not kind)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                _derive(tuple(bad), stored_contents=contents)
        self.assertEqual(len(self.f.journal.list_records()), 1)

    def test_journal_failure_does_not_persist_partial_cycle(self):
        with patch.object(self.f.journal, "_append_locked", side_effect=RuntimeError("disk failure")):
            with self.assertRaisesRegex(RuntimeError, "disk failure"):
                self.f.run()
        self.assertFalse(self.f.journal._connection.in_transaction)
        self.assertEqual(self.f.journal.list_records(), ())

    def test_codec_rejects_unknown_types_and_float(self):
        for value in (0.1, float("nan"), object()):
            with self.assertRaises(TypeError):
                encode(value)
        with self.assertRaises(ValueError):
            decode({"type": "os.system", "fields": {}})

    def test_foreign_and_null_finding_prompt_provenance_rejected(self):
        self.f.run()
        payload = self.f.journal.list_records()[0].payload
        inputs, contents = decode(payload["inputs"]), decode(payload["contents"])
        from InvestmentResearchOrchestrator.models.enums import EvidencePayloadKind as K
        for changes in ({"prompt_hash": "0" * 64}, {"prompt_hash": None}, {"prompt_id": "foreign"}, {"provider_id": "foreign", "source_reference": "foreign"}, {"collected_at": None}):
            bad = list(inputs)
            bad[2] = tuple(replace(r, **changes) if r.payload_kind is K.FINDING else r for r in inputs[2])
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                _derive(tuple(bad), stored_contents=contents)

    def test_old_wave_cannot_be_relabelled_current(self):
        self.f.run()
        payload = self.f.journal.list_records()[0].payload
        inputs, contents = decode(payload["inputs"]), decode(payload["contents"])
        import json
        from InvestmentResearchOrchestrator.models.enums import EvidencePayloadKind as K
        bad = list(inputs)
        iro = inputs[1].iro_result
        artifacts = tuple(replace(a, attempt_index=1) for a in iro.freeze_artifacts)
        bad[1] = replace(inputs[1], iro_result=replace(iro, re_research_attempt=1, freeze_artifacts=artifacts))
        bad[2] = tuple(replace(r, payload=json.dumps(dict(json.loads(r.payload), attempt=1))) if r.payload_kind is K.CONTRADICTION_EVALUATION else r for r in inputs[2])
        with self.assertRaisesRegex(ValueError, "current wave"):
            _derive(tuple(bad), stored_contents=contents)

    def test_current_research_wave_replay_and_old_wave_isolation(self):
        # A resolved later wave can reuse the same stored semantic outputs, but
        # every plan/record/freeze/current contradiction binding must agree.
        self.f.run()
        payload = self.f.journal.list_records()[0].payload
        inputs, contents = decode(payload["inputs"]), decode(payload["contents"])
        import json
        from InvestmentResearchOrchestrator.models.enums import EvidencePayloadKind as K
        iro = inputs[1].iro_result
        old_to_new = {u.research_id: u.research_id.replace(":unit:", ":attempt:1:unit:") for u in iro.plan.units}
        plan = replace(iro.plan, units=tuple(replace(u, research_id=old_to_new[u.research_id]) for u in iro.plan.units))
        artifacts = tuple(replace(a, research_id=old_to_new[a.research_id], attempt_index=1) for a in iro.freeze_artifacts)
        records = []
        for r in inputs[2]:
            if r.payload_kind is K.DECISION_RESEARCH_ADMISSION:
                continue
            data = json.loads(r.payload)
            if r.payload_kind is K.CONTRADICTION_EVALUATION:
                data["attempt"] = 1
            if r.payload_kind is K.PROMPT_FREEZE:
                data["attempt_index"] = 1
            if r.payload_kind is K.FINDING:
                data["finding_id"] = f"{old_to_new[r.research_id]}:{r.committee_id}:0"
            records.append(replace(r, research_id=old_to_new.get(r.research_id, r.research_id), payload=json.dumps(data)))
        bad = list(inputs)
        contradiction = replace(iro.contradiction, attempt=1, re_research_requests=replace(iro.contradiction.re_research_requests, attempt=1))
        bad[1] = replace(inputs[1], iro_result=replace(iro, re_research_attempt=1, plan=plan, freeze_artifacts=artifacts, contradiction=contradiction))
        bad[2] = inputs[2] + tuple(records)
        current_contents = tuple(text.replace(":unit:", ":attempt:1:unit:") for text in contents)
        replayed, _, _ = _derive(tuple(bad), stored_contents=current_contents)
        self.assertEqual(len(replayed.evaluations), 2)

    def test_cio_carries_all_semantic_output_ids(self):
        result = self.f.run()
        decision = result.decisions[0]
        expected = tuple(e.ev_record.source.semantic_output_id for e in result.evaluations)
        self.assertEqual(decision.semantic_output_ids, expected)
        self.assertIn(decision.semantic_output_id, expected)

    def test_configured_probability_and_producer_authority(self):
        for binding in (replace(self.f.plans[0].binding, producer_id="forged"), replace(self.f.plans[0].binding, probability_policy_version="other")):
            from OperationalCioCycle.semantic import validate_plan
            with self.assertRaisesRegex(ValueError, "producer/probability"):
                validate_plan(replace(self.f.plans[0], binding=binding))

    def test_physical_journal_binding(self):
        with self.assertRaisesRegex(ValueError, "physical journal"):
            self.f.run(config=replace(self.f.config, journal_id="invented"))
        self.assertEqual(self.f.kb_http.calls, [])

    def test_symmetric_strict_no_incumbent_bonus(self):
        from InvestmentDecisionVerticalSlice.opportunity_comparison import compare_opportunities
        result = self.f.run()
        a, b = result.evaluations
        self.assertIs(compare_opportunities("reverse", b, a).status, ComparisonStatus.LEFT_SUPERIOR)
        self.assertIs(compare_opportunities("roles", replace(a, role=b.role), replace(b, role=a.role)).status, ComparisonStatus.RIGHT_SUPERIOR)

    def test_equal_ev_no_rotation(self):
        self.f.http.mutate = lambda value: dict(value, outcomes=[dict(statement="exact", probability="1", payoff="8")])
        result = self.f.run()
        self.assertIs(result.comparisons[0].status, ComparisonStatus.EQUAL)
        self.assertIsNone(result.decisions[0].superior_opportunity_id)

    def test_unit_and_probability_policy_isolation(self):
        self.f.run()
        payload = self.f.journal.list_records()[0].payload
        inputs, contents = decode(payload["inputs"]), decode(payload["contents"])
        for plan in (replace(self.f.plans[1], unit_id="USD"), replace(self.f.plans[1], binding=replace(self.f.plans[1].binding,
                probability_policy_version="other", provenance=replace(self.f.plans[1].binding.provenance, policy_version="other")))):
            altered = list(inputs)
            altered[6] = (self.f.plans[0], plan)
            result, _, _ = _derive(tuple(altered), stored_contents=contents)
            self.assertIs(result.comparisons[0].status, ComparisonStatus.INCOMPARABLE)
            self.assertEqual(len(result.decisions), 2)

    def test_exact_decimal_not_float_rounded(self):
        self.f.http.mutate = lambda value: dict(value, outcomes=[dict(statement="up", probability="0.6", payoff="20.00000000000000000000001"), dict(statement="down", probability="0.4", payoff="-10")])
        result = self.f.run()
        self.assertEqual(result.evaluations[0].ev_record.calculation.expected_value.value, Decimal("8.000000000000000000000006"))

    def test_provider_unavailable_and_malformed_output_never_persist(self):
        self.f.http.mutate = lambda value: "not valid JSON"
        with self.assertRaises(ValueError):
            self.f.run()
        self.assertEqual(self.f.journal.list_records(), ())

    def test_single_provider_committee_cannot_authorize_cio(self):
        self.f.arguments["iro_run_arguments"]["provider_by_committee"] = {"a": "grok", "b": "grok"}
        with self.assertRaisesRegex(ValueError, "independent configured providers"):
            self.f.run()
        self.assertEqual(self.f.journal.list_records(), ())

    def test_explicit_candidate_outside_watchlist_completes_without_snapshot_mutation(self):
        self.f.arguments["watchlist_memberships"] = self.f.arguments["watchlist_memberships"][1:]
        result = self.f.run()
        member = next(x for x in result.universe.members if x.subject.subject_id == "candidate")
        self.assertEqual(member.sources, ("explicit_candidate",))
        self.assertTrue(member.eligible)
        inputs = decode(self.f.journal.list_records()[0].payload["inputs"])
        self.assertEqual([x.membership.portfolio_subject_id for x in inputs[1].snapshot.watchlist_entries], ["watch-only"])
        unit = next(x for x in inputs[1].iro_result.plan.units if x.subject_id == "candidate")
        self.assertEqual(unit.task_type, "CANDIDATE_RESEARCH")
        self.assertEqual(len(result.evaluations), 2)
        self.assertEqual(replay_cycle(self.f.journal, "cycle", self.f.config.journal_id), result)

    def test_outside_candidate_without_admission_cannot_enter_universe(self):
        self.f.arguments["watchlist_memberships"] = self.f.arguments["watchlist_memberships"][1:]
        with self.assertRaisesRegex(ValueError, "identity coverage"):
            self.f.run(admissions=())
        self.assertEqual(self.f.journal.list_records(), ())

    def test_candidate_admission_provenance_cannot_change_on_replay(self):
        self.f.run()
        payload = self.f.journal.list_records()[0].payload
        inputs = list(decode(payload["inputs"]))
        inputs[5] = (replace(self.f.admissions[0], provenance="forged"),)
        with self.assertRaisesRegex(ValueError, "admission/universe"):
            _derive(tuple(inputs), stored_contents=decode(payload["contents"]))

    def test_tied_superior_candidates_are_not_arbitrarily_selected(self):
        admissions = self.f.admissions + (CandidateAdmission(self.f.subjects[2], "admit-two", "explicit-v1"),)
        plans = self.f.plans + (replace(self.f.plans[1], subject=self.f.subjects[2]),)
        result = self.f.run(admissions=admissions, plans=plans)
        self.assertIs(result.decisions[0].posture, CioActionPosture.NO_ACTION_UNRESOLVED)
        self.assertIsNone(result.decisions[0].superior_opportunity_id)
        self.assertEqual(result.decisions[0].unresolved_reasons, ("AMBIGUOUS_TOP_OPPORTUNITY",))


if __name__ == "__main__":
    unittest.main()
