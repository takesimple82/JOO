import ast
import unittest
from decimal import Decimal
from enum import Enum
from pathlib import Path
from unittest.mock import Mock, patch

from EvidenceContradiction.models import (
    EvidenceContradictionStatus,
)
from EvidenceProposition.models import (
    ExactObservedNumericProposition,
)
from EvidenceSupersession.models import (
    ExplicitPropositionSupersession,
)
from EvidenceSupersessionApplicability.classification import (
    classify_explicit_supersession_applicability,
)
from EvidenceSupersessionApplicability.models import (
    EvidenceSupersessionApplicabilityStatus,
)


def make_proposition(**overrides) -> ExactObservedNumericProposition:
    values = {
        "proposition_id": "proposition-a",
        "finding_id": "finding-a",
        "subject_id": "subject",
        "predicate_id": "predicate",
        "value": Decimal("1"),
        "unit_id": "unit",
        "effective_context_id": "context",
    }
    values.update(overrides)
    return ExactObservedNumericProposition(**values)


def make_relation(
    superseded: str = "proposition-a",
    superseding: str = "proposition-b",
) -> ExplicitPropositionSupersession:
    return ExplicitPropositionSupersession(
        superseded,
        superseding,
    )


class UnrelatedStatus(Enum):
    VALUE = "value"


class ExplodingProposition:
    @property
    def proposition_id(self):
        raise AssertionError("proposition_id accessed prematurely")


class EvidenceSupersessionApplicabilityTests(unittest.TestCase):
    def test_exact_enum_contract(self):
        self.assertEqual(
            EvidenceSupersessionApplicabilityStatus.__name__,
            "EvidenceSupersessionApplicabilityStatus",
        )
        self.assertEqual(
            EvidenceSupersessionApplicabilityStatus.__bases__,
            (Enum,),
        )
        self.assertEqual(
            list(EvidenceSupersessionApplicabilityStatus.__members__),
            [
                "NOT_CONTRADICTION_CANDIDATE",
                "RELATION_ENDPOINT_MISMATCH",
                "APPLICABLE",
            ],
        )
        self.assertEqual(
            [
                member.value
                for member in EvidenceSupersessionApplicabilityStatus
            ],
            [
                "not_contradiction_candidate",
                "relation_endpoint_mismatch",
                "applicable",
            ],
        )
        self.assertEqual(
            len(EvidenceSupersessionApplicabilityStatus),
            3,
        )
        self.assertEqual(
            len(EvidenceSupersessionApplicabilityStatus.__members__),
            3,
        )
        public_methods = {
            name
            for name, value in
            EvidenceSupersessionApplicabilityStatus.__dict__.items()
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, set())
        self.assertIsInstance(
            hash(EvidenceSupersessionApplicabilityStatus.APPLICABLE),
            int,
        )
        with self.assertRaises(AttributeError):
            EvidenceSupersessionApplicabilityStatus.APPLICABLE.value = (
                "changed"
            )

    @patch(
        "EvidenceSupersessionApplicability.classification."
        "classify_exact_observed_numeric_contradiction_candidate"
    )
    @patch(
        "EvidenceSupersessionApplicability.classification."
        "validate_explicit_proposition_supersession"
    )
    def test_upstream_calls_once_in_order(
        self,
        validate_relation,
        classify_contradiction,
    ):
        calls = []
        validate_relation.side_effect = (
            lambda relation: calls.append(("validate", relation))
        )
        classify_contradiction.side_effect = (
            lambda left, right: (
                calls.append(("classify", left, right))
                or EvidenceContradictionStatus
                .NO_CONTRADICTION_CANDIDATE
            )
        )
        left = object()
        right = object()
        relation = object()

        result = classify_explicit_supersession_applicability(
            left,
            right,
            relation,
        )

        self.assertIs(
            result,
            EvidenceSupersessionApplicabilityStatus
            .NOT_CONTRADICTION_CANDIDATE,
        )
        validate_relation.assert_called_once_with(relation)
        classify_contradiction.assert_called_once_with(left, right)
        self.assertEqual(
            calls,
            [
                ("validate", relation),
                ("classify", left, right),
            ],
        )
        self.assertIs(calls[0][1], relation)
        self.assertIs(calls[1][1], left)
        self.assertIs(calls[1][2], right)

    @patch(
        "EvidenceSupersessionApplicability.classification."
        "classify_exact_observed_numeric_contradiction_candidate"
    )
    @patch(
        "EvidenceSupersessionApplicability.classification."
        "validate_explicit_proposition_supersession"
    )
    def test_relation_failure_prevents_contradiction_call(
        self,
        validate_relation,
        classify_contradiction,
    ):
        error = ValueError("relation failure")
        validate_relation.side_effect = error

        with self.assertRaises(ValueError) as caught:
            classify_explicit_supersession_applicability(
                object(),
                object(),
                object(),
            )

        self.assertIs(caught.exception, error)
        validate_relation.assert_called_once()
        classify_contradiction.assert_not_called()

    @patch(
        "EvidenceSupersessionApplicability.classification."
        "classify_exact_observed_numeric_contradiction_candidate"
    )
    @patch(
        "EvidenceSupersessionApplicability.classification."
        "validate_explicit_proposition_supersession"
    )
    def test_contradiction_exception_propagates_unchanged(
        self,
        validate_relation,
        classify_contradiction,
    ):
        error = TypeError("proposition failure")
        classify_contradiction.side_effect = error

        with self.assertRaises(TypeError) as caught:
            classify_explicit_supersession_applicability(
                object(),
                object(),
                object(),
            )

        self.assertIs(caught.exception, error)
        validate_relation.assert_called_once()
        classify_contradiction.assert_called_once()

    def test_noncandidate_statuses_do_not_inspect_ids(self):
        statuses = (
            EvidenceContradictionStatus.NOT_ELIGIBLE,
            EvidenceContradictionStatus
            .NO_CONTRADICTION_CANDIDATE,
        )
        for status in statuses:
            with self.subTest(status=status):
                with patch(
                    "EvidenceSupersessionApplicability."
                    "classification."
                    "validate_explicit_proposition_supersession"
                ), patch(
                    "EvidenceSupersessionApplicability."
                    "classification."
                    "classify_exact_observed_numeric_"
                    "contradiction_candidate",
                    return_value=status,
                ):
                    result = (
                        classify_explicit_supersession_applicability(
                            ExplodingProposition(),
                            ExplodingProposition(),
                            object(),
                        )
                    )
                self.assertIs(
                    result,
                    EvidenceSupersessionApplicabilityStatus
                    .NOT_CONTRADICTION_CANDIDATE,
                )

    def test_unknown_status_does_not_inspect_ids_and_raises(self):
        unknown_values = (object(), None, UnrelatedStatus.VALUE)
        for status in unknown_values:
            with self.subTest(status=status):
                with patch(
                    "EvidenceSupersessionApplicability."
                    "classification."
                    "validate_explicit_proposition_supersession"
                ), patch(
                    "EvidenceSupersessionApplicability."
                    "classification."
                    "classify_exact_observed_numeric_"
                    "contradiction_candidate",
                    return_value=status,
                ):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        "^unsupported evidence contradiction status$",
                    ):
                        classify_explicit_supersession_applicability(
                            ExplodingProposition(),
                            ExplodingProposition(),
                            object(),
                        )

    def test_mocked_candidate_endpoint_statuses(self):
        left = make_proposition(proposition_id="left")
        right = make_proposition(proposition_id="right")
        cases = (
            (
                make_relation("left", "right"),
                EvidenceSupersessionApplicabilityStatus.APPLICABLE,
            ),
            (
                make_relation("right", "left"),
                EvidenceSupersessionApplicabilityStatus.APPLICABLE,
            ),
            (
                make_relation("left", "unrelated"),
                EvidenceSupersessionApplicabilityStatus
                .RELATION_ENDPOINT_MISMATCH,
            ),
            (
                make_relation("other", "unrelated"),
                EvidenceSupersessionApplicabilityStatus
                .RELATION_ENDPOINT_MISMATCH,
            ),
        )
        for relation, expected in cases:
            with self.subTest(relation=relation):
                with patch(
                    "EvidenceSupersessionApplicability."
                    "classification."
                    "validate_explicit_proposition_supersession"
                ), patch(
                    "EvidenceSupersessionApplicability."
                    "classification."
                    "classify_exact_observed_numeric_"
                    "contradiction_candidate",
                    return_value=(
                        EvidenceContradictionStatus
                        .CONTRADICTION_CANDIDATE
                    ),
                ):
                    result = (
                        classify_explicit_supersession_applicability(
                            left,
                            right,
                            relation,
                        )
                    )
                self.assertIs(result, expected)

    def test_integrated_forward_and_reverse_relations_apply(self):
        left = make_proposition(
            proposition_id="left",
            value=Decimal("1"),
        )
        right = make_proposition(
            proposition_id="right",
            finding_id="finding-b",
            value=Decimal("2"),
        )
        for relation in (
            make_relation("left", "right"),
            make_relation("right", "left"),
        ):
            with self.subTest(relation=relation):
                self.assertIs(
                    classify_explicit_supersession_applicability(
                        left,
                        right,
                        relation,
                    ),
                    EvidenceSupersessionApplicabilityStatus.APPLICABLE,
                )

    def test_integrated_noncandidate_pairs(self):
        left = make_proposition(proposition_id="left")
        equal = make_proposition(
            proposition_id="right",
            finding_id="finding-b",
        )
        noncomparable = make_proposition(
            proposition_id="right",
            finding_id="finding-b",
            subject_id="different",
            value=Decimal("2"),
        )
        relation = make_relation("left", "right")
        pairs = (
            (left, equal),
            (left, noncomparable),
            (left, left),
        )
        for first, second in pairs:
            with self.subTest(second=second):
                self.assertIs(
                    classify_explicit_supersession_applicability(
                        first,
                        second,
                        relation,
                    ),
                    EvidenceSupersessionApplicabilityStatus
                    .NOT_CONTRADICTION_CANDIDATE,
                )

    def test_integrated_endpoint_mismatches(self):
        left = make_proposition(
            proposition_id="left",
            value=Decimal("1"),
        )
        right = make_proposition(
            proposition_id="right",
            finding_id="finding-b",
            value=Decimal("2"),
        )
        relations = (
            make_relation("left", "unrelated"),
            make_relation("other", "unrelated"),
        )
        for relation in relations:
            with self.subTest(relation=relation):
                self.assertIs(
                    classify_explicit_supersession_applicability(
                        left,
                        right,
                        relation,
                    ),
                    EvidenceSupersessionApplicabilityStatus
                    .RELATION_ENDPOINT_MISMATCH,
                )

    def test_argument_order_is_independent(self):
        left = make_proposition(
            proposition_id="left",
            value=Decimal("1"),
        )
        right = make_proposition(
            proposition_id="right",
            finding_id="finding-b",
            value=Decimal("2"),
        )
        relations = (
            make_relation("left", "right"),
            make_relation("left", "unrelated"),
        )
        for relation in relations:
            with self.subTest(relation=relation):
                self.assertIs(
                    classify_explicit_supersession_applicability(
                        left,
                        right,
                        relation,
                    ),
                    classify_explicit_supersession_applicability(
                        right,
                        left,
                        relation,
                    ),
                )

    def test_exact_identifier_matching_without_normalization(self):
        cases = (
            ("left", "RIGHT"),
            ("left", " right "),
            ("\u00e9", "e\u0301"),
        )
        for left_id, relation_left_id in cases:
            with self.subTest(
                left_id=repr(left_id),
                relation_id=repr(relation_left_id),
            ):
                left = make_proposition(
                    proposition_id=left_id,
                    value=Decimal("1"),
                )
                right = make_proposition(
                    proposition_id="right",
                    finding_id="finding-b",
                    value=Decimal("2"),
                )
                relation = make_relation(
                    relation_left_id,
                    "right",
                )
                self.assertIs(
                    classify_explicit_supersession_applicability(
                        left,
                        right,
                        relation,
                    ),
                    EvidenceSupersessionApplicabilityStatus
                    .RELATION_ENDPOINT_MISMATCH,
                )

    def test_duplicate_proposition_ids_cannot_match_valid_relation(self):
        left = make_proposition(
            proposition_id="same",
            value=Decimal("1"),
        )
        right = make_proposition(
            proposition_id="same",
            finding_id="finding-b",
            value=Decimal("2"),
        )
        relation = make_relation("same", "other")

        self.assertIs(
            classify_explicit_supersession_applicability(
                left,
                right,
                relation,
            ),
            EvidenceSupersessionApplicabilityStatus
            .RELATION_ENDPOINT_MISMATCH,
        )

    def test_inputs_and_field_objects_are_preserved(self):
        left_id = " left "
        right_id = " right "
        left = make_proposition(
            proposition_id=left_id,
            value=Decimal("1.00"),
        )
        right = make_proposition(
            proposition_id=right_id,
            finding_id="finding-b",
            value=Decimal("2.00"),
        )
        relation = make_relation(left_id, right_id)
        snapshots = (repr(left), repr(right), repr(relation))

        result = classify_explicit_supersession_applicability(
            left,
            right,
            relation,
        )

        self.assertIs(
            result,
            EvidenceSupersessionApplicabilityStatus.APPLICABLE,
        )
        self.assertEqual(
            (repr(left), repr(right), repr(relation)),
            snapshots,
        )
        self.assertIs(left.proposition_id, left_id)
        self.assertIs(right.proposition_id, right_id)
        self.assertIs(
            relation.superseded_proposition_id,
            left_id,
        )
        self.assertIs(
            relation.superseding_proposition_id,
            right_id,
        )

    def test_production_structure_and_import_boundaries(self):
        package = Path(__file__).resolve().parents[1]
        models_tree = ast.parse(
            (package / "models.py").read_text()
        )
        classification_tree = ast.parse(
            (package / "classification.py").read_text()
        )

        model_imports = [
            node.module
            for node in ast.walk(models_tree)
            if isinstance(node, ast.ImportFrom)
        ]
        self.assertEqual(model_imports, ["enum"])

        classification_imports = {
            node.module
            for node in ast.walk(classification_tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            classification_imports,
            {
                "EvidenceProposition.models",
                "EvidenceContradiction.models",
                "EvidenceContradiction.classification",
                "EvidenceSupersession.models",
                "EvidenceSupersession.validation",
                "EvidenceSupersessionApplicability.models",
            },
        )
        functions = [
            node
            for node in classification_tree.body
            if isinstance(node, ast.FunctionDef)
        ]
        self.assertEqual(
            [node.name for node in functions],
            ["classify_explicit_supersession_applicability"],
        )
        self.assertFalse(
            any(
                isinstance(node, (ast.For, ast.While))
                for node in ast.walk(classification_tree)
            )
        )
        self.assertFalse(
            any(
                isinstance(node, ast.ClassDef)
                for node in ast.walk(classification_tree)
            )
        )

    def test_frozen_packages_have_no_reverse_dependency(self):
        repository = Path(__file__).resolve().parents[2]
        evidence_suffixes = (
            "Validation",
            "Provenance",
            "Assessment",
            "Aggregation",
            "Proposition",
            "Comparison",
            "Contradiction",
            "Supersession",
        )
        frozen_packages = (
            "ResearchDomain",
            *(f"Evidence{name}" for name in evidence_suffixes),
        )
        target = "EvidenceSupersession" + "Applicability"
        for package_name in frozen_packages:
            for source in (
                repository / package_name
            ).rglob("*.py"):
                tree = ast.parse(source.read_text())
                modules = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        modules.extend(
                            alias.name for alias in node.names
                        )
                    elif isinstance(node, ast.ImportFrom):
                        modules.append(node.module or "")
                self.assertFalse(
                    any(
                        module == target
                        or module.startswith(f"{target}.")
                        for module in modules
                    ),
                    source,
                )


if __name__ == "__main__":
    unittest.main()
