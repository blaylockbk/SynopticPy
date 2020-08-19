**Brian Blaylock**

# ☁ Synoptic API for Python

These functions help access data from the Synoptic API (formerly MesoWest) and returns the JSON data as a **[Pandas DataFrame](https://pandas.pydata.org/docs/)**.

|🌐 Synoptic API Webpage|
|--
|https://developers.synopticdata.com

---

## 🐍 Conda Environment
I have provided an `envirnoment.yml` file that lists the minimum pckages requried (plus some extras that might be useful if you are working with weather data.)

If you have Anaconda installed, create this environment with 

    conda env create -f environment.yml
    
Then activate the `synoptic` environment with

    conda activate synoptic
    
If conda environments are new to you, I suggest you become familiar with [managing conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

## 📝 Jupyter Notebook Examples

The notebooks direcotry shows some practical examples of using these functions to get and show data.

## 👨🏻‍💻 `get_Synoptic.py` -- All the useful functions in one module

There is a separate function for each of the Synoptic services

1. `synoptic_api` - a generalized wrapper for making an API request and returns a requests object.
1. `stations_metadata` - Returns metadata (information) about stations. [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/metadata/)
1. `stations_timeseries` - Return data for a period of time [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/timeseries/)
1. `stations_nearesttime` - Return observation closest to the requested time [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/nearesttime/)
1. `stations_latest` - Return the most recent observations [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/latest/)
1. 🏗 `stations_precipitation` - Return precipitation data (with derived quantities) [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/precipitation/) 
1. 🏗 `stations_latency` - Latency information for a station [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/latency/)
1. 🏗 `stations_qcsegments` - Quality control for a period [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/qcsegments/)
1. `networks` - Return information about networks of stations [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/networks/)
1. `networktypes` - Return network category information [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/information/)
1. `variables` - Return available variables [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/variables/)
1. `qctypes` - Return quality control information [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/qctypes/)`
1. `auth` - Manage tokens (you are better off doing this in the browser in your [Synoptic profile](https://developers.synopticdata.com/settings/)) [Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/auth/)

## 🧭 Function Parameters
Function arguments are stiched together to create a web query. The parameters you can use depend on the API service. Synoptic's [API Explorer](https://developers.synopticdata.com/mesonet/explorer/) can help you determine what parameters can be used.

You should first become familiar with the [Station Selector arguments](https://developers.synopticdata.com/mesonet/v2/station-selectors/). These include keying in on specific stations or a set of stations within an area (`stid`, `radius`, `vars`, `state`, etc.).

One note about how my python functions work...all lists are joined together into a comma separated string. For instance, if you are requesting three stations, you could do `stid=['WBB', 'KSLC', 'KMRY']`, and that will be converted to a comma separated list `stid=WBB,KSLC,KMRY` requried for the API request URL. Also, any input that is a datetime object will be converted to a string required by the API (e.g., `start=datetime(2020,1,1)` will be converted to `start=YYYYmmddHHMM` when the querey is made.)

## ♻ Returned Data
The data retrieved from the Synoptic API is converted from JSON to a Pandas DataFrame. If you look at the raw JSON, you will see that the observation values are returned as "sets" and "values", (e.g., "air_temp_set_1", "pressure_set_1d", etc.). This is because some stations have more than one sensor for a variable (wind at more than one level) or is reported at more than one interval (ozone at 1 hr and 15 min intervals). I don't really like this, and it gets in my way. Almsot always, I want the set/value with the most data or the most recent observation. My functions by default will strip the "set_1" and "value_1" labels on the returned data. If there are more than one set or value, then the "set" and "value" labels will be retained if there are more than one.

- If a querey returns `air_temp_set_1` and `air_temp_set_2`, then the labels are renamed `air_temp` and `air_temp_set_2`.
- If a querey returns `pressure_set_1` and `pressure_set_1d`, then the labels are renames `pressure_set_1` and `pressure` if set_1d has more observations than set_1.

It makes sense to me, but if you are confused and don't trust what I'm doing, you can turn this "relabeling" off with `rename_set_1=False` and `rename_value_1=False` (for the appropriate function).

---

**Best of Luck 🍀**  
-Brian