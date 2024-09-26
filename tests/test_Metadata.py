"""Tests for Metadata Class."""

from datetime import datetime

from synoptic.services import Metadata


def test_all_stations():
    s = Metadata()
    assert len(s.df)


def test_all_stations_complete():
    s = Metadata(complete=1)
    assert len(s.df)


def test_all_stations_obrange():
    s = Metadata(
        state="UT",
        obrange=(
            datetime(2000, 1, 1),
            datetime(2001, 1, 1),
        ),
    )
    assert len(s.df)


def test_radius():
    s = Metadata(radius="ukbkb,10")
    assert len(s.df)


def test_one_station():
    s = Metadata(stid="ukbkb")
    assert len(s.df) == 1


def test_complete():
    s = Metadata(radius="ukbkb,10", complete=1)
    assert len(s.df)


def test_sensorvars():
    s = Metadata(radius="ukbkb,10", sensorvars=1)
    assert len(s.df)


def test_column_names():
    df = Metadata(radius="wbb,10").df

    # I rename column `STATUS` to `is_active` and cast as bool
    assert "is_active" in df.columns
    assert "status" not in df.columns

    # I rename `RESTRICTED` to `is_restricted`
    assert "is_restricted" in df.columns
    assert "restricted" not in df.columns


def test_single_station_with_null_in_staus_column():
    s = Metadata(stid="KU10")
    assert len(s.df) == 1
