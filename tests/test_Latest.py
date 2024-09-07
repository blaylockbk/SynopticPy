"""Tests for the Latest Class."""

import synoptic.services as ss
from datetime import datetime, timedelta


def test_within_as_int():
    s = ss.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=30,
    )
    assert len(s.df)


def test_within_as_timedelta():
    s = ss.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=timedelta(hours=2),
    )
    assert len(s.df)


def test_within_as_duration_string():
    s = ss.Latest(
        stid="kslc",
        vars="air_temp,wind_speed",
        within="30m",
    )
    assert len(s.df)
