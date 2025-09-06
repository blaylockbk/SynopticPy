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
        )
    )


def attach_units(df, units_dict):
    """Attach units information as a new column.

    Parameters
    ----------
    units_dict : dict
        A mapping of the variable names to unit, as provided by
        `SynopticAPI().UNITS`.
    """
    return df.with_columns(
        pl.col("variable").replace(units_dict).alias("units"),
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
        pl.col("ELEVATION", "LATITUDE", "LONGITUDE").str.strip_chars().cast(pl.Float64),
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
    # TODO: Need to implement parsing cloud_layer
    # TODO: Do I need to have a `qc_passed` column to be consistent with the Latest service?

    observations = []
    qc = []
    latency = []
    sensor_variables = []

    for s in S.STATION:
        observations.append({"stid": s["STID"]} | s.pop("OBSERVATIONS", {}))
        if "QC" in s:
            qc.append(
                {"stid": s["STID"], "date_time": observations[-1]["date_time"]}
                | s.pop("QC", {})
            )
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

    # Attach QC flags if available.
    if qc:
        qc_flags = (
            pl.DataFrame(qc, infer_schema_length=None)
            .unpivot(index=["stid", "date_time"], value_name="qc_flags")
            .filter(pl.col("qc_flags").is_not_null())
            .explode("date_time", "qc_flags")
            # TODO: Do I need to have a `qc_passed` column to be consistent with the Latest service?
        )
        observed = observed.join(
            qc_flags,
            on=["stid", "date_time", "variable"],
            how="full",
            coalesce=True,
        )

    # Cast 'date_time' column from string to datetime
    observed = observed.with_columns(pl.col("date_time").str.to_datetime())

    # Parse the variable name
    observed = observed.pipe(parse_raw_variable_column)

    # Attach the variable's units
    observed = observed.pipe(attach_units, S.UNITS)

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
        # TODO: DO I need to handle QC like I do in timeseries?
        qc.append({"stid": s["STID"]} | s.pop("QC", {}))
        latency.append({"stid": s["STID"]} | s.pop("LATENCY", {}))
        sensor_variables.append({"stid": s["STID"]} | s.pop("SENSOR_VARIABLES", {}))

    # Get Observations DataFrame
    df = pl.DataFrame(observations, infer_schema_length=None)

    ## *************************************************************************
    ## BUG: Synoptic API -- This doesn't seem to be an issue anymore
    ## The ozone_concentration_value_1 value is returned as string but should
    ## be a float.
    # if "ozone_concentration_value_1" in df.columns:
    #    df = df.with_columns(
    #        pl.struct(
    #            [
    #                pl.col("ozone_concentration_value_1")
    #                .struct.field("value")
    #                .replace("", None)
    #                .cast(pl.Float64),
    #                pl.col("ozone_concentration_value_1").struct.field("date_time"),
    #            ]
    #        ).alias("ozone_concentration_value_1")
    #    )
    ## *************************************************************************

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
            pass

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
    observed = observed.with_columns(
        pl.col("date_time").str.to_datetime("%Y-%m-%dT%H:%M:%S%#z")
    )

    # Parse the variable name
    observed = observed.pipe(parse_raw_variable_column)
    observed = observed.pipe(attach_units, S.UNITS)

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
    observations = []
    qc = []
    latency = []
    sensor_variables = []

    for s in S.STATION:
        observations.append({"stid": s["STID"]} | s.pop("OBSERVATIONS", {}))
        qc.append({"stid": s["STID"]} | s.pop("QC", {}))
        latency.append({"stid": s["STID"]} | s.pop("LATENCY", {}))
        sensor_variables.append({"stid": s["STID"]} | s.pop("SENSOR_VARIABLES", {}))

    df = (
        pl.DataFrame(observations, infer_schema_length=None)
        .explode("precipitation")
        .unnest("precipitation")
        .with_columns(
            pl.col("first_report", "last_report").str.to_datetime(),
            pl.lit(S.UNITS["precipitation"]).alias("units"),
        )
    )

    # Join the metadata to the observed values
    metadata = station_metadata_to_dataframe(S.STATION)
    df = df.join(metadata, on="stid", how="full", coalesce=True)

    return df


def parse_stations_latency(S: "SynopticAPI") -> pl.DataFrame:
    """Parse STATION portion of JSON object for the 'latency' service."""
    observations = []
    qc = []
    latency = []
    sensor_variables = []

    for s in S.STATION:
        observations.append({"stid": s["STID"]} | s.pop("OBSERVATIONS", {}))
        qc.append({"stid": s["STID"]} | s.pop("QC", {}))
        latency.append({"stid": s["STID"]} | s.pop("LATENCY", {}))
        sensor_variables.append({"stid": s["STID"]} | s.pop("SENSOR_VARIABLES", {}))

    df = pl.DataFrame(latency).explode("date_time", "values")

    # Join the metadata to the observed values
    metadata = station_metadata_to_dataframe(S.STATION)
    df = df.join(metadata, on="stid", how="full", coalesce=True)

    return df
