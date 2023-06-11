from pyscript import Element
from pyodide.http import open_url
import js
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import sys

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


# ==================================================
# If you using this page as a template,
# PLEASE use your own token. You can
# create a *free* Synoptic account and
# Mesonet API token here:
# https://developers.synopticdata.com/mesonet/
brian_token = "d25c2abe02b94001a82e7790d9c30f06"
# ==================================================


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


def calculate_distance(lat1, lon1, lat2, lon2):
    # Calculate the difference in degrees between two lat/lon points
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

def draw_state_polygon(ax, state, **kwargs):
    data = json.loads(
        open_url(
            f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/USA/{state}.geo.json"
        ).read()
    )

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


def main(display):
    # -------------------------------------------------------------------
    # Get and validate input values
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
    smooth_type = Element("smootherSelector1").value
    smooth_time_str = Element("smootherInput").value
    smooth_stat = Element("smootherSelector2").value
    if smooth_type:
        try:
            smooth_time = pd.to_timedelta(smooth_time_str)
        except:
            print("⛔ ERROR: Smoother duration could not be parsed by Pandas.")
            print("    └ Input a timedelta string like '12min', '6H', '3D' instead.")

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
    # print("User Input")
    # print(f" ├──{stid=}")
    # print(f" ├──{startTime=} {startDuration=} {start=}")
    # print(f" ├──{endTime=} {endDuration=} {end=}")
    # print(f" ├──{variable=}")
    # print(f" ├──{units=}")
    # print(f" ├──{obtimezone=}")
    # print(f" ├──{smooth_type=}")
    # print(f" ├──{smooth_stat=}")
    # print(f" └──{smooth_time=}")

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

    if user_token:
        print(f"Request URL: {url}")
    else:
        print(f"Request URL: {url.replace(token,'*****')}")

    try:
        data = json.loads(open_url(url).read())
    except:
        print(f"💥 FATAL: Could not read {url}")

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

        # Sort Column order alphabetically
        df = df.reindex(columns=df.columns.sort_values())

        # Break wind into U and V components, if speed and direction are available
        if all(["wind_speed" in senvars, "wind_direction" in senvars]):
            for i_spd, i_dir in zip(
                senvars["wind_speed"].keys(), senvars["wind_direction"].keys()
            ):
                u, v = spddir_to_uv(obs[i_spd], obs[i_dir])
                this_set = "_".join(i_spd.split("_")[-2:])
                df[f"wind_u_{this_set}"] = u
                df[f"wind_v_{this_set}"] = v
                data["UNITS"]["wind_u"] = data["UNITS"]["wind_speed"]
                data["UNITS"]["wind_v"] = data["UNITS"]["wind_speed"]

        # In the DataFrame attributes, Convert some strings to float/int
        # (i.e., ELEVATION, latitude, longitude) BUT NOT STID!
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

        # Rename lat/lon to lowercase to match CF convenctions
        df.attrs["latitude"] = df.attrs.pop("LATITUDE")
        df.attrs["longitude"] = df.attrs.pop("LONGITUDE")

        # Include other info
        for i in data.keys():
            if i != "STATION":
                df.attrs[i] = data[i]
        df.attrs["SENSOR_VARIABLES"] = senvars
        # df.attrs["params"] = params
        df.attrs["service"] = "stations_timeseries"

        Z[df.attrs["STID"]] = df

    if station_order:
        # Sort stations in order they were requested
        Z = {i: Z[i] for i in station_order if i in Z.keys()}

    fig, ax = plt.subplots()  # Timeseries
    fig2, ax2 = plt.subplots()  # Map

    states_added = []
    station_info = ""
    for STID, df in Z.items():
        try:
            if smooth_type == "rolling" and smooth_stat.lower() != "none":
                preserve_attrs = df.attrs
                print(f"Apply smoothing:{smooth_type=}; {smooth_stat=}; {smooth_time=}")
                df = getattr(df.rolling(smooth_time), smooth_stat)()
                df.attrs = preserve_attrs
            elif smooth_type == "resample" and smooth_stat.lower() != "none":
                preserve_attrs = df.attrs
                print(f"Apply smoothing:{smooth_type=}; {smooth_stat=}; {smooth_time=}")
                df = getattr(df.resample(smooth_time, label="right"), smooth_stat)()
                df.attrs = preserve_attrs

            alphas = np.linspace(1, 0.3, len(df.columns))
            for alpha, column in zip(alphas, sorted(df.columns)):
                set_derived = column.split("_")[-1]
                label = STID
                if set_derived[0] != "1":
                    # indicate this is the nth dataset
                    label += "$^{" + set_derived[0] + "}$"
                if set_derived.endswith("d"):
                    # indicate this is a derived value
                    label += "$^{*}$"

                if column.startswith("wind_direction"):
                    ax.scatter(
                        df.index,
                        df[column],
                        marker="o",
                        s=3,
                        label=label,
                        alpha=alpha,
                    )
                else:
                    ax.plot(
                        df.index,
                        df[column],
                        marker="o",
                        markersize=3,
                        linestyle="-",
                        label=label,
                        alpha=alpha,
                    )
            mesowest = f"""<a href="https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn={df.attrs['STID']}" target="_blank">MesoWest</a>"""
            station_info += f"<br><h3>{df.attrs['STID']} - {df.attrs['NAME']} {mesowest}</h3>{pd.DataFrame(pd.Series(df.attrs)).rename(columns={0:''}).to_html(classes='table table-striped table-sm')}<br>"
        except Exception as e:
            print(f"⛔ ERROR: Timeseries figure >> {e}")

        # Create a map of station locations
        try:
            ax2.grid(color="w", linewidth=2, alpha=0.8, zorder=1)
            try:
                state = df.attrs.get("STATE")
                if state not in states_added:
                    states_added.append(state)

                    draw_state_polygon(
                        ax=ax2,
                        state=state,
                        facecolor=".9",
                        edgecolor=".5",
                        alpha=0.5,
                        zorder=2,
                    )
            except:
                print(
                    f"⚠️ WARNING: Map figure >> Could not plot {state} state boundary."
                )
            point = df.attrs.get("longitude"), df.attrs.get("latitude")
            art = ax2.scatter(*point, zorder=3)
            ax2.text(
                *point,
                f"  {df.attrs.get('STID')}",
                color=art.get_facecolor()[-1],
                ha="left",
                va="center",
                zorder=4,
            )
        except Exception as e:
            print(f"⛔ ERROR: Map figure >> {e}")

    Element("station-info").element.innerHTML = station_info

    var_label = variable.replace("_", " ").title()
    if var_label.lower() == "air temp":
        var_label = "Air Temperature"

    # ----------
    # Map bounds
    # Use zoomed-in map boundary if max distance between stations is large.
    latitudes = [i.attrs["latitude"] for i in Z.values()]
    longitudes = [i.attrs["longitude"] for i in Z.values()]
    points = zip(latitudes, longitudes)
    pairs = list(itertools.product(points, repeat=2))

    threshold = 1.5
    pad = 0.05
    max_distance = max(list(map(lambda x: calculate_distance(*x[0], *x[1]), pairs)))
    xlim = (min(longitudes) - pad / 2, max(longitudes) + pad / 2)
    ylim = (min(latitudes) - pad, max(latitudes) + pad)

    if max_distance < threshold:
        ax2.set_xlim(*xlim)
        ax2.set_ylim(*ylim)

    # -------------------------------
    # Label indicating timezone units
    ax.text(
        1.0,
        0.0,
        f"{obtimezone.upper()} ",
        transform=ax.transAxes,
        va="bottom",
        ha="right",
    )

    # ----------------------------------
    # Label indicating smoothing options
    if smooth_type != "none":
        ax.set_title(
            f"{smooth_time_str} {smooth_type.title()} {smooth_stat.upper()}",
            loc="right",
            fontsize=8,
        )

    # ---------
    # Cosmetics
    ax.set_ylabel(f'{var_label} ({df.attrs.get("UNITS").get(variable)})')
    ax.set_title(var_label)

    if variable == "wind_direction":
        ticks, labels = wind_degree_labels()
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels)

    ax.spines[["right", "top", "bottom"]].set_visible(False)
    ax.legend()
    ax.grid(color="w", linewidth=2, alpha=0.8)
    ax2.set_xlabel("Longitude")
    ax2.set_ylabel("Latitude")
    ax2.xaxis.set_major_formatter(
        mpl.ticker.ScalarFormatter(useOffset=False, useMathText=False)
    )
    ax2.xaxis.get_major_formatter().set_scientific(False)
    ax2.xaxis.get_major_formatter().set_useOffset(False)
    ax2.xaxis.get_major_formatter().set_useMathText(False)
    ax2.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.2f"))
    ax2.yaxis.set_major_formatter(
        mpl.ticker.ScalarFormatter(useOffset=False, useMathText=False)
    )
    ax2.yaxis.get_major_formatter().set_scientific(False)
    ax2.yaxis.get_major_formatter().set_useOffset(False)
    ax2.yaxis.get_major_formatter().set_useMathText(False)
    ax2.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.2f"))
    fig.tight_layout()
    fig2.tight_layout()
    display(fig, target="figure-timeseries", append=False)
    display(fig2, target="figure-map", append=False)
    print("🏁 Finished!\n")
