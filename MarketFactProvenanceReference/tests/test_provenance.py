import ast
import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path
from typing import get_type_hints

from MarketFactProvenanceReference.models import (
    ExplicitMarketFactProvenanceReference,
)
from MarketFactProvenanceReference.validation import (
    validate_explicit_market_fact_provenance_reference,
)


def make_provenance(**overrides):
    values = {
        "fact_id": "fact-001",
        "source_identity": "source-001",
        "collected_at": "collected-at-001",
    }
    values.update(overrides)
    return ExplicitMarketFactProvenanceReference(**values)


class StringSubclass(str):
    pass


class ProvenanceSubclass(
    ExplicitMarketFactProvenanceReference
):
    pass


FIELD_NAMES = (
    "fact_id",
    "source_identity",
    "collected_at",
)


class MarketFactProvenanceReferenceTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(
            ExplicitMarketFactProvenanceReference
        )
        self.assertEqual(
            [field.name for field in model_fields],
            list(FIELD_NAMES),
        )
        self.assertEqual(
            get_type_hints(
                ExplicitMarketFactProvenanceReference
            ),
            {name: str for name in FIELD_NAMES},
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__post_init__",
            ExplicitMarketFactProvenanceReference.__dict__,
        )
        self.assertNotIn(
            "__slots__",
            ExplicitMarketFactProvenanceReference.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        first = make_provenance()
        same = make_provenance()
        different = make_provenance(fact_id="fact-002")
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        self.assertNotEqual(first, different)
        with self.assertRaises(FrozenInstanceError):
            first.fact_id = "replacement"

    def test_exact_model_type(self):
        for value in (
            None,
            object(),
            {},
            ProvenanceSubclass(
                "fact-001",
                "source-001",
                "collected-at-001",
            ),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^provenance must be "
                    "ExplicitMarketFactProvenanceReference$",
                ):
                    validate_explicit_market_fact_provenance_reference(
                        value
                    )

    def test_exact_string_types(self):
        invalid = (
            None,
            1,
            b"identity",
            StringSubclass("identity"),
        )
        for field_name in FIELD_NAMES:
            for value in invalid:
                with self.subTest(
                    field=field_name,
                    value_type=type(value),
                ):
                    with self.assertRaisesRegex(
                        TypeError,
                        f"^{field_name} must be str$",
                    ):
                        validate_explicit_market_fact_provenance_reference(
                            make_provenance(
                                **{field_name: value}
                            )
                        )

    def test_blank_identifiers_are_rejected(self):
        for field_name in FIELD_NAMES:
            for value in ("", " ", "\t\n"):
                with self.subTest(
                    field=field_name,
                    value=repr(value),
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"^{field_name} must not be blank$",
                    ):
                        validate_explicit_market_fact_provenance_reference(
                            make_provenance(
                                **{field_name: value}
                            )
                        )

    def test_validation_order(self):
        cases = (
            (
                make_provenance(
                    fact_id=None,
                    source_identity=None,
                    collected_at=None,
                ),
                TypeError,
                "fact_id must be str",
            ),
            (
                make_provenance(
                    fact_id=" ",
                    source_identity=None,
                ),
                ValueError,
                "fact_id must not be blank",
            ),
            (
                make_provenance(source_identity=None),
                TypeError,
                "source_identity must be str",
            ),
            (
                make_provenance(source_identity=" "),
                ValueError,
                "source_identity must not be blank",
            ),
            (
                make_provenance(collected_at=None),
                TypeError,
                "collected_at must be str",
            ),
            (
                make_provenance(collected_at=" "),
                ValueError,
                "collected_at must not be blank",
            ),
        )
        for provenance, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_market_fact_provenance_reference(
                        provenance
                    )

    def test_success_preserves_identifiers(self):
        values = {
            "fact_id": " fact-\u00e9 ",
            "source_identity": " source-e\u0301 ",
            "collected_at": " collected-at-001 ",
        }
        provenance = ExplicitMarketFactProvenanceReference(
            **values
        )
        self.assertIsNone(
            validate_explicit_market_fact_provenance_reference(
                provenance
            )
        )
        for field_name, value in values.items():
            self.assertIs(
                getattr(provenance, field_name),
                value,
            )

    def test_collected_at_is_opaque_string(self):
        for value in (
            "not-iso",
            "2024-01-01T00:00:00Z",
            " yesterday ",
        ):
            with self.subTest(value=repr(value)):
                self.assertIsNone(
                    validate_explicit_market_fact_provenance_reference(
                        make_provenance(
                            collected_at=value
                        )
                    )
                )

    def test_scope_dependencies_and_public_api(self):
        root = Path(__file__).resolve().parents[1]
        model_tree = ast.parse(
            (root / "models.py").read_text()
        )
        validation_tree = ast.parse(
            (root / "validation.py").read_text()
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(model_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"dataclasses"},
        )
        self.assertEqual(
            {
                node.module
                for node in ast.walk(validation_tree)
                if isinstance(node, ast.ImportFrom)
            },
            {"MarketFactProvenanceReference.models"},
        )
        self.assertEqual(
            [
                node.name
                for node in model_tree.body
                if isinstance(node, ast.ClassDef)
            ],
            ["ExplicitMarketFactProvenanceReference"],
        )
        self.assertEqual(
            [
                node.name
                for node in validation_tree.body
                if isinstance(node, ast.FunctionDef)
            ],
            [
                "validate_explicit_market_fact_"
                "provenance_reference"
            ],
        )
        production = (
            (root / "models.py").read_text()
            + (root / "validation.py").read_text()
        )
        for forbidden in (
            "ProviderGateway",
            "FactStore",
            "MarketSnapshotProducer",
            "Portfolio",
            "InvestmentResearchOrchestrator",
            "Automation",
            "source_class",
            "payload",
            "supersession",
            "runtime",
            "persistence",
        ):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
