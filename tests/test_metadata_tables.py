"""Tests for metadata table classes."""

import synoptic.synoptic_polars as sp


def test_QCTypes():
    s = sp.QCTypes()
    assert len(s.df)

    s = sp.QCTypes(id=1)
    assert len(s.df)


def test_Variables():
    s = sp.Variables()
    assert len(s.df)


def test_Networks():
    s = sp.Networks()
    assert len(s.df)

    s = sp.Networks(id=1)
    assert len(s.df) == 1

    s = sp.Networks(id=[1, 2, 3])
    assert len(s.df) == 3

    s = sp.Networks(shortname="uunet,raws")
    assert len(s.df) == 2


def test_NetworkTypes():
    s = sp.NetworkTypes()
    assert len(s.df)
