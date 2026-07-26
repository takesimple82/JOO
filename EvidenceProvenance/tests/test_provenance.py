import pathlib
import unittest
from dataclasses import FrozenInstanceError, fields
from typing import get_type_hints

from EvidenceProvenance.models import (
    SOURCE_CLASSES,
    EvidenceProvenanceMetadata,
)
from EvidenceProvenance.validation import (
    validate_evidence_provenance,
)
from ResearchDomain.models import ResearchFinding


def make_metadata(
    finding_id="finding-001",
    source_class="primary",
) -> EvidenceProvenanceMetadata:
    return EvidenceProvenanceMetadata(
        finding_id=finding_id,
        source_class=source_class,
    )


class DerivedMetadata(EvidenceProvenanceMetadata):
    pass


class EvidenceProvenanceTests(unittest.TestCase):
    def test_exact_model_contract(self):
        self.assertEqual(
            [field.name for field in fields(EvidenceProvenanceMetadata)],
            ["finding_id", "source_class"],
        )
        self.assertEqual(
            get_type_hints(EvidenceProvenanceMetadata),
            {
                "finding_id": str,
                "source_class": str,
            },
        )
        self.assertEqual(
            SOURCE_CLASSES,
            ("primary", "secondary", "unknown"),
        )

    def test_model_is_frozen_and_hashable(self):
        metadata = make_metadata()

        with self.assertRaises(FrozenInstanceError):
            metadata.source_class = "secondary"

        self.assertIsInstance(hash(metadata), int)
        self.assertEqual({metadata}, {metadata})

    def test_all_canonical_source_classes_are_valid(self):
        for source_class in SOURCE_CLASSES:
            with self.subTest(source_class=source_class):
                metadata = make_metadata(
                    source_class=source_class
                )
                original = (
                    metadata.finding_id,
                    metadata.source_class,
                )

                result = validate_evidence_provenance(metadata)

                self.assertIsNone(result)
                self.assertEqual(
                    (
                        metadata.finding_id,
                        metadata.source_class,
                    ),
                    original,
                )

    def test_requires_exact_metadata_type(self):
        values = (object(), DerivedMetadata("finding-001", "primary"))
        for value in values:
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaisesRegex(
                    TypeError,
                    "metadata must be EvidenceProvenanceMetadata",
                ):
                    validate_evidence_provenance(value)

    def test_finding_id_type_and_blank_validation(self):
        with self.assertRaisesRegex(
            TypeError,
            "finding_id must be str",
        ):
            validate_evidence_provenance(
                make_metadata(finding_id=None)
            )

        for value in ("", " ", "\t", "\n"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "finding_id must not be blank",
                ):
                    validate_evidence_provenance(
                        make_metadata(finding_id=value)
                    )

    def test_source_class_must_be_string(self):
        with self.assertRaisesRegex(
            TypeError,
            "source_class must be str",
        ):
            validate_evidence_provenance(
                make_metadata(source_class=None)
            )

    def test_invalid_source_classes_are_rejected_without_aliases(self):
        invalid_values = (
            "",
            "invalid",
            "PRIMARY",
            "Primary",
            " primary",
            "primary ",
            " secondary ",
            "\tunknown",
            "unknown\n",
        )
        for value in invalid_values:
            with self.subTest(value=repr(value)):
                metadata = make_metadata(source_class=value)
                original = (
                    metadata.finding_id,
                    metadata.source_class,
                )

                with self.assertRaisesRegex(
                    ValueError,
                    (
                        "source_class must be primary, "
                        "secondary, or unknown"
                    ),
                ):
                    validate_evidence_provenance(metadata)

                self.assertEqual(
                    (
                        metadata.finding_id,
                        metadata.source_class,
                    ),
                    original,
                )

    def test_research_finding_contract_remains_unchanged(self):
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

    def test_package_has_no_logging_or_runtime_dependencies(self):
        package_root = pathlib.Path(__file__).parents[1]
        source = (
            package_root.joinpath("models.py").read_text()
            + package_root.joinpath("validation.py").read_text()
        )
        prohibited_names = (
            "ResearchLogging",
            "ResearchOrchestrator",
            "PipelineRuntime",
            "CommitteeRuntime",
            "ExecutionEngine",
            "AIAdapter",
            "providers",
            "EvidenceScore",
            "corroboration",
        )
        for name in prohibited_names:
            with self.subTest(name=name):
                self.assertNotIn(name, source)


if __name__ == "__main__":
    unittest.main()
