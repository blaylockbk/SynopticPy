"""Tests for the NearestTime Class."""

from datetime import datetime, timedelta, UTC

from synoptic import NearestTime


def test_qced_air_temp():
    """Get quality controlled temperature at a time there is a flagged observation."""
    # This produces a QCed air temperature
    s = NearestTime(
        stid="kslc",
        attime="2024-08-17 17:55:00",
        vars="air_temp",
        within=5,
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )
    assert len(s.df())
    assert any(s.df()["qc_flags"].is_not_null())
    assert (
        s.QC_SUMMARY["TOTAL_OBSERVATIONS_FLAGGED"] == (~s.df()["qc_passed"]).sum() == 1
    )


def test_radius_kmry():
    """Get all station data for 10 mile radius around KMRY."""
    s = NearestTime(
        radius="KMRY,10",
        attime=datetime(2024, 1, 1),
        within=10,
    )

    assert (
        len(s.STATION)
        == s.df()["stid"].n_unique()
        == s.SUMMARY["NUMBER_OF_OBJECTS"]
        == 30
    )


def test_kmry_wind_qc():
    """Get wind data for stations within 10 miles of KMRY and check QC flags."""
    s = NearestTime(
        radius="KMRY,10",
        attime=datetime(2024, 1, 1),
        within=timedelta(minutes=60),
        vars="wind_speed",
        qc=True,
        qc_checks="all",
    )

    assert (
        len(s.STATION)
        == s.df()["stid"].n_unique()
        == s.SUMMARY["NUMBER_OF_OBJECTS"]
        == 28
    )

    assert (
        s.QC_SUMMARY["TOTAL_OBSERVATIONS_FLAGGED"] == (~s.df()["qc_passed"]).sum() == 3
    )


def test_showemptystations():
    """Test bounding box with showemptystations."""
    df = NearestTime(
        attime="2024-11-09",
        within=120,
        bbox=[-120, 40, -119, 41],
        showemptystations=True,
    ).df()
    assert len(df)


def test_utah_ozone():
    """Test Utah ozone air quality."""
    df = NearestTime(
        attime=datetime(2024, 7, 23, 18),
        within="30m",
        network=9,  # Utah's Division of Air Quality
        vars="ozone_concentration",
    ).df()
    assert len(df)


def test_utah_pm25():
    """Test Utah PM 2.5 air quality."""
    df = NearestTime(
        attime=datetime(2023, 12, 19, 21),
        within="30m",
        network=9,  # Utah's Division of Air Quality
        vars="PM_25_concentration",
    ).df()
    assert len(df)
