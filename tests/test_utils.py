"""Tests for some needed utilities."""

import synoptic
import synoptic.accessors
from synoptic.json_parsers import parse_obrange
from synoptic.services import string_to_timedelta, Latest
from datetime import datetime, timedelta
import pytest


@pytest.mark.parametrize(
    "obrange,expected",
    [
        ("2024010501", "2024010501"),
        ("20240105,20240106", "20240105,20240106"),
        (["2024010501", "2024020506"], "2024010501,2024020506"),
        (("2024010501", "2024020506"), "2024010501,2024020506"),
        (datetime(2024, 1, 5, 6, 1), "202401050601"),
        (
            (datetime(2024, 1, 5, 6, 1), datetime(2024, 4, 5)),
            "202401050601,202404050000",
        ),
    ],
)
def test_parse_obrange(obrange, expected):
    assert parse_obrange(obrange) == expected


@pytest.mark.parametrize("obrange", [200, 3.14, "2014", "201401,201405"])
def test_parse_obrange_ERROR(obrange):
    """Test that parse_obrange produces an error for bad input."""
    try:
        _ = parse_obrange(obrange)
    except:
        assert 1 == 1
        return
    assert 1 == 0


@pytest.mark.parametrize(
    "duration,expected",
    [
        ("PT3H", timedelta(hours=3)),
        ("PT30M", timedelta(minutes=30)),
        ("P1DT6H10M", timedelta(days=1, hours=6, minutes=10)),
        ("PT3H20M", timedelta(hours=3, minutes=20)),
        ("P1DT3H20M", timedelta(days=1, hours=3, minutes=20)),
        ("P1DT3H20M", timedelta(days=1, hours=3, minutes=20)),
        ("30m", timedelta(minutes=30)),
        ("3d6h30m10s", timedelta(days=3, hours=6, minutes=30, seconds=10)),
    ],
)
def test_string_to_timedelta(duration, expected):
    assert string_to_timedelta(duration) == expected


def test_with_network_name():
    df = Latest(radius="ukbkb,10").df.pipe(
        synoptic.accessors.with_network_name
    )
    assert "network_name" in df.columns
    assert len(df)
