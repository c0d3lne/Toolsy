"""Read and deduplicate gamertags from a UTF-8 TXT file."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class GamertagImportError(Exception):
    """Raised when an input file cannot be imported safely."""


@dataclass(frozen=True)
class ImportResult:
    """Names imported from a file and a summary of the lines processed."""

    gamertags: tuple[str, ...]
    total_lines: int
    imported_count: int
    duplicates_skipped: int
    blank_lines_ignored: int


def import_gamertags(
    file_path: str | Path,
    existing_names: Iterable[str] = (),
) -> ImportResult:
    """Import unique, trimmed names from a UTF-8 encoded .txt file.

    Duplicate detection is case-insensitive while the spelling and
    capitalization of the first occurrence are preserved.
    """
    if not str(file_path).strip():
        raise GamertagImportError("No file path was provided.")

    try:
        path = Path(file_path).expanduser()
    except (TypeError, ValueError) as exc:
        raise GamertagImportError("The file path is not valid.") from exc

    if path.suffix.lower() != ".txt":
        raise GamertagImportError("Please select a .txt file.")

    try:
        if not path.exists():
            raise GamertagImportError(f"File does not exist: {path}")
        if not path.is_file():
            raise GamertagImportError("The selected path is not a file.")
    except OSError as exc:
        raise GamertagImportError(f"The selected path cannot be accessed: {exc}") from exc

    seen_names = {
        name.strip().casefold()
        for name in existing_names
        if name.strip()
    }
    gamertags = []
    total_lines = 0
    duplicates_skipped = 0
    blank_lines_ignored = 0

    try:
        with path.open("r", encoding="utf-8-sig", errors="strict") as source:
            for line in source:
                total_lines += 1
                gamertag = line.strip()
                if not gamertag:
                    blank_lines_ignored += 1
                    continue

                normalized_name = gamertag.casefold()
                if normalized_name in seen_names:
                    duplicates_skipped += 1
                    continue

                seen_names.add(normalized_name)
                gamertags.append(gamertag)
    except UnicodeDecodeError as exc:
        raise GamertagImportError(
            "The file is not valid UTF-8 text. Save it as UTF-8 and try again."
        ) from exc
    except FileNotFoundError as exc:
        raise GamertagImportError(f"File does not exist: {path}") from exc
    except PermissionError as exc:
        raise GamertagImportError(f"The file cannot be read: {path}") from exc
    except (OSError, ValueError) as exc:
        raise GamertagImportError(f"The file could not be read: {exc}") from exc

    imported_names = tuple(gamertags)
    return ImportResult(
        gamertags=imported_names,
        total_lines=total_lines,
        imported_count=len(imported_names),
        duplicates_skipped=duplicates_skipped,
        blank_lines_ignored=blank_lines_ignored,
    )
