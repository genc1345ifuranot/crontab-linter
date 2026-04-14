"""Tests for crontab_linter.presets module."""
import pytest
from crontab_linter.presets import resolve_preset, is_preset, list_presets


def test_resolve_yearly():
    result = resolve_preset("@yearly")
    assert result is not None
    expr, desc = result
    assert expr == "0 0 1 1 *"
    assert "January" in desc


def test_resolve_annually_same_as_yearly():
    r1 = resolve_preset("@yearly")
    r2 = resolve_preset("@annually")
    assert r1 == r2


def test_resolve_monthly():
    result = resolve_preset("@monthly")
    assert result is not None
    assert result[0] == "0 0 1 * *"


def test_resolve_weekly():
    result = resolve_preset("@weekly")
    assert result is not None
    assert result[0] == "0 0 * * 0"


def test_resolve_daily():
    result = resolve_preset("@daily")
    assert result is not None
    assert result[0] == "0 0 * * *"


def test_resolve_midnight_same_as_daily():
    r1 = resolve_preset("@daily")
    r2 = resolve_preset("@midnight")
    assert r1 == r2


def test_resolve_hourly():
    result = resolve_preset("@hourly")
    assert result is not None
    assert result[0] == "0 * * * *"


def test_resolve_reboot():
    result = resolve_preset("@reboot")
    assert result is not None
    expr, desc = result
    assert expr == "@reboot"
    assert "startup" in desc.lower()


def test_resolve_unknown_returns_none():
    assert resolve_preset("@unknown") is None
    assert resolve_preset("* * * * *") is None
    assert resolve_preset("") is None


def test_resolve_case_insensitive():
    assert resolve_preset("@Daily") is not None
    assert resolve_preset("@HOURLY") is not None


def test_resolve_strips_whitespace():
    result = resolve_preset("  @weekly  ")
    assert result is not None


def test_is_preset_true():
    assert is_preset("@daily") is True
    assert is_preset("@hourly") is True
    assert is_preset("@reboot") is True


def test_is_preset_false():
    assert is_preset("0 * * * *") is False
    assert is_preset("@unknown") is False


def test_list_presets_returns_list():
    presets = list_presets()
    assert isinstance(presets, list)
    assert len(presets) > 0


def test_list_presets_structure():
    presets = list_presets()
    for p in presets:
        assert "alias" in p
        assert "expression" in p
        assert "description" in p


def test_list_presets_contains_reboot():
    aliases = [p["alias"] for p in list_presets()]
    assert "@reboot" in aliases
