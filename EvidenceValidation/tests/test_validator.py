import pathlib
import unittest
from unittest.mock import patch

from EvidenceValidation.validator import EvidenceValidator
from ResearchDomain.models import ResearchFinding


def make_finding() -> ResearchFinding:
    return ResearchFinding(
        finding_id="finding-001",
        research_id="research-001",
        committee_id="committee-001",
        category="financial",
        statement="Revenue increased year over year.",
        source="Company filing",
        event_date="2026-07-01",
        publication_date="2026-07-15",
        verification_status="verified",
    )


class EvidenceValidatorTests(unittest.TestCase):
    def test_valid_finding_delegates_once_and_returns_none(self):
        finding = make_finding()
        original = vars(finding).copy()

        with patch(
            (
                "EvidenceValidation.validator."
                "validate_research_finding"
            ),
            return_value=None,
        ) as domain_validator:
            result = EvidenceValidator().validate(finding)

        self.assertIsNone(result)
        domain_validator.assert_called_once_with(finding)
        self.assertIs(
            domain_validator.call_args.args[0],
            finding,
        )
        self.assertEqual(vars(finding), original)

    def test_real_domain_validation_accepts_valid_finding(self):
        finding = make_finding()
        original = vars(finding).copy()

        result = EvidenceValidator().validate(finding)

        self.assertIsNone(result)
        self.assertEqual(vars(finding), original)

    def test_domain_exception_identity_propagates_unchanged(self):
        finding = make_finding()
        error = ValueError("domain validation failed")
        result = None

        with patch(
            (
                "EvidenceValidation.validator."
                "validate_research_finding"
            ),
            side_effect=error,
        ) as domain_validator:
            try:
                result = EvidenceValidator().validate(finding)
            except ValueError as caught:
                self.assertIs(caught, error)
            else:
                self.fail("domain exception did not propagate")

        self.assertIsNone(result)
        domain_validator.assert_called_once_with(finding)

    def test_representative_domain_failures_propagate(self):
        invalid_cases = (
            (
                "wrong input type",
                object(),
                TypeError,
                "finding must be ResearchFinding",
            ),
            (
                "blank finding id",
                self._finding_with(finding_id=" "),
                ValueError,
                "finding_id must not be blank",
            ),
            (
                "incorrect event date type",
                self._finding_with(event_date=None),
                TypeError,
                "event_date must be str",
            ),
            (
                "unsupported verification status",
                self._finding_with(verification_status="pending"),
                ValueError,
                "verification_status must be verified",
            ),
        )

        for name, finding, error_type, message in invalid_cases:
            with self.subTest(case=name):
                result = None
                with self.assertRaisesRegex(error_type, message):
                    result = EvidenceValidator().validate(finding)
                self.assertIsNone(result)

    def test_validation_does_not_mutate_any_field(self):
        finding = make_finding()
        original = vars(finding).copy()

        EvidenceValidator().validate(finding)

        self.assertEqual(vars(finding), original)
        for name, value in original.items():
            self.assertIs(getattr(finding, name), value)

    def test_production_runtime_isolation(self):
        source = pathlib.Path(
            __file__
        ).parents[1].joinpath("validator.py").read_text()

        prohibited_names = (
            "ResearchOrchestrator",
            "PipelineRuntime",
            "CommitteeRuntime",
            "ExecutionEngine",
            "AIAdapter",
            "providers",
            "ResearchReport",
        )
        for name in prohibited_names:
            with self.subTest(name=name):
                self.assertNotIn(name, source)

    @staticmethod
    def _finding_with(**overrides):
        values = vars(make_finding()).copy()
        values.update(overrides)
        return ResearchFinding(**values)


if __name__ == "__main__":
    unittest.main()
