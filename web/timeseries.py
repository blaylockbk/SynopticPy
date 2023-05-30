from pyscript import Element
from pyodide.http import open_url
import js
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys

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
token = "d25c2abe02b94001a82e7790d9c30f06"
# ==================================================

# Rename "set_1" and "value_1" names is a convience I prefer.
## You can turn these off in your requests by setting `rename_set_1`
## and `rename_value_1` to False in your function call where applicable.
def _rename_set_1(df):
    """
    Rename Variable Columns Names

    Remove the 'set_1' and 'set_1d' from column names
    Sets 2+ will retain their full names.
    The user should refer to SENSOR_VARIABLES to see which
    variables are derived

    """

    ## Get list of current column names
    dummy_columns = list(df.columns)

    # Remove '_set_1' and '_set_1d' from column name
    var_names = [
        "_".join(v.split("_")[:-2]) if "_set_1" in v else v for v in dummy_columns
    ]

    # Number of observations in each column
    obs_count = list(df.count())

    # Sometimes, set_1 and set_1d are both returned. In that
    # case, we need to determin which column has the most
    # observations and use that as the main variable. The set
    # with fewer data will retain the 'set_1' or 'set_1d' label.
    renames = {}
    for i, name in enumerate(var_names):
        # Determine all indices this variable type is located
        var_bool = [v.startswith(name + "_set_1") for v in dummy_columns]
        var_idx = np.where(var_bool)[0]

        if len(var_idx) == 1:
            # This variable is only listed once. Rename with var_name
            renames[dummy_columns[i]] = var_names[var_idx[0]]
        elif len(var_idx) > 1:
            # This variable is listed more than once.
            # Determine which set has the most non-NaN data and
            # rename that column as var_name.
            max_idx = var_idx[np.argmax([obs_count[i] for i in var_idx])]
            if max_idx == i:
                # If the current iteration matches the var_idx with
                # the most data, rename the column without set number.
                renames[dummy_columns[i]] = var_names[max_idx]
            else:
                # If the current iteration does not match the var_idx
                # with the most data, then retain the original column
                # name with the set number.
                renames[dummy_columns[i]] = dummy_columns[i]
        else:
            # This case should only occur during my testing.
            renames[dummy_columns[i]] = dummy_columns[i]
    df.rename(columns=renames, inplace=True)
    df.attrs["RENAMED"] = renames
    return df


def main(display):
    # -------------------------------------------------------------------
    # Get and validate input values
    # -------------------------------------------------------------------
    stid = Element("stidInput").value.replace(" ", "").upper()
    try:
        duration = pd.to_timedelta(Element("durationInput").value)
    except:
        print(
            "⛔ ERROR: Duration could not be parsed by Pandas. Try something like '12min', '6H', '3D' instead."
        )
    if duration > pd.to_timedelta("356D"):
        duration = pd.to_timedelta("356D")
        print(
            "⚠️ WARNING: Requested too long of a dataset; setting duration to 366 days."
        )
    try:
        end = pd.to_datetime(Element("endTimeInput").value)
    except:
        print(
            "⛔ ERROR: End time could not be parsed by Pandas. Use the format 'YYYY-MM-DD HH:MM' instead."
        )
    start = end - duration
    variable = Element("variableSelector").value
    smooth_type = Element("smootherSelector1").value
    smooth_stat = Element("smootherSelector2").value
    try:
        smooth_time = pd.to_timedelta(Element("smootherInput").value)
    except:
        print(
            "⛔ ERROR: Duration could not be parsed by Pandas. Try something like '12min', '6H', '3D' instead."
        )

    for ele in js.document.getElementsByName("unitsRadioOptions"):
        if ele.checked:
            units = ele.value
            break

    for ele in js.document.getElementsByName("timezoneRadioOptions"):
        if ele.checked:
            obtimezone = ele.value
            break

    color_cycle = []
    for ele in js.document.getElementsByName("color"):
        color_cycle.append(ele.value)
        # Color cycle for plot lines

    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=color_cycle)
    # -------------------------------------------------------------------

    print("")
    # Write input values to page
    # print("User Input")
    # print(f" ├──{stid=}")
    # print(f" ├──{duration=}")
    # print(f" ├──{start=}")
    # print(f" ├──{end=}")
    # print(f" ├──{variable=}")
    # print(f" ├──{units=}")
    # print(f" ├──{obtimezone=}")
    # print(f" ├──{smooth_type=}")
    # print(f" ├──{smooth_stat=}")
    # print(f" └──{smooth_time=}")

    if "=" in stid:
        # User used the "backdoor" to specify a new station query
        # e.g. stid="radius=wbb,10&limit=5"
        custom_query = True
        url = f"https://api.synopticdata.com/v2/stations/timeseries?start={start:%Y%m%d%H%M}&end={end:%Y%m%d%H%M}&{stid}&vars={variable}&units={units}&obtimezone={obtimezone}&token={token}"
    else:
        # User requested a comma-separated list of station IDs
        custom_query = False
        url = f"https://api.synopticdata.com/v2/stations/timeseries?start={start:%Y%m%d%H%M}&end={end:%Y%m%d%H%M}&stid={stid}&vars={variable}&units={units}&obtimezone={obtimezone}&token={token}"

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

    rename_set_1 = True

    # Build a separate pandas.DataFrame for each station.
    Z = {}
    for stn in data["STATION"]:
        obs = stn.pop("OBSERVATIONS")
        senvars = stn.pop("SENSOR_VARIABLES")

        # Turn Data into a DataFrame
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

        if rename_set_1:
            df = _rename_set_1(df)

        # Drop Row if all data is NaN/None
        df.dropna(how="all", inplace=True)

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

        if len(df.columns) != len(set(df.columns)):
            warnings.warn("🤹🏼‍♂️ DataFrame contains duplicate column names.")

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

    if not custom_query:
        # Sort stations in order they were requested
        Z = {i: Z[i] for i in stid.split(",") if i in Z.keys()}

    fig, ax = plt.subplots()

    station_info = ""
    for STID, df in Z.items():
        try:
            if smooth_type == "rolling" and smooth_stat.lower() != "none":
                preserve_attrs = df.attrs
                print(f"Apply smoothing:{smooth_type=}; {smooth_stat=}; {smooth_time=}")
                df = getattr(df.rolling(smooth_time), smooth_stat)()
                df.attrs = preserve_attrs
            elif smooth_type == "resample" and smooth_stat.lower() != "none":
                print(f"Apply smoothing:{smooth_type=}; {smooth_stat=}; {smooth_time=}")
                df = getattr(df.resample(smooth_time, label="right"), smooth_stat)()

            ax.plot(
                df.index,
                df[variable],
                marker="o",
                markersize=3,
                linestyle="-",
                label=STID,
            )
            mesowest = f"""<a href="https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn={df.attrs['STID']}" target="_blank">MesoWest</a>"""
            station_info += f"<br><h3>{df.attrs['STID']} - {df.attrs['NAME']} {mesowest}</h3>{pd.DataFrame(pd.Series(df.attrs)).rename(columns={0:''}).to_html(classes='table table-striped table-sm')}<br>"
        except Exception as e:
            print(f"⛔ ERROR: {e}")

    Element("station-info").element.innerHTML = station_info

    var_label = variable.replace("_", " ").title()
    if var_label.lower() == "air temp":
        var_label = "Air Temperature"

    ax.text(
        1.0,
        0.0,
        f"{obtimezone.upper()} ",
        transform=ax.transAxes,
        va="bottom",
        ha="right",
    )
    ax.set_ylabel(f'{var_label} ({df.attrs.get("UNITS").get(variable)})')
    ax.set_title(var_label)

    ax.spines[["right", "top", "bottom"]].set_visible(False)
    ax.legend()
    ax.grid(color="w", linewidth=2, alpha=0.8)
    plt.tight_layout()
    display(fig, target="graph-area", append=False)
