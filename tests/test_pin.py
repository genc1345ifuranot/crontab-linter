import pytest
from pathlib import Path
from crontab_linter.pin import pin, unpin, list_pins, get_pin, PinEntry


@pytest.fixture
def pfile(tmp_path):
    return tmp_path / "pins.json"


def test_pin_new(pfile):
    e = pin("* * * * *", label="every minute", path=pfile)
    assert e.expression == "* * * * *"
    assert e.label == "every minute"


def test_pin_persists(pfile):
    pin("0 * * * *", path=pfile)
    entries = list_pins(path=pfile)
    assert len(entries) == 1
    assert entries[0].expression == "0 * * * *"


def test_pin_multiple(pfile):
    pin("* * * * *", path=pfile)
    pin("0 0 * * *", path=pfile)
    assert len(list_pins(path=pfile)) == 2


def test_pin_deduplicates(pfile):
    pin("* * * * *", label="a", path=pfile)
    pin("* * * * *", label="b", path=pfile)
    entries = list_pins(path=pfile)
    assert len(entries) == 1
    assert entries[0].label == "b"


def test_pin_merges_tags(pfile):
    pin("* * * * *", tags=["t1"], path=pfile)
    pin("* * * * *", tags=["t2"], path=pfile)
    e = get_pin("* * * * *", path=pfile)
    assert "t1" in e.tags
    assert "t2" in e.tags


def test_unpin_existing(pfile):
    pin("* * * * *", path=pfile)
    result = unpin("* * * * *", path=pfile)
    assert result is True
    assert list_pins(path=pfile) == []


def test_unpin_missing(pfile):
    result = unpin("* * * * *", path=pfile)
    assert result is False


def test_get_existing(pfile):
    pin("0 12 * * *", label="noon", path=pfile)
    e = get_pin("0 12 * * *", path=pfile)
    assert e is not None
    assert e.label == "noon"


def test_get_missing(pfile):
    assert get_pin("0 12 * * *", path=pfile) is None


def test_list_empty(pfile):
    assert list_pins(path=pfile) == []


def test_roundtrip_dict():
    e = PinEntry(expression="5 4 * * *", label="test", tags=["x"])
    assert PinEntry.from_dict(e.to_dict()).expression == e.expression
    assert PinEntry.from_dict(e.to_dict()).tags == ["x"]
