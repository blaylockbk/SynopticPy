"""Tests for some needed utilities."""

from synoptic.services import string_to_timedelta
from datetime import timedelta
import pytest


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
