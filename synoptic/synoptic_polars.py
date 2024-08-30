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

TODO: Use token from 1) environment variable, 2) config.toml, 3) function argument
TODO: Does not parse non-numeric values (document this fact), like wind_cardinal_direction. (TODO: Are there any others?)
    These are what I found so far...'wind_cardinal_direction_set_1d', 'weather_condition_set_1d', 'weather_summary_set_1d'
TODO: Provide helper function to do proper pivot
TODO: Provide helper function to do proper rolling and resample windows (https://docs.pola.rs/user-guide/transformations/time-series/resampling/)
TODO: Document how to write to Parquet so user doesn't have to make API call to get data again (i.e., doing research)
TODO: Extensive testing.
TODO: Add some quick, standardized plots (leverage seaborn, cartopy optional)
TODO: Special case for 'obrange'???
TODO: Can polars parse duration strings like '1h' and '1h30m' to a duration?
TODO: Maybe don't join *all* metadata columns, only those really necessary.    <-- Let the user decide to drop things.

TODO: If wind_speed and wind_direction are included, derive wind_u and wind_v
"""

import os
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


def metadata_to_dataframe(metadata: dict) -> pl.DataFrame:
    """Convert station metadata to a DataFrame."""
    # TODO: Check that we don't have "OBSERVATION" or "SENSOR_VARIABLES" keys
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
        .drop("UNITS")  # Unnecessary?
    )


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
        self.SUMMARY = self.json["SUMMARY"]

        if "QC_SUMMARY" in self.json.keys():
            self.QC_SUMMARY = self.json["QC_SUMMARY"]

        if "UNITS" in self.json.keys():
            self.UNITS = self.json["UNITS"]

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


class TimeSeries(SynopticAPI):
    """Get time series data.

    https://docs.synopticdata.com/services/time-series
    """

    def __init__(self, **params):
        super().__init__("timeseries", **params)

        dfs = []
        sensor_variables = {}
        for station in self.json["STATION"]:
            stid = station["STID"]
            observations = station.pop("OBSERVATIONS")
            sensor_variables = station.pop("SENSOR_VARIABLES")
            metadata = metadata_to_dataframe(station)

            z = (
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
                    pl.col("variable").replace(self.UNITS).alias("units"),
                )
                .filter(pl.col("value").is_not_null())
            ).join(metadata, how="cross")
            dfs.append(z)
            sensor_variables[stid] = sensor_variables
        df = pl.concat(dfs, how="diagonal_relaxed")
        df = df.rename({i: i.lower() for i in df.columns})
        self.df = df


class Latest(SynopticAPI):
    def __init__(self, **params):
        super().__init__("latest", **params)

        dfs = []
        sensor_variables = {}
        for station in self.json["STATION"]:
            stid = station["STID"]
            observations = station.pop("OBSERVATIONS")
            sensor_variables = station.pop("SENSOR_VARIABLES")
            metadata = metadata_to_dataframe(station)

            z = (
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
                    pl.col("variable").replace(self.UNITS).alias("units"),
                )
                .filter(pl.col("value").is_not_null())
            ).join(metadata, how="cross")
            dfs.append(z)
            sensor_variables[stid] = sensor_variables
        df = pl.concat(dfs, how="diagonal_relaxed")
        df = df.rename({i: i.lower() for i in df.columns})
        self.df = df


class NearestTime(SynopticAPI):
    # NOTE: This code is identical to "Latest". Can it be simplified??
    def __init__(self, **params):
        super().__init__("nearesttime", **params)

        dfs = []
        sensor_variables = {}
        for station in self.json["STATION"]:
            stid = station["STID"]
            observations = station.pop("OBSERVATIONS")
            sensor_variables = station.pop("SENSOR_VARIABLES")
            metadata = metadata_to_dataframe(station)

            z = (
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
                    pl.col("variable").replace(self.UNITS).alias("units"),
                )
                .filter(pl.col("value").is_not_null())
            ).join(metadata, how="cross")
            dfs.append(z)
            sensor_variables[stid] = sensor_variables
        df = pl.concat(dfs, how="diagonal_relaxed")
        df = df.rename({i: i.lower() for i in df.columns})
        self.df = df


class Precipitation(SynopticAPI):
    def __init__(self, **params):
        super().__init__("precipitation", **params)

        dfs = []
        for station in self.json["STATION"]:
            stid = station["STID"]
            observations = station.pop("OBSERVATIONS")
            metadata = metadata_to_dataframe(station)

            z = (
                pl.DataFrame(observations)
                .with_columns(
                    pl.col("ob_start_time_1").str.to_datetime(),
                    pl.col("ob_end_time_1").str.to_datetime(),
                    pl.lit(self.UNITS["precipitation"]).alias("units"),
                )
                .rename(
                    {
                        "ob_start_time_1": "ob_start_time",
                        "ob_end_time_1": "ob_end_time",
                        "total_precip_value_1": "total_precip",
                        "count_1": "count",
                    }
                )
            ).join(metadata, how="cross")
            dfs.append(z)
        df = pl.concat(dfs, how="diagonal_relaxed")
        df = df.rename({i: i.lower() for i in df.columns})
        self.df = df
