"""Parse Synoptic's JSON into DataFrames."""

from typing import TYPE_CHECKING

import polars as pl

if TYPE_CHECKING:
    from synoptic.services import SynopticAPI


def unnest_period_of_record(
    df: pl.DataFrame | pl.LazyFrame,
) -> pl.DataFrame | pl.LazyFrame:
    """Un-nest the PERIOD_OF_RECORD column struct."""
    return df.with_columns(
        pl.struct(
            pl.col("PERIOD_OF_RECORD")
            .struct.field("start")
            .cast(pl.String)
            .str.to_datetime(time_zone="UTC")
            .alias("PERIOD_OF_RECORD_START"),
            pl.col("PERIOD_OF_RECORD")
            .struct.field("end")
            .cast(pl.String)
            .str.to_datetime(time_zone="UTC")
            .alias("PERIOD_OF_RECORD_END"),
        ).alias("PERIOD_OF_RECORD"),
    ).unnest("PERIOD_OF_RECORD")


def parse_raw_variable_column(
    df: pl.DataFrame | pl.LazyFrame,
    units_dict: dict,
) -> pl.DataFrame | pl.LazyFrame:
    """Parse the raw values in the 'variable' column.

    For example:

    | variable                 | -> | variable          | sensor_index | is_derived |
    |--------------------------|----|-------------------|--------------|------------|
    | relative_humidity_set_1d | -> | relative_humidity |       1      | True       |
    | air_temp_set_1           | -> | air_temp          |       1      | False      |
    | air_temp_set_2           | -> | air_temp          |       2      | False      |

    Parameters
    ----------
    df : DataFrame or LazyFrame
        Must have the column "variable" in it's raw form as provided
        by the Synoptic API.
    units_dict : dict
        A mapping of the variable names to unit, as provided by
        `SynopticAPI().UNITS`.
    """
    return (
        df.with_columns(
            pl.col("variable").str.extract_groups(
                r"(?<variable>.+)_(?:value|set)_(?<sensor_index>\d)(?<is_derived>d?)"
            )
        )
        .unnest("variable")
        .with_columns(
            pl.col("is_derived") == "d",
            pl.col("sensor_index").cast(pl.UInt32),
            pl.col("variable").replace(units_dict).alias("units"),
        )
    )


def station_metadata_to_dataframe(STATION: list[dict]):
    """From STATION, produce the metadata DataFrame."""
    a = []
    for metadata in STATION:
        metadata = metadata.copy()
        metadata.pop("OBSERVATIONS", None)
        metadata.pop("SENSOR_VARIABLES", None)
        metadata.pop("LATENCY", None)
        metadata.pop("QC", None)
        a.append(metadata)
    df = pl.DataFrame(a, infer_schema_length=None).lazy()
    df = df.with_columns(
        pl.col("STID").cast(pl.String),
        pl.col("ID", "MNET_ID").cast(pl.UInt32),
        pl.col("ELEVATION", "LATITUDE", "LONGITUDE").cast(pl.Float64),
        is_active=pl.when(pl.col("STATUS") == "ACTIVE")
        .then(True)
        .otherwise(pl.when(pl.col("STATUS") == "INACTIVE").then(False)),
    ).drop("UNITS", "STATUS")

    if "RESTRICTED" in df.collect_schema().names():
        df = df.rename({"RESTRICTED": "is_restricted"})

    if "ELEV_DEM" in df.collect_schema().names():
        # This isn't in the Latency request
        df = df.with_columns(pl.col("ELEV_DEM").cast(pl.Float64))

    df = df.pipe(unnest_period_of_record)
    df = df.rename({i: i.lower() for i in df.collect_schema().names()})

    return df.collect()


def parse_stations_timeseries(S: "SynopticAPI") -> pl.DataFrame:
    """Parse all STATION items for 'timeseries' service into long-format DataFrame.

    Parameters
    ----------
    s : SynopticAPI instance
    """
    # TODO: Need to do something with the list of qc data
    # TODO: Need to implement parsing cloud_layer

    observations = []
    qc = []
    latency = []
    sensor_variables = []

    for s in S.STATION:
        observations.append({"stid": s["STID"]} | s.pop("OBSERVATIONS", {}))
        qc.append({"stid": s["STID"]} | s.pop("QC", {}))
        latency.append({"stid": s["STID"]} | s.pop("LATENCY", {}))
        sensor_variables.append({"stid": s["STID"]} | s.pop("SENSOR_VARIABLES", {}))

    df = pl.DataFrame(observations, infer_schema_length=None)

    cols_with_float = []
    cols_with_string = []
    cols_with_cloud_layer = []
    cols_with_other = []

    for col, schema in df.schema.items():
        if col in {"date_time", "stid"}:
            continue
        elif schema == pl.List(pl.Float64):
            cols_with_float.append(col)
        elif schema == pl.List(pl.String):
            cols_with_string.append(col)
        elif col.startswith("cloud_layer"):
            print(f"WARNING: {col} not implemented.")
            cols_with_cloud_layer.append(col)
        else:
            cols_with_other.append(col)
            print(f"WARNING: Unknown schema for {col=} {schema=}")

    to_concat = []

    # Unpack the float observations
    if cols_with_float:
        observed_float = (
            df.select(["stid", "date_time"] + cols_with_float)
            .with_columns(
                pl.col(cols_with_float).fill_null(
                    pl.lit(None, dtype=pl.Float64).repeat_by(
                        pl.col("date_time").list.len()
                    )  # https://stackoverflow.com/q/78810432/2383070
                )
            )
            .explode(["date_time"] + cols_with_float)
            .unpivot(cols_with_float, index=["stid", "date_time"])
        )
        to_concat.append(observed_float)

    # Unpack the string observations
    #   Put values in column 'value_string'
    if cols_with_string:
        observed_string = (
            df.select(["stid", "date_time"] + cols_with_string)
            .with_columns(
                pl.col(cols_with_string).fill_null(
                    pl.lit(None, dtype=pl.String).repeat_by(
                        pl.col("date_time").list.len()
                    )  # https://stackoverflow.com/q/78810432/2383070
                )
            )
            .explode(["date_time"] + cols_with_string)
            .unpivot(cols_with_string, index=["stid", "date_time"])
            .rename({"value": "value_sting"})
        )
        to_concat.append(observed_string)

    # Unpack the cloud layer.
    #   Put sky_condition in 'value_sting' column
    #   and height_agl in 'value' column
    # TODO if cols_with_cloud_layer:
    # TODO     observed_cloud_layer = (
    # TODO         df.select(["stid", "date_time"] + cols_with_cloud_layer)
    # TODO         .with_columns(
    # TODO             pl.col(cols_with_cloud_layer).fill_null(
    # TODO                 pl.lit(None).repeat_by(
    # TODO                     pl.col("date_time").list.len()
    # TODO                 )  # https://stackoverflow.com/q/78810432/2383070
    # TODO             )
    # TODO         )
    # TODO         .explode(["date_time"] + cols_with_cloud_layer)
    # TODO         .unpivot(cols_with_cloud_layer, index=["stid", "date_time"])
    # TODO         .rename({"value": "value_sting"})
    # TODO     )
    # TODO     to_concat.append(observed_cloud_layer)

    # Join all observation values
    observed = pl.concat(to_concat, how="diagonal_relaxed")

    # Cast 'date_time' column from string to datetime
    observed = observed.with_columns(pl.col("date_time").str.to_datetime())

    # Parse the variable name
    observed = observed.pipe(parse_raw_variable_column, S.UNITS)

    # Join the metadata to the observed values
    metadata = station_metadata_to_dataframe(S.STATION)
    observed = observed.join(metadata, on="stid", how="full", coalesce=True)

    if "qc" in observed.columns:
        observed = (
            observed.unnest("qc")
            .rename({"status": "qc_passed"})
            .with_columns(
                pl.col("qc_passed").replace_strict({"failed": False, "passed": True})
            )
        )

    return observed


def OLD_parse_stations_timeseries(S: "SynopticAPI") -> pl.DataFrame:
    """Parse all STATION items for 'timeseries' service into long-format DataFrame.

    Parameters
    ----------
    s : SynopticAPI instance
    """
    dfs = []
    for station in S.STATION:
        observations = station.get("OBSERVATIONS")
        qc = station.get("QC")
        metadata = station_metadata_to_dataframe(station)

        df = pl.DataFrame(observations)

        if not len(df):
            # The values of STATION[n]["OBSERVATIONS"] is an empty dict,
            # occurs if `showemptystatoins=True`.
            dfs.append(metadata)
            continue

        observed_float = df.select(pl.col("date_time"), pl.col(pl.Float64)).unpivot(
            index="date_time"
        )
        observed_string = (
            df.select(pl.col("date_time"), pl.col(pl.String).exclude("date_time"))
            .unpivot(index="date_time")
            .rename({"value": "value_string"})
        )

        observed = pl.concat(
            [i for i in (observed_float, observed_string) if len(i)],
            how="diagonal_relaxed",
        )

        col_order = ["date_time", "variable"]
        observed = (
            observed.with_columns(pl.col("date_time").str.to_datetime())
            .select(col_order + [pl.exclude(col_order)])
            .with_columns(
                pl.col("variable").str.extract_groups(
                    r"(?<variable>.+)_set_(?<sensor_index>\d)(?<is_derived>d?)"
                )
            )
            .unnest("variable")
            .with_columns(
                pl.col("is_derived") == "d",
                pl.col("sensor_index").cast(pl.UInt32),
                pl.col("variable").replace(S.UNITS).alias("units"),
            )
        )

        if any(metadata["QC_FLAGGED"]):
            qc = (
                pl.DataFrame(qc)
                .with_columns(
                    date_time=pl.Series(observations["date_time"]).str.to_datetime()
                )
                .unpivot(index="date_time", value_name="qc_flags")
                .with_columns(
                    pl.col("variable").str.extract_groups(
                        r"(?<variable>.+)_set_(?<sensor_index>\d)(?<is_derived>d?)"
                    )
                )
                .unnest("variable")
                .with_columns(
                    pl.col("is_derived") == "d",
                    pl.col("sensor_index").cast(pl.UInt32),
                )
            )

            # Attach the QC information to the observations
            observed = observed.join(
                qc,
                on=["date_time", "variable", "sensor_index", "is_derived"],
                how="full",
                coalesce=True,
            )

        # Attach the metadata to the observations
        observed = observed.join(metadata, how="cross")

        dfs.append(observed)

    df = pl.concat(dfs, how="diagonal_relaxed")

    # Clean up
    df = df.pipe(unnest_period_of_record)
    df = df.rename({i: i.lower() for i in df.columns})

    if "qc_flagged" in df.columns:
        # Don't want to confuse the user with this column, so drop it.
        # The user only needs to check for the `qc_flags` column to see if
        # the observation was QCed.
        df = df.drop("qc_flagged")

    return df


def parse_stations_latest_nearesttime(S: "SynopticAPI") -> pl.DataFrame:
    """Parse STATIONS items for 'latest' and 'nearesttime' service.

    Parameters
    ----------
    S : SynopticAPI instance
    """
    # Unpack Latest/Nearest time JSON into parts
    observations = []
    qc = []
    latency = []
    sensor_variables = []

    for s in S.STATION:
        observations.append({"stid": s["STID"]} | s.pop("OBSERVATIONS", {}))
        qc.append({"stid": s["STID"]} | s.pop("QC", {}))
        latency.append({"stid": s["STID"]} | s.pop("LATENCY", {}))
        sensor_variables.append({"stid": s["STID"]} | s.pop("SENSOR_VARIABLES", {}))

    # Get Observations DataFrame
    df = pl.DataFrame(observations, infer_schema_length=None)

    # *************************************************************************
    # BUG: Synoptic API
    # The ozone_concentration_value_1 value is returned as string but should
    # be a float.
    if "ozone_concentration_value_1" in df.columns:
        df = df.with_columns(
            pl.struct(
                [
                    pl.col("ozone_concentration_value_1")
                    .struct.field("value")
                    .replace("", None)
                    .cast(pl.Float64),
                    pl.col("ozone_concentration_value_1").struct.field("date_time"),
                ]
            ).alias("ozone_concentration_value_1")
        )
    # *************************************************************************

    # Separate columns by value type
    cols_with_float = []
    cols_with_string = []
    cols_with_cloud_layer = []
    cols_with_other = []

    for col, schema in df.schema.items():
        if hasattr(schema, "fields"):
            if pl.Field("value", pl.Float64) in schema.fields:
                cols_with_float.append(col)
            elif pl.Field("value", pl.String) in schema.fields:
                cols_with_string.append(col)
            elif col.startswith("cloud_layer"):
                cols_with_cloud_layer.append(col)
            elif pl.Field("value", pl.Struct) in schema.fields:
                cols_with_other.append(col)
                print(f"WARNING: Unknown struct for {col=} {schema=}")
        else:
            print(f"{col=}, {schema=}")

    to_concat = []

    # Unpack the float observations
    if cols_with_float:
        observed_float = (
            df.select(["stid"] + cols_with_float)
            .select("stid", "^.*value.*$")
            .unpivot(index="stid")
            .unnest("value")
            .drop_nulls()
        )
        to_concat.append(observed_float)

    # Unpack the string observations
    #   Put values in column 'value_string'
    if cols_with_string:
        observed_string = (
            df.select(["stid"] + cols_with_string)
            .select("stid", "^.*value.*$")
            .unpivot(index="stid")
            .unnest("value")
            .rename({"value": "value_string"})
            .drop_nulls()
        )
        to_concat.append(observed_string)

    # Unpack the cloud layer.
    #   Put sky_condition in 'value_sting' column
    #   and height_agl in 'value' column
    if cols_with_cloud_layer:
        observed_cloud_layer = (
            (
                df.select(["stid"] + cols_with_cloud_layer)
                .select("stid", "^.*value.*$")
                .unpivot(index="stid")
                .unnest("value")
                .drop_nulls()
            )
            .unnest("value")
            .rename({"sky_condition": "value_string", "height_agl": "value"})
        )
        to_concat.append(observed_cloud_layer)

    # Join all observation values
    observed = pl.concat(to_concat, how="diagonal_relaxed")

    # Cast 'date_time' column from string to datetime
    observed = observed.with_columns(pl.col("date_time").str.to_datetime())

    # Parse the variable name
    observed = observed.pipe(parse_raw_variable_column, S.UNITS)

    # Join the metadata to the observed values
    metadata = station_metadata_to_dataframe(S.STATION)
    observed = observed.join(metadata, on="stid", how="full", coalesce=True)

    if "qc" in observed.columns:
        observed = (
            observed.unnest("qc")
            .rename({"status": "qc_passed"})
            .with_columns(
                pl.col("qc_passed").replace_strict({"failed": False, "passed": True})
            )
        )

    return observed


def parse_stations_precipitation(S: "SynopticAPI") -> pl.DataFrame:
    """Parse STATIONS portion of JSON object of SynopticAPI instance for 'precipitation' service.

    Parameters
    ----------
    s : SynopticAPI instance
    """
    dfs = []
    for station in S.STATION:
        observations = station.get("OBSERVATIONS")
        metadata = station_metadata_to_dataframe(station)

        if not observations:
            # The value of STATION[n]["OBSERVATIONS"] is an empty dict,
            # in the case of `showemptystatoins=True`.
            dfs.append(metadata)
            continue

        z = (
            pl.DataFrame(observations["precipitation"]).with_columns(
                pl.col("first_report").str.to_datetime(),
                pl.col("last_report").str.to_datetime(),
                pl.lit(S.UNITS["precipitation"]).alias("units"),
            )
        ).join(metadata, how="cross")
        dfs.append(z)
    df = pl.concat(dfs, how="diagonal_relaxed")
    df = df.rename({i: i.lower() for i in df.columns})
    return df


def parse_stations_latency(S: "SynopticAPI") -> pl.DataFrame:
    """Parse STATION portion of JSON object for the 'latency' service."""
    dfs = []
    for station in S.STATION:
        metadata = station_metadata_to_dataframe(station)

        latency = (
            pl.DataFrame(station["LATENCY"])
            .with_columns(
                pl.col("date_time").str.to_datetime(),
                pl.duration(minutes="values").alias("latency"),
            )
            .drop("values")
        )

        # Attach the metadata to the observations
        latency = latency.join(metadata, how="cross")
        dfs.append(latency)

    df = pl.concat(dfs, how="diagonal_relaxed")

    # Clean up
    df = df.pipe(unnest_period_of_record)
    df = df.rename({i: i.lower() for i in df.columns})

    return df
