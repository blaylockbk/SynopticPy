"""Synoptic Data to Polars DataFrame."""

import requests
import polars as pl
from datetime import datetime, timedelta
from typing import Literal, Optional

# Available API Services
# https://developers.synopticdata.com/mesonet/v2/
_stations = {"metadata", "timeseries", "precipitation", "nearesttime", "latest"}
_other = {"auth", "networks", "networktypes", "variables", "qctypes"}
_services = _stations | _other

ServiceType = Literal[
    "metadata",
    "timeseries",
    "precipitation",
    "nearesttime",
    "latest",
    "auth",
    "networks",
    "networktypes",
    "variables",
    "qctypes",
]


class SynopticAPI:
    """Request data from the Synoptic Data API.

    Parameters
    ----------
    service : str
        The Synoptic API service to use.
    **parms
        Synoptic API request arguments.
        Lists are converted to comma-separated strings.
        Datetime and timedelta are converted to strings.
    """

    def __init__(self, service: ServiceType, **params):
        self.service = service

        if self.service in _stations:
            self.endpoint = f"https://api.synopticdata.com/v2/stations/{service}"
        else:
            self.endpoint = f"https://api.synopticdata.com/v2/{service}"

        # ----------------
        # Parse parameters

        # Force all param keys to be lower case.
        params = {k.lower(): v for k, v in params.items()}

        for key, value in params.items():
            # Convert lists to comma-separated string.
            #   stid=['KSLC', 'KMRY'] --> stid='KSLC,KRMY'.
            #   radius=[40, -100, 10] --> radius='40,-100,10'
            if isinstance(value, list) and key not in ["obrange"]:
                params[key] = ",".join([str(i) for i in value])

            # TODO: Special case for 'obrange'

            # Convert datetime to string 'YYYYmmddHHMM'.
            elif key in {"start", "end", "expire", "attime"}:
                if isinstance(value, datetime):
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
        # Check returned data
        self.code = self.json["SUMMARY"]["RESPONSE_CODE"]
        self.message = self.json["SUMMARY"]["RESPONSE_MESSAGE"]

        if self.code != 1:
            # TODO: create a custom exception to print this message
            print("FATAL: Not a valid Synoptic API request.")
            print(f"  ├─ message: {self.message}")
            print(f"  └─ url: {self.response.url}")
            raise ValueError()

    def df(self):
        """Parse JSON data as Polars DataFrame."""
        df = pl.DataFrame(self.json["STATION"][0]["OBSERVATIONS"])
        # TODO: loop over each station
        #  - cast datetime column
        #  - attach metadata
        #  - concat all dfs together
        return df
