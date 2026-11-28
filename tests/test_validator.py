"""Tests for the documented modern Xbox gamertag formatting checks."""

from pathlib import Path
import unittest


from toolsy_core.validator import (
    ValidationStatus,
    validate_gamertag,
    validate_gamertags,
)


class ValidateGamertagTests(unittest.TestCase):
    def assert_valid(self, gamertag):
        result = validate_gamertag(gamertag)
        self.assertEqual(result.status, ValidationStatus.VALID)
        self.assertIsNone(result.reason)
        return result

    def assert_invalid(self, gamertag, reason_fragment):
        result = validate_gamertag(gamertag)
        self.assertEqual(result.status, ValidationStatus.INVALID)
        self.assertIn(reason_fragment, result.reason)
        return result

    def test_nonempty_short_name_passes_without_an_official_minimum_rule(self):
        self.assert_valid("A")
        self.assert_valid("P3")

    def test_empty_name_is_invalid(self):
        self.assert_invalid("", "empty")

    def test_twelve_rendered_characters_pass_standard_limit(self):
        self.assert_valid("ABCDEFGHIJKL")

    def test_thirteen_to_fifteen_latin_characters_include_preview_note(self):
        for name in ("ABCDEFGHIJKLM", "ABCDEFGHIJKLMNO"):
            with self.subTest(name=name):
                result = self.assert_valid(name)
                self.assertIn("Insider preview", result.note)

    def test_sixteen_rendered_characters_are_too_long(self):
        self.assert_invalid("ABCDEFGHIJKLMNOP", "Too long")

    def test_non_latin_name_over_twelve_rendered_characters_is_invalid(self):
        self.assert_invalid("東京東京東京東京東京東京東京", "Too long")

    def test_supported_ascii_letters_digits_apostrophe_and_spaces(self):
        self.assert_valid("A B'9")
        # Xbox publishes U+0020 as supported but gives no placement rule.
        self.assert_valid(" A  B ")

    def test_supported_latin_diacritics_and_extended_letters(self):
        self.assert_valid("Zoë")
        self.assert_valid("Āngström")

    def test_supported_non_latin_scripts(self):
        for name in ("東京", "한글", "Привет", "Ελλάδα", "שלום", "مرحبا"):
            with self.subTest(name=name):
                self.assert_valid(name)

    def test_supported_thai_diacritic_counts_as_one_rendered_character(self):
        self.assert_valid("กิ")

    def test_unsupported_punctuation_and_emoji_have_clear_reasons(self):
        self.assert_invalid("Bad#Name", "U+0023")
        self.assert_invalid("Tag😀", "U+1F600")

    def test_unsupported_whitespace_control_character_is_reported(self):
        self.assert_invalid("Alpha\tBeta", "U+0009")

    def test_diacritic_without_base_character_is_invalid(self):
        self.assert_invalid("\u0e34A", "Invalid formatting")

    def test_multiple_names_keep_order_and_original_spelling(self):
        results = validate_gamertags(["MiXeD", "Bad#Tag", "東京"])

        self.assertEqual(
            tuple(result.gamertag for result in results),
            ("MiXeD", "Bad#Tag", "東京"),
        )
        self.assertEqual(
            tuple(result.status for result in results),
            (
                ValidationStatus.VALID,
                ValidationStatus.INVALID,
                ValidationStatus.VALID,
            ),
        )


if __name__ == "__main__":
    unittest.main()
