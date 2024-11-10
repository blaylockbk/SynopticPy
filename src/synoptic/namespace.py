from typing import Literal

import polars as pl
import polars.selectors as cs


@pl.api.register_dataframe_namespace("synoptic")
class SynopticFrame:
    """Custom Polars namespace for SynopticPy DataFrames."""

    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

    def with_local_timezone(self) -> pl.DataFrame | dict:
        """Convert datetime columns from UTC to local timezone.

        Returns
        -------
        DataFrame if only one unique timezone is present, else returns
        a dict of DataFrames, one item for each timezone.
        """
        df = self._df

        if len(df["timezone"].unique()) > 1:
            a = {}
            for i in df.partition_by("timezone"):
                tz = i["timezone"].unique().item()
                a[tz] = i.with_columns(cs.datetime().dt.convert_time_zone(tz))
            return a
        else:
            tz = df["timezone"].unique().item()
            return df.with_columns(cs.datetime().dt.convert_time_zone(tz))

    def pivot(self, *, sensor_index: int = 1, **kwargs) -> pl.DataFrame:
        """Pivot a long-form SynopticPy DataFrame to wide-form.

        This likely gets what you're looking for, but it is recommended
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
        """Provide ``wind_u`` and ``wind_v`` columns from wind speed and direction.

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
        """Provide DataFrame with ``network_name`` column.

        Parameters
        ----------
        which : {'short', 'long'}
            Specify if the network shortname or longname is joined.
        """
        from synoptic.services import Networks

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
