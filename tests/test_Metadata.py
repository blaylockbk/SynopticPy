"""Tests for Metadata Class."""

import synoptic.services as ss


def test_radius():
    s = ss.Metadata(radius="ukbkb,10")
    assert len(s.df)


def test_one_station():
    s = ss.Metadata(stid="ukbkb")
    assert len(s.df) == 1


def test_complete():
    s = ss.Metadata(radius="ukbkb,10", complete=1)
    assert len(s.df)


def test_sensorvars():
    s = ss.Metadata(radius="ukbkb,10", sensorvars=1)
    assert len(s.df)
