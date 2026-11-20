"""Application loop and safe placeholder handling for unfinished features."""

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

        write_output(f"{selected_feature} is not available yet.")
