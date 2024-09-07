"""Tests for the TimeSeries Class."""

import synoptic.services as ss
from datetime import datetime


def test_string_date_input():
    s = ss.TimeSeries(
        stid="UKBKB",
        start=datetime(2024, 1, 1),
        end="2024-1-1 06:00",
    )
    assert len(s.df)
    assert s.params["start"] == "202401010000"
    assert s.params["end"] == "202401010600"


def test_all_qc_on():
    s = ss.TimeSeries(
        stid="kslc",
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )
    assert len(s.df)
    assert s.params["recent"] == str(6 * 60)


def test_radius_with_complete_metadata():
    s = ss.TimeSeries(
        radius=["kslc", 5],
        recent="6h",
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
        complete=1,
    )
    assert len(s.df)
    assert s.params["radius"] == "kslc,5"
