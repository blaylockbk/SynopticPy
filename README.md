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

---

**Best of Luck 🍀**  
-Brian