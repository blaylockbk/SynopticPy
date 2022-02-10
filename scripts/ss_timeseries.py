#!/p/home/blaylock/anaconda3/envs/synoptic/bin/python

"""
========================
Multi-Station Timeseries
========================

Create a figure showing a timeseries of multiple weather stations.

Mimic the function of https://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/ts_multistations.cgi

Usage
-----

ss_timeseries.py ukbkb kslc kmry
ss_timeseries.py ukbkb kslc kmry --vars air_temp relative_humidity --units English --recent 1D
ss_timeseries.py psink psrim --var air_temp --recent 3D

"""

import argparse
from ast import parse
from email.policy import default
from pydoc import describe
import matplotlib.pyplot as plt
import pandas as pd

from synoptic.plots import plot_timeseries, plot_timeseries_wind


def parse_extra_arguments(extra_args):
    """
    Turn the list of extra arguments into a dictionary.

    For example, if

        extra_args = ['--units', 'English', '--vars', 'air_temp', 'wind_speed']

    turns those into

        {'units': 'English', 'vars': ['air_temp', 'wind_speed']}

    """
    extra = {}
    for i in extra_args:
        if i.startswith("--"):
            key = i.replace("--", "")
            extra[key] = None
        else:
            if extra[key] is None:
                extra[key] = i
            else:
                extra[key] = [extra[key]]
                extra[key].append(i)

    return extra


# =======================================================================
# CLI Arguments
# =======================================================================
description = """
Plot a station timeseries.

Examples:

    ss_timeseries.py ukbkb kslc kmry
    ss_timeseries.py ukbkb kslc kmry --vars air_temp relative_humidity --units English --recent 1D
    ss_timeseries.py psink psrim --var air_temp --recent 3D

    TODO: right now, you can't do a radius plot because the `stid` argument is hardcoded.
    TODO: let the extra --recent argument play more nicely with the --start and --end arguments. Default should be --recent 12H

"""
parser = argparse.ArgumentParser(description=description)

parser.add_argument(
    "stid",
    type=str,
    nargs="+",
    help="station IDs",
)
parser.add_argument(
    "--start",
    type=lambda x: pd.to_datetime(x),
    default=pd.Timestamp("now").ceil("1h") - pd.to_timedelta("12H"),
    help="Start datetime of the timeseries",
)
parser.add_argument(
    "--end",
    type=lambda x: pd.to_datetime(x),
    default=pd.Timestamp("now").ceil("1h"),
    help="End datetime of the timeseries",
)
parser.add_argument(
    "--vars",
    type=str,
    nargs="+",
    default="air_temp",
    help="List of variables to retrieve",
)
parser.add_argument("-v", "--verbose", action="store_true")


args, extra_args = parser.parse_known_args()
extra = parse_extra_arguments(extra_args)

if args.verbose:
    print(f"{args=}")
    print(f"{extra_args=}")
    print(f"{extra=}")

# (end arguments)
# =======================================================================


if __name__ == "__main__":
    plot_timeseries(**vars(args), **extra)

    plt.show()
