import synoptic.synoptic_polars as sp
from datetime import datetime, timedelta
import polars as pl


def test_SynopticAPI():
    s = sp.SynopticAPI(
        "timeseries",
        start="2024-06-01",
        end="2024-06-01 01:00",
        radius="kslc,30",
    )


def test_TimeSeries():
    s = sp.TimeSeries(
        stid="UKBKB",
        start=datetime(2024, 1, 1),
        end="2024-1-1 06:00",
    )
    assert len(s.df)


def test_TimeSeries2():
    s = sp.TimeSeries(
        stid="kslc",
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )
    assert len(s.df)


def test_TimeSeries3():
    s = sp.TimeSeries(
        radius="kslc,5",
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
        complete=1,
    )
    assert len(s.df)


def test_Latest():
    s = sp.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within="30",
    )
    assert len(s.df)

    s = sp.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within="30m",
    )
    assert len(s.df)


def test_NearestTime():
    # This should produce a QCed air temperature
    s = sp.NearestTime(
        stid="kslc",
        attime="2024-08-17 17:55:00",
        within=5,
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )
    assert len(s.df)


def test_Precipitation():
    s = sp.Precipitation(
        stid="WBB",
        start="2024-06-01",
        end="2024-06-06",
    )
    assert len(s.df)


def test_Precipitation2():
    s = sp.Precipitation(
        stid="WBB",
        recent=timedelta(days=20),
    )
    assert len(s.df)


def test_Precipitation3():
    s = sp.Precipitation(
        stid="WBB,UKBKB",
        start="2024-06-01",
        end="2024-06-06",
        pmode="last",
        accum_hours=["12,24,100"],
    )
    assert len(s.df)


def test_Metadata():
    s = sp.Metadata(radius="ukbkb,10")
    assert len(s.df)


def test_QCTypes():
    s = sp.QCTypes()
    assert len(s.df)


def test_Variables():
    s = sp.Variables()
    assert len(s.df)


def test_Networks():
    s = sp.Networks()
    assert len(s.df)


def test_NetworkTypes():
    s = sp.NetworkTypes()
    assert len(s.df)


def test_Metadata_complete():
    s = sp.Metadata(radius="ukbkb,10", complete=1)
    assert len(s.df)


def test_Latency():
    s = sp.Latency(
        radius="UKBKB,10",
        vars="air_temp",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 2),
        stats="all",
    )
    assert len(s.df)
