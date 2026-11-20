"""Tests for TXT gamertag importing and safe input handling."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from gamertag_finder.importer import (
    GamertagImportError,
    import_gamertags,
)


class ImportGamertagsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)

    def write_file(self, name, content):
        file_path = self.directory / name
        file_path.write_bytes(content)
        return file_path

    def test_imports_normal_txt_file(self):
        file_path = self.write_file(
            "gamertags.txt", b"Alpha\nBravo\nCharlie"
        )

        result = import_gamertags(file_path)

        self.assertEqual(result.gamertags, ("Alpha", "Bravo", "Charlie"))
        self.assertEqual(result.total_lines, 3)
        self.assertEqual(result.imported_count, 3)
        self.assertEqual(result.duplicates_skipped, 0)
        self.assertEqual(result.blank_lines_ignored, 0)

    def test_skips_case_insensitive_duplicates_and_existing_names(self):
        file_path = self.write_file(
            "gamertags.txt", "Alpha\nALPHA\nBeta\n".encode("utf-8")
        )

        result = import_gamertags(file_path, existing_names=["beta"])

        self.assertEqual(result.gamertags, ("Alpha",))
        self.assertEqual(result.duplicates_skipped, 2)
        self.assertEqual(result.imported_count, 1)

    def test_ignores_blank_and_whitespace_only_lines(self):
        file_path = self.write_file(
            "gamertags.txt", b"\n   \nAlpha\n\t\n"
        )

        result = import_gamertags(file_path)

        self.assertEqual(result.total_lines, 4)
        self.assertEqual(result.gamertags, ("Alpha",))
        self.assertEqual(result.blank_lines_ignored, 3)

    def test_empty_file_returns_empty_summary(self):
        file_path = self.write_file("gamertags.txt", b"")

        result = import_gamertags(file_path)

        self.assertEqual(result.gamertags, ())
        self.assertEqual(result.total_lines, 0)
        self.assertEqual(result.imported_count, 0)
        self.assertEqual(result.duplicates_skipped, 0)
        self.assertEqual(result.blank_lines_ignored, 0)

    def test_missing_file_reports_clear_error(self):
        with self.assertRaisesRegex(GamertagImportError, "does not exist"):
            import_gamertags(self.directory / "missing.txt")

    def test_rejects_non_txt_file(self):
        file_path = self.write_file("gamertags.csv", b"Alpha\n")

        with self.assertRaisesRegex(GamertagImportError, r"\.txt"):
            import_gamertags(file_path)

    def test_rejects_directory_as_input(self):
        directory_path = self.directory / "folder.txt"
        directory_path.mkdir()

        with self.assertRaisesRegex(GamertagImportError, "not a file"):
            import_gamertags(directory_path)

    def test_unreadable_file_reports_clear_error(self):
        file_path = self.write_file("gamertags.txt", b"Alpha\n")

        with patch.object(Path, "open", side_effect=PermissionError):
            with self.assertRaisesRegex(GamertagImportError, "cannot be read"):
                import_gamertags(file_path)

    def test_invalid_utf8_fails_without_replacing_characters(self):
        file_path = self.write_file("gamertags.txt", b"Alpha\n\xff\xfe")

        with self.assertRaisesRegex(GamertagImportError, "valid UTF-8"):
            import_gamertags(file_path)

    def test_preserves_unusual_utf8_characters(self):
        file_path = self.write_file(
            "gamertags.txt", "Zoë\n東京\nÑandú\n".encode("utf-8")
        )

        result = import_gamertags(file_path)

        self.assertEqual(result.gamertags, ("Zoë", "東京", "Ñandú"))

    def test_trims_outer_spaces_and_preserves_capitalization(self):
        file_path = self.write_file(
            "gamertags.txt", b"  MiXeD Case  \n"
        )

        result = import_gamertags(file_path)

        self.assertEqual(result.gamertags, ("MiXeD Case",))

    def test_accepts_utf8_bom(self):
        file_path = self.write_file(
            "gamertags.txt", b"\xef\xbb\xbfAlpha\n"
        )

        result = import_gamertags(file_path)

        self.assertEqual(result.gamertags, ("Alpha",))


if __name__ == "__main__":
    unittest.main()
