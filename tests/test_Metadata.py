"""Tests for Metadata Class."""

import synoptic


def test_all_stations():
    s = synoptic.Metadata()
    assert len(s.df)


def test_all_stations_comlete():
    s = synoptic.Metadata(complete=1)
    assert len(s.df)


def test_radius():
    s = synoptic.Metadata(radius="ukbkb,10")
    assert len(s.df)


def test_one_station():
    s = synoptic.Metadata(stid="ukbkb")
    assert len(s.df) == 1


def test_complete():
    s = synoptic.Metadata(radius="ukbkb,10", complete=1)
    assert len(s.df)


def test_sensorvars():
    s = synoptic.Metadata(radius="ukbkb,10", sensorvars=1)
    assert len(s.df)


def test_column_names():
    df = synoptic.Metadata(radius="wbb,10").df

    # I rename column `STATUS` to `is_active` and cast as bool
    assert "is_active" in df.columns
    assert "status" not in df.columns

    # I rename `RESTRICTED` to `is_restricted`
    assert "is_restricted" in df.columns
    assert "restricted" not in df.columns


def test_single_station_with_null_in_staus_column():
    s = synoptic.Metadata(stid="KU10")
    assert len(s.df) == 1
