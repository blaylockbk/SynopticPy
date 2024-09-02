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


def test_TimeSeries2():
    s = sp.TimeSeries(
        stid="kslc",
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )


def test_Latest():
    s = sp.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within="30",
    )

    s = sp.Latest(
        stid="ukbkb,wbb,naa",
        vars="air_temp,wind_speed",
        within="30m",
    )

def test_NearestTime():
    # This should produce a QC'ed air temperature
    s = sp.NearestTime(
        stid="kslc",
        attime="2024-08-17 17:55:00",
        within=5,
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )

def test_Precipitation():
    s = sp.Precipitation(
        stid="WBB",
        start="2024-06-01",
        end="2024-06-06",
    )


def test_Precipitation2():
    s = sp.Precipitation(
        stid="WBB",
        recent=timedelta(days=20),
    )


def test_Precipitation3():
    sp.Precipitation(
        stid="WBB,UKBKB",
        start="2024-06-01",
        end="2024-06-06",
        pmode="last",
        accum_hours=["12,24,100"],
    ).df
