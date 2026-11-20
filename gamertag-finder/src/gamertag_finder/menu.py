"""Text-only banner and menu for the first application stage."""

MENU_OPTIONS = (
    ("1", "Import Gamertags"),
    ("2", "Check Gamertags"),
    ("3", "View Results"),
    ("4", "Claim Gamertag"),
    ("5", "Proxy Manager"),
    ("6", "Watchlist"),
    ("7", "Export Results"),
    ("8", "Settings"),
    ("9", "Exit"),
)

ASCII_LOGO = r"""
   _____                          ____
  / ____|                        |  __|
 | |  __  __ _ _ __ ___   ___ _ __| |__ _   _ ____
 | | |_ |/ _` | '_ ` _ \ / _ \ '__|  __| | | |_  /
 | |__| | (_| | | | | | |  __/ |  | |  | |_| |/ /
  \_____|\__,_|_| |_| |_|\___|_|  |_|   \__, /___|
                                          __/ |
                                         |___/
"""


def display_menu(output_fn=print):
    """Write the ASCII banner and available menu choices."""
    output_fn(ASCII_LOGO)
    output_fn(">> GAMERTAG FINDER :: LOCAL CONSOLE")
    output_fn("=" * 44)
    for number, label in MENU_OPTIONS:
        output_fn(f" [{number}] {label}")
    output_fn("=" * 44)
