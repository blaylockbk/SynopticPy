"""Tests for the Precipitation Class."""

from datetime import datetime, timedelta

import numpy as np

from synoptic.services import Precipitation


def test_pmode_total():
    """Get total precipitation for a time period.

    Note that if `pmode` is omitted, the Precipitation class forces
    `pmode='totals'` because we don't want legacy JSON product.
    """
    df = Precipitation(
        radius="WBB,10",
        pmode="totals",
        start="2024-06-01",
        end="2024-06-06",
    ).df()

    assert len(df), "Should not have gotten an empty dataframe."
    assert df.filter(stid="WBB")["total"][0] == 0.254


def test_pmode_total_recent():
    """Get total precipitation for last 20 days."""
    df = Precipitation(
        stid="WBB",
        recent=timedelta(days=20),
    ).df()
    assert len(df)


def test_pmode_last_accum():
    """Get last 12h, 24h, and 100h precipitation totals for two stations."""
    df = Precipitation(
        stid="WBB,UKBKB",
        end="2024-09-05",
        pmode="last",
        accum_hours=["12,24,100"],
    ).df()
    assert len(df) == 6


def test_pmode_interval_daily():
    """Get daily precipitation for WBB station over a Month."""
    df = Precipitation(
        stid="wbb",
        start=datetime(2024, 8, 1),
        end=datetime(2024, 9, 1),
        pmode="intervals",
        units="english",
        interval="day",
    ).df()

    assert len(df) == 31, "There should be 31 row, one for each day of the month."
    assert np.isclose(
        df["total"].sum(), 1.15
    ), "Expected total precipitation to be 1.5 inches."


def test_showemptystations():
    """Test the case with showemptystation==True."""
    df = Precipitation(
        start="2024-10-10",
        end="2024-11-01",
        bbox=[-120, 40, -119, 41],
        showemptystations=True,
    ).df()
    assert len(df)
