"""Application loop and safe handling for unfinished features."""

from .importer import GamertagImportError, import_gamertags
from .menu import MENU_OPTIONS, display_menu

EXIT_OPTION = "9"
FEATURE_OPTIONS = tuple(
    (number, label)
    for number, label in MENU_OPTIONS
    if number != EXIT_OPTION
)


def main(input_fn=None, output_fn=None):
    """Run the interactive menu until the user exits or input closes."""
    read_input = input if input_fn is None else input_fn
    write_output = print if output_fn is None else output_fn
    available_choices = ", ".join(number for number, _ in MENU_OPTIONS)
    imported_gamertags = []

    while True:
        display_menu(write_output)
        try:
            selection = read_input("Select an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            write_output("\nExiting Gamertag Finder.")
            return

        if selection == EXIT_OPTION:
            write_output("Exiting Gamertag Finder.")
            return

        selected_feature = dict(FEATURE_OPTIONS).get(selection)
        if selected_feature is None:
            write_output(
                f"Invalid selection. Choose one of: {available_choices}."
            )
            continue

        if selection == "1":
            try:
                file_path = read_input("Path to .txt file: ").strip()
            except (EOFError, KeyboardInterrupt):
                write_output("\nImport cancelled.")
                continue

            if len(file_path) >= 2 and file_path[0] == file_path[-1] == '"':
                file_path = file_path[1:-1]

            try:
                result = import_gamertags(file_path, imported_gamertags)
            except GamertagImportError as exc:
                write_output(f"Import failed: {exc}")
                continue

            imported_gamertags.extend(result.gamertags)
            write_output(f"Total lines read: {result.total_lines}")
            write_output(f"Gamertags imported: {result.imported_count}")
            write_output(f"Duplicates skipped: {result.duplicates_skipped}")
            write_output(f"Blank lines ignored: {result.blank_lines_ignored}")
            write_output("Imported names:")
            if result.gamertags:
                for gamertag in result.gamertags:
                    write_output(f" - {gamertag}")
            else:
                write_output(" (none)")
            continue

        write_output(f"{selected_feature} is not available yet.")
