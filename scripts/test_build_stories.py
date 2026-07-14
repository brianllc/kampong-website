import unittest
import build_stories as b


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(b.slugify("Primary One"), "primary-one")

    def test_punctuation_and_number(self):
        self.assertEqual(
            b.slugify("Getting Better in Chinese, Part 1"),
            "getting-better-in-chinese-part-1",
        )

    def test_ampersand(self):
        self.assertEqual(b.slugify("Spoons & Balloons"), "spoons-and-balloons")


class TestCleanSection(unittest.TestCase):
    def test_strips_parenthetical_and_titlecases(self):
        self.assertEqual(b.clean_section("Lower primary (P1 to P3)"), "Lower Primary")

    def test_plain(self):
        self.assertEqual(b.clean_section("Kindergarten"), "Kindergarten")


MANIFEST = """# Book Order

## 1. Kindergarten

1. Kindergarten — `Drafts/my-first-day-at-kindergarten.md`
2. Spoons and Balloons — `Drafts/spoons-and-balloons.md`

## 2. Lower primary (P1 to P3)

4. Primary One — `Drafts/first-day-of-primary-school.md` *(placement tentative)*
"""


class TestParseManifest(unittest.TestCase):
    def test_order_and_fields(self):
        items = b.parse_manifest(MANIFEST)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["title"], "Kindergarten")
        self.assertEqual(items[0]["src"], "Drafts/my-first-day-at-kindergarten.md")
        self.assertEqual(items[0]["section"], "Kindergarten")
        self.assertEqual(items[2]["title"], "Primary One")
        self.assertEqual(items[2]["section"], "Lower Primary")
        self.assertEqual(items[2]["src"], "Drafts/first-day-of-primary-school.md")


DRAFT = """# Spoons and Balloons
<!-- status: awaiting read · level: K · year: ~1987 -->

One evening, Brian sat down.

He drew a spoon.
"""

DRAFT_NO_YEAR = """# Mystery
<!-- status: awaiting read · level: K (placement tentative) · year: ? -->

A paragraph.
"""


class TestParseDraft(unittest.TestCase):
    def test_title_year_paragraphs(self):
        title, year, paras = b.parse_draft(DRAFT)
        self.assertEqual(title, "Spoons and Balloons")
        self.assertEqual(year, "~1987")
        self.assertEqual(paras, ["One evening, Brian sat down.", "He drew a spoon."])

    def test_unknown_year_is_none(self):
        title, year, paras = b.parse_draft(DRAFT_NO_YEAR)
        self.assertIsNone(year)
        self.assertEqual(title, "Mystery")


class TestMdInline(unittest.TestCase):
    def test_escapes_then_emphasis(self):
        self.assertEqual(
            b.md_inline("**Author's note:** really *Chrysopogon* & <b>x</b>"),
            "<strong>Author's note:</strong> really <em>Chrysopogon</em> "
            "&amp; &lt;b&gt;x&lt;/b&gt;",
        )


class TestFirstSentence(unittest.TestCase):
    def test_first_sentence(self):
        self.assertEqual(
            b.first_sentence(["One evening, Brian sat down. He drew a spoon."]),
            "One evening, Brian sat down.",
        )


if __name__ == "__main__":
    unittest.main()
