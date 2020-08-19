**Brian Blaylock**  
🌐 [Webpage](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/home.html)

# ☁ Synoptic API for Python (_unofficial_)

![](./images/synoptic_logo.png)

The [Synoptic Mesonet API](https://synopticdata.com/mesonet-api) (formerly MesoWest) gives you access to real-time and historical surface-based weather observations for thousands of stations.

I wrote these functions to quickly access data from the Synoptic API  and convert the JSON data to a **[Pandas DataFrame](https://pandas.pydata.org/docs/)**. Maybe this will be helpful to others who are getting started with the Synoptic API and Python. The idea is loosely based on the obsolete [MesoPy](https://github.com/mesowx/MesoPy) python wrapper, but converting the data to a Pandas DataFrame instead of a simple dictionary makes the data more *ready-to-use*.

|🌐 Synoptic API Webpage|
|--
|https://developers.synopticdata.com


---

## 🐍 Conda Environment
I have provided an `environment.yml` file that lists the minimum packages required (plus some extras that might be useful if you are working with weather data).

If you have Anaconda installed, create this environment with 

    conda env create -f environment.yml
    
Then activate the `synoptic` environment with

    conda activate synoptic
    
If conda environments are new to you, I suggest you become familiar with [managing conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

## 📝 Jupyter Notebook Examples

The [notebooks directory](https://github.com/blaylockbk/Synoptic_API/tree/master/notebooks) contains some practical examples of using these functions to get and show data.

## 👨🏻‍💻 `get_Synoptic.py` -- All the useful functions in one module

To use my functions, make sure the `get_Synoptic.py` file is in your working directory or PYTHONPATH.

```python
from get_Synoptic import function_name
```

There is a separate function for each of the Synoptic services.

1. `synoptic_api` - A generalized wrapper for making an API request and returns a `requests` object. You *could* access the raw JSON from this object, but the other functions will convert that JSON to a Pandas DataFrame. Generally, you won't use this function directly.
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
Function arguments are stitched together to create a web query. The parameters you can use to filter the data depend on the API service. Synoptic's [API Explorer](https://developers.synopticdata.com/mesonet/explorer/) can help you determine what parameters can be used for each service.

If this is new to you, I recommend you become familiar with the [Station Selector arguments](https://developers.synopticdata.com/mesonet/v2/station-selectors/) first. These include keying in on specific stations or a set of stations within an area of interest(`stid`, `radius`, `vars`, `state`, etc.).

**One note about how my python functions work...** All lists are joined together into a comma separated string. For instance, if you are requesting three stations, you could do `stid=['WBB', 'KSLC', 'KMRY']`, and that will be converted to a comma separated list `stid='WBB,KSLC,KMRY'` required for the API request URL. Also, any input that is a datetime object (any datetime that can be parsed with f-string, `f'{DATE:%Y%m%d%H%M}'`) will be converted to a string required by the API (e.g., `start=datetime(2020,1,1)` will be converted to `start='YYYYmmddHHMM'` when the query is made.)

## ♻ Returned Data
The data retrieved from the Synoptic API is converted from JSON to a Pandas DataFrame. 

If you look at the raw JSON returned, you will see that the observation values are returned as "sets" and "values", (e.g., `air_temp_set_1`, `pressure_set_1d`, etc.). This is because some stations have more than one sensor for a variable (wind at more than one level) or is reported at more than one interval (ozone at 1 hr and 15 min intervals). Time series requests return "sets" and nearest time requests return "values".


I don't really like dealing with the set labels. Almost always, I want the **set**/**value** with the most data or the most recent observation. My functions, by default, will strip the `set_1` and `value_1` from the labels on the returned data. If there are more than one set or value, then the "set" and "value" labels will be retained for those extra sets.

- If a query returns `air_temp_set_1` and `air_temp_set_2`, then the labels are renamed `air_temp` and `air_temp_set_2`.
- If a query returns `pressure_set_1` and `pressure_set_1d`, then the labels are renamed `pressure_set_1` and `pressure` _if **set_1d** has more observations than **set_1**_.
- If a query returns `dew_point_temperature_value_1` at 00:00 UTC and `dew_point_temperature_value_1d` at 00:15 UTC are both returned, then the labels are renamed `dew_point_temperature_value_1` and `dew_point_temperature` because the derived quantity is the most recent observation available.

In short, all sets and values are always returned, but column labels are simplified for the columns that I am most likely looking to use. 

For the renamed columns, it is up to the user to know if the data is a derived quantity and which set/value it is. To find out, look for attributes "SENSOR_VARIABLES" and "RENAME" in the DataFrame attributes, or look at the raw JSON.

This makes sense to me, but if you are confused and don't trust what I'm doing, you can turn this "relabeling" off with `rename_set_1=False` and `rename_value_1=False` (for the appropriate function).

---

**Best of Luck 🍀**  
-Brian