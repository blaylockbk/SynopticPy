"""Polars custom accessors."""

from synoptic.services import Networks


import polars as pl


from typing import Literal


def with_network_name(df: pl.DataFrame, which: Literal["short", "long"] = "short"):
    """Provide DataFrame with a new column `network_name`.

    Parameters
    ----------
    which : {'short', 'long'}
        Specify if the network shortname or longname is joined.
    """
    if "mnet_id" not in df.columns:
        raise ValueError("Column 'mnet_id' is not in the DataFrame.")

    return df.join(
        Networks(id=df["mnet_id"].unique().to_list(), verbose=False)
        .df.select("mnet_id", f"{which}name")
        .rename({f"{which}name": "network_name"}),
        on="mnet_id",
    )


# TODO: with_network_name
# TODO: with_network_longname
# TODO: with_network_type_name
