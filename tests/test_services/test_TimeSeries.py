"""Tests for the TimeSeries Class."""

from datetime import datetime

from synoptic.services import TimeSeries


def test_string_date_input():
    """Get time series data using mixed types of datetime input."""
    s = TimeSeries(
        stid="UKBKB",
        start=datetime(2024, 1, 1),
        end="2024-1-1 06:00",
    )
    assert len(s.df())
    assert s.params["start"] == "202401010000"
    assert s.params["end"] == "202401010600"


def test_all_qc_on():
    """Get quality controlled time series data for recent 6 hours."""
    s = TimeSeries(
        stid="kslc",
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )
    assert len(s.df())
    assert s.params["recent"] == str(6 * 60)


def test_radius_with_complete_metadata():
    """Get quality controlled time series data with complete station metadata."""
    s = TimeSeries(
        radius=["kslc", 5],
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
        complete=1,
    )
    assert len(s.df())
    assert s.params["radius"] == "kslc,5"


def test_column_names():
    """Get time series data and check for expected column names."""
    df = TimeSeries(stid="wbb,ukbkb", recent=30).df()

    # Column `STATUS` is renamed `is_active` and cast as bool
    assert "is_active" in df.columns
    assert "status" not in df.columns

    # Column `RESTRICTED` is renames `is_restricted`
    assert "is_restricted" in df.columns
    assert "restricted" not in df.columns
