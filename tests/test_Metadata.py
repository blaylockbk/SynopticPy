"""Tests for Metadata Class."""

import synoptic.synoptic_polars as sp

def test_radius():
    s = sp.Metadata(radius="ukbkb,10")
    assert len(s.df)


def test_one_station():
    s = sp.Metadata(stid="ukbkb")
    assert len(s.df) == 1


def test_complete():
    s = sp.Metadata(radius="ukbkb,10", complete=1)
    assert len(s.df)

def test_sensorvars():
    s = sp.Metadata(radius="ukbkb,10", sensorvars=1)
    assert len(s.df)
