"""Tests for the Stage 2 launcher menu and its placeholder behavior."""

from pathlib import Path
import sys
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
            with self.subTest(option=label):
                output = self.run_app([number, "9"])
                self.assertIn(f"{label} is not available yet.", output)

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
