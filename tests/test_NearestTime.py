"""Tests for the NearestTime Class."""

import synoptic.services as ss
from datetime import datetime


def test_qced_air_temp():
    # This produces a QCed air temperature
    s = ss.NearestTime(
        stid="kslc",
        attime="2024-08-17 17:55:00",
        vars="air_temp",
        within=5,
        qc="on",
        qc_flags="on",
        qc_checks="all",
        qc_remove_data="off",
    )
    assert len(s.df)
    assert any(s.df["qc_flags"].is_not_null())
