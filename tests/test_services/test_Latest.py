"""Tests for the Latest Class."""

from synoptic.services import Latest
from datetime import timedelta


def test_within_as_int():
    """Get latest temperature and wind within 30 minutes (parameter as int)."""
    s = Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=30,
    )
    assert len(s.df())


def test_param_as_bool():
    """Get latest temperature and wind within 30 minutes (parameter as int)."""
    s = Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        showemptyvars=True,
    )
    assert len(s.df())


def test_within_as_timedelta():
    """Get latest temperature and wind within 2 hours (parameter as timedelta)."""
    s = Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within=timedelta(hours=2),
    )
    assert len(s.df())


def test_within_as_duration_string():
    """Get latest temperature and wind within 30 minutes (parameter as string)."""
    s = Latest(
        stid="kslc",
        vars="air_temp,wind_speed",
        within="30m",
    )
    assert len(s.df())


def test_stid_with_string_ob_values():
    """Get Latest value for all variables."""
    df = Latest(stid="kslc").df()
    assert "value" in df.columns
    assert "value_string" in df.columns
