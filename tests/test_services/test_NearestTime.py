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
    assert s.QC_SUMMARY["TOTAL_OBSERVATIONS_FLAGGED"] == (~s.df()["qc_passed"]).sum() == 1


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
        qc_check="all",
    )

    assert (
        len(s.STATION)
        == s.df()["stid"].n_unique()
        == s.SUMMARY["NUMBER_OF_OBJECTS"]
        == 28
    )

    assert s.QC_SUMMARY["TOTAL_OBSERVATIONS_FLAGGED"] == (~s.df()["qc_passed"]).sum() == 3

    for i in s.STATION:
        if i["STID"] == "E1554":
            assert i["OBSERVATIONS"] == {
                "wind_speed_value_1": {
                    "value": 0.0,
                    "date_time": "2024-01-01T00:00:00Z",
                    "qc": {"status": "failed", "qc_flags": [3]},
                }
            }
            E1554 = s.df().filter(stid="E1554")
            assert E1554["date_time"][0] == datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
            assert E1554["variable"][0] == "wind_speed"
            assert E1554["value"][0] == 0
            assert E1554["qc_flags"].to_list() == [[3]]
            assert not E1554["qc_passed"][0]

def test_showemptystations():
    """Test bounding box with showemptystations."""
    df = NearestTime(
        attime="2024-11-09",
        within=120,
        bbox=[-120, 40, -119, 41],
        showemptystations=True,
    ).df()
    assert len(df)
