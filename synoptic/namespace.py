from synoptic.services import Networks


import polars as pl


from typing import Literal


@pl.api.register_dataframe_namespace("synoptic")
class SynopticFrame:
    """Custom polars namespace for SynopticPy DataFrames."""

    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

    def pivot(self, *, sensor_index=1, **kwargs) -> pl.DataFrame:
        """Pivot a long-form Synoptic DataFrame to wide-form.

        This likely gets what you're looking for, but is is recommended
        to use Polars directly to accomplish more customized pivots.

        - Long-form DataFrame has a row for each observation.
        - Wide-form DataFrame has a station  variables are in their own column for each station.

        Parameters
        ----------
        sensor_index : int
            Sensor index to filter prior to the pivot.
        **kwargs :
            Keyword arguments for Polars `pivot`.
        """
        df = self._df

        kwargs.setdefault("on", "variable")
        kwargs.setdefault(
            "index", ["date_time", "stid", "latitude", "longitude", "elevation"]
        )
        kwargs.setdefault("values", "value")
        kwargs.setdefault("aggregate_function", "mean")

        df = df.filter(sensor_index=sensor_index).pivot(**kwargs)

        return df

    def with_wind_uv(self) -> pl.DataFrame:
        """Create new columns 'wind_u' and 'wind_v'.

        **IMPORTANT** Requires a wide-form DataFrame (pivoted) with
        columns `wind_speed` and `wind_direction`.
        """
        df = self._df

        if ("wind_speed" not in df.columns) | ("wind_direction" not in df.columns):
            raise ValueError(
                "Must pivot the DataFrame with columns 'wind_speed' and 'wind_direction'."
            )

        df = df.with_columns(
            wind_u=-pl.col("wind_speed") * pl.col("wind_direction").radians().sin(),
            wind_v=-pl.col("wind_speed") * pl.col("wind_direction").radians().cos(),
        )

        return df

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
