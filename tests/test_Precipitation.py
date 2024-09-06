"""Tests for the Precipitation Class."""

import synoptic.synoptic_polars as sp
from datetime import datetime, timedelta


def test_defaults():
    s = sp.Precipitation(
        stid="WBB",
        start="2024-06-01",
        end="2024-06-06",
    )
    assert len(s.df)


def test_recent():
    s = sp.Precipitation(
        stid="WBB",
        recent=timedelta(days=20),
    )
    assert len(s.df)


def test_pmode_last_accum():
    s = sp.Precipitation(
        stid="WBB,UKBKB",
        start="2024-06-01",
        end="2024-06-06",
        pmode="last",
        accum_hours=["12,24,100"],
    )
    assert len(s.df)
