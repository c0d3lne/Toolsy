# Gamertag Finder

A modular, local-first Python terminal application for importing gamertags,
validating names, reviewing availability results, and exporting them. Checks
will never reserve or claim a name. Availability will remain `UNKNOWN` unless a
safe, official checking method is verified.

## Project checklist

- [x] Stage 1 – Create the project folder structure.
- [x] Stage 2 – Create the main application entry point.
- [ ] Stage 3 – Build the TXT gamertag importer.
- [ ] Stage 4 – Build the gamertag validation system.
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

Stages 1 and 2 are complete. Stage 2 adds only the launcher, menu, and
placeholder responses; the listed product features are not implemented yet.

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
`src/gamertag_finder/menu.py`, and `tests/test_app.py` are implemented in Stage
2. Other `.py` files in the tree are planned for later stages.
`data/imports/` and `data/exports/` are ready for local files. Add
`gamertags.txt` and `proxies.txt` to `data/imports/` when implementing the
relevant stages.

## Planned Python files

### Application modules

- `src/gamertag_finder/__init__.py` — marks the source folder as a Python package.
- `src/gamertag_finder/__main__.py` — supports launching the package with
  `python -m gamertag_finder`.
- `src/gamertag_finder/app.py` — runs the menu loop, validates selections, exits
  cleanly, and reports unfinished options without pretending they work.
- `src/gamertag_finder/menu.py` — contains the ASCII banner and menu labels.
  Stage 2 keeps this presentation deliberately simple; the fuller terminal
  styling remains for Stage 11.
- `src/gamertag_finder/config.py` — centralizes local input, watchlist, and
  export paths and application settings.
- `src/gamertag_finder/models.py` — defines shared gamertag and result-status
  data structures.
- `src/gamertag_finder/importer.py` — reads one-name-per-line TXT files and
  reports unreadable or empty input clearly.
- `src/gamertag_finder/validator.py` — checks names against documented rules
  without making network requests.
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
- `tests/test_importer.py` — checks line parsing, blank lines, and file errors.
- `tests/test_validator.py` — checks valid and invalid name cases.
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
- Stage 2 tests cover the logo and all menu labels, every unfinished feature
  option, invalid selections, exit, and end-of-input handling.
- No third-party packages were installed.
