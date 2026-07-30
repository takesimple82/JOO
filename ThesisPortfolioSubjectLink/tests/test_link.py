import unittest
from dataclasses import FrozenInstanceError, MISSING, fields
from typing import get_type_hints

from ThesisPortfolioSubjectLink.models import (
    ExplicitThesisPortfolioSubjectLink,
)
from ThesisPortfolioSubjectLink.validation import (
    validate_explicit_thesis_portfolio_subject_link,
)


def make_link(**overrides):
    values = {
        "thesis_id": "thesis-001",
        "portfolio_subject_id": "subject-001",
    }
    values.update(overrides)
    return ExplicitThesisPortfolioSubjectLink(**values)


class StringSubclass(str):
    pass


class LinkSubclass(ExplicitThesisPortfolioSubjectLink):
    pass


class ThesisPortfolioSubjectLinkTests(unittest.TestCase):
    def test_exact_model_contract(self):
        model_fields = fields(ExplicitThesisPortfolioSubjectLink)
        self.assertEqual(
            [field.name for field in model_fields],
            ["thesis_id", "portfolio_subject_id"],
        )
        self.assertEqual(
            get_type_hints(ExplicitThesisPortfolioSubjectLink),
            {
                "thesis_id": str,
                "portfolio_subject_id": str,
            },
        )
        for field in model_fields:
            self.assertIs(field.default, MISSING)
            self.assertIs(field.default_factory, MISSING)
        self.assertNotIn(
            "__slots__",
            ExplicitThesisPortfolioSubjectLink.__dict__,
        )

    def test_frozen_hashable_structural_equality(self):
        first = make_link()
        same = make_link()
        self.assertEqual(first, same)
        self.assertEqual(hash(first), hash(same))
        with self.assertRaises(FrozenInstanceError):
            first.thesis_id = "replacement"

    def test_exact_link_type_and_subclass_rejection(self):
        for value in (
            None,
            object(),
            LinkSubclass("thesis-001", "subject-001"),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^link must be "
                    "ExplicitThesisPortfolioSubjectLink$",
                ):
                    validate_explicit_thesis_portfolio_subject_link(
                        value
                    )

    def test_thesis_id_requires_exact_string(self):
        for value in (
            None,
            1,
            b"thesis-001",
            StringSubclass("thesis-001"),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^thesis_id must be str$",
                ):
                    validate_explicit_thesis_portfolio_subject_link(
                        make_link(thesis_id=value)
                    )

    def test_thesis_id_rejects_blank(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^thesis_id must not be blank$",
                ):
                    validate_explicit_thesis_portfolio_subject_link(
                        make_link(thesis_id=value)
                    )

    def test_portfolio_subject_id_requires_exact_string(self):
        for value in (
            None,
            1,
            b"subject-001",
            StringSubclass("subject-001"),
        ):
            with self.subTest(value_type=type(value)):
                with self.assertRaisesRegex(
                    TypeError,
                    "^portfolio_subject_id must be str$",
                ):
                    validate_explicit_thesis_portfolio_subject_link(
                        make_link(portfolio_subject_id=value)
                    )

    def test_portfolio_subject_id_rejects_blank(self):
        for value in ("", " ", "\t", "\n", " \t\n "):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(
                    ValueError,
                    "^portfolio_subject_id must not be blank$",
                ):
                    validate_explicit_thesis_portfolio_subject_link(
                        make_link(portfolio_subject_id=value)
                    )

    def test_validation_order(self):
        cases = (
            (
                make_link(
                    thesis_id=None,
                    portfolio_subject_id=None,
                ),
                TypeError,
                "thesis_id must be str",
            ),
            (
                make_link(
                    thesis_id=" ",
                    portfolio_subject_id=None,
                ),
                ValueError,
                "thesis_id must not be blank",
            ),
            (
                make_link(portfolio_subject_id=None),
                TypeError,
                "portfolio_subject_id must be str",
            ),
            (
                make_link(portfolio_subject_id=" "),
                ValueError,
                "portfolio_subject_id must not be blank",
            ),
        )
        for link, error_type, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    error_type,
                    f"^{message}$",
                ):
                    validate_explicit_thesis_portfolio_subject_link(
                        link
                    )

    def test_success_preserves_identity_and_whitespace(self):
        thesis_id = " thesis-\u00e9 "
        portfolio_subject_id = " subject-e\u0301 "
        link = ExplicitThesisPortfolioSubjectLink(
            thesis_id,
            portfolio_subject_id,
        )
        self.assertIsNone(
            validate_explicit_thesis_portfolio_subject_link(link)
        )
        self.assertIs(link.thesis_id, thesis_id)
        self.assertIs(
            link.portfolio_subject_id,
            portfolio_subject_id,
        )

    def test_duplicates_and_shared_endpoints_are_allowed(self):
        first = make_link()
        duplicate = make_link()
        shared_thesis = make_link(
            portfolio_subject_id="subject-002"
        )
        shared_subject = make_link(thesis_id="thesis-002")
        self.assertEqual(first, duplicate)
        self.assertNotEqual(first, shared_thesis)
        self.assertNotEqual(first, shared_subject)

    def test_identifier_representation_is_not_normalized(self):
        self.assertNotEqual(
            make_link(thesis_id="\u00e9"),
            make_link(thesis_id="e\u0301"),
        )
        self.assertNotEqual(
            make_link(portfolio_subject_id="subject"),
            make_link(portfolio_subject_id="SUBJECT"),
        )


if __name__ == "__main__":
    unittest.main()
