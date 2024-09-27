"""Tests for the NearestTime Class."""

from datetime import datetime

import synoptic.services as ss


def test_qced_air_temp():
    """Get quality controlled temperature at a time there is a flagged observation."""
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
