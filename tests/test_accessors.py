"""Test DataFrame accessors."""

import synoptic.accessors
from synoptic.services import Latest


def test_with_network_name():
    """Join the "network_name" column to a Synoptic DataFrame."""
    df = Latest(radius="ukbkb,10").df.pipe(synoptic.accessors.with_network_name)
    assert "network_name" in df.columns
    assert len(df)
