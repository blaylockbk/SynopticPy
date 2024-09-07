"""Tests for the Precipitation Class."""

import synoptic.services as ss
from datetime import datetime, timedelta


def test_defaults():
    s = ss.Precipitation(
        stid="WBB",
        start="2024-06-01",
        end="2024-06-06",
    )
    assert len(s.df)


def test_recent():
    s = ss.Precipitation(
        stid="WBB",
        recent=timedelta(days=20),
    )
    assert len(s.df)


def test_pmode_last_accum():
    s = ss.Precipitation(
        stid="WBB,UKBKB",
        start="2024-06-01",
        end="2024-06-06",
        pmode="last",
        accum_hours=["12,24,100"],
    )
    assert len(s.df)
