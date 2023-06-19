from pyscript import Element
from pyodide.http import open_url
import js
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats
import itertools
import sys
import re

from matplotlib.patches import Polygon

print(f"Python version:", sys.version)
print(f"imported matplotlib {mpl.__version__}")
print(f"imported pandas {pd.__version__}")
print(f"imported numpy {np.__version__}")

mpl.rcParams["date.autoformatter.day"] = "%b %d\n%Y"
mpl.rcParams["date.autoformatter.hour"] = "%b %d\n%H:%M"
mpl.rcParams["figure.figsize"] = [10, 6]
mpl.rcParams["axes.labelsize"] = "large"
mpl.rcParams["xtick.labelsize"] = "medium"
mpl.rcParams["ytick.labelsize"] = "medium"
mpl.rcParams["axes.titlesize"] = "xx-large"
mpl.rcParams["axes.facecolor"] = ".95"
mpl.rcParams["axes.spines.left"] = False
mpl.rcParams["axes.spines.bottom"] = False
mpl.rcParams["axes.spines.top"] = False
mpl.rcParams["axes.spines.right"] = False
mpl.rcParams["xtick.major.size"] = 0
mpl.rcParams["xtick.minor.size"] = 0
mpl.rcParams["ytick.major.size"] = 0
mpl.rcParams["ytick.minor.size"] = 0


# ╔════════════════════════════════════════════════════════════════════╗
# ║   If you using this page as a template PLEASE use your own token.  ║
# ╠════════════════════════════════════════════════════════════════════╣
# ║You can create a *free* Synoptic account and Mesonet API token here:║
# ║          https://developers.synopticdata.com/mesonet/              ║
# ╚════════════════════════════════════════════════════════════════════╝
brian_token = "d25c2abe02b94001a82e7790d9c30f06"

precip_vars = [
    "precip_accum",
    "precip_accum_one_minute",
    "precip_accum_ten_minute",
    "precip_accum_fifteen_minute",
    "precip_accum_30_minute",
    "precip_accum_one_hour",
    "precip_accum_three_hour",
    "precip_storm",
    "precip_accum_six_hour",
    "precip_accum_24_hour",
    "precip_smoothed",
    "precip_manual",
    "precip_accum_manual",
    "precip_accum_5_minute_manual",
    "precip_accum_10_minute_manual",
    "precip_accum_15_minute_manual",
    "precip_accum_3_hour_manual",
    "precip_accum_6_hour_manual",
    "precip_accum_24_hour_manual",
    "precip_accum_12_hour",
    "precip_accum_five_minute",
    "precip_accum_since_00utc",
    "precip_accum_since_7_local",
    "precip_accum_since_local_midnight",
    "precip_interval",
]


def spddir_to_uv(wspd, wdir, round=3):
    """Compute u and v wind components from wind speed and direction.

    https://earthscience.stackexchange.com/a/11989/18840

    NOTE: You could use MetPy; but dealing with units is slow.

    NOTE: Watch for components near zero caused by limitation of float precision of sin(180)

    Parameters
    ----------
    wspd, wdir : array_like
        Arrays of wind speed and wind direction (in degrees)

    Returns
    -------
    u and v wind components
    """
    if isinstance(wspd, list) or isinstance(wdir, list):
        wspd = np.array(wspd)
        wdir = np.array(wdir)

    wdir = np.deg2rad(wdir)

    u = -wspd * np.sin(wdir)
    v = -wspd * np.cos(wdir)

    if round:
        u = u.round(round)
        v = v.round(round)

    return u, v


def wind_degree_labels(res="m"):
    """Wind degree increment and direction labels

    This is useful for labeling a matplotlib wind direction axis ticks.

    .. code-block:: python

        plt.yticks(*wind_degree_labels())

    .. code-block:: python

        ticks, labels = wind_degree_labels()
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels)

    ..image:: https://rechneronline.de/geo-coordinates/wind-rose.png

    Parameters
    ----------
    res : {'l', 'm', 'h'} or {90, 45, 22.5}
        Low, medium, and high increment resolution.
        - l : returns 4 cardinal directions [N, E, S, W, N]
        - m : returns 8 cardinal directions [N, NE, E, SE, ...]
        - h : returns 16 cardinal directions [N, NNE, NE, ENE, E, ...]
    """
    labels = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N",
    ]
    degrees = np.arange(0, 361, 22.5)

    if res in ["l", 90]:
        return degrees[::4], labels[::4]
    elif res in ["m", 45]:
        return degrees[::2], labels[::2]
    elif res in ["h", 22.5]:
        return degrees, labels


def plot_standard(df, only_plot_set_1=True, *, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    if only_plot_set_1:
        df = df.filter(regex="set_1")

    if "precip_intervals_set_1d" in df.columns:
        df = df.drop("precip_intervals_set_1d", axis=1)

    for column in sorted(df.columns):
        variable = re.sub(r"_set_\d+d?", "", column)
        units = df.attrs.get("UNITS").get(variable)

        if variable == "air_temp":
            variable = "air temperature"
        elif variable == "precip_accumulated":
            variable = "Accumulated Precipitation"

        var_label = variable.replace("_", " ").title()

        # Set type will be an integer (starting at 1) and my end in "d"
        # to indicate it is a "derived" value.
        set_type = column.split("_")[-1]
        label = df.attrs["STID"]
        if set_type[0] != "1":
            # indicate this is the nth dataset
            label += "$^{" + set_type[0] + "}$"
        if set_type.endswith("d"):
            # indicate this is a derived value
            label += "$^{*}$"

        if variable == "wind_direction":
            ax.scatter(df.index, df[column], marker="o", s=3, label=label, **kwargs)
            ticks, labels = wind_degree_labels()
            ax.set_yticks(ticks)
            ax.set_yticklabels(labels)
        else:
            ax.plot(
                df.index,
                df[column],
                marker="o",
                markersize=3,
                linestyle="-",
                label=label,
                **kwargs,
            )

        # Cosmetics (labels, etc.)
        ax.set_ylabel(f"{var_label} ({units})")
        ax.set_title(var_label)

    return ax


def plot_spread_bars(df, ax=None, **kwargs):
    """Special case when smooth.method = 'spread'"""
    if ax is None:
        ax = plt.gca()

    # Specify the column to plot (only first set)
    set = 0
    column = sorted(df.columns)[set][0]
    variable = re.sub(r"_set_\d+d?", "", column)
    units = df.attrs.get("UNITS").get(variable)
    if variable == "air_temp":
        variable = "air temperature"
    var_label = variable.replace("_", " ").title()

    # Set type will be an integer (starting at 1) and my end in "d"
    # to indicate it is a "derived" value.
    set_type = column.split("_")[-1]
    label = df.attrs["STID"]
    if set_type[0] != "1":
        # indicate this is the nth dataset
        label += "$^{" + set_type[0] + "}$"
    if set_type.endswith("d"):
        # indicate this is a derived value
        label += "$^{*}$"

    # Bar Min -> Median
    art = ax.bar(
        df.index,
        df[column]["median"] - df[column]["min"],
        pd.to_timedelta(df.index.freq),
        df[column]["min"],
        edgecolor="w",
        alpha=0.6,
        label=label,
        **kwargs,
    )

    # Bar Median -> Max
    ax.bar(
        df.index,
        df[column]["max"] - df[column]["median"],
        pd.to_timedelta(df.index.freq),
        df[column]["median"],
        edgecolor="w",
        color=art.patches[0].get_facecolor(),
        alpha=0.6,
        **kwargs,
    )

    # Point Mean
    ax.scatter(
        df.index, df[column]["mean"], marker="d", s=5, color="w", alpha=0.5, **kwargs
    )

    # Cosmetics (labels)
    ax.set_ylabel(f"{var_label} ({units})")
    ax.set_title(var_label)

    if variable == "wind_direction":
        ticks, labels = wind_degree_labels()
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels)

    return ax


def plot_station_on_map(df, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    point = df.attrs.get("LONGITUDE"), df.attrs.get("LATITUDE")
    art = ax.scatter(*point, **kwargs)
    ax.text(
        *point,
        f"  {df.attrs.get('STID')}",
        color=art.get_facecolor()[-1],
        ha="left",
        va="center",
        zorder=art.get_zorder(),
    )

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.xaxis.set_major_formatter(
        mpl.ticker.ScalarFormatter(useOffset=False, useMathText=False)
    )
    ax.xaxis.get_major_formatter().set_scientific(False)
    ax.xaxis.get_major_formatter().set_useOffset(False)
    ax.xaxis.get_major_formatter().set_useMathText(False)
    ax.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_formatter(
        mpl.ticker.ScalarFormatter(useOffset=False, useMathText=False)
    )
    ax.yaxis.get_major_formatter().set_scientific(False)
    ax.yaxis.get_major_formatter().set_useOffset(False)
    ax.yaxis.get_major_formatter().set_useMathText(False)
    ax.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.2f"))


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the difference in degrees between two lat/lon points"""
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # Calculate differences between latitudes and longitudes
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Calculate the square of half the chord length between the points
    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2
    )

    # Calculate the angular distance in radians
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    # Calculate the distance in degrees
    distance_deg = np.degrees(c)

    return distance_deg


def draw_state_polygon(state, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    url = f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/{state}.geo.json"

    data = json.loads(open_url(url).read())

    for feature in data["features"]:
        if feature["geometry"]["type"] == "Polygon":
            for coordinates in feature["geometry"]["coordinates"]:
                polygon = Polygon(coordinates, closed=True, **kwargs)
                ax.add_patch(polygon)
        elif feature["geometry"]["type"] == "MultiPolygon":
            for coordinates in feature["geometry"]["coordinates"]:
                for i in coordinates:
                    polygon = Polygon(i, closed=True, **kwargs)
                    ax.add_patch(polygon)
        else:
            print("⚠️ WARNING: Trouble plotting state polygon.")


def get_network_info(id=None):
    if id:
        id = f"id={','.join([str(i) for i in id])}&"
    else:
        id = ""

    url = f"https://api.synopticdata.com/v2/networks?{id}token=d25c2abe02b94001a82e7790d9c30f06"
    data = json.loads(open_url(url).read())

    df = pd.DataFrame(data["MNET"]).set_index("ID")
    df.index = df.index.astype(int)
    return df


class Smoother:
    """An object to hold smoothing parameters and do smoothing.

    Usage
    -----
    Presently, you must explicitly set the smoothing params after instantiation.
    >>> smooth = Smoother()
    >>> smooth.method = "rolling"
    >>> smooth.interval = "3H"
    >>> smooth.stat = "mean"
    >>> df2 = smooth.smooth_dataframe(df)
    """

    def __init__(self):
        self._method = None
        self._interval = None
        self._interval_str = None
        self._stat = None

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        methods = {"rolling", "resample", None}
        if isinstance(value, str):
            value = value.lower()
        if value == "none":
            value = None
            self._interval = None
            self._interval_str = None
            self._stat = None
        if value in methods:
            self._method = value
        else:
            print("⛔ ERROR: Smoother method must be one of the following:")
            print(f"    └ {methods}")
            raise ValueError(
                f"Invalid value for 'method'. Allowed values are one of {methods}."
            )

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self.interval_str = value
        try:
            value = pd.to_timedelta(value)
        except (ValueError, TypeError):
            print(f"⛔ ERROR: Smoother interval {value} could not be parsed by Pandas.")
            print(f"    └ Input a timedelta string like '12min', '6H', '3D' instead.")
            raise ValueError(
                "Invalid value for 'interval'. Must be a Pandas-parsable timedelta."
            )
        self._interval = value

    @property
    def stat(self):
        return self._stat

    @stat.setter
    def stat(self, value):
        stats = {"mean", "max", "min", "median", "std", "var", "count", "spread"}
        if value == "none":
            value = None
        elif value not in stats:
            print(
                f"⚠️ WARNING: Smoother stat {value} is not in the list of expected values."
            )
            print(f"    └ {stats}")
        self._stat = value

    def __repr__(self) -> str:
        return f"Smoother: {self.method=} {self.interval=} {self._interval_str=} {self.stat=}"

    @property
    def label(self):
        return f"{self.interval_str} {self.method.title()} {self.stat.upper()}"

    def smooth_dataframe_circular(self, df):
        """Compute wind direction circular statistics; i.e. circular mean"""
        preserve_attrs = df.attrs
        if self.method is None:
            print(f"⚠️ WARNING: No smoothing performed. {self.method=}.")
        elif self.stat.lower() == "spread":
            raise NotImplementedError(
                "Spread statistics not available for wind direction"
            )
        else:
            df = df.pipe(np.deg2rad)
            statDict = {
                "mean": scipy.stats.circmean,
                "var": scipy.stats.circvar,
                "std": scipy.stats.circstd,
                "std": scipy.stats.circstd,
                "max": np.max,
                "min": np.min,
                "median": np.median,
                "count": "NOT IMPLEMENTED",
            }
            if self.method == "rolling":
                df = df.rolling(self.interval).agg(
                    statDict[self.stat], nan_policy="omit"
                )
            elif self.method == "resample":
                df = df.resample(self.interval).agg(
                    statDict[self.stat], nan_policy="omit"
                )
            df = df.pipe(np.rad2deg)

        df.attrs = preserve_attrs
        return df

    def smooth_dataframe(self, df):
        """Smooth a Pandas Dataframe according to the smoothing parameters. Index must be a datetime."""
        preserve_attrs = df.attrs
        if self.method is None:
            print(f"⚠️ WARNING: No smoothing performed. {self.method=}.")
        elif self.stat.lower() == "spread":
            # "spread" is a special case
            if self.method == "resample":
                df = df.resample(self.interval).agg(["max", "min", "median", "mean"])
            elif self.method == "rolling":
                df = df.rolling(self.interval).agg(["max", "min", "median", "mean"])
        else:
            if self.method == "rolling":
                df = df.rolling(self.interval).agg(self.stat)
            elif self.method == "resample":
                df = df.resample(self.interval).agg(self.stat)
        df.attrs = preserve_attrs
        return df


def main(display):
    # -------------------------------------------------------------------
    # Parse and validate input values
    # -------------------------------------------------------------------

    # Parse token
    token = Element("tokenInput").value
    if token == "":
        token = brian_token
        user_token = False
    else:
        user_token = True

    # Parse station selector
    stid = Element("stidInput").value.replace(" ", "")
    if "=" in stid:
        # User used the "backdoor" for advanced station query
        # e.g. radius=wbb,10&limit=5
        station_selector = stid
        station_order = None
    else:
        # User requested a comma-separated list of station IDs
        # e.g. WBB,UKBKB,KMRY
        station_selector = f"stid={stid.upper()}"
        station_order = stid.upper().split(",")

    # Parse variable
    variable = Element("variableSelector").value
    if variable == "precip":
        variable = f"{','.join(precip_vars)}&precip=1"

    # Parse start and end date
    startTime = Element("startTimeInput").value
    endTime = Element("endTimeInput").value

    try:
        startTime = pd.to_datetime(startTime)
        startDuration = None
    except:
        try:
            startDuration = pd.to_timedelta(startTime)
            startTime = None
        except:
            print("⛔ ERROR: Start time could not be parsed by Pandas.")
            print("          Try a datetime like 'YYYY-MM-DD HH:MM' or")
            print("          a timedelta string like '12min', '6H', '3D'.")

    try:
        endTime = pd.to_datetime(endTime)
        endDuration = None
    except:
        try:
            endDuration = pd.to_timedelta(endTime)
            endTime = None
        except:
            print("⛔ ERROR: End time could not be parsed by Pandas.")
            print("    ├ Try a datetime like 'YYYY-MM-DD HH:MM' or")
            print("    └ a timedelta string like '12min', '6H', '3D'.")

    if startDuration and endTime:
        start = endTime - startDuration
        end = endTime
    elif startTime and endDuration:
        start = startTime
        end = startTime + endDuration
    elif startTime and endTime:
        start = startTime
        end = endTime
    else:
        print("💥 FATAL: Error with start and end input.")

    if start > end:
        print(f"⛔ ERROR: Start time must be before end time. {start=}, {end=}")
    if (end - start) > pd.to_timedelta("356D"):
        start = end - pd.to_timedelta("356D")
        print("⚠️ WARNING: Requested too long a timeseries.")
        print("    └ Only returning last 366 days requested.")

    # Parse smoother options
    smooth = Smoother()
    smooth.method = Element("smootherSelector1").value
    if smooth.method:
        smooth.interval = Element("smootherInput").value
        smooth.stat = Element("smootherSelector2").value

    smooth.method = Element("smootherSelector1").value
    smooth.interval = Element("smootherInput").value
    smooth.stat = Element("smootherSelector2").value

    # Parse units
    for ele in js.document.getElementsByName("unitsRadioOptions"):
        if ele.checked:
            units = ele.value
            break

    # Parse timezone
    for ele in js.document.getElementsByName("timezoneRadioOptions"):
        if ele.checked:
            obtimezone = ele.value
            break

    # Parse colors
    color_cycle = []
    for ele in js.document.getElementsByName("color"):
        color_cycle.append(ele.value)
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=color_cycle)

    # Write input values to page
    if False:
        print("User Input")
        print(f" ├─{stid=}")
        print(f" ├─{startTime=} {startDuration=} {start=}")
        print(f" ├─{endTime=} {endDuration=} {end=}")
        print(f" ├─{variable=}")
        print(f" ├─{units=}")
        print(f" ├─{obtimezone=}")
        print(f" ├─{smooth.method=}")
        print(f" ├─{smooth.interval=}")
        print(f" ├─{smooth.interval_str=}")
        print(f" └─{smooth.stat=}")

    # ------------------------------------------------------------------
    # Request data via Synoptic API
    # ------------------------------------------------------------------
    base_url = "https://api.synopticdata.com/v2/stations/timeseries?"
    arguments = [
        f"start={start:%Y%m%d%H%M}",
        f"end={end:%Y%m%d%H%M}",
        f"{station_selector}",
        f"vars={variable}",
        f"units={units}",
        f"obtimezone={obtimezone}",
        f"token={token}",
    ]
    url = base_url + "&".join(arguments)
    url_hidden = url.replace(token, "*****")

    # ----------------------
    # Hyperlink to JSON data
    if user_token:
        print(f"Request URL: {url}")
        Element(
            "json-download"
        ).element.innerHTML = f"<i class='fa-solid fa-download'></i> <a href='{url}' target='_blank' title='Raw JSON: supply your own API token'>JSON</a>"
    else:
        print(f"Request URL: {url_hidden}")
        Element(
            "json-download"
        ).element.innerHTML = f"<i class='fa-solid fa-download'></i> <a href='{url_hidden}' target='_blank' title='Raw JSON: supply your own API token'>JSON</a>"

    # --------------
    # Read JSON data
    try:
        data = json.loads(open_url(url).read())
    except:
        print(f"💥 FATAL: Could not load {url}")

    if data["SUMMARY"]["RESPONSE_MESSAGE"].upper() == "OK":
        status_symbol = "✅"
    else:
        status_symbol = "❌"
    print(
        f"{status_symbol} Response Message: {data['SUMMARY']['RESPONSE_MESSAGE']}. Received [{data['SUMMARY'].get('NUMBER_OF_OBJECTS')}] stations. Timer: {data['SUMMARY'].get('DATA_QUERY_TIME', 'n/a')}"
    )

    # ------------------------------------------------------------------
    # Organize Station Data
    # ------------------------------------------------------------------
    # Build a separate pandas.DataFrame for each station.
    Z = {}
    for stn in data["STATION"]:
        obs = stn.pop("OBSERVATIONS")
        senvars = stn.pop("SENSOR_VARIABLES")

        # Turn station observations into a DataFrame
        df = pd.DataFrame(obs).set_index("date_time")

        # Remaining data in dict will be returned as attribute
        df.attrs = stn

        # Convert datetime index string to datetime
        df.index = pd.to_datetime(df.index)

        # Sort column order alphabetically
        df = df.reindex(columns=df.columns.sort_values())

        # Break wind into U and V components, if speed and direction are available
        if "wind_speed" in senvars and "wind_direction" in senvars:
            for i_spd, i_dir in zip(
                senvars["wind_speed"].keys(), senvars["wind_direction"].keys()
            ):
                u, v = spddir_to_uv(obs[i_spd], obs[i_dir])
                df[i_spd.replace("wind_speed", "wind_u")] = u
                df[i_spd.replace("wind_speed", "wind_v")] = v
                data["UNITS"]["wind_u"] = data["UNITS"]["wind_speed"]
                data["UNITS"]["wind_v"] = data["UNITS"]["wind_speed"]

        # In the DataFrame attributes, Convert some strings to float/int
        # (i.e., ELEVATION, latitude, longitude) BUT NOT STID
        # because some STIDs could be all numeric characters.
        for k, v in df.attrs.items():
            if isinstance(v, str) and k not in ["STID"]:
                try:
                    n = float(v)
                    if n.is_integer():
                        df.attrs[k] = int(n)
                    else:
                        df.attrs[k] = n
                except:
                    pass

        # Include other info
        for i in data.keys():
            if i != "STATION":
                df.attrs[i] = data[i]
        df.attrs["SENSOR_VARIABLES"] = senvars
        df.attrs["service"] = "stations_timeseries"
        df.attrs = dict(sorted(df.attrs.items()))

        # Insert dataframe in Z dictionary
        Z[df.attrs["STID"]] = df

    # ------------------------------------------
    # Sort stations in order they were requested
    if station_order:
        Z = {i: Z[i] for i in station_order if i in Z.keys()}

    # ---------------------------
    # Join Network ID information
    network_ids = {i.attrs["MNET_ID"] for i in Z.values()}
    network_df = get_network_info(network_ids)
    for i in Z.values():
        id = i.attrs["MNET_ID"]
        i.attrs[
            "MNET_ID"
        ] = f"{id} - {network_df.loc[id].SHORTNAME} :: {network_df.loc[id].LONGNAME}"

    # ---------------------
    # Figures and Smoothing
    # ---------------------

    # ------------------------
    # Tab 1: Timeseries Figure
    fig, ax = plt.subplots()
    for i, (station, df) in enumerate(Z.items()):
        if smooth.method:
            if variable == "wind_direction":
                df = smooth.smooth_dataframe_circular(df)
            else:
                df = smooth.smooth_dataframe(df)

        if smooth.method and smooth.stat == "spread":
            df.pipe(plot_spread_bars, ax=ax, zorder=1000 - i)
        else:
            df.pipe(plot_standard, False, ax=ax, zorder=1000 - i)

    # Label indicating timezone units
    ax.text(
        1.0,
        0.0,
        f"{obtimezone.upper()} ",
        transform=ax.transAxes,
        va="bottom",
        ha="right",
    )

    # Label indicating smoothing options
    if smooth.method:
        ax.set_title(
            smooth.label,
            loc="right",
            fontsize=8,
        )

    # Cosmetics
    ax.legend()
    ax.grid(color="w", linewidth=2, alpha=0.8, zorder=1)

    fig.tight_layout()
    display(fig, target="figure-timeseries", append=False)

    # -------------------------
    # Tab 2: Station Map Figure
    fig2, ax2 = plt.subplots()  # Map
    states = {df.attrs.get("STATE") for _, df in Z.items()}
    for state in states:
        draw_state_polygon(
            state,
            facecolor=".9",
            edgecolor=".5",
            alpha=0.5,
            zorder=2,
        )

    for i, (station, df) in enumerate(Z.items()):
        plot_station_on_map(df, ax=ax2, zorder=1000 - i)

    ax2.grid(color="w", linewidth=2, alpha=0.8, zorder=1)

    # Map bounds
    # Use zoomed-in map boundary if max distance between stations is large.
    latitudes = [i.attrs["LATITUDE"] for i in Z.values()]
    longitudes = [i.attrs["LONGITUDE"] for i in Z.values()]
    points = zip(latitudes, longitudes)
    pairs = list(itertools.product(points, repeat=2))

    threshold = 0.5
    pad = 0.08
    max_distance = max(list(map(lambda x: calculate_distance(*x[0], *x[1]), pairs)))
    xlim = (min(longitudes) - pad / 2, max(longitudes) + pad / 2)
    ylim = (min(latitudes) - pad, max(latitudes) + pad)

    if max_distance < threshold:
        plt.gca().set_xlim(*xlim)
        plt.gca().set_ylim(*ylim)

    fig2.tight_layout()
    display(fig2, target="figure-map", append=False)

    # ---------------------------------
    # Tab 3: Station Information Tables
    station_info = ""
    for STID, df in Z.items():
        mesowest = f"""<a href="https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn={df.attrs['STID']}" target="_blank">MesoWest</a>"""
        station_info += f"<br>"
        station_info += f"<h3>{df.attrs['STID']} - {df.attrs['NAME']} {mesowest}</h3>"
        station_info += f"{pd.DataFrame(pd.Series(df.attrs)).rename(columns={0:''}).to_html(classes='table table-striped table-sm')}"
        station_info += f"<br>"
    Element("station-info").element.innerHTML = station_info

    print("🏁 Finished!\n")
