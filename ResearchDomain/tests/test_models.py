import pathlib
import unittest
from dataclasses import fields
from typing import get_type_hints

from PipelineRuntime.models import PipelineExecution
from ResearchDomain.models import (
    ResearchFinding,
    ResearchReport,
    ResearchTask,
)
from ResearchDomain.validation import (
    validate_research_finding,
    validate_research_report,
    validate_research_task,
)


def make_pipeline() -> PipelineExecution:
    return PipelineExecution(
        pipeline_id="pipeline-001",
        name="Research Pipeline",
        committees=[],
    )


def make_task() -> ResearchTask:
    return ResearchTask(
        research_id="research-001",
        title="Company Research",
        objective="Evaluate the investment evidence",
        priority="P1",
        pipeline=make_pipeline(),
    )


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


def make_report(
    status: str = "completed",
    error: str = "",
) -> ResearchReport:
    return ResearchReport(
        research_id="research-001",
        title="Company Research Report",
        findings=[make_finding()],
        status=status,
        error=error,
    )


class ResearchDomainModelTests(unittest.TestCase):
    def test_exact_model_contracts(self):
        self.assertEqual(
            [field.name for field in fields(ResearchTask)],
            [
                "research_id",
                "title",
                "objective",
                "priority",
                "pipeline",
            ],
        )
        self.assertEqual(
            get_type_hints(ResearchTask),
            {
                "research_id": str,
                "title": str,
                "objective": str,
                "priority": str,
                "pipeline": PipelineExecution,
            },
        )
        self.assertEqual(
            [field.name for field in fields(ResearchFinding)],
            [
                "finding_id",
                "research_id",
                "committee_id",
                "category",
                "statement",
                "source",
                "event_date",
                "publication_date",
                "verification_status",
            ],
        )
        self.assertEqual(
            get_type_hints(ResearchFinding),
            {
                "finding_id": str,
                "research_id": str,
                "committee_id": str,
                "category": str,
                "statement": str,
                "source": str,
                "event_date": str,
                "publication_date": str,
                "verification_status": str,
            },
        )
        self.assertEqual(
            [field.name for field in fields(ResearchReport)],
            [
                "research_id",
                "title",
                "findings",
                "status",
                "error",
            ],
        )
        self.assertEqual(
            get_type_hints(ResearchReport),
            {
                "research_id": str,
                "title": str,
                "findings": list[ResearchFinding],
                "status": str,
                "error": str,
            },
        )

    def test_valid_objects_return_none(self):
        self.assertIsNone(validate_research_task(make_task()))
        self.assertIsNone(
            validate_research_finding(make_finding())
        )
        self.assertIsNone(validate_research_report(make_report()))

    def test_valid_enum_values(self):
        for priority in ("P0", "P1", "P2"):
            with self.subTest(priority=priority):
                task = make_task()
                task.priority = priority
                self.assertIsNone(validate_research_task(task))

        for status in (
            "verified",
            "partially_verified",
            "unverified",
        ):
            with self.subTest(verification_status=status):
                finding = make_finding()
                finding.verification_status = status
                self.assertIsNone(
                    validate_research_finding(finding)
                )

        completed = make_report()
        failed = make_report(status="failed", error="research failed")
        self.assertIsNone(validate_research_report(completed))
        self.assertIsNone(validate_research_report(failed))

    def test_top_level_object_types(self):
        cases = (
            (
                validate_research_task,
                object(),
                "task must be ResearchTask",
            ),
            (
                validate_research_finding,
                object(),
                "finding must be ResearchFinding",
            ),
            (
                validate_research_report,
                object(),
                "report must be ResearchReport",
            ),
        )
        for validator, value, message in cases:
            with self.subTest(validator=validator.__name__):
                with self.assertRaisesRegex(TypeError, message):
                    validator(value)

    def test_research_task_string_type_validation(self):
        for field_name in (
            "research_id",
            "title",
            "objective",
            "priority",
        ):
            with self.subTest(field=field_name):
                task = make_task()
                setattr(task, field_name, None)
                with self.assertRaisesRegex(
                    TypeError,
                    f"{field_name} must be str",
                ):
                    validate_research_task(task)

    def test_research_task_blank_validation(self):
        for field_name in (
            "research_id",
            "title",
            "objective",
        ):
            for value in ("", " ", "\t", "\n"):
                with self.subTest(field=field_name, value=repr(value)):
                    task = make_task()
                    setattr(task, field_name, value)
                    with self.assertRaisesRegex(
                        ValueError,
                        f"{field_name} must not be blank",
                    ):
                        validate_research_task(task)

    def test_research_task_priority_validation(self):
        for priority in ("", "P3", "p0", "high"):
            with self.subTest(priority=priority):
                task = make_task()
                task.priority = priority
                with self.assertRaisesRegex(
                    ValueError,
                    "priority must be P0, P1, or P2",
                ):
                    validate_research_task(task)

    def test_research_task_pipeline_type_validation(self):
        task = make_task()
        task.pipeline = object()

        with self.assertRaisesRegex(
            TypeError,
            "pipeline must be PipelineExecution",
        ):
            validate_research_task(task)

    def test_research_finding_all_string_types(self):
        field_names = (
            "finding_id",
            "research_id",
            "committee_id",
            "category",
            "statement",
            "source",
            "event_date",
            "publication_date",
            "verification_status",
        )
        for field_name in field_names:
            with self.subTest(field=field_name):
                finding = make_finding()
                setattr(finding, field_name, None)
                with self.assertRaisesRegex(
                    TypeError,
                    f"{field_name} must be str",
                ):
                    validate_research_finding(finding)

    def test_research_finding_all_blank_strings(self):
        field_names = (
            "finding_id",
            "research_id",
            "committee_id",
            "category",
            "statement",
            "source",
            "event_date",
            "publication_date",
            "verification_status",
        )
        for field_name in field_names:
            for value in ("", " ", "\t", "\n"):
                with self.subTest(field=field_name, value=repr(value)):
                    finding = make_finding()
                    setattr(finding, field_name, value)
                    with self.assertRaisesRegex(
                        ValueError,
                        f"{field_name} must not be blank",
                    ):
                        validate_research_finding(finding)

    def test_research_finding_verification_enum(self):
        for value in ("pending", "Verified", "unknown"):
            with self.subTest(verification_status=value):
                finding = make_finding()
                finding.verification_status = value
                with self.assertRaisesRegex(
                    ValueError,
                    "verification_status must be verified",
                ):
                    validate_research_finding(finding)

    def test_research_report_field_types(self):
        cases = (
            ("research_id", None, "research_id must be str"),
            ("title", None, "title must be str"),
            (
                "findings",
                (),
                r"findings must be list\[ResearchFinding\]",
            ),
            ("status", None, "status must be str"),
            ("error", None, "error must be str"),
        )
        for field_name, value, message in cases:
            with self.subTest(field=field_name):
                report = make_report()
                setattr(report, field_name, value)
                with self.assertRaisesRegex(TypeError, message):
                    validate_research_report(report)

    def test_research_report_blank_identity_fields(self):
        for field_name in ("research_id", "title"):
            for value in ("", " ", "\t", "\n"):
                with self.subTest(field=field_name, value=repr(value)):
                    report = make_report()
                    setattr(report, field_name, value)
                    with self.assertRaisesRegex(
                        ValueError,
                        f"{field_name} must not be blank",
                    ):
                        validate_research_report(report)

    def test_research_report_finding_element_type(self):
        report = make_report()
        report.findings.append(object())

        with self.assertRaisesRegex(
            TypeError,
            "findings must contain only ResearchFinding",
        ):
            validate_research_report(report)

    def test_research_report_status_enum(self):
        for status in ("", "pending", "Completed", "error"):
            with self.subTest(status=status):
                report = make_report()
                report.status = status
                with self.assertRaisesRegex(
                    ValueError,
                    "status must be completed or failed",
                ):
                    validate_research_report(report)

    def test_completed_report_requires_empty_error(self):
        for error in ("failure", " "):
            with self.subTest(error=repr(error)):
                report = make_report(error=error)
                with self.assertRaisesRegex(
                    ValueError,
                    "completed report error must be empty",
                ):
                    validate_research_report(report)

    def test_failed_report_requires_nonblank_error(self):
        for error in ("", " ", "\t", "\n"):
            with self.subTest(error=repr(error)):
                report = make_report(status="failed", error=error)
                with self.assertRaisesRegex(
                    ValueError,
                    "failed report error must be nonblank",
                ):
                    validate_research_report(report)

    def test_empty_findings_are_valid(self):
        for status, error in (
            ("completed", ""),
            ("failed", "research failed"),
        ):
            with self.subTest(status=status):
                report = make_report(status=status, error=error)
                report.findings = []
                self.assertIsNone(validate_research_report(report))

    def test_validation_does_not_mutate_inputs(self):
        task = make_task()
        finding = make_finding()
        report = make_report()
        task_values = vars(task).copy()
        pipeline_values = vars(task.pipeline).copy()
        finding_values = vars(finding).copy()
        report_values = vars(report).copy()
        findings = list(report.findings)
        report_finding_values = vars(report.findings[0]).copy()

        validate_research_task(task)
        validate_research_finding(finding)
        validate_research_report(report)

        self.assertEqual(vars(task), task_values)
        self.assertEqual(vars(task.pipeline), pipeline_values)
        self.assertEqual(vars(finding), finding_values)
        self.assertEqual(vars(report), report_values)
        self.assertEqual(report.findings, findings)
        self.assertEqual(
            vars(report.findings[0]),
            report_finding_values,
        )

    def test_no_runtime_import_or_execution_dependency(self):
        package_root = pathlib.Path(__file__).parents[1]
        source = (
            (package_root / "models.py").read_text()
            + (package_root / "validation.py").read_text()
        )

        self.assertNotIn("PipelineRuntime.runtime", source)
        self.assertNotIn("CommitteeRuntime", source)
        self.assertNotIn("ExecutionEngine", source)
        self.assertNotIn("AIAdapter", source)


if __name__ == "__main__":
    unittest.main()
