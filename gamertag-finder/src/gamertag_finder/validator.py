"""Offline checks for documented modern Xbox gamertag formatting rules.

The rules and their known rollout limits are documented in README.md. This
module checks formatting only; it cannot confirm availability or account
eligibility for Xbox features that are still in preview.
"""

from dataclasses import dataclass
from enum import Enum
import unicodedata
from typing import Iterable


class ValidationStatus(str, Enum):
    """A formatting-only result for an imported gamertag."""

    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class ValidationResult:
    """Validation status and any reason or qualification for one name."""

    gamertag: str
    status: ValidationStatus
    reason: str | None = None
    note: str | None = None


# Xbox's published modern-gamertag character table lists these creatable
# characters/ranges. Reserved punctuation is deliberately not included.
_SUPPORTED_RANGES = (
    (0x0020, 0x0020),  # Space
    (0x0027, 0x0027),  # Apostrophe
    (0x0030, 0x0039),  # ASCII digits
    (0x0041, 0x005A),  # ASCII uppercase letters
    (0x0061, 0x007A),  # ASCII lowercase letters
    (0x00C0, 0x00F6),  # Latin-1 Supplement
    (0x00F8, 0x00FF),  # Latin-1 Supplement
    (0x0100, 0x017F),  # Latin Extended-A
    (0x0400, 0x045F),  # Cyrillic
    (0x05D0, 0x05EA),  # Hebrew
    (0x0620, 0x064A),  # Arabic
    (0x0660, 0x0669),  # Arabic-Indic digits
    (0x0671, 0x06D3),  # Urdu Arabic characters
    (0x06F0, 0x06F9),  # Urdu digits
    (0x0900, 0x094F),  # Devanagari
    (0x0966, 0x096F),  # Devanagari digits
    (0x0985, 0x09B9),  # Bengali
    (0x0E01, 0x0E3A),  # Thai
    (0x0E40, 0x0E4E),  # Thai
    (0x0390, 0x03CE),  # Greek
    (0x1100, 0x1112),  # Hangul Jamo consonants
    (0x1161, 0x1175),  # Hangul Jamo vowels
    (0x11A8, 0x11C2),  # Hangul Jamo consonant clusters
    (0x3041, 0x3096),  # Hiragana
    (0x30A1, 0x30FA),  # Katakana
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0xAC00, 0xD7A3),  # Hangul syllables
)

_MAX_STANDARD_RENDERED_LENGTH = 12
_MAX_PREVIEW_RENDERED_LENGTH = 15
_MARK_CATEGORIES = {"Mn", "Mc", "Me"}


def _is_supported_character(character: str) -> bool:
    codepoint = ord(character)
    return any(
        start <= codepoint <= end
        for start, end in _SUPPORTED_RANGES
    )


def _is_latin_character(character: str) -> bool:
    codepoint = ord(character)
    return (
        codepoint == 0x0020
        or codepoint == 0x0027
        or 0x0030 <= codepoint <= 0x0039
        or 0x0041 <= codepoint <= 0x005A
        or 0x0061 <= codepoint <= 0x007A
        or 0x00C0 <= codepoint <= 0x00F6
        or 0x00F8 <= codepoint <= 0x00FF
        or 0x0100 <= codepoint <= 0x017F
    )


def _rendered_character_count(gamertag: str) -> tuple[int, str | None]:
    """Count bases, treating supported combining marks as diacritics."""
    rendered_count = 0
    has_base = False
    base_has_mark = False

    for character in gamertag:
        if unicodedata.category(character) in _MARK_CATEGORIES:
            if not has_base or base_has_mark:
                return (
                    rendered_count,
                    "Invalid formatting: each diacritic must follow a "
                    "base character, with no more than one diacritic "
                    "per character.",
                )
            base_has_mark = True
            continue

        rendered_count += 1
        has_base = True
        base_has_mark = False

    return rendered_count, None


def validate_gamertag(gamertag: str) -> ValidationResult:
    """Check one name against published modern gamertag format rules."""
    if not isinstance(gamertag, str):
        return ValidationResult(
            gamertag=str(gamertag),
            status=ValidationStatus.INVALID,
            reason="Gamertag must be text.",
        )

    if gamertag == "":
        return ValidationResult(
            gamertag=gamertag,
            status=ValidationStatus.INVALID,
            reason="Gamertag is empty.",
        )

    for character in gamertag:
        if not _is_supported_character(character):
            return ValidationResult(
                gamertag=gamertag,
                status=ValidationStatus.INVALID,
                reason=(
                    f"Unsupported character U+{ord(character):04X} "
                    f"({character!r})."
                ),
            )

    rendered_count, formatting_error = _rendered_character_count(gamertag)
    if formatting_error:
        return ValidationResult(
            gamertag=gamertag,
            status=ValidationStatus.INVALID,
            reason=formatting_error,
        )

    contains_non_latin = any(
        not _is_latin_character(character)
        and unicodedata.category(character) not in _MARK_CATEGORIES
        for character in gamertag
    )
    if (
        contains_non_latin
        and rendered_count > _MAX_STANDARD_RENDERED_LENGTH
    ):
        return ValidationResult(
            gamertag=gamertag,
            status=ValidationStatus.INVALID,
            reason=(
                "Too long: the documented format supports up to 12 "
                "rendered characters for names containing non-Latin "
                "characters."
            ),
        )

    if rendered_count > _MAX_PREVIEW_RENDERED_LENGTH:
        return ValidationResult(
            gamertag=gamertag,
            status=ValidationStatus.INVALID,
            reason=(
                "Too long: the largest currently announced modern "
                "gamertag format is 15 rendered characters."
            ),
        )

    if rendered_count > _MAX_STANDARD_RENDERED_LENGTH:
        return ValidationResult(
            gamertag=gamertag,
            status=ValidationStatus.VALID,
            note=(
                "The 13–15 character allowance was announced for unique, "
                "available gamertags in an Xbox Insider preview. This "
                "offline check cannot confirm rollout or eligibility."
            ),
        )

    return ValidationResult(
        gamertag=gamertag,
        status=ValidationStatus.VALID,
    )


def validate_gamertags(
    gamertags: Iterable[str],
) -> tuple[ValidationResult, ...]:
    """Validate names in order without changing their spelling."""
    return tuple(validate_gamertag(name) for name in gamertags)
