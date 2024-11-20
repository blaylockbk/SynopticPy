"""Get Synoptic Weather API data as a Polars DataFrame."""

import os
import re
import warnings
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Literal

import polars as pl
import requests
import toml

import synoptic.namespace  # noqa: E402, F401
from synoptic.json_parsers import (
    parse_stations_latency,
    parse_stations_latest_nearesttime,
    parse_stations_precipitation,
    parse_stations_timeseries,
)
from synoptic.token import ANSI, Token, configure
from synoptic.params import validate_params

# Initialize Token to get any environment or configured value
TOKEN = Token()
if TOKEN.token:
    TOKEN.is_valid()

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
    x : str, datetime, tuple
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
    """
    Request data from Synoptic's Weather API.

    This is the parent class for all other services.

    Parameters
    ----------
    service : {'timeseries', 'latest', 'nearesttime', 'precipitation', ...}
        The Synoptic API service to request data from. Refer to the
        Synoptic Weather Data API documentation for a full list of
        services: https://docs.synopticdata.com/services/weather-data-api
    token : str
        A 32-character Synoptic account token. If None, attempts to
        retrieve the token from the following sources (in order):

        1. Environment variable ``SYNOPTIC_TOKEN``,
        2. The ``token="..."`` value in ``~/.config/SynopticPy/config.toml``.
    verbose : bool
        If True, prints each step of the request process.
    **params : dict, optional
        Additional Synoptic API request parameters. Refer to the
        Synoptic Weather Data API documentation for expected and valid
        arguments for each service: https://docs.synopticdata.com/services/weather-data-api

        This class accepts the following extended input:

        - Where Synoptic expects comma-separated strings, you can instead provided a list or tuple (e.g., ``stid=['wbb', 'ukbkb']``, ``radius=('wbb', 20)``).
        - Datetime parameters like ``start`` and ``end`` can be a *datetime.datetime* or a string in the format ``YYYY-MM-DD HH:MM``.
        - Duration parameters like ``recent`` can be a *datetime.timedelta* or a duration string (e.g., ``'1d12h'``, ``30m``).
        - Parameters that accept ``0``, ``1``, ``on``, ``off`` can be given as boolean values.
    """

    def __init__(
        self,
        service: ServiceType,
        *,
        token: str | Token | None = None,
        verbose=True,
        **params,
    ):
        self.help_url = "https://docs.synopticdata.com/services/weather-data-api"
        self.verbose = verbose
        self.service = service

        # -------------
        # Get API token
        if token is None and TOKEN.token is not None:
            self.token = TOKEN
        elif isinstance(token, str):
            self.token = Token(token)
        elif isinstance(token, Token):
            self.token = token

        # ----------------
        # Parse parameters

        # Force all param keys to be lower case.
        params = {k.lower(): v for k, v in params.items()}
        params["token"] = self.token

        validate_params(self.service, **params)

        # Ignore request to change default 'timeformat' (always use ISO date)
        params.pop("timeformat", None)

        # Ignore request to change default 'output' (always return json)
        params.pop("output", None)

        # Ignore request to change default 'fields`' (always get all fields)
        params.pop("fields", None)

        # Ignore request to change 'obtimezone' (always return UTC)
        params.pop("obtimezone", None)

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
        if self.service in _services_stations:
            self.endpoint = f"https://api.synopticdata.com/v2/stations/{service}"
        else:
            self.endpoint = f"https://api.synopticdata.com/v2/{service}"

        if self.verbose:
            print(
                f"🚚💨 Speedy delivery from Synoptic's {ANSI.text(service, ANSI.GREEN)} service."
            )

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
        if hasattr(self, "QC_SUMMARY"):
            messages += (
                f"│ QC Checks: {len(self.QC_SUMMARY.get('QC_CHECKS_APPLIED'))}\n"
            )
        messages += "╰──────────────────────────────────────╯"
        return messages


class TimeSeries(SynopticAPI):
    """
    Get time series data for one or more stations.

    Refer to the official documentation: https://docs.synopticdata.com/services/time-series

    Parameters
    ----------
    start : datetime or str, optional
        The start time of the desired time range as a *datetime.datetime* or a string in the form ``'YYYYMMDDHHMM'`` or ``'YYYY-MM-DD HH:MM'``.
        Required if ``recent`` is not provided.
    end : datetime or str, optional
        The end time of the desired time range as a *datetime.datetime* or a string in the form ``'YYYYMMDDHHMM'`` or ``'YYYY-MM-DD HH:MM'``.
        Required if `recent` is not provided.
    recent : timedelta, int, or str, optional
        A *datetime.timedelta*, integer (representing minutes), or a duration string (e.g., `'3h'`) that specifies the period of data to retrieve prior to the current time.
        Required if ``start`` and ``end`` are not provided.
    **station_selection :
        Station selection parameters such as ``stid``, ``state``, ``county``, ``radius``, ``bbox``, ``vars``, ``varsoperator``, etc.
        Refer to the Synoptic API documentation for details.
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    **optional_parameters :
        Additional parameters such as `units`, `precip`, `qc`, etc.

    Notes
    -----
    - If `recent` is provided, `start` and `end` are not needed.
    - If `start` and `end` are provided, `recent` should not be used.
    """

    def __init__(self, **params):
        super().__init__("timeseries", **params)

    @lru_cache
    def df(self, with_latency=False) -> pl.DataFrame:
        """Stations timeseries DataFrame.

        Parameters
        ----------
        with_latency : bool
            If True, return data with latency column from the Latency service.
        """
        df = parse_stations_timeseries(self)

        if with_latency:
            latency = Latency(**self.params).df
            cols = [
                "date_time",
                "id",
                "stid",
                "name",
                "elevation",
                "latitude",
                "longitude",
            ]
            df = df.join(
                latency.select(cols + ["latency"]),
                on=cols,
                how="left",
            )
        return df


class Latest(SynopticAPI):
    """Get the most recent data from one or more stations.

    Refer to the official documentation: https://docs.synopticdata.com/services/latest

    Parameters
    ----------
    **station_selection :
        Station selection parameters such as ``stid``, ``state``, ``county``, ``radius``, ``bbox``, ``vars``, ``varsoperator``, etc.
        Refer to the Synoptic API documentation for details.
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    within : timedelta, int, optional
        Limit data to within a certain time window.
    minmax :
    minmaxtype :
    minmaxtimezone :
    **optional_parameters
        units, precip, qc, etc.
    """

    def __init__(self, **params):
        super().__init__("latest", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Stations latest DataFrame."""
        df = parse_stations_latest_nearesttime(self)
        return df


class NearestTime(SynopticAPI):
    """Get data nearest a specified time for one or more stations.

    Refer to the official documentation: https://docs.synopticdata.com/services/nearest-time

    Parameters
    ----------
    attime : datetime, YYYYMMDDHHMM
        If not given, will act like Latest request.
    within : timedelta, int, duration string
        Required if `atttime` is given.
    **station_selection :
        Station selection parameters such as ``stid``, ``state``, ``county``, ``radius``, ``bbox``, ``vars``, ``varsoperator``, etc.
        Refer to the Synoptic API documentation for details.
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    **optional_parameters
        units, precip, qc, etc.
    """

    def __init__(self, **params):
        super().__init__("nearesttime", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Stations nearest time DataFrame."""
        df = parse_stations_latest_nearesttime(self)
        return df


class Precipitation(SynopticAPI):
    """
    Request derived precipitation total or intervals.

    Refer to the official documentation: https://docs.synopticdata.com/services/precipitation

    Parameters
    ----------
    start : datetime or str, optional
        The start time of the desired time range as a *datetime.datetime* or a string in the form ``'YYYYMMDDHHMM'`` or ``'YYYY-MM-DD HH:MM'``.
        Required if ``recent`` is not provided.
    end : datetime or str, optional
        The end time of the desired time range as a *datetime.datetime* or a string in the form ``'YYYYMMDDHHMM'`` or ``'YYYY-MM-DD HH:MM'``.
        Required if `recent` is not provided.
    recent : timedelta, int, or str, optional
        A *datetime.timedelta*, integer (representing minutes), or a duration string (e.g., `'3h'`) that specifies the period of data to retrieve prior to the current time.
        Required if ``start`` and ``end`` are not provided.
    **station_selection :
        Station selection parameters such as ``stid``, ``state``, ``county``, ``radius``, ``bbox``, ``vars``, ``varsoperator``, etc.
        Refer to the Synoptic API documentation for details.
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    pmode : {'totals', 'intervals', 'last'}
        Precipitation mode. Default is *"totals"*.
    interval : int | {'hour', 'day', 'week', 'month', 'year'}
        Integer hours, or string interval. Default is *"day"*.
    interval_window : int
        Time window in hours
    **optional_parameters
        units, precip, qc, etc.
    """

    def __init__(self, **params):
        # Don't allow legacy precip service with pmode omitted.
        params.setdefault("pmode", "totals")

        super().__init__("precipitation", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Stations precipitation DataFrame."""
        df = parse_stations_precipitation(self)
        return df


class QCSegments(SynopticAPI):
    """Get quality control segments. NOT IMPLEMENTED.

    Refer to the official documentation: https://docs.synopticdata.com/services/quality-control-segments
    """

    def __init__(self, **params):
        super().__init__("qcsegments", **params)
        raise NotImplementedError()


class Latency(SynopticAPI):
    """
    Request station latency.

    Refer to the official documentation: https://docs.synopticdata.com/services/latency

    Parameters
    ----------
    start : datetime or str, optional
        The start time of the desired time range as a *datetime.datetime* or a string in the form ``'YYYYMMDDHHMM'`` or ``'YYYY-MM-DD HH:MM'``.
        Required if ``recent`` is not provided.
    end : datetime or str, optional
        The end time of the desired time range as a *datetime.datetime* or a string in the form ``'YYYYMMDDHHMM'`` or ``'YYYY-MM-DD HH:MM'``.
        Required if `recent` is not provided.
    **station_selection :
        Station selection parameters such as ``stid``, ``state``, ``county``, ``radius``, ``bbox``, ``vars``, ``varsoperator``, etc.
        Refer to the Synoptic API documentation for details.
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    stats : {'min', 'max', 'mean', 'median', 'count', 'stdev', 'all'}
    **optional_parameters
        units, precip, qc, etc.
    """

    def __init__(self, **params):
        super().__init__("latency", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Stations latency DataFrame."""
        df = parse_stations_latency(self)
        return df


class Metadata(SynopticAPI):
    """Retrieve metadata for one or more stations.

    Refer to the official documentation: https://docs.synopticdata.com/services/metadata

    Parameters
    ----------
    **station_selection :
        Station selection parameters such as ``stid``, ``state``, ``county``, ``radius``, ``bbox``, ``vars``, ``varsoperator``, etc.
        Refer to the Synoptic API documentation for details.
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    stats : {'min', 'max', 'mean', 'median', 'count', 'stdev', 'all'}
    complete : bool
    sensorvars : bool
    obrange : str, tuple
        Start and end datetime, as a tuple ``(datetime.datetime, datetime.datetime)`` or string ``YYMMDDHHMM,YYMMDDHHMM`
    """

    def __init__(self, **params):
        # `start` and `end` are not valid parameters, but `obrange` is.
        # This has confused users, such as https://github.com/blaylockbk/SynopticPy/issues/55.

        # Check if 'start' or 'end' is in the parameters
        if "start" in params or "end" in params:
            raise ValueError(
                "The Metadata service does not accept a 'start' or 'end' parameter; "
                "Rather, 'obrange' is the accepted parameter. "
                "Please change your query to use `obrange=(start_datetime, end_datetime)` or `obrange=start_datetime`.",
            )

        super().__init__("metadata", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Stations metadata DataFrame."""
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
        return df


class QCTypes(SynopticAPI):
    """Get all QC types and names.

    Refer to the official documentation: https://docs.synopticdata.com/services/quality-control-types

    Parameters
    ----------
    shortname :
    id :
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    """

    def __init__(self, **params):
        super().__init__("qctypes", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Quality control typres DataFrame."""
        df = pl.DataFrame(self.QCTYPES).with_columns(
            pl.col("ID", "SOURCE_ID").cast(pl.UInt32)
        )
        df = df.rename({i: i.lower() for i in df.columns})
        return df


class Variables(SynopticAPI):
    """
    Get all available variables.

    Provides variable name, variable index, long name, and default unit.

    Refer to the official documentation: https://docs.synopticdata.com/services/variables

    Parameters
    ----------
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    """

    def __init__(self, **params):
        super().__init__("variables", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Variables DataFrame."""
        df = pl.concat(
            [
                pl.DataFrame(i)
                .transpose(header_name="variable", include_header=True)
                .unnest("column_0")
                for i in self.VARIABLES
            ]
        ).with_columns(pl.col("vid").cast(pl.UInt32))
        return df


class Networks(SynopticAPI):
    """Get all available networks.

    Refer to the official documentation: https://docs.synopticdata.com/services/networks

    Parameters
    ----------
    id :
    shortname :
    sortby : {'alphabet'} (optional)
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    """

    def __init__(self, **params):
        super().__init__("networks", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Networks DataFrame."""
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
        return df


class NetworkTypes(SynopticAPI):
    """Get all available network types.

    Refer to the official documentation: https://docs.synopticdata.com/services/network-types

    Parameters
    ----------
    id :
    token : str, optional
        Synoptic API token. Required if the ``SYNOPTIC_TOKEN`` environment variable and the config file entry are not set.
    """

    def __init__(self, **params):
        super().__init__("networktypes", **params)

    @lru_cache
    def df(self) -> pl.DataFrame:
        """Network types DataFrame."""
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
        return df
