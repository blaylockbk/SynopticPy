"""
Synoptic Data to Polars DataFrame.

QUESTION: Are derived variables flagged if the variable used to derive it is also flagged?

Note: Does not parse non-numeric values (document this fact), like wind_cardinal_direction. (TODO: Are there any others?)
    These are what I found so far...'wind_cardinal_direction_set_1d', 'weather_condition_set_1d', 'weather_summary_set_1d'

TODO: Allow user to cast values column to float or string, then drop null rows

TODO: Option to join Network name from mnet_id (call column network_name; call argument "with_network_name")

TODO: Let user use Boolean input (True/False) for params like `qc_remvoe_data` amd others that have 0/1 input

TODO: Latency: unnest statistics column if present and cast to appropriate datetime and duration types
TODO: Timeseries: could have argument `with_latency` and make a latency request and join to data.

TODO: Need to use to_timezone(timezone=...) if obtimezone='local'

TODO: Extensive testing and examples. Tests for each service in their own files.

TODO: Provide helper function to do proper pivot
TODO: Provide helper function to do proper rolling and resample windows (https://docs.pola.rs/user-guide/transformations/time-series/resampling/)
TODO: Add some quick, standardized plots (leverage seaborn, cartopy optional)
TODO: Document how to write to Parquet so user doesn't have to make API call to get data again (i.e., doing research)
TODO: Metadata: need to handle 'obrange' param.
TODO: If wind_speed and wind_direction are included, derive wind_u and wind_v
TODO: Metadata: Not implemented; parsing sensor_variables column when `sensorvars=1`

"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import polars as pl
import requests
import toml

from synoptic.json_parsers import (
    parse_stations_latency,
    parse_stations_latest_nearesttime,
    parse_stations_precipitation,
    parse_stations_timeseries,
)

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
]


class SynopticAPIError(Exception):
    """Custom exception for SynopticAPI errors."""

    pass


def string_to_timedelta(x: str) -> timedelta:
    """
    Parse a duration string to a timedelta.

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


def parse_obrange(x: str | datetime | tuple[datetime, datetime]):
    """Parse obrange argument.

    Parameters
    ----------
    x
        obrange may be given as the following:
        - Start date as string `'YYYYMMDDHHMM'` (end date is current time)
        - Start date as `datetime` (end date is current time)
        - Start and end date as string `['YYYYMMDDHHMM','YYYYMMDDHHMM']`
        - Start and end date as datetime `(datetime,datetime)`
    """
    if hasattr(x, "hour"):
        return f"{x:%Y%m%d%H%M}"
    elif (
        isinstance(x, list | tuple)
        and all(hasattr(i, "hour") for i in x)
        and len(x) == 2
    ):
        return f"{x[0]:%Y%m%d%H%M},{x[1]:%Y%m%d%H%M}"
    elif (
        isinstance(x, list | tuple)
        and all(isinstance(i, str) for i in x)
        and len(x) == 2
    ):
        return ",".join(x)  # type: ignore
    elif isinstance(x, str) and bool(re.fullmatch(r"\d{8,12}(,\d{8,12})?", x)):
        return x
    else:
        raise ValueError(
            "Trouble parsing `obrange`; try using a single `datetime` or tuple of datetimes like `(start, end)`."
        )


class SynopticAPI:
    """Request data from the Synoptic Data Weather API.

    Parameters
    ----------
    service : {'timeseries', 'latest', 'nearesttime', 'precipitation', etc.}
        The Synoptic API service to request data from.
        Refer to the Synoptic Weather Data API documentation for a full
        list of services: https://docs.synopticdata.com/services/weather-data-api
    token : str
        A 32-character Synoptic account token.
        If None, tries to get value from the following:
        1. Environment variable `SYNOPTIC_TOKEN`,
        2. The `token="..."` value in `~/.config/SynopticPy/config.toml`.
    verbose : bool
        Print each step.
    **params
        Synoptic API request arguments. Refer to the Synoptic Weather
        Data API documentation for expected and valid arguments for
        each service: https://docs.synopticdata.com/services/weather-data-api

        This Class can accept specific inputs:
        - Any comma separated strings can be given as a list instead
          (i.e., `stid=['wbb', 'ukbkb']`).
        - Datetime arguments like `start` and `end` may be
          a `datetime.datetime` or string in format `YYYY-MM-DD HH:MM`.
        - Duration arguments like `recent` can be a `datetime.timedelta`
          or a duration string like `1d12h` or `30m`.
        - Parameters that accept input as 0/1 or on/off
          may be given as a boolean instead (i.e., True/False).
    """

    def __init__(
        self,
        service: ServiceType,
        *,
        token: str | None = None,
        verbose=True,
        **params,
    ):
        self.help_url = "https://docs.synopticdata.com/services/weather-data-api"
        self.verbose = verbose

        # -------------
        # Get API token
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
                        " │                                                             │\n"
                        " │ You can sign up for a free open-access acount at            │\n"
                        " │ https://customer.synopticdata.com/signup/                   │\n"
                        " ╰─────────────────────────────────────────────────────────────╯\n"
                    )
                self.token_source = f"Config File: {_config_path}"
            else:
                self.token_source = "environment variable SYNOPTIC_TOKEN"

        else:
            self.token_source = "class constructor argument `token='...'`"

        # ----------------
        # Parse parameters

        # Force all param keys to be lower case.
        params = {k.lower(): v for k, v in params.items()}
        params["token"] = token

        # Don't allow user to specify 'timeformat'
        params.pop("timeformat", None)

        # Don't allow user to specify `output`
        params.pop("output", None)

        for key, value in params.items():
            if key == "obrange":
                params[key] = parse_obrange(value)

            # Convert lists to comma-separated string.
            #   stid=['KSLC', 'KMRY'] --> stid='KSLC,KRMY'.
            #   radius=[40, -100, 10] --> radius='40,-100,10'
            elif isinstance(value, (list, tuple)):
                params[key] = ",".join([str(i) for i in value])

            # Handle Boolean input
            # Some examples that can be given as boolean:
            #   complete, showemptystations, showemptyvars, precip, all_reports, hfmetars, sensorvars
            # Special Cases:
            #   qc, qc_remove_data, qc_flag
            elif isinstance(value, bool):
                if key in {"qc", "qc_remove_data", "qc_flag"}:
                    params[key] = "on" if value else "off"
                else:
                    params[key] = int(value)

            # Convert datetime or string datetime to 'YYYYMMDDHHMM'.
            elif key in {"start", "end", "expire", "attime"}:
                if isinstance(value, str) and "-" in value:
                    try:
                        # Try to parse the string as a datetime
                        value = pl.Series([value]).str.to_datetime().item()
                    except:
                        raise SynopticAPIError(
                            "\n"
                            f"Wrong datetime format for {key}={value}. \n"
                            "Try using a datetime object or string like 'YYYY-MM-DD HH:MM'."
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

        # --------------------------------
        # Make API request (get JSON data)
        self.service = service
        if self.service in _services_stations:
            self.endpoint = f"https://api.synopticdata.com/v2/stations/{service}"
        else:
            self.endpoint = f"https://api.synopticdata.com/v2/{service}"

        if self.verbose:
            print(f"🚚💨 Speedy delivery from Synoptic {service} service.")

        self.response = requests.get(self.endpoint, params=params)
        self.url = self.response.url
        self.json = self.response.json()

        # ----------------------------------------------------
        # Attach each JSON key-value pair as a class attribute
        for key, value in self.json.items():
            setattr(self, key, value)

        # -------------------
        # Check returned data
        # Note: SUMMARY is always returned in the JSON.
        if self.SUMMARY["RESPONSE_CODE"] != 1:
            raise SynopticAPIError(
                "\n"
                f"🛑 FATAL: Not a valid Synoptic API request.\n"
                f"  ├─ message: {self.SUMMARY['RESPONSE_MESSAGE']}\n"
                f"  └─ url: {self.response.url}\n"
                f"See {self.help_url} for help."
            )

        if self.verbose:
            print(
                f"📦 Received data from {self.SUMMARY.get('NUMBER_OF_OBJECTS'):,} stations."
            )

    def __repr__(self):
        """Notebook representation."""
        messages = f"╭─ Synoptic {self.service} service ─────\n"
        if hasattr(self, "STATION"):
            messages += f"│ Stations : {self.SUMMARY.get('NUMBER_OF_OBJECTS'):,}\n"
        if hasattr(self, "df"):
            messages += f"│ Total Obs: {len(self.df):,}\n"
        if hasattr(self, "QC_SUMMARY"):
            messages += (
                f"│ QC Checks: {len(self.QC_SUMMARY.get('QC_CHECKS_APPLIED'))}\n"
            )
        messages += "╰──────────────────────────────────────╯"
        return messages


class TimeSeries(SynopticAPI):
    """Get time series data for a station or stations.

    https://docs.synopticdata.com/services/time-series

    Parameters
    ----------
    with_latency : bool
        If True, return data with latency column from the Latency service.
    **params
        - `start`, `end` | `recent`
        https://docs.synopticdata.com/services/timeseries
    """

    def __init__(self, with_latency=False, **params):
        super().__init__("timeseries", **params)
        self.df = parse_stations_timeseries(self)

        if with_latency:
            latency = Latency(**params).df
            cols = [
                "date_time",
                "id",
                "stid",
                "name",
                "elevation",
                "latitude",
                "longitude",
            ]
            self.df = self.df.join(
                latency.select(cols + ["latency"]),
                on=cols,
                how="left",
            )


class Latest(SynopticAPI):
    """Get the most recent data from a station or stations.

    https://docs.synopticdata.com/services/latest

    Parameters
    ----------
    **params
        - `within` (optional)
    """

    def __init__(self, **params):
        super().__init__("latest", **params)
        self.df = parse_stations_latest_nearesttime(self)


class NearestTime(SynopticAPI):
    """Get data closest to the requested time for a station or stations.

    https://docs.synopticdata.com/services/nearest-time

    Parameters
    ----------
    **params
        - `attime`
        - `within` (optional)
    """

    def __init__(self, **params):
        super().__init__("nearesttime", **params)
        self.df = parse_stations_latest_nearesttime(self)


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
        self.df = parse_stations_precipitation(self)


class Latency(SynopticAPI):
    """
    Request station latency.

    https://docs.synopticdata.com/services/latency

    Parameters
    ----------
    **params
        - Station selection parameters.
        - `start` and `end` | `recent`
    """

    def __init__(self, **params):
        super().__init__("latency", **params)
        self.df = parse_stations_latency(self)


class Metadata(SynopticAPI):
    """Retrieve metadata for a station or stations.

    Parameters
    ----------
    complete : {0,1}
    sensorvars : {0,1}
        If 1, returns a struct for sensor_variables.
    **params
        https://docs.synopticdata.com/services/metadata
    """

    def __init__(self, **params):
        super().__init__("metadata", **params)

        df = pl.DataFrame(
            self.STATION,
            schema_overrides={
                "STID": pl.String,
                "STATUS": pl.String,
                "ID": pl.UInt32,
                "MNET_ID": pl.UInt32,
                "WIMS_ID": pl.UInt32,
            },
        )

        df = (
            df.with_columns(
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
                pl.col("ELEVATION", "LATITUDE", "LONGITUDE", "ELEV_DEM")
                .cast(pl.String)
                .str.strip_chars()
                .cast(pl.Float64),
                is_active=pl.when(pl.col("STATUS") == "ACTIVE")
                .then(True)
                .otherwise(pl.when(pl.col("STATUS") == "INACTIVE").then(False)),
            )
            .unnest("PERIOD_OF_RECORD")
            .drop("UNITS", "STATUS")
            .rename({"RESTRICTED": "is_restricted"})
        )

        df = df.rename({i: i.lower() for i in df.columns})
        self.df = df


class QCSegments(SynopticAPI):
    """Get quality control segments."""

    def __init__(self, **params):
        super().__init__("qcsegments", **params)
        raise NotImplementedError()


class QCTypes(SynopticAPI):
    """Get all QC types and names."""

    def __init__(self, **params):
        super().__init__("qctypes", **params)

        df = pl.DataFrame(self.QCTYPES).with_columns(
            pl.col("ID", "SOURCE_ID").cast(pl.UInt32)
        )
        df = df.rename({i: i.lower() for i in df.columns})
        self.df = df


class Variables(SynopticAPI):
    """Get all available variables.

    Provides variable name, variable index, long name, and default unit.
    """

    def __init__(self, **params):
        super().__init__("variables", **params)
        df = pl.concat(
            [
                pl.DataFrame(i)
                .transpose(header_name="variable", include_header=True)
                .unnest("column_0")
                for i in self.VARIABLES
            ]
        ).with_columns(pl.col("vid").cast(pl.UInt32))
        self.df = df


class Networks(SynopticAPI):
    """Get all available networks."""

    def __init__(self, **params):
        super().__init__("networks", **params)
        df = (
            pl.concat([pl.DataFrame(i) for i in self.MNET], how="diagonal_relaxed")
            .with_columns(
                pl.col("ID", "CATEGORY").cast(pl.UInt32),
                pl.col("LAST_OBSERVATION").str.to_datetime(),
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
            )
            .unnest("PERIOD_OF_RECORD")
        )

        df = df.rename({i: i.lower() for i in df.columns}).rename({"id": "mnet_id"})
        self.df = df


class NetworkTypes(SynopticAPI):
    """Get all available network types."""

    def __init__(self, **params):
        super().__init__("networktypes", **params)
        df = (
            pl.DataFrame(self.MNETCAT)
            .with_columns(
                pl.col("ID").cast(pl.UInt32),
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
            )
            .unnest("PERIOD_OF_RECORD")
        )
        df = df.rename({i: i.lower() for i in df.columns}).rename({"id": "mnetcat_id"})
        self.df = df
