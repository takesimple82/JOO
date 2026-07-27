import pathlib
import unittest
from collections.abc import Sequence
from dataclasses import FrozenInstanceError, MISSING, fields
from typing import get_type_hints
from unittest.mock import patch

from EvidenceAggregation.models import (
    EvidenceAggregationBatch,
    EvidenceAggregationItem,
    EvidenceAggregationMetadata,
)
from EvidenceAggregation.validation import (
    validate_evidence_aggregation_batch,
)
from EvidenceAssessment.assessor import (
    ASSESSMENT_POLICY_VERSION,
)
from EvidenceAssessment.models import EvidenceAssessmentResult
from EvidenceProvenance.models import EvidenceProvenanceMetadata
from EvidenceValidation.models import EvidenceValidationResult
from ResearchDomain.models import ResearchFinding


def make_item(
    finding_id="finding-001",
    aggregation_key="group-001",
    source_reference_id="source-reference-001",
) -> EvidenceAggregationItem:
    finding = ResearchFinding(
        finding_id=finding_id,
        research_id="research-001",
        committee_id="committee-001",
        category="financial",
        statement="Revenue increased.",
        source="Company filing",
        event_date="2026-07-01",
        publication_date="2026-07-02",
        verification_status="verified",
    )
    provenance = EvidenceProvenanceMetadata(
        finding_id=finding_id,
        source_class="primary",
    )
    validation = EvidenceValidationResult(
        valid=True,
        issues=(),
    )
    assessment = EvidenceAssessmentResult(
        finding_id=finding_id,
        assessable=True,
        policy_version=ASSESSMENT_POLICY_VERSION,
        dimensions=(),
        validation=validation,
    )
    metadata = EvidenceAggregationMetadata(
        finding_id=finding_id,
        aggregation_key=aggregation_key,
        source_reference_id=source_reference_id,
    )
    return EvidenceAggregationItem(
        finding=finding,
        provenance=provenance,
        assessment=assessment,
        metadata=metadata,
    )


class DerivedBatch(EvidenceAggregationBatch):
    pass


class DerivedTuple(tuple):
    pass


class ExampleSequence(Sequence):
    def __init__(self, values):
        self._values = values

    def __getitem__(self, index):
        return self._values[index]

    def __len__(self):
        return len(self._values)


class TrackingIterable:
    def __init__(self, values):
        self._values = values
        self.iterated = False

    def __iter__(self):
        self.iterated = True
        return iter(self._values)


class EvidenceAggregationBatchTests(unittest.TestCase):
    def test_exact_model_contract_and_identity(self):
        model_fields = fields(EvidenceAggregationBatch)
        self.assertEqual(
            [field.name for field in model_fields],
            ["items"],
        )
        self.assertEqual(
            get_type_hints(EvidenceAggregationBatch),
            {
                "items": tuple[EvidenceAggregationItem, ...],
            },
        )
        self.assertIs(model_fields[0].default, MISSING)
        self.assertIs(model_fields[0].default_factory, MISSING)

        first = make_item("finding-001")
        second = make_item("finding-002")
        items = (first, second)
        batch = EvidenceAggregationBatch(items=items)

        self.assertIs(batch.items, items)
        self.assertIs(batch.items[0], first)
        self.assertIs(batch.items[1], second)
        self.assertEqual(batch.items, (first, second))

        with self.assertRaises(FrozenInstanceError):
            batch.items = ()

    def test_exact_batch_type_is_required(self):
        cases = (
            object(),
            DerivedBatch(items=()),
        )
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^batch must be EvidenceAggregationBatch$",
                ):
                    validate_evidence_aggregation_batch(value)

    def test_collection_must_be_exact_tuple(self):
        item = make_item()
        generator = (value for value in (item,))
        sequence = ExampleSequence([item])
        iterable = TrackingIterable([item])
        cases = (
            [item],
            DerivedTuple((item,)),
            generator,
            sequence,
            iterable,
        )

        for value in cases:
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^items must be tuple$",
                ):
                    validate_evidence_aggregation_batch(
                        EvidenceAggregationBatch(items=value)
                    )

        self.assertFalse(iterable.iterated)
        self.assertIs(next(generator), item)

    def test_empty_tuple_is_valid_without_item_validation(self):
        items = ()
        batch = EvidenceAggregationBatch(items=items)

        with patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_item"
        ) as item_validator:
            result = validate_evidence_aggregation_batch(batch)

        self.assertIsNone(result)
        self.assertIs(batch.items, items)
        item_validator.assert_not_called()

    def test_items_validate_exactly_once_in_supplied_order(self):
        first = make_item("finding-001")
        second = make_item("finding-002")
        third = make_item("finding-003")
        items = (first, second, third)
        calls = []

        with patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_item",
            side_effect=lambda item: calls.append(item),
        ) as item_validator:
            result = validate_evidence_aggregation_batch(
                EvidenceAggregationBatch(items=items)
            )

        self.assertIsNone(result)
        self.assertEqual(calls, [first, second, third])
        self.assertEqual(item_validator.call_count, 3)
        for index, item in enumerate(items):
            self.assertIs(calls[index], item)

    def test_first_item_failure_propagates_and_stops(self):
        first = make_item("finding-001")
        second = make_item("finding-002")
        third = make_item("finding-003")
        error = ValueError("accepted item failure")
        calls = []

        def validate(item):
            calls.append(item)
            if item is second:
                raise error

        with patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_item",
            side_effect=validate,
        ):
            try:
                validate_evidence_aggregation_batch(
                    EvidenceAggregationBatch(
                        items=(first, second, third)
                    )
                )
            except ValueError as caught:
                self.assertIs(caught, error)
                self.assertEqual(
                    str(caught),
                    "accepted item failure",
                )
            else:
                self.fail("item exception did not propagate")

        self.assertEqual(calls, [first, second])

    def test_repeated_same_item_object_is_permitted(self):
        item = make_item()
        items = (item, item)
        batch = EvidenceAggregationBatch(items=items)

        self.assertIsNone(
            validate_evidence_aggregation_batch(batch)
        )
        self.assertIs(batch.items, items)
        self.assertIs(batch.items[0], item)
        self.assertIs(batch.items[1], item)

    def test_equal_item_values_are_permitted(self):
        first = make_item()
        second = make_item()
        self.assertEqual(first, second)

        batch = EvidenceAggregationBatch(
            items=(first, second),
        )

        self.assertIsNone(
            validate_evidence_aggregation_batch(batch)
        )
        self.assertIs(batch.items[0], first)
        self.assertIs(batch.items[1], second)

    def test_shared_structural_identifiers_are_permitted(self):
        base = make_item(
            finding_id="finding-shared",
            aggregation_key="group-shared",
            source_reference_id="source-shared",
        )
        same_finding = make_item(
            finding_id="finding-shared",
            aggregation_key="group-other",
            source_reference_id="source-other",
        )
        same_group = make_item(
            finding_id="finding-other",
            aggregation_key="group-shared",
            source_reference_id="source-another",
        )
        same_source = make_item(
            finding_id="finding-third",
            aggregation_key="group-third",
            source_reference_id="source-shared",
        )
        items = (
            base,
            same_finding,
            same_group,
            same_source,
        )

        self.assertIsNone(
            validate_evidence_aggregation_batch(
                EvidenceAggregationBatch(items=items)
            )
        )

    def test_validation_does_not_mutate_or_reorder(self):
        first = make_item("finding-001")
        second = make_item("finding-002")
        items = (second, first)
        batch = EvidenceAggregationBatch(items=items)
        item_values = tuple(vars(item).copy() for item in items)
        finding_values = tuple(
            vars(item.finding).copy()
            for item in items
        )

        validate_evidence_aggregation_batch(batch)

        self.assertIs(batch.items, items)
        self.assertIs(batch.items[0], second)
        self.assertIs(batch.items[1], first)
        self.assertEqual(
            tuple(vars(item) for item in items),
            item_values,
        )
        self.assertEqual(
            tuple(vars(item.finding) for item in items),
            finding_values,
        )

    def test_dependency_and_feature_boundaries(self):
        package_root = pathlib.Path(__file__).parents[1]
        production_source = (
            package_root.joinpath("models.py").read_text()
            + package_root.joinpath("validation.py").read_text()
        )
        prohibited_dependencies = (
            "EvidenceValidation",
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
            "AggregationOptions",
            "AggregationPolicy",
            "AggregationContext",
            "AggregationExecution",
            "BatchResult",
            "AcceptedRecord",
            "RejectedRecord",
            "DuplicateRecord",
        )
        for symbol in prohibited_symbols:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, production_source)


if __name__ == "__main__":
    unittest.main()
