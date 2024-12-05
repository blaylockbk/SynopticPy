"""Test DataFrame accessors."""

from synoptic.services import Latest, TimeSeries


def test_with_network_name():
    """Join the "network_name" column to a Synoptic DataFrame."""
    df = Latest(radius="ukbkb,10").df()
    df = df.synoptic.with_network_name()
    assert "network_name" in df.columns
    assert len(df)


def test_with_local_timezone():
    df = TimeSeries(stid="wbb", recent=30).df()
    df = df.synoptic.with_local_timezone()


def test_write_met():
    """Writing output for MET's ASCII2NC tool."""
    df = TimeSeries(stid="ubkbk,wbb", recent=60).df()
    df.synoptic.write_met("sample_ascii_for_met.txt")
