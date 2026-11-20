"""Tests for the menu, importer integration, and placeholder behavior."""

from pathlib import Path
import sys
import tempfile
import unittest


SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from gamertag_finder.app import FEATURE_OPTIONS, main


class MainMenuTests(unittest.TestCase):
    def run_app(self, selections):
        output = []
        pending_selections = iter(selections)

        def read_input(_prompt):
            try:
                return next(pending_selections)
            except StopIteration as exc:
                raise EOFError from exc

        main(input_fn=read_input, output_fn=output.append)
        return "\n".join(output)

    def test_menu_shows_ascii_title_and_every_option(self):
        output = self.run_app(["9"])

        self.assertIn("GAMERTAG FINDER", output)
        self.assertIn("_____", output)
        for number, label in (*FEATURE_OPTIONS, ("9", "Exit")):
            with self.subTest(option=label):
                self.assertIn(f"[{number}] {label}", output)

    def test_unfinished_feature_options_are_explicit_placeholders(self):
        for number, label in FEATURE_OPTIONS:
            if number == "1":
                continue
            with self.subTest(option=label):
                output = self.run_app([number, "9"])
                self.assertIn(f"{label} is not available yet.", output)

    def test_import_menu_option_reports_import_summary_and_names(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_file = Path(temporary_directory) / "gamertags.txt"
            input_file.write_text("  Alpha  \n\nBeta\n", encoding="utf-8")

            output = self.run_app(["1", str(input_file), "9"])

        self.assertIn("Total lines read: 3", output)
        self.assertIn("Gamertags imported: 2", output)
        self.assertIn("Duplicates skipped: 0", output)
        self.assertIn("Blank lines ignored: 1", output)
        self.assertIn(" - Alpha", output)
        self.assertIn(" - Beta", output)

    def test_import_menu_option_keeps_session_names_unique(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            first_file = Path(temporary_directory) / "first.txt"
            second_file = Path(temporary_directory) / "second.txt"
            first_file.write_text("Alpha\n", encoding="utf-8")
            second_file.write_text("alpha\nBeta\n", encoding="utf-8")

            output = self.run_app(
                ["1", str(first_file), "1", str(second_file), "9"]
            )

        self.assertIn("Duplicates skipped: 1", output)
        self.assertIn("Gamertags imported: 1", output)
        self.assertIn(" - Beta", output)

    def test_import_failure_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_file = Path(temporary_directory) / "missing.txt"
            output = self.run_app(["1", str(missing_file), "9"])

        self.assertIn("Import failed: File does not exist:", output)
        self.assertIn("Exiting Gamertag Finder.", output)

    def test_invalid_selections_are_reported_and_menu_continues(self):
        output = self.run_app(["abc", "10", "", "9"])

        self.assertEqual(output.count("Invalid selection."), 3)
        self.assertIn("Exiting Gamertag Finder.", output)

    def test_exit_option_stops_the_menu(self):
        output = self.run_app(["9"])

        self.assertIn("Exiting Gamertag Finder.", output)
        self.assertNotIn("Invalid selection.", output)

    def test_end_of_input_exits_cleanly(self):
        output = self.run_app([])

        self.assertIn("Exiting Gamertag Finder.", output)


if __name__ == "__main__":
    unittest.main()
