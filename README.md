# Toolsy

Toolsy is a Windows desktop app for generating gamertag ideas, checking name formats, importing lists, managing tested proxies, and keeping a local watchlist.

## Features

- Generate names in several styles and send them to the Name Checker.
- Paste a list of names or import them from a TXT file.
- Check gamertag formatting locally.
- Test saved HTTP, HTTPS, and SOCKS proxies and rotate through working entries.
- Keep a local watchlist and application preferences.
- Choose a theme and installed system font.

## Development status

Toolsy is still in development. No API is connected. Name Checker validates formatting only; it does not check Xbox availability. Proxy rotation is not connected to name checks. Expect bugs as development continues.

## Run on Windows

1. Install Python 3.10 or newer.
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Start the application from this folder: `python gui/main.py`

## Local data

Settings, generated results, imported lists, watchlists, and proxies are saved in `data/`. These personal files are excluded from Git. Use the Settings page to export or back up local data.

## Developer

C0d3lne
