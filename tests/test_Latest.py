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


def test_all_stats():
    s = ss.Latency(
        radius="UKBKB,10",
        vars="air_temp",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 2),
        stats="all",
    )
    assert len(s.df)
