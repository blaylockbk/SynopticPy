"""Tests for metadata table classes."""

import synoptic.services as ss


def test_QCTypes():
    """Get DataFrame of all quality control types."""
    s = ss.QCTypes()
    assert len(s.df())

    s = ss.QCTypes(id=1)
    assert len(s.df())


def test_Variables():
    """Get DataFrame of all variables."""
    s = ss.Variables()
    assert len(s.df())


def test_NetworkTypes():
    """Get DataFrame of all network types."""
    s = ss.NetworkTypes()
    assert len(s.df())


class TestNetworks:
    """Get DataFrame of all networks."""

    def test_networks_default(self):
        s = ss.Networks()
        assert len(s.df())

    def test_networks_1(self):
        s = ss.Networks(id=1)
        assert len(s.df()) == 1

    def test_networks_123(self):
        s = ss.Networks(id=[1, 2, 3])
        assert len(s.df()) == 3

    def test_networks_shortname(self):
        s = ss.Networks(shortname="uunet,raws")
        assert len(s.df()) == 2
