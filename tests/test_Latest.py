"""Tests for the Latest Class."""

from synoptic.services import Latest
from datetime import timedelta


def test_within_as_int():
    s = Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=30,
    )
    assert len(s.df)


def test_within_as_timedelta():
    s = Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=timedelta(hours=2),
    )
    assert len(s.df)


def test_within_as_duration_string():
    s = Latest(
        stid="kslc",
        vars="air_temp,wind_speed",
        within="30m",
    )
    assert len(s.df)


def test_stid_with_string_ob_values():
    df = Latest(stid="kslc").df
    assert "value" in df.columns
    assert "value_string" in df.columns
