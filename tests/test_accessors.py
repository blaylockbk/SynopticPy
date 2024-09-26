"""Test DataFrame accessors."""

import synoptic.accessors
from synoptic.services import Latest


def test_with_network_name():
    df = Latest(radius="ukbkb,10").df.pipe(synoptic.accessors.with_network_name)
    assert "network_name" in df.columns
    assert len(df)
