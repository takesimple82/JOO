import pathlib
import unittest
from collections.abc import Sequence
from dataclasses import FrozenInstanceError, MISSING, fields
from typing import get_type_hints
from unittest.mock import patch

from EvidenceAggregation.models import (
    EvidenceAggregationGroup,
    EvidenceAggregationItem,
    EvidenceAggregationMetadata,
)
from EvidenceAggregation.validation import (
    validate_evidence_aggregation_group,
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


class DerivedGroup(EvidenceAggregationGroup):
    pass


class DerivedString(str):
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


class EvidenceAggregationGroupTests(unittest.TestCase):
    def test_exact_model_contract_and_identity(self):
        model_fields = fields(EvidenceAggregationGroup)
        self.assertEqual(
            [field.name for field in model_fields],
            ["aggregation_key", "items"],
        )
        self.assertEqual(
            get_type_hints(EvidenceAggregationGroup),
            {
                "aggregation_key": str,
                "items": tuple[EvidenceAggregationItem, ...],
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)

        key = "".join(("group", "-", "001"))
        first = make_item("finding-001", key)
        second = make_item("finding-002", key)
        items = (first, second)
        group = EvidenceAggregationGroup(key, items)

        self.assertIs(group.aggregation_key, key)
        self.assertIs(group.items, items)
        self.assertIs(group.items[0], first)
        self.assertIs(group.items[1], second)
        self.assertEqual(group.items, (first, second))

        with self.assertRaises(FrozenInstanceError):
            group.items = ()

    def test_exact_group_type_is_required(self):
        item = make_item()
        cases = (
            object(),
            DerivedGroup("group-001", (item,)),
        )
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^group must be EvidenceAggregationGroup$",
                ):
                    validate_evidence_aggregation_group(value)

    def test_aggregation_key_must_be_exact_string(self):
        item = make_item()
        cases = (
            None,
            DerivedString("group-001"),
        )
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    TypeError,
                    "^aggregation_key must be str$",
                ):
                    validate_evidence_aggregation_group(
                        EvidenceAggregationGroup(
                            value,
                            (item,),
                        )
                    )

    def test_blank_keys_are_rejected(self):
        item = make_item()
        for value in ("", " ", "\t", "\n"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "^aggregation_key must not be blank$",
                ):
                    validate_evidence_aggregation_group(
                        EvidenceAggregationGroup(
                            value,
                            (item,),
                        )
                    )

    def test_surrounding_whitespace_is_preserved(self):
        key = " group-001 "
        item = make_item(aggregation_key=key)
        items = (item,)
        group = EvidenceAggregationGroup(key, items)

        self.assertIsNone(
            validate_evidence_aggregation_group(group)
        )
        self.assertIs(group.aggregation_key, key)
        self.assertEqual(
            group.aggregation_key,
            " group-001 ",
        )
        self.assertEqual(
            group.items[0].metadata.aggregation_key,
            " group-001 ",
        )

    def test_items_must_be_exact_tuple(self):
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
                    validate_evidence_aggregation_group(
                        EvidenceAggregationGroup(
                            "group-001",
                            value,
                        )
                    )

        self.assertFalse(iterable.iterated)
        self.assertIs(next(generator), item)

    def test_empty_group_is_rejected_before_item_validation(self):
        group = EvidenceAggregationGroup("group-001", ())

        with patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_item"
        ) as item_validator:
            with self.assertRaisesRegex(
                ValueError,
                "^items must not be empty$",
            ):
                validate_evidence_aggregation_group(group)

        item_validator.assert_not_called()

    def test_items_validate_exactly_once_in_order(self):
        key = "group-001"
        first = make_item("finding-001", key)
        second = make_item("finding-002", key)
        third = make_item("finding-003", key)
        calls = []

        with patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_item",
            side_effect=lambda item: calls.append(item),
        ) as item_validator:
            result = validate_evidence_aggregation_group(
                EvidenceAggregationGroup(
                    key,
                    (first, second, third),
                )
            )

        self.assertIsNone(result)
        self.assertEqual(calls, [first, second, third])
        self.assertEqual(item_validator.call_count, 3)

    def test_upstream_failure_propagates_before_linkage(self):
        invalid = make_item(
            "finding-001",
            "different-key",
        )
        later = make_item("finding-002", "group-001")
        error = ValueError("accepted item failure")
        calls = []

        def validate(item):
            calls.append(item)
            if item is invalid:
                raise error

        with patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_item",
            side_effect=validate,
        ):
            try:
                validate_evidence_aggregation_group(
                    EvidenceAggregationGroup(
                        "group-001",
                        (invalid, later),
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

        self.assertEqual(calls, [invalid])

    def test_linkage_mismatch_stops_processing(self):
        first = make_item("finding-001", "group-001")
        mismatch = make_item("finding-002", "other-group")
        later = make_item("finding-003", "group-001")
        calls = []

        with patch(
            "EvidenceAggregation.validation."
            "validate_evidence_aggregation_item",
            side_effect=lambda item: calls.append(item),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "^item aggregation_key must match "
                "group aggregation_key$",
            ):
                validate_evidence_aggregation_group(
                    EvidenceAggregationGroup(
                        "group-001",
                        (first, mismatch, later),
                    )
                )

        self.assertEqual(calls, [first, mismatch])

    def test_duplicate_structures_are_permitted(self):
        key = "group-001"
        repeated = make_item(
            "finding-shared",
            key,
            "source-shared",
        )
        equal = make_item(
            "finding-shared",
            key,
            "source-shared",
        )
        same_finding = make_item(
            "finding-shared",
            key,
            "source-other",
        )
        same_source = make_item(
            "finding-other",
            key,
            "source-shared",
        )
        self.assertEqual(repeated, equal)
        items = (
            repeated,
            repeated,
            equal,
            same_finding,
            same_source,
        )

        self.assertIsNone(
            validate_evidence_aggregation_group(
                EvidenceAggregationGroup(key, items)
            )
        )

    def test_validation_preserves_identity_order_and_values(self):
        key = "group-001"
        first = make_item("finding-001", key)
        second = make_item("finding-002", key)
        items = (second, first)
        group = EvidenceAggregationGroup(key, items)
        item_values = tuple(vars(item).copy() for item in items)
        finding_values = tuple(
            vars(item.finding).copy()
            for item in items
        )

        validate_evidence_aggregation_group(group)

        self.assertIs(group.aggregation_key, key)
        self.assertIs(group.items, items)
        self.assertIs(group.items[0], second)
        self.assertIs(group.items[1], first)
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
            "GroupRequest",
            "GroupResult",
            "GroupingPolicy",
            "GroupingContext",
            "GroupBuilder",
            "GroupFactory",
            "GroupIndex",
            "GroupCollection",
            "class EvidenceAggregator",
            "AggregationRequest",
            "AggregationResult",
            "AggregationExecution",
            "AcceptedGroup",
            "RejectedGroup",
            "DuplicateGroup",
        )
        for symbol in prohibited_symbols:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, production_source)


if __name__ == "__main__":
    unittest.main()
