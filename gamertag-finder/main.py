"""Windows-friendly launcher for the Gamertag Finder application."""

from pathlib import Path
import sys


SOURCE_DIRECTORY = Path(__file__).resolve().parent / "src"
source_path = str(SOURCE_DIRECTORY)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from gamertag_finder.app import main


if __name__ == "__main__":
    main()
