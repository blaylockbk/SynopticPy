"""Synoptic Data to Polars DataFrame.

My goal...

```python
import synoptic

df = synoptic.timeseries(params)
df = synoptic.metadata(params)
df = synoptic.nearest_time(params)
df = synoptic.latest(params)
df = synoptic.precipitation(params)

df.synoptic.pivot(...)
df.synoptic.resample(...)
```

Put each of these functions are in the 'services.py' file.

The default DataFrame is in long format; one row for each unique observation

QUESTION: Are derived variables flagged if the variable used to derive it is also flagged?

Note: Does not parse non-numeric values (document this fact), like wind_cardinal_direction. (TODO: Are there any others?)
    These are what I found so far...'wind_cardinal_direction_set_1d', 'weather_condition_set_1d', 'weather_summary_set_1d'
TODO: Allow user to cast values column to float or string, then drop null rows

TODO: Need to handle the QC data column.
TODO: Extensive testing.
TODO: Provide helper function to do proper pivot
TODO: Provide helper function to do proper rolling and resample windows (https://docs.pola.rs/user-guide/transformations/time-series/resampling/)
TODO: Add some quick, standardized plots (leverage seaborn, cartopy optional)
TODO: Document how to write to Parquet so user doesn't have to make API call to get data again (i.e., doing research)
TODO: Special case for 'obrange'???
TODO: If wind_speed and wind_direction are included, derive wind_u and wind_v
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal, Optional

import polars as pl
import requests
import toml

# Available API Services
# https://docs.synopticdata.com/services/weather-data-api
_services_stations = {
    "timeseries",
    "latest",
    "nearesttime",
    "precipitation",
    "qcsegments",
    "latency",
    "metadata",
}
_services_metadata = {
    "qctypes",
    "variables",
    "networks",
    "networktypes",
    # "auth", # needs special handling and considerations
}
_services = _services_stations | _services_metadata

ServiceType = Literal[
    "timeseries",
    "latest",
    "nearesttime",
    "precipitation",
    "qcsegments",
    "latency",
    "metadata",
    "qctypes",
    "variables",
    "networks",
    "networktypes",
    # "auth",
]


class SynopticAPIError(Exception):
    """Custom exception for SynopticAPI errors."""

    pass


class SynopticAPI:
    """Request data from the Synoptic Data API.

    Parameters
    ----------
    service : {'timeseries', 'latest', 'neartesttime', 'precipitation', etc.}
        The Synoptic API service to use. Refer to the Synoptic Weather
        Data API documentation for a full list of services:
        https://docs.synopticdata.com/services/weather-data-api
    token : str
        A 32-character Synoptic account token. If None, tries to get
        value from the following:
        1. Environment variable `SYNOPTIC_TOKEN`,
        2. `token="..."` value in `~/.config/SynopticPy/config.toml`.
    **parms
        Synoptic API request arguments.
        - Lists are converted to comma-separated strings.
        - Datetime and timedelta are converted to strings.
        - Datetime can a string in format `'YYYY-MM-DD HH:MM'`

        Refer to the Synoptic Weather Data API documentation for valid
        arguments for each service:
        https://docs.synopticdata.com/services/weather-data-api
    """

    def __init__(self, service: ServiceType, *, token: Optional[str] = None, **params):
        self.service = service

        if self.service in _services_stations:
            self.endpoint = f"https://api.synopticdata.com/v2/stations/{service}"
        else:
            self.endpoint = f"https://api.synopticdata.com/v2/{service}"

        self.help_url = "https://docs.synopticdata.com/services/weather-data-api"

        # ---------
        # Get token
        if token is None:
            token = os.getenv("SYNOPTIC_TOKEN")
            if token is None:
                _config_path = os.getenv(
                    "SYNOPTICPY_CONFIG_PATH", "~/.config/SynopticPy"
                )
                _config_path = Path(_config_path).expanduser()
                _config_file = _config_path / "config.toml"
                if _config_file.exists():
                    try:
                        # new token configuration
                        token = toml.load(_config_file).get("token")
                    except:
                        # legacy token configuration
                        token = toml.load(_config_file)["default"].get("token")
                else:
                    raise SynopticAPIError(
                        "\n"
                        " ╭─SynopticPy:FATAL────────────────────────────────────────────╮\n"
                        " │ A valid Synoptic token is required. Do one of the following:│\n"
                        " │  1) Specify `token='1234567889ABCDE...'` in your request.   │\n"
                        " │  2) Set environment variable SYNOPTIC_TOKEN.                │\n"
                        " │  3) Configure a token in ~/.config/SynopticPy/config.toml   │\n"
                        " ╰─────────────────────────────────────────────────────────────╯\n"
                    )

        # ----------------
        # Parse parameters

        # Force all param keys to be lower case.
        params = {k.lower(): v for k, v in params.items()}
        params["token"] = token

        for key, value in params.items():
            # Convert lists to comma-separated string.
            #   stid=['KSLC', 'KMRY'] --> stid='KSLC,KRMY'.
            #   radius=[40, -100, 10] --> radius='40,-100,10'
            if isinstance(value, list) and key not in ["obrange"]:
                params[key] = ",".join([str(i) for i in value])

            # TODO: Special case for 'obrange'???

            # Convert datetime or string datetime to 'YYYYMMDDHHMM'.
            elif key in {"start", "end", "expire", "attime"}:
                if isinstance(value, str) and "-" in value:
                    try:
                        # Try to parse the string as a datetime
                        value = pl.Series([value]).str.to_datetime().item()
                    except:
                        raise SynopticAPIError(
                            "\n"
                            f"Wrong datetime format for {key}.\n"
                            "Try using a datetime object or string like `YYYY-MM-DD HH:MM`."
                        )

                if hasattr(value, "minute"):
                    params[key] = f"{value:%Y%m%d%H%M}"
                else:
                    params[key] = str(value)

            # Convert timedelta to int in minutes
            elif key in {"recent", "within"}:
                if isinstance(value, str) and not value.isnumeric():
                    value = string_to_timedelta(value)

                if hasattr(value, "total_seconds"):
                    params[key] = f"{value.total_seconds() / 60:.0f}"

        self.params = params

        # ----------------
        # Make API request
        self.response = requests.get(self.endpoint, params=params)
        self.url = self.response.url
        self.json = self.response.json()

        # -------------------
        # Attach request data
        self.SUMMARY = self.json.get("SUMMARY")
        self.QC_SUMMARY = self.json.get("QC_SUMMARY")  # If None, then param `qc='off'`
        self.UNITS = self.json.get("UNITS")
        self.STATION = self.json.get("STATION")

        # -------------------
        # Check returned data
        if self.SUMMARY["RESPONSE_CODE"] != 1:
            raise SynopticAPIError(
                "\n"
                f"FATAL: Not a valid Synoptic API request.\n"
                f"  ├─ message: {self.SUMMARY['RESPONSE_MESSAGE']}\n"
                f"  └─ url: {self.response.url}\n"
                f"See {self.help_url} for help."
            )

        # -----------------------------
        # Parse STATIONS into DataFrame
        if service == "timeseries":
            self.df = parse_stations_timeseries(self)
        elif service in ["nearesttime", "latest"]:
            self.df = parse_stations_latest_nearesttime(self)
        elif service == "precipitation":
            self.df = parse_stations_precipitation(self)

    def __repr__(self):
        return f"SynopticAPI: \nservice={self.service}"

    def __str__(self):
        return "String Synoptic: TODO"


class TimeSeries(SynopticAPI):
    """Get time series data for a station or stations.

    https://docs.synopticdata.com/services/time-series

    Parameters
    ----------
    **params
        - `start`, `end` | `recent`
    """

    def __init__(self, **params):
        super().__init__("timeseries", **params)


class Latest(SynopticAPI):
    def __init__(self, **params):
        super().__init__("latest", **params)


class NearestTime(SynopticAPI):
    # NOTE: This code is identical to "Latest". Can it be simplified??
    def __init__(self, **params):
        super().__init__("nearesttime", **params)


class Precipitation(SynopticAPI):
    """
    Request derived precipitation total or intervals.

    https://docs.synopticdata.com/services/precipitation

    Parameters
    ----------
    **params
        - Station selection parameters.
        - `start` and `end` | `recent`

    Optional Parameters
    -------------------
    pmode : {'totals', 'intervals', 'last'}
        Default is totals.
    interval : int | {'hour', 'day', 'week', 'month', 'year'}
        Integer hours, or string interval.
        Default is "day" if not set.
    """

    def __init__(self, **params):
        # Don't allow legacy precip service with pmode omitted.
        params.setdefault("pmode", "totals")

        super().__init__("precipitation", **params)


def string_to_timedelta(x: str) -> timedelta:
    """
    Parse a string representing days, hours, minutes, seconds to a timedelta.

    x : str
        String representation of duration. Can use ISO 8601 duration, in
        a limited fashion, or a Polars-style period string.
        - `'PT30M'` = 30 minutes
        - `'P1DT6H'` = 1 day, 6 hours
        - `'30m'` = 30 minutes
        - `'3d6h30m10s'` = 3 days, 6 hours, 30 minutes, 10 seconds
    """
    x = x.lower()
    x = x.replace("p", "").replace("t", "")
    pattern = r"(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?"

    groups = re.match(pattern, x).groupdict()
    kwargs = {k: int(v) for k, v in groups.items() if v is not None}
    return timedelta(**kwargs)


def station_metadata_to_dataframe(metadata: dict) -> pl.DataFrame:
    """Convert station metadata to a DataFrame."""
    # TODO: Check that we don't have "OBSERVATION" or "SENSOR_VARIABLES" keys
    metadata = metadata.copy()
    metadata.pop("OBSERVATIONS", None)
    metadata.pop("SENSOR_VARIABLES", None)
    return (
        pl.DataFrame(metadata)
        .with_columns(
            pl.struct(
                pl.col("PERIOD_OF_RECORD")
                .struct.field("start")
                .str.to_datetime()
                .alias("PERIOD_OF_RECORD_START"),
                pl.col("PERIOD_OF_RECORD")
                .struct.field("end")
                .str.to_datetime()
                .alias("PERIOD_OF_RECORD_END"),
            ).alias("PERIOD_OF_RECORD"),
            pl.col("STID").cast(pl.String),
            pl.col("ID", "MNET_ID").cast(pl.UInt32),
            pl.col("ELEVATION", "LATITUDE", "LONGITUDE", "ELEV_DEM").cast(pl.Float64),
        )
        .unnest("PERIOD_OF_RECORD")
        .drop("UNITS")  # Not needed because is is also in json["UNITS"].
    )


def parse_stations_timeseries(S: SynopticAPI) -> pl.DataFrame:
    """Parse STATIONS portion of JSON object of SynopticAPI instance for 'timeseries' service.

    Parameters
    ----------
    s : SynopticAPI instance
    """
    dfs = []
    for station in S.STATION:
        observations = station["OBSERVATIONS"]
        qc = station.get("QC")  # Use 'get' because it is not always provided.
        metadata = station_metadata_to_dataframe(station)

        observed = (
            pl.DataFrame(observations)
            .with_columns(pl.col("date_time").str.to_datetime())
            .unpivot(index="date_time")
            .with_columns(
                pl.col("variable").str.extract_groups(
                    r"(?<variable>.+)_set_(?<sensor>\d)(?<derived>d?)"
                )
            )
            .unnest("variable")
            .with_columns(
                pl.col("value").cast(
                    pl.Float64, strict=False
                ),  # Values must be numbers
                pl.col("derived") == "d",
                pl.col("sensor").cast(pl.UInt32),
                pl.col("variable").replace(S.UNITS).alias("units"),
            )
        )

        # TODO: or is `if metadata["QC_FLAGGED"].item():` more appropriate here?
        if "QC" in station.keys():
            qc = (
                pl.DataFrame(qc)
                .with_columns(
                    date_time=pl.Series(observations["date_time"]).str.to_datetime()
                )
                .unpivot(index="date_time", value_name="qc_flags")
                .with_columns(
                    pl.col("variable").str.extract_groups(
                        r"(?<variable>.+)_set_(?<sensor>\d)(?<derived>d?)"
                    )
                )
                .unnest("variable")
                .with_columns(
                    pl.col("derived") == "d",
                    pl.col("sensor").cast(pl.UInt32),
                )
            )
            observed = observed.join(
                qc,
                on=["date_time", "variable", "sensor", "derived"],
                how="full",
                coalesce=True,
            )

        observed = observed.join(metadata, how="cross")

        dfs.append(observed)

    df = pl.concat(dfs, how="diagonal_relaxed")
    df = df.rename({i: i.lower() for i in df.columns})

    return df


def parse_stations_latest_nearesttime(S: SynopticAPI) -> pl.DataFrame:
    """Parse STATIONS portion of JSON object of SynopticAPI instance for 'latest' and 'nearesttime' service.

    Parameters
    ----------
    s : SynopticAPI instance
    """
    # The JSON structure for the latest and nearest time services are identical.
    dfs = []
    for station in S.STATION:
        observations = station["OBSERVATIONS"]
        metadata = station_metadata_to_dataframe(station)

        observed = (
            pl.DataFrame(observations)
            .transpose(include_header=True, header_name="variable")
            .unnest("column_0")
            .with_columns(pl.col("date_time").str.to_datetime())
            .select("date_time", "variable", "value")
            .with_columns(
                pl.col("variable").str.extract_groups(
                    r"(?<variable>.+)_value_(?<sensor>\d)(?<derived>d?)"
                )
            )
            .unnest("variable")
            .with_columns(
                pl.col("value").cast(
                    pl.Float64, strict=False
                ),  # Values must be numbers
                pl.col("derived") == "d",
                pl.col("sensor").cast(pl.UInt32),
                pl.col("variable").replace(S.UNITS).alias("units"),
            )
        )

        if metadata["QC_FLAGGED"].item():
            qc_flags = {}
            for k, v in observations.items():
                if "qc" in v.keys():
                    qc_flags[k] = v["qc"].get("qc_flags")
                else:
                    qc_flags[k] = None
            qc = (
                pl.DataFrame(qc_flags)
                .transpose(include_header=True, header_name="variable")
                .rename({"column_0": "qc_flags"})
                .with_columns(
                    pl.col("variable").str.extract_groups(
                        r"(?<variable>.+)_value_(?<sensor>\d)(?<derived>d?)"
                    )
                )
                .unnest("variable")
                .with_columns(
                    pl.col("derived") == "d",
                    pl.col("sensor").cast(pl.UInt32),
                )
            )
            observed = observed.join(
                qc,
                on=["variable", "sensor", "derived"],
                how="full",
                coalesce=True,
            )

        observed = observed.join(metadata, how="cross")
        dfs.append(observed)
    df = pl.concat(dfs, how="diagonal_relaxed")
    df = df.rename({i: i.lower() for i in df.columns})
    return df


def parse_stations_precipitation(S: SynopticAPI) -> pl.DataFrame:
    """Parse STATIONS portion of JSON object of SynopticAPI instance for 'precipitation' service.

    Parameters
    ----------
    s : SynopticAPI instance
    """
    dfs = []
    for station in S.STATION:
        observations = station["OBSERVATIONS"]
        metadata = station_metadata_to_dataframe(station)

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
