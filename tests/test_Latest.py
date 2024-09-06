"""Tests for the Latest Class."""

import synoptic.synoptic_polars as sp
from datetime import datetime, timedelta


def test_within_as_int():
    s = sp.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=30,
    )
    assert len(s.df)

def test_within_as_timedelta():
    s = sp.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=timedelta(hours=2),
    )
    assert len(s.df)


def test_within_as_duration_string():
    s = sp.Latest(
        stid="kslc",
        vars="air_temp,wind_speed",
        within="30m",
    )
    assert len(s.df)
