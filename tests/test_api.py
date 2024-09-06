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




def test_Latency():
    s = sp.Latency(
        radius="UKBKB,10",
        vars="air_temp",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 2),
        stats="all",
    )
    assert len(s.df)
