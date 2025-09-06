"""Tests for Metadata Class."""

from datetime import date, datetime

import pytest

from synoptic.services import Metadata


def test_all_stations():
    """Get metadata for all Synoptic's stations."""
    s = Metadata()
    assert len(s.df())


@pytest.mark.skipif(True, reason="This times out on my personal computer.")
def test_all_stations_complete():
    """Get complete metadata for all stations."""
    s = Metadata(complete=1)
    assert len(s.df())


@pytest.mark.skipif(True, reason="This times out on my personal computer.")
def test_all_stations_obrange():
    """Get metadata for an obrange."""
    s = Metadata(
        state="UT",
        obrange=(
            datetime(2000, 1, 1),
            datetime(2000, 1, 5),
        ),
    )
    assert len(s.df())


def test_obrange_as_date():
    """Get metadata for an obrange, using datetime.date."""
    s = Metadata(
        state="RI",
        obrange=(
            date(2024, 1, 1),
            date(2024, 1, 2),
        ),
    )
    assert len(s.df())


def test_radius():
    """Get metadata for all stations within radius."""
    s = Metadata(radius="ukbkb,10")
    assert len(s.df())


def test_one_station():
    """Get metadata for a single station."""
    s = Metadata(stid="ukbkb")
    assert len(s.df()) == 1


def test_complete():
    """Get complete metadata for many stations."""
    s = Metadata(radius="ukbkb,10", complete=1)
    assert len(s.df())


def test_sensorvars():
    """Get metadata with sensorvars."""
    s = Metadata(radius="ukbkb,10", sensorvars=1)
    assert len(s.df())


def test_column_names():
    """Get metadata and check expected column names."""
    df = Metadata(radius="wbb,10").df()

    # I rename column `STATUS` to `is_active` and cast as bool
    assert "is_active" in df.columns
    assert "status" not in df.columns

    # I rename `RESTRICTED` to `is_restricted`
    assert "is_restricted" in df.columns
    assert "restricted" not in df.columns


def test_single_station_with_null_in_status_column():
    """Get metadata for a station with null in a status column."""
    s = Metadata(stid="KU10")
    assert len(s.df()) == 1
