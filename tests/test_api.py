import synoptic.services as ss


def test_SynopticAPI():
    s = ss.SynopticAPI(
        "timeseries",
        start="2024-06-01",
        end="2024-06-01 01:00",
        radius="kslc,30",
    )
