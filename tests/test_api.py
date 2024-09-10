import synoptic.services as ss
from datetime import datetime, timedelta
import polars as pl


def test_SynopticAPI():
    s = ss.SynopticAPI(
        "timeseries",
        start="2024-06-01",
        end="2024-06-01 01:00",
        radius="kslc,30",
    )
