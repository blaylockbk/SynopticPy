import js
from pyscript import Element
import asyncio
from pyodide.http import pyfetch
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

print(f"imported matplotlib {mpl.__version__}")
print(f"imported pandas {pd.__version__}")
print(f"imported numpy {np.__version__}")

# Change default date formatter
plt.rcParams["date.autoformatter.day"] = "%b %d\n%H:%M"
plt.rcParams["date.autoformatter.hour"] = "%b %d\n%H:%M"

config = {
    "default": {
        "verbose": True,
        "hide_token": True,
        "rename_value_1": True,
        "rename_set_1": True,
        "token": "0bbe0e9fda7945a68951cc1bdebb2b0d",
    }
}

# Available API Services
# https://developers.synopticdata.com/mesonet/v2/
_service = {"auth", "networks", "networktypes", "variables", "qctypes"}
_stations = {"metadata", "timeseries", "precipitation", "nearesttime", "latest"}
_service.update(_stations)

# Station Selector Parameters Set
_stn_selector = {
    "stid",
    "country",
    "state",
    "country",
    "status",
    "nwszone",
    "nwsfirezone",
    "cwa",
    "gacc",
    "subgacc",
    "vars",
    "varsoperator",
    "network",
    "radius",
    "limit",
    "bbox",
    "fields",
}


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


async def request(
    url,
    method="GET",
    body=None,
    headers=None,
    **fetch_kwargs,
):
    """
    Async request function. Pass in Method and make sure to await!
    Parameters:
        url: str = URL to make request to
        method: str = {"GET", "POST", "PUT", "DELETE"} from `JavaScript` global fetch())
        body: str = body as json string. Example, body=json.dumps(my_dict)
        headers: dict[str, str] = header as dict, will be converted to string...
            Example, headers=json.dumps({"Content-Type": "application/json"})
        fetch_kwargs: Any = any other keyword arguments to pass to `pyfetch` (will be passed to `fetch`)
    Return:
        response: pyodide.http.FetchResponse = use with .status or await.json(), etc.
    """
    kwargs = {
        "method": method,
        "mode": "cors",
    }  # CORS: https://en.wikipedia.org/wiki/Cross-origin_resource_sharing
    if body and method not in ["GET", "HEAD"]:
        kwargs["body"] = body
    if headers:
        kwargs["headers"] = headers
    kwargs.update(fetch_kwargs)

    response = await pyfetch(url, **kwargs)
    return response

# Get input values
stid = Element("stidInput").value
duration = pd.to_timedelta(Element("durationInput").value)
end = pd.to_datetime(Element("endTimeInput").value)
start = end - duration
variable = Element("variableSelector").value
smooth_type = Element("smootherSelector1").value
smooth_stat = Element("smootherSelector2").value
smooth_time = Element("smootherInput").value
for ele in js.document.getElementsByName("unitsRadioOptions"):
    if ele.checked:
        units = ele.value
        break

# Write input values to page
display(f"{stid=}", target="display-write")
display(f"{duration=}", target="display-write")
display(f"{start=}", target="display-write")
display(f"{end=}", target="display-write")
display(f"{variable=}", target="display-write")
display(f"{units=}", target="display-write")
display(f"{smooth_type=}", target="display-write")
display(f"{smooth_stat=}", target="display-write")
display(f"{smooth_time=}", target="display-write")


token = "0bbe0e9fda7945a68951cc1bdebb2b0d"
url = f"https://api.synopticdata.com/v2/stations/timeseries?start={start:%Y%m%d%H%M}&end={end:%Y%m%d%H%M}&stid={stid}&vars={variable}&units={units}&token={token}"

print(f"Request URL: {url}")


async def main():
    headers = {"Content-type": "application/json"}
    response = await request(
        url,
        method="GET",
        # headers=headers,
    )
    print(f"GET request=> status:{response.status}")
    print(f"GET request=> json:{await response.json()}")


    rename_set_1 = True
    data = response.json()

    # Build a separate pandas.DataFrame for each station.
    Z = []
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
        #df.attrs["params"] = params
        df.attrs["service"] = "stations_timeseries"

        Z.append(df)


    fig, ax = plt.subplots(figsize=[10,6])
    for df in Z:
        plt.plot(df.index, df.air_temp, marker='o', markersize=3, linestyle='-', label=df.attrs['STID'])
    plt.ylabel('Temperature (F)')
    plt.title('Air Temperature')
    plt.legend()
    plt.grid(alpha=.2)
    plt.tight_layout()
    display(fig, target="graph-area", append=False)

asyncio.ensure_future(main())

