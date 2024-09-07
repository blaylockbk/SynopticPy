"""Tests for metadata table classes."""

import synoptic.services as ss


def test_QCTypes():
    s = ss.QCTypes()
    assert len(s.df)

    s = ss.QCTypes(id=1)
    assert len(s.df)


def test_Variables():
    s = ss.Variables()
    assert len(s.df)


def test_Networks():
    s = ss.Networks()
    assert len(s.df)

    s = ss.Networks(id=1)
    assert len(s.df) == 1

    s = ss.Networks(id=[1, 2, 3])
    assert len(s.df) == 3

    s = ss.Networks(shortname="uunet,raws")
    assert len(s.df) == 2


def test_NetworkTypes():
    s = ss.NetworkTypes()
    assert len(s.df)
