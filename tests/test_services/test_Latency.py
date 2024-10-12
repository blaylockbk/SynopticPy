from datetime import datetime
from synoptic.services import Latency


def test_all_stats():
    """Get all statistics in a Latency request."""
    s = Latency(
        radius="UKBKB,10",
        vars="air_temp",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 2),
        stats="all",
    )
    assert len(s.df())
