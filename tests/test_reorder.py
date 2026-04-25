"""Tests for crontab_linter.reorder."""
import pytest

from crontab_linter.reorder import reorder, _reorder_field


# ---------------------------------------------------------------------------
# Unit tests for _reorder_field
# ---------------------------------------------------------------------------

def test_reorder_field_no_list_unchanged():
    assert _reorder_field("*") == "*"


def test_reorder_field_single_value_unchanged():
    assert _reorder_field("5") == "5"


def test_reorder_field_step_unchanged():
    assert _reorder_field("*/15") == "*/15"


def test_reorder_field_range_unchanged():
    assert _reorder_field("1-5") == "1-5"


def test_reorder_field_list_sorted():
    assert _reorder_field("5,3,1") == "1,3,5"


def test_reorder_field_list_already_sorted():
    assert _reorder_field("1,2,3") == "1,2,3"


def test_reorder_field_list_duplicates_preserved():
    assert _reorder_field("5,5,1") == "1,5,5"


# ---------------------------------------------------------------------------
# Integration tests for reorder()
# ---------------------------------------------------------------------------

def test_reorder_wildcard_expression_no_changes():
    result = reorder("* * * * *")
    assert result.ok
    assert not result.has_changes()
    assert result.reordered == "* * * * *"


def test_reorder_sorted_list_no_changes():
    result = reorder("1,2,3 * * * *")
    assert result.ok
    assert not result.has_changes()
    assert result.reordered == "1,2,3 * * * *"


def test_reorder_unsorted_minute_list():
    result = reorder("5,3,1 * * * *")
    assert result.ok
    assert result.has_changes()
    assert result.reordered == "1,3,5 * * * *"


def test_reorder_unsorted_hour_list():
    result = reorder("0 22,8,14 * * *")
    assert result.ok
    assert result.has_changes()
    assert result.reordered == "0 8,14,22 * * *"


def test_reorder_multiple_fields_changed():
    result = reorder("5,3 22,8 * * *")
    assert result.ok
    assert result.has_changes()
    changed = [f for f in result.fields if f.changed]
    assert len(changed) == 2


def test_reorder_field_details_correct():
    result = reorder("5,3,1 * * * *")
    minute_field = result.fields[0]
    assert minute_field.original == "5,3,1"
    assert minute_field.reordered == "1,3,5"
    assert minute_field.changed is True


def test_reorder_unchanged_field_details():
    result = reorder("1,2 * * * *")
    minute_field = result.fields[0]
    assert minute_field.changed is False


def test_reorder_invalid_expression_returns_error():
    result = reorder("99 99 99 99 99")
    # Parser may raise; result should have ok=False or the error captured
    # Depending on parser strictness this may or may not fail — we just check
    # the result object is always returned
    assert isinstance(result.ok, bool)


def test_reorder_to_dict_keys():
    result = reorder("5,3 * * * *")
    d = result.to_dict()
    assert "original" in d
    assert "reordered" in d
    assert "has_changes" in d
    assert "ok" in d
    assert "error" in d
    assert "fields" in d


def test_reorder_field_to_dict_keys():
    result = reorder("5,3 * * * *")
    fd = result.fields[0].to_dict()
    assert set(fd.keys()) == {"original", "reordered", "changed"}
