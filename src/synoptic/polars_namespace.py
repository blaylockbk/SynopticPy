import warnings
from pathlib import Path
from typing import Literal

import polars as pl
import polars.selectors as cs


@pl.api.register_dataframe_namespace("synoptic")
class SynopticFrame:
    """Custom Polars namespace for SynopticPy DataFrames."""

    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df

    def write_met(self, file: Path | str) -> None:
        """Write to 11-column ASCII file for Model Evaluation Tools (MET) ASCII2NC tool.

        WARNING: I haven't actually tested that the file it writes can
        be used by MET's ASCII2NC tool. This is primarily a proof of
        concept. Please open a PR if you want to see this feature
        improved and tested.

        > The default ASCII point observation format consists of one row of data
        > per observation value. Each row of data consists of 11 columns as shown
        > in [Table 7.4](https://met.readthedocs.io/en/latest/Users_Guide/reformat_point.html#table-reformat-point-ascii2nc-format).

        Description
        https://met.readthedocs.io/en/latest/Users_Guide/reformat_point.html#ascii2nc-tool

        Sample Data
        https://github.com/dtcenter/MET/blob/main_v11.1/data/sample_obs/ascii/sample_ascii_obs_varname.txt
        """
        if isinstance(file, str):
            file = Path(file)

        warnings.warn(
            "`write_met` is experimental and proof of concept. NEEDS TESTING WIT MET's ASCII2NC tool."
        )

        # Get 11 columns of data required.
        met = self._df.filter(~pl.col("value").is_null()).select(
            pl.lit("MESONET").alias("Message_Type"),
            pl.col("stid").alias("Station_ID"),
            pl.col("date_time").dt.strftime("%Y%m%d_%H%M%S").alias("Valid_Time"),
            pl.col("latitude").alias("Lat"),
            pl.col("longitude").alias("Lon"),
            pl.col("elevation").alias("Elevation") * 0.3048,  # feet to meters
            pl.col("variable").alias("Variable_Name"),
            pl.lit(None).alias("Level"),
            pl.lit(None).alias("Height"),
            pl.when(pl.col("qc_flagged"))
            .then(pl.lit("flagged"))
            .otherwise(pl.lit("passed"))
            .alias("QC_String"),
            pl.col("value").alias("Observation_Value"),
        )

        # Replace Synoptic's variable name with GRIB short name
        # TODO: List is incomplete
        met = met.with_columns(
            pl.col("Variable_Name").replace(
                {
                    "air_temp": "TMP",
                    "relative_humidity": "RH",
                    "dew_point_temperature": "DPT",
                    "wind_speed": "WIND",
                    "wind_direction": "WDIR",
                    "sea_level_pressure": "PRMSL",
                    "pressure": "PRES",
                }
            )
        )

        # Write ASCII file
        # TODO: The file written is space-delimitated, not fixed with.
        # TODO: Is that OK for MET? If not, need to use formatted np.savetxt.
        met.with_columns(pl.all().cast(str)).fill_null("NA").write_csv(
            file,
            separator=" ",
            include_header=False,
        )

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

        networks = (
            Networks(id=df["mnet_id"].unique().to_list(), verbose=False)
            .df()
            .select("mnet_id", f"{which}name")
            .rename({f"{which}name": "network_name"})
        )

        return df.join(
            networks,
            on="mnet_id",
        )
