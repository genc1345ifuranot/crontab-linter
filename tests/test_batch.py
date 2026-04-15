"""Tests for batch validation module and formatter."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from crontab_linter.batch import validate_batch, validate_batch_file, BatchResult
from crontab_linter.batch_formatter import format_batch


VALID_LINES = [
    "*/5 * * * *  # every 5 minutes\n",
    "0 9 * * 1-5  # weekday mornings\n",
]

INVALID_LINES = [
    "99 * * * *   # bad minute\n",
]

MIXED_LINES = VALID_LINES + INVALID_LINES


def test_batch_all_valid():
    result = validate_batch(VALID_LINES)
    assert result.total == 2
    assert result.valid_count == 2
    assert result.invalid_count == 0


def test_batch_invalid_entry():
    result = validate_batch(INVALID_LINES)
    assert result.total == 1
    assert result.invalid_count == 1
    entry = result.entries[0]
    assert not entry.is_valid()


def test_batch_mixed():
    result = validate_batch(MIXED_LINES)
    assert result.total == 3
    assert result.valid_count == 2
    assert result.invalid_count == 1


def test_batch_skips_blank_and_comment_lines():
    lines = ["\n", "# full comment line\n"] + VALID_LINES
    result = validate_batch(lines)
    assert result.total == 2


def test_batch_entry_has_comment():
    result = validate_batch(["0 0 * * *  # midnight\n"])
    assert result.entries[0].comment == "midnight"


def test_batch_entry_no_comment():
    result = validate_batch(["0 0 * * *\n"])
    assert result.entries[0].comment is None


def test_batch_entry_has_explanation():
    result = validate_batch(["0 0 * * *\n"])
    entry = result.entries[0]
    assert entry.explanation is not None
    assert len(entry.explanation) > 0


def test_batch_parse_error_captured():
    result = validate_batch(["not_a_cron_at_all\n"])
    assert result.total == 1
    entry = result.entries[0]
    assert entry.parse_error is not None
    assert not entry.is_valid()


def test_batch_preset_resolved():
    result = validate_batch(["@daily\n"])
    assert result.total == 1
    assert result.entries[0].is_valid()


def test_format_batch_plain_contains_summary():
    result = validate_batch(VALID_LINES)
    output = format_batch(result, fmt="plain")
    assert "Summary" in output
    assert "2 expression(s)" in output


def test_format_batch_plain_shows_ok():
    result = validate_batch(["* * * * *\n"])
    output = format_batch(result, fmt="plain")
    assert "[OK]" in output


def test_format_batch_plain_shows_invalid():
    result = validate_batch(INVALID_LINES)
    output = format_batch(result, fmt="plain")
    assert "[INVALID]" in output


def test_format_batch_json_structure():
    result = validate_batch(VALID_LINES)
    raw = format_batch(result, fmt="json")
    data = json.loads(raw)
    assert "summary" in data
    assert data["summary"]["total"] == 2
    assert "entries" in data
    assert len(data["entries"]) == 2


def test_format_batch_json_entry_has_explanation():
    result = validate_batch(["0 12 * * *\n"])
    data = json.loads(format_batch(result, fmt="json"))
    assert data["entries"][0]["explanation"]


def test_validate_batch_file(tmp_path: Path):
    cron_file = tmp_path / "crontab.txt"
    cron_file.write_text(textwrap.dedent("""\
        # my crontab
        0 6 * * *   # morning
        */10 * * * *
    """))
    result = validate_batch_file(str(cron_file))
    assert result.total == 2
    assert result.valid_count == 2
