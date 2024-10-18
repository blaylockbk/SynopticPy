from synoptic.services import Networks


import polars as pl


from typing import Literal


@pl.api.register_dataframe_namespace("synoptic")
class SynopticFrame:
    """Custom polars namespace for SynopticPy DataFrames."""

    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

    def with_network_name(
        self, which: Literal["short", "long"] = "short"
    ) -> pl.DataFrame:
        """Provide DataFrame with a new column `network_name`.

        Parameters
        ----------
        which : {'short', 'long'}
            Specify if the network shortname or longname is joined.
        """
        df = self._df

        if "mnet_id" not in df.columns:
            raise ValueError("Column 'mnet_id' is not in the DataFrame.")

        return df.join(
            Networks(id=df["mnet_id"].unique().to_list(), verbose=False)
            .df()
            .select("mnet_id", f"{which}name")
            .rename({f"{which}name": "network_name"}),
            on="mnet_id",
        )
