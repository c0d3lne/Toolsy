# Gamertag Finder

A modular, local-first Python terminal application for importing gamertags,
validating names, reviewing availability results, and exporting them. Checks
will never reserve or claim a name. Availability will remain `UNKNOWN` unless a
safe, official checking method is verified.

## Project checklist

- [x] Stage 1 – Create the project folder structure.
- [x] Stage 2 – Create the main application entry point.
- [x] Stage 3 – Build the TXT gamertag importer.
- [x] Stage 4 – Build the gamertag validation system.
- [ ] Stage 5 – Investigate and implement a verified availability-checking method.
- [ ] Stage 6 – Build the results display and status indicators.
- [ ] Stage 7 – Build the manual claim assistant.
- [ ] Stage 8 – Build the proxy manager.
- [ ] Stage 9 – Build the watchlist.
- [ ] Stage 10 – Build CSV and TXT exporting.
- [ ] Stage 11 – Build the cyber-style interface.
- [ ] Stage 12 – Connect all modules together.
- [ ] Stage 13 – Test the complete application.
- [ ] Stage 14 – Review security, dependencies and unexpected behaviour.
- [ ] Stage 15 – Prepare the finished project for download and local Windows use.

Stages 1 through 4 are complete. Availability checking and the remaining
product features are not implemented yet.

## Planned folder structure

```text
gamertag-finder/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
├── data/
│   ├── imports/                 # Local gamertag and proxy input files
│   └── exports/                 # Generated CSV and TXT results
├── src/
│   └── gamertag_finder/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── menu.py
│       ├── config.py
│       ├── models.py
│       ├── importer.py
│       ├── validator.py
│       ├── availability.py
│       ├── results.py
│       ├── claim_assistant.py
│       ├── proxy_manager.py
│       ├── watchlist.py
│       ├── exporter.py
│       └── terminal_ui.py
└── tests/
    ├── test_app.py
    ├── test_importer.py
    ├── test_validator.py
    ├── test_availability.py
    ├── test_results.py
    ├── test_claim_assistant.py
    ├── test_proxy_manager.py
    ├── test_watchlist.py
    ├── test_exporter.py
    └── test_terminal_ui.py
```

`main.py`, `src/gamertag_finder/__init__.py`,
`src/gamertag_finder/__main__.py`, `src/gamertag_finder/app.py`,
`src/gamertag_finder/menu.py`, and `tests/test_app.py` were implemented in Stage
2. Stage 3 adds `src/gamertag_finder/importer.py` and
`tests/test_importer.py`. Stage 4 adds `src/gamertag_finder/validator.py` and
`tests/test_validator.py`. Other `.py` files in the tree are planned for later
stages.
`data/imports/` and `data/exports/` are ready for local files. Add
`gamertags.txt` and `proxies.txt` to `data/imports/` when implementing the
relevant stages.

## Planned Python files

### Application modules

- `src/gamertag_finder/__init__.py` — marks the source folder as a Python package.
- `src/gamertag_finder/__main__.py` — supports launching the package with
  `python -m gamertag_finder`.
- `src/gamertag_finder/app.py` — runs the menu loop, stores imported names for
  the current session, reports import summaries and formatting results, and
  handles unfinished options without pretending they work.
- `src/gamertag_finder/menu.py` — contains the ASCII banner and menu labels.
  Stage 2 keeps this presentation deliberately simple; the fuller terminal
  styling remains for Stage 11.
- `src/gamertag_finder/config.py` — centralizes local input, watchlist, and
  export paths and application settings.
- `src/gamertag_finder/models.py` — defines shared gamertag and result-status
  data structures.
- `src/gamertag_finder/importer.py` — reads UTF-8 `.txt` files one line at a
  time, trims entries, skips blank and case-insensitive duplicate names, and
  returns import counts. Invalid UTF-8 is rejected rather than silently
  altered.
- `src/gamertag_finder/validator.py` — checks modern gamertags against the
  documented character ranges and length rules without making network
  requests. A valid result means formatting-only; it does not mean available
  or claimable.
- `src/gamertag_finder/availability.py` — owns the availability-checking
  boundary. It must return `UNKNOWN` unless a safe, official method is verified;
  it must not claim or reserve names.
- `src/gamertag_finder/results.py` — formats result rows and status counts for
  display.
- `src/gamertag_finder/claim_assistant.py` — offers a manual action that opens a
  verified official Xbox claiming page; it will not automate claiming.
- `src/gamertag_finder/proxy_manager.py` — imports, numbers, and displays proxy
  entries and their test status. Proxy support will not be used to bypass
  service limits or access controls.
- `src/gamertag_finder/watchlist.py` — stores and presents watched names and
  uses only the safe checking behavior established for availability.
- `src/gamertag_finder/exporter.py` — exports results to CSV and TXT.
- `src/gamertag_finder/terminal_ui.py` — handles the terminal logo, colors,
  progress feedback, statistics, and menu presentation.

### Planned test modules

- `tests/test_app.py` — checks application startup and menu coordination.
- `tests/test_importer.py` — checks normal, duplicate, blank, empty, missing,
  unreadable, unusual-character, whitespace, BOM, and invalid-encoding files.
- `tests/test_validator.py` — checks length boundaries, supported and
  unsupported characters, spaces, diacritics, empty input, and batch results.
- `tests/test_availability.py` — checks status handling, including safe
  `UNKNOWN` behavior when no verified method is available.
- `tests/test_results.py` — checks displayed statuses and summary counts.
- `tests/test_claim_assistant.py` — checks manual-link behavior without opening
  a real browser during tests.
- `tests/test_proxy_manager.py` — checks proxy parsing, numbering, and reported
  test states.
- `tests/test_watchlist.py` — checks adding, removing, loading, and safe
  monitoring of watched names.
- `tests/test_exporter.py` — checks CSV and TXT output.
- `tests/test_terminal_ui.py` — checks terminal output and status formatting.

## Dependencies and local requirements

- **Python 3.10 or newer** is planned for local Windows use.
- **Third-party runtime dependencies: none planned.** File handling, CSV,
  command-line interaction, browser launching, and test support can use the
  Python standard library.
- `requirements.txt` is intentionally empty apart from a note. A dependency
  will only be added if a later stage demonstrates it is necessary.
- The interface will use standard terminal color support where available and
  degrade to readable plain text otherwise; no color package is planned.
- No network-checking package or service will be added unless Stage 5 verifies
  that its use is safe and supported.

## Stage 1 verification

The directories and README checklist were created and inspected. No application
code existed at the end of Stage 1, so module tests were deferred then.

## Stage 2 implementation and verification

- `main.py` is the local launcher; run it from this folder with
  `python main.py`.
- The menu and app loop live in separate package modules. Unfinished options
  only display “not available yet”; no feature behavior is simulated.
- `python -m unittest discover -s tests -v` runs the Stage 2 menu tests.
- Stage 2 tests cover the logo and menu labels, the then-unfinished feature
  options, invalid selections, exit, and end-of-input handling.
- No third-party packages were installed.

## Stage 3 implementation and verification

- From the menu, choose **Import Gamertags** and enter the path to a `.txt` file.
  Quoted paths are accepted for Windows paths copied from File Explorer.
- UTF-8 and UTF-8-with-BOM files are supported. Invalid UTF-8 is reported with
  instructions to save the file as UTF-8; no replacement characters are
  inserted.
- Blank lines are ignored. Outer whitespace is trimmed. Duplicate comparison
  is case-insensitive, while the spelling and capitalization of the first
  occurrence are preserved, including duplicates from earlier imports in the
  same session.
- Imported names and counts are held in the application session. No name
  validation or availability check is performed at this stage.
- `python -m unittest discover -s tests -v` runs the Stage 2 and Stage 3 tests;
  all 20 tests passed during Stage 3 verification.
- A live console run imported a sample containing whitespace, a blank line, a
  case-insensitive duplicate, and a Unicode name; the summary and imported list
  matched the input.

## Stage 4 format rules and verification

This app validates **modern** gamertag components, not classic gamertags or the
display suffix. Rules were checked against Microsoft documentation on
2026-11-20:

- The published GDK baseline is at most 12 rendered characters. Supported
  combining diacritics do not add another rendered character; the GDK docs
  allow up to one diacritic per character.
- Microsoft documents specific creatable character ranges: Latin letters and
  digits, apostrophe, U+0020 space, selected Latin extensions, and listed
  language ranges for Cyrillic, Hebrew, Arabic/Urdu, Devanagari, Bengali, Thai,
  Greek, Hangul, Hiragana, Katakana, and CJK. Other Unicode characters and
  reserved punctuation are rejected.
- An Xbox Insider announcement dated 2026-06-24 describes a preview allowing
  up to 15 rendered characters for unique, available gamertags. Names that
  need a suffix or contain non-Latin characters may remain limited to 12.
  Accordingly, this offline validator accepts 13–15 character Latin names with
  an explicit preview/eligibility note; it cannot determine availability or
  whether that preview applies to the user's account.
- The official GDK sources reviewed did not state a minimum length or rules
  about where spaces may appear or whether spaces may repeat. The validator
  rejects an empty string, but does not invent a positive minimum or space
  placement restriction. The Stage 3 importer still trims surrounding
  whitespace from file entries.
- No name validation establishes availability, eligibility, or claimability.

Sources:

- [Microsoft GDK: Modern gamertags definition and terminology](https://learn.microsoft.com/en-us/gaming/gdk/docs/services/fundamentals/identity/user-profile/gamertags/live-modern-gamertags-definition?view=gdk-2604)
- [Microsoft GDK: UTF-8 character ranges for modern gamertags](https://learn.microsoft.com/en-us/gaming/gdk/docs/services/fundamentals/identity/user-profile/gamertags/live-modern-gamertags-unicode?view=gdk-2610)
- [Xbox Wire: Unique gamertags expanded to 15 characters (Insider preview)](https://news.xbox.com/en-us/2026/06/24/xbox-insiders-august-2026-console-features/)

- Choose **Check Gamertags** after importing to see `VALID` and `INVALID`
  groups, invalid reasons, counts, and any preview caveats. No online check is
  made.
- `python -m unittest discover -s tests -v` runs the Stage 2–4 tests.
- All 36 automated tests passed, including validation boundaries, supported
  Unicode scripts, invalid characters, reasons, and menu integration.
- A console run confirmed that the empty-import message appears, then validated
  a mixed sample into separate valid and invalid groups with counts.
