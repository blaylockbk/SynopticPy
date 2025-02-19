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


def test_showemptystations():
    """Test bounding box with showemptystations."""
    df = TimeSeries(
        recent=30,
        bbox=[-120, 40, -119, 41],
        showemptystations=True,
    ).df()
    assert len(df)


def test_showemptystations2():
    """Test show empty stations again."""
    df = TimeSeries(
        bbox=[-105, 37, -103, 39],
        vars="fuel_moisture",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 31),
        showemptystations=True,
    ).df()
    assert len(df)


def test_utah_ozone():
    """Test Utah ozone air quality."""
    df = TimeSeries(
        start=datetime(2024, 7, 23, 21),
        end=datetime(2024, 7, 25, 21),
        network=9,  # Utah's Division of Air Quality
        vars="ozone_concentration",
    ).df()
    assert len(df)


def test_convert_LATITUDE_with_white_space():
    """Test cast LATITUDE data to float when white space is present.

    The value " 42.870000" is present in this test case.
    """
    df = TimeSeries(
        bbox=[-90, 40, -85, 44],
        start=datetime(2024, 8, 24, 00, 00, 00),
        end=datetime(2024, 8, 24, 1, 00, 00),
    ).df()

    assert len(df)
