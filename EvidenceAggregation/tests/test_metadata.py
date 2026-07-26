import pathlib
import unittest
from dataclasses import FrozenInstanceError, fields
from typing import get_type_hints

from EvidenceAggregation.models import (
    EvidenceAggregationMetadata,
)
from EvidenceAggregation.validation import (
    validate_evidence_aggregation_metadata,
)


def make_metadata(**overrides) -> EvidenceAggregationMetadata:
    values = {
        "finding_id": "finding-001",
        "aggregation_key": "group-001",
        "source_reference_id": "source-reference-001",
    }
    values.update(overrides)
    return EvidenceAggregationMetadata(**values)


class DerivedMetadata(EvidenceAggregationMetadata):
    pass


class EvidenceAggregationMetadataTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            [
                field.name
                for field in fields(EvidenceAggregationMetadata)
            ],
            [
                "finding_id",
                "aggregation_key",
                "source_reference_id",
            ],
        )
        self.assertEqual(
            get_type_hints(EvidenceAggregationMetadata),
            {
                "finding_id": str,
                "aggregation_key": str,
                "source_reference_id": str,
            },
        )

        prohibited_fields = {
            "source_identity",
            "claim_id",
            "score",
            "grade",
            "confidence",
            "corroboration",
            "independence",
        }
        self.assertTrue(
            prohibited_fields.isdisjoint(
                {
                    field.name
                    for field in fields(
                        EvidenceAggregationMetadata
                    )
                }
            )
        )

    def test_model_is_frozen_and_hashable(self):
        metadata = make_metadata()

        with self.assertRaises(FrozenInstanceError):
            metadata.aggregation_key = "group-002"

        self.assertIsInstance(hash(metadata), int)

    def test_valid_values_return_none_without_mutation(self):
        metadata = make_metadata()
        original_values = vars(metadata).copy()

        result = validate_evidence_aggregation_metadata(metadata)

        self.assertIsNone(result)
        self.assertEqual(vars(metadata), original_values)

    def test_nonblank_surrounding_whitespace_is_preserved(self):
        metadata = make_metadata(
            finding_id=" finding-001 ",
            aggregation_key="\tgroup-001\n",
            source_reference_id=" source-reference-001 ",
        )
        original_values = vars(metadata).copy()

        self.assertIsNone(
            validate_evidence_aggregation_metadata(metadata)
        )
        self.assertEqual(vars(metadata), original_values)
        self.assertEqual(metadata.finding_id, " finding-001 ")
        self.assertEqual(metadata.aggregation_key, "\tgroup-001\n")
        self.assertEqual(
            metadata.source_reference_id,
            " source-reference-001 ",
        )

    def test_exact_model_type_is_required(self):
        cases = (
            object(),
            DerivedMetadata(
                finding_id="finding-001",
                aggregation_key="group-001",
                source_reference_id="source-reference-001",
            ),
        )

        for value in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^metadata must be "
                    "EvidenceAggregationMetadata$",
                ):
                    validate_evidence_aggregation_metadata(value)

    def test_non_string_fields_are_rejected_in_field_order(self):
        cases = (
            (
                {"finding_id": None},
                "finding_id must be str",
            ),
            (
                {
                    "finding_id": None,
                    "aggregation_key": None,
                },
                "finding_id must be str",
            ),
            (
                {"aggregation_key": None},
                "aggregation_key must be str",
            ),
            (
                {"source_reference_id": None},
                "source_reference_id must be str",
            ),
        )

        for overrides, message in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(
                    TypeError,
                    f"^{message}$",
                ):
                    validate_evidence_aggregation_metadata(
                        make_metadata(**overrides)
                    )

    def test_blank_fields_are_rejected_with_exact_messages(self):
        fields_and_messages = (
            ("finding_id", "finding_id must not be blank"),
            (
                "aggregation_key",
                "aggregation_key must not be blank",
            ),
            (
                "source_reference_id",
                "source_reference_id must not be blank",
            ),
        )
        blank_values = ("", " ", "\t", "\n")

        for field_name, message in fields_and_messages:
            for value in blank_values:
                with self.subTest(
                    field_name=field_name,
                    value=value,
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{message}$",
                    ):
                        validate_evidence_aggregation_metadata(
                            make_metadata(
                                **{field_name: value}
                            )
                        )

    def test_blank_validation_order_is_deterministic(self):
        metadata = EvidenceAggregationMetadata(
            finding_id=" ",
            aggregation_key=" ",
            source_reference_id=" ",
        )

        with self.assertRaisesRegex(
            ValueError,
            "^finding_id must not be blank$",
        ):
            validate_evidence_aggregation_metadata(metadata)

    def test_package_has_no_runtime_or_upstream_dependencies(self):
        package_root = pathlib.Path(__file__).parents[1]
        production_source = (
            package_root.joinpath("models.py").read_text()
            + package_root.joinpath("validation.py").read_text()
        )
        prohibited_dependencies = (
            "ResearchDomain",
            "EvidenceValidation",
            "EvidenceProvenance",
            "EvidenceAssessment",
            "ResearchLogging",
            "ResearchOrchestrator",
            "PipelineRuntime",
            "CommitteeRuntime",
            "ExecutionEngine",
            "AIAdapter",
            "providers",
        )
        for dependency in prohibited_dependencies:
            with self.subTest(dependency=dependency):
                self.assertNotIn(
                    dependency,
                    production_source,
                )

        prohibited_symbols = (
            "class EvidenceAggregator",
            "AggregationRequest",
            "AggregationResult",
            "AcceptedEvidence",
            "RejectedEvidence",
            "DuplicateEvidence",
        )
        for symbol in prohibited_symbols:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, production_source)

    def test_existing_packages_do_not_import_evidence_aggregation(
        self,
    ):
        package_root = pathlib.Path(__file__).parents[1]
        repository_root = package_root.parent

        for path in repository_root.iterdir():
            if (
                not path.is_dir()
                or path == package_root
                or path.name.startswith(".")
            ):
                continue
            for source_file in path.rglob("*.py"):
                with self.subTest(path=source_file):
                    self.assertNotIn(
                        "EvidenceAggregation",
                        source_file.read_text(),
                    )


if __name__ == "__main__":
    unittest.main()
