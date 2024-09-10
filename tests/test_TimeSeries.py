"""Tests for the TimeSeries Class."""

import synoptic
from datetime import datetime


def test_string_date_input():
    s = synoptic.TimeSeries(
        stid="UKBKB",
        start=datetime(2024, 1, 1),
        end="2024-1-1 06:00",
    )
    assert len(s.df)
    assert s.params["start"] == "202401010000"
    assert s.params["end"] == "202401010600"


def test_all_qc_on():
    s = synoptic.TimeSeries(
        stid="kslc",
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )
    assert len(s.df)
    assert s.params["recent"] == str(6 * 60)


def test_radius_with_complete_metadata():
    s = synoptic.TimeSeries(
        radius=["kslc", 5],
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
        complete=1,
    )
    assert len(s.df)
    assert s.params["radius"] == "kslc,5"


def test_column_names():
    df = synoptic.TimeSeries(stid="wbb,ukbkb", recent=30).df

    # Column `STATUS` is renamed `is_active` and cast as bool
    assert "is_active" in df.columns
    assert "status" not in df.columns

    # Column `RESTRICTED` is renames `is_restricted`
    assert "is_restricted" in df.columns
    assert "restricted" not in df.columns
