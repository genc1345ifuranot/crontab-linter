"""Tests for crontab_linter.compress and compress_formatter."""
import pytest
from crontab_linter.compress import compress, CompressResult, FieldCompression
from crontab_linter.compress_formatter import (
    format_compress_plain,
    format_compress_json,
    format_compress,
)
import json


def test_no_compression_needed():
    result = compress("*/5 * * * *")
    assert result.ok
    assert not result.has_changes
    assert result.compressed == "*/5 * * * *"


def test_step_one_minute_compressed():
    result = compress("*/1 * * * *")
    assert result.ok
    assert result.has_changes
    assert result.compressed == "* * * * *"
    assert any(c.name == "minute" for c in result.changes)


def test_full_range_minute_compressed():
    result = compress("0-59 * * * *")
    assert result.ok
    assert result.compressed.startswith("*")
    assert result.changes[0].name == "minute"
    assert "0-59" in result.changes[0].reason


def test_full_range_hour_compressed():
    result = compress("0 0-23 * * *")
    assert result.ok
    change_names = [c.name for c in result.changes]
    assert "hour" in change_names
    assert result.compressed == "0 * * * *"


def test_full_range_month_compressed():
    result = compress("0 0 1 1-12 *")
    assert result.ok
    change_names = [c.name for c in result.changes]
    assert "month" in change_names


def test_full_step_range_compressed():
    result = compress("0-59/1 * * * *")
    assert result.ok
    assert result.compressed.startswith("*")


def test_multiple_compressions():
    result = compress("*/1 0-23 * * *")
    assert result.ok
    assert len(result.changes) == 2
    assert result.compressed == "* * * * *"


def test_already_wildcard_not_reported():
    result = compress("* * * * *")
    assert result.ok
    assert not result.has_changes
    assert result.compressed == "* * * * *"


def test_invalid_expression_returns_error():
    result = compress("99 * * * *")
    assert not result.ok
    assert result.error is not None
    assert result.compressed == "99 * * * *"


def test_to_dict_keys():
    result = compress("*/1 * * * *")
    d = result.to_dict()
    assert "original" in d
    assert "compressed" in d
    assert "ok" in d
    assert "has_changes" in d
    assert "changes" in d
    assert "error" in d


def test_field_compression_to_dict():
    fc = FieldCompression(name="minute", original="*/1", compressed="*", reason="step 1")
    d = fc.to_dict()
    assert d["name"] == "minute"
    assert d["original"] == "*/1"
    assert d["compressed"] == "*"
    assert d["reason"] == "step 1"


def test_format_plain_no_changes():
    result = compress("*/5 * * * *")
    out = format_compress_plain(result)
    assert "already minimal" in out
    assert "*/5 * * * *" in out


def test_format_plain_with_changes():
    result = compress("*/1 * * * *")
    out = format_compress_plain(result)
    assert "Changes:" in out
    assert "minute" in out
    assert "->" in out


def test_format_plain_error():
    result = compress("99 * * * *")
    out = format_compress_plain(result)
    assert "Error:" in out


def test_format_json_valid():
    result = compress("*/1 * * * *")
    out = format_compress_json(result)
    data = json.loads(out)
    assert data["ok"] is True
    assert data["has_changes"] is True


def test_format_dispatch_plain():
    result = compress("*/5 * * * *")
    assert format_compress(result, "plain") == format_compress_plain(result)


def test_format_dispatch_json():
    result = compress("*/5 * * * *")
    assert format_compress(result, "json") == format_compress_json(result)
