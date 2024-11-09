"""Parse Synoptic's JSON into DataFrames."""

from typing import TYPE_CHECKING

import polars as pl

if TYPE_CHECKING:
    from synoptic.services import SynopticAPI


def unnest_period_of_record(df: pl.DataFrame) -> pl.DataFrame:
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


def station_metadata_to_dataframe(metadata: dict) -> pl.DataFrame:
    """Convert STATION metadata from JSON to a DataFrame."""
    metadata = metadata.copy()
    metadata.pop("OBSERVATIONS", None)
    metadata.pop("SENSOR_VARIABLES", None)
    metadata.pop("LATENCY", None)
    metadata.pop("QC", None)
    df = (
        pl.DataFrame(metadata)
        .with_columns(
            pl.col("STID").cast(pl.String),
            pl.col("ID", "MNET_ID").cast(pl.UInt32),
            pl.col("ELEVATION", "LATITUDE", "LONGITUDE").cast(pl.Float64),
            is_active=pl.when(pl.col("STATUS") == "ACTIVE")
            .then(True)
            .otherwise(pl.when(pl.col("STATUS") == "INACTIVE").then(False)),
        )
        .drop("UNITS", "STATUS")
    )
    if "RESTRICTED" in df.columns:
        df = df.rename({"RESTRICTED": "is_restricted"})

    if "ELEV_DEM" in df.columns:
        # This isn't in the Latency request
        df = df.with_columns(pl.col("ELEV_DEM").cast(pl.Float64))

    if len(df) > 1:
        # When param `complete=1`, some stations have multiple providers
        # and is given as a list of key-value pairs of provider name and
        # url. But Polars loads this as individual rows.
        # I'll just return the first.
        df = df[0]

    return df


def parse_stations_timeseries(S: "SynopticAPI") -> pl.DataFrame:
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

        if not observations:
            # The value of STATION[n]["OBSERVATIONS"] is an empty dict,
            # in the case of `showemptystatoins=True`.
            dfs.append(metadata)
            continue

        df = pl.DataFrame(observations)

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
    s : SynopticAPI instance
    """
    # The JSON structure for the latest and nearest time services are identical.
    dfs = []
    for station in S.STATION:
        observations = station.get("OBSERVATIONS")
        metadata = station_metadata_to_dataframe(station)

        # Tip: It's informative to look at the unique schema for all observations with
        # `{dtype for col, dtype in pl.DataFrame(observations).schema.items()}`

        if not observations:
            # The value of STATION[n]["OBSERVATIONS"] is an empty dict,
            # in the case of `showemptystatoins=True`.
            dfs.append(metadata)
            continue

        # TODO: Someday Polars might let you select nested column by wildcard
        # TODO: https://github.com/pola-rs/polars/issues/11067
        df = pl.DataFrame(observations)

        col_has_float_value = []
        col_has_string_value = []
        col_has_struct_value = []
        for col, struct in df.schema.items():
            if pl.Field("value", pl.Float64) in struct.fields:
                col_has_float_value.append(col)
            elif pl.Field("value", pl.String) in struct.fields:
                col_has_string_value.append(col)
            elif pl.Field("value", pl.Struct) in struct.fields:
                col_has_struct_value.append(col)
            else:
                print(f"WARNING: Unknown struct for {col=} {struct=}")

        # Parse all observations with Float64 values. (column 'value')
        observed_float = df.select(col_has_float_value)
        if len(observed_float):
            z = []
            for i in col_has_float_value:
                z.append(df.select(i).unnest(i).with_columns(variable=pl.lit(i)))
            z = pl.concat(z, how="diagonal_relaxed")

            col_order = ["date_time", "variable", "value"]
            col_order += [col for col in z.columns if col not in col_order]

            z = z.select(col_order)

            if "qc" in z.columns:
                z = (
                    z.unnest("qc")
                    .rename({"status": "qc_passed"})
                    .with_columns(
                        pl.col("qc_passed").replace_strict(
                            {"failed": False, "passed": True}
                        )
                    )
                )
            observed_float = z

        # TODO: Do I need to do the same loops as I did for observed_float?
        # Parse all observations with String values. (Column 'value_string')
        observed_string = df.select(col_has_string_value)
        if len(observed_string):
            observed_string = (
                observed_string.transpose(include_header=True, header_name="variable")
                .unnest("column_0")
                .rename({"value": "value_string"})
            )

        # TODO: Need to handle the special nested data structure
        if col_has_struct_value:
            print(
                f"WARNING: There are {len(col_has_struct_value)} columns"
                f" in {metadata['STID'].item()} that are not parsed because"
                f" of nested data structure; {col_has_struct_value}"
            )

        # Join float and string observations
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
                    r"(?<variable>.+)_value_(?<sensor_index>\d)(?<is_derived>d?)"
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
            qc_flags = {}
            for k, v in observations.items():
                if "qc" in v.keys():
                    qc_flags[k] = [v["qc"].get("qc_flags")]
                else:
                    qc_flags[k] = [None]
            qc = (
                pl.DataFrame(qc_flags)
                .transpose(include_header=True, header_name="variable")
                .rename({"column_0": "qc_flags"})
                .with_columns(
                    pl.col("variable").str.extract_groups(
                        r"(?<variable>.+)_value_(?<sensor_index>\d)(?<is_derived>d?)"
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
                on=["variable", "sensor_index", "is_derived"],
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

    # Don't want to confuse the user with this column, so drop it.
    # The user only needs to check for the `qc_flags` column to see if
    # the observation was QCed.
    df = df.drop("qc_flagged")
    return df


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
