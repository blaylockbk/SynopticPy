from pyscript import Element
from pyodide.http import open_url
import js
import io
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


# from pathlib import Path
# print("Current Directory: ", Path("./").resolve())
# print("   Contents:", list(Path("./").resolve().glob("*")))
# print("Back one Directory: ", Path("../").resolve())
# print("   Contents:", list(Path("../").resolve().glob("*")))


for font in mpl.font_manager.findSystemFonts(["../assets/fonts"]):
    mpl.font_manager.fontManager.addfont(font)
plt.rcParams["font.sans-serif"] = ["Mona Sans", "Mona-Sans", "Hubot-Sans"]
mpl.rcParams["date.autoformatter.day"] = "%b %d\n%Y"
mpl.rcParams["date.autoformatter.hour"] = "%b %d\n%H:%M"
mpl.rcParams["figure.figsize"] = [10, 6]
mpl.rcParams["figure.dpi"] = 140
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


def plot_message(text, **kwargs):
    fig, ax = plt.subplots()

    # Add text in the middle of the axes
    ax.text(
        0.5,
        0.5,
        text,
        ha="center",
        va="center",
        wrap=True,
        fontsize=25,
        transform=ax.transAxes,
        **kwargs,
    )

    # Hide the axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    return fig, ax


def plot_station_on_map(df, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()

    point = float(df["start"].get("LONGITUDE")), float(df["start"].get("LATITUDE"))
    art = ax.scatter(*point, **kwargs)
    ax.text(
        *point,
        f"  {df['start'].get('STID')}",
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

    try:
        data = json.loads(open_url(url).read())
    except:
        print(f"⛔ ERROR: Could not get GeoJSON for {state=}")
        print(f"     └─ {url=}")
        return

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
            print(f"⚠️ WARNING: Trouble plotting polygon for {state=}.")


def draw_city_names(xlim, ylim, ax=None, **kwargs):
    """Add City Names to map from a list of world airports.

    US Cities from https://github.com/kelvins/US-Cities-Database
    """
    if ax is None:
        ax = plt.gca()

    try:
        df = pd.read_csv("../assets/data/us-cities.csv")
        df = df[(df["LATITUDE"].between(*ylim)) & (df["LONGITUDE"].between(*xlim))]
    except:
        print(f"⛔ ERROR: Could not get city names from file.")
        return

    if len(df) == 0:
        # print(f"⚠️ Warning: No nearby cities found.")
        return

    for i, row in df.iterrows():
        ax.text(
            row.LONGITUDE,
            row.LATITUDE,
            row.CITY,
            fontsize=35,
            fontweight="bold",
            va="center",
            ha="center",
            alpha=0.8,
            color="w",
            clip_on=True,
            zorder=2,
        )


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


def format_timedelta(td):
    """Function to convert timedelta to human-readable format"""
    minutes = td.total_seconds() // 60
    if minutes < 60:
        return f"{int(minutes)} minutes ago"
    hours = minutes // 60
    if hours < 24:
        return f"{int(hours)} hours ago"
    days = hours // 24
    return f"{int(days)} days ago"


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

    # Write input values to page
    if False:
        print("User Input")
        print(f" ├─{stid=}")
        print(f" ├─{units=}")
        print(f" └─{obtimezone=}")

    # ------------------------------------------------------------------
    # Request data via Synoptic API
    # ------------------------------------------------------------------
    base_url = "https://api.synopticdata.com/v2/stations/latest?"
    arguments = [
        f"{station_selector}",
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
        print(f"💥 FATAL: Could not load or read {url}")
        fig, ax = plot_message(
            "Error loading the JSON. Please report this issue and provide the full Synoptic API request URL from fatal output below.",
        )
        Element(
            "table-latest"
        ).element.innerHTML = "<br><br><h1>Error loading JSON</h1>"
        display(fig, target="figure-map", append=False)
        Element(
            "station-info"
        ).element.innerHTML = "<br><br><h1>Error loading JSON</h1>"
        return

    if data["SUMMARY"]["RESPONSE_MESSAGE"].upper() == "OK":
        status_symbol = "✅"
    else:
        status_symbol = "❌"

    print(
        f"{status_symbol} Response Message: {data['SUMMARY']['RESPONSE_MESSAGE']}. Received [{data['SUMMARY'].get('NUMBER_OF_OBJECTS')}] stations. Timer: {data['SUMMARY'].get('DATA_QUERY_TIME', 'n/a')}"
    )

    if data["SUMMARY"]["RESPONSE_MESSAGE"] != "OK":
        msg = data["SUMMARY"]["RESPONSE_MESSAGE"].replace(
            "Please contact support@synopticdata.com.", ""
        )
        fig, ax = plot_message(msg)
        Element(
            "table-latest"
        ).element.innerHTML = f'<br><br><h1>Error:<br>{msg}</h1><br> Problems with this URL <a href="{url}" target="_blank">{url}</a>. If you do not believe you are in error, please <a href="https://github.com/blaylockbk/SynopticPy/issues" target="_blank">report this</a>.'
        display(fig, target="figure-map", append=False)
        Element(
            "station-info"
        ).element.innerHTML = f'<br><br><h1>Error:<br>{msg}</h1><br> Problems with this URL <a href="{url}" target="_blank">{url}</a>. If you do not believe you are in error, please <a href="https://github.com/blaylockbk/SynopticPy/issues" target="_blank">report this</a>.'
        return

    # ------------------------------------------------------------------
    # Organize Station Data
    # ------------------------------------------------------------------
    # Build a separate pandas.DataFrame for each station.
    Z = {}
    for stn in data["STATION"]:
        obs = stn.pop("OBSERVATIONS")
        senvars = stn.pop("SENSOR_VARIABLES")

        metadata_table = pd.DataFrame(stn).T.sort_index()

        value_table = pd.DataFrame(obs).T.sort_index()
        value_table["unit"] = [
            data["UNITS"]["_".join(i.split("_")[:-2])] for i in value_table.index
        ]
        value_table["date_time"] = pd.to_datetime(value_table["date_time"])
        value_table["time_ago"] = (
            pd.Timestamp.utcnow() - value_table["date_time"]
        ).apply(format_timedelta)
        value_table = value_table[["value", "unit", "time_ago", "date_time"]]

        # Don't include data from "* days ago"
        value_table = value_table.loc[~value_table.time_ago.str.contains("days ago")]

        Z[stn["STID"]] = (metadata_table, value_table)

    # ------------------------------------------
    # Sort stations in order they were requested
    if station_order:
        Z = {i: Z[i] for i in station_order if i in Z.keys()}
    else:
        try:
            # Try to sort stations by DISTANCE
            Z = dict(sorted(Z.items(), key=lambda i: i[1].attrs.get("DISTANCE")))
        except:
            pass

    # ---------------------------
    # Join Network ID information
    # TODO:
    # network_ids = {df['start']["MNET_ID"] for stid, (df, _) in Z.items()}
    # network_df = get_network_info(network_ids)
    # for i in Z.values():
    #    id = i.attrs["MNET_ID"]
    #    i.attrs[
    #        "MNET_ID"
    #    ] = f"{id} - {network_df.loc[id].SHORTNAME} :: {network_df.loc[id].LONGNAME}"

    # ---------------------
    # Figures and Smoothing
    # ---------------------

    # ------------------------
    # Tab 1: Table Latest
    table_latest = ""
    for STID, (meta_df, value_df) in Z.items():
        table_latest += f"<br>"
        table_latest += (
            f"<h3>{meta_df['start']['STID']} - {meta_df['start']['NAME']}</h3>"
        )
        table_latest += f"{value_df.to_html(classes='table table-striped table-sm')}"
        table_latest += f"<br>"
    Element("table-latest").element.innerHTML = table_latest

    # -------------------------
    # Tab 2: Station Map Figure
    fig2, ax2 = plt.subplots()  # Map
    states = {df["start"].get("STATE") for _, (df, _) in Z.items()}
    for state in states:
        draw_state_polygon(
            state,
            facecolor=".9",
            edgecolor=".5",
            alpha=0.5,
            zorder=2,
        )

    for i, (station, (df, _)) in enumerate(Z.items()):
        plot_station_on_map(df, ax=ax2, zorder=1000 - i)

    ax2.grid(color="w", linewidth=2, alpha=0.8, zorder=1)

    # Map bounds
    # Use zoomed-in map boundary if max distance between stations is large.
    latitudes = [float(i["start"]["LATITUDE"]) for i, _ in Z.values()]
    longitudes = [float(i["start"]["LONGITUDE"]) for i, _ in Z.values()]
    points = zip(latitudes, longitudes)
    pairs = list(itertools.product(points, repeat=2))

    threshold = 2.5  # degree lat/lon before map zooms out to show full state
    pad = 0.08
    max_distance = max(list(map(lambda x: calculate_distance(*x[0], *x[1]), pairs)))
    xlim = (min(longitudes) - pad / 2, max(longitudes) + pad / 2)
    ylim = (min(latitudes) - pad, max(latitudes) + pad)

    if max_distance < threshold:
        plt.gca().set_xlim(*xlim)
        plt.gca().set_ylim(*ylim)
        draw_city_names(xlim, ylim, ax=ax2)

    fig2.tight_layout()
    display(fig2, target="figure-map", append=False)

    # ---------------------------------
    # Tab 3: Station Information Tables
    station_info = ""
    for STID, (meta_df, value_df) in Z.items():
        mesowest = f"""<a href="https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn={meta_df['start']['STID']}" target="_blank">MesoWest</a>"""
        station_info += f"<br>"
        station_info += f"<h3>{meta_df['start']['STID']} - {meta_df['start']['NAME']} {mesowest}</h3>"
        station_info += f"{meta_df.to_html(classes='table table-striped table-sm')}"
        station_info += f"<br>"
    Element("station-info").element.innerHTML = station_info

    print("🏁 Finished!\n")
