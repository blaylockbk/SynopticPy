
|![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/master/images/Balloon_logo/balloon_bkb_sm.png)|**Brian Blaylock**<br>🌐 [Webpage](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/home.html)<br> 🎉This is my first PyPI package|
|:--|:--|

## ☁ Synoptic API for Python (_unofficial_)

![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/master/images/synoptic_logo.png)

The [Synoptic Mesonet API](https://synopticdata.com/mesonet-api) (formerly MesoWest) gives you access to real-time and historical surface-based weather and environmental observations for thousands of stations. Synoptic is _free_ up to 5,000 API requests and 5 million service units each month. That's a generous amount, but if you need even more data, a [paid tier](https://synopticdata.com/pricing) is available (through Synoptic, not me).

> #### 🌐 Register for a free account at the Synoptic API Webpage
>> https://developers.synopticdata.com
>
> You will need to obtain an API token before using this python package.

I wrote these functions to conveniently access data from the Synoptic API and convert the JSON data to a **[Pandas DataFrame](https://pandas.pydata.org/docs/)**. This may be helpful to others who are getting started with the Synoptic API and Python. The idea is loosely based on the obsolete [MesoPy](https://github.com/mesowx/MesoPy) python wrapper, but returning the data as a Pandas DataFrame instead of a simple dictionary, making the retrieved data more *ready-to-use*.

#### Contributing Guidelines (and disclaimer)
Since this package is a work in progress, it is distributed "as is." I do not make any guarantee it will work for you out of the box. In fact, this is my first experience publishing a package to PyPI. Any revisions I make are purely for my benefit. Sorry if I break something, but I usually only push updates to GitHub if the code is in a reasonably functional state (at least, in the way I use it).

With that said, I am happy to share this project with you. You are welcome to open issues and submit pull requests, but know that I may or may not get around to doing anything about it. If this is helpful to you in any way, I'm glad.

---

## 🐍 Installation and Conda Environment
#### Option 1: pip
Install the last published version from PyPI. This requires the following are already installed:  
`numpy`, `pandas`, `requests`. It's optional, but you will want `matplotlib`, and `cartopy`, too.

```bash
pip install SynopticPy
```

#### Option 2: conda
If conda environments are new to you, I suggest you become familiar with [managing conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

I have provided a sample Anaconda [environment.yml](https://github.com/blaylockbk/SynopticPy/blob/master/environment.yml) file that lists the minimum packages required plus some extras that might be useful when working with other types of weather data. Look at the bottom lines of that yaml file...there are two ways to install SynopticPy with pip. Comment out the lines you don't want.

For the latest development code:
```yaml
- pip:
    - git+https://github.com/blaylockbk/SynopticPy.git
```
For the latest published version
```yaml
- pip:
    - SynopticPy
```

First, create the virtual environment with 

```bash
conda env create -f environment.yml
```

Then, activate the `synoptic` environment. Don't confuse this _environment_ name with the _package_ name.

```bash
conda activate synoptic
```

Occasionally, you might want to update all the packages in the environment.

```bash
conda env update -f environment.yml
```

> #### Alternative "Install" Method
> There are several other ways to "install" a python package so you can import them. One alternatively is you can `git clone https://github.com/blaylockbk/SynopticPy.git` this repository to any directory. To import the package, you will need to update your PYTHONPATH environment variable to find the directory you put this package or add the line `sys.path.append("/path/to/SynotpicPy")` at the top of your python script.

## 🔨 Setup

Before you can retrieve data from the Synoptic API, **you need to register as a Synoptic user and obtain a _token_**. Follow the instructions at the [Getting Started Page](https://developers.synopticdata.com/mesonet/v2/getting-started/). When you have a token, edit `synoptic/config.cfg` with your personal API **token**, _not your API key_.  The config file should look should look something like this:
    
```
[Synoptic]
token = 1234567890abcdefg
```

If you don't do this step, don't worry. When you import `synoptic.services`,
a quick check will make sure the token in the config file is valid. If not,
you will be prompted to update the token in the config file.

### 📝 Jupyter Notebook Examples

I have provided a number of [notebooks](https://github.com/blaylockbk/SynopticPy/tree/master/notebooks) on GitHub that contain some practical examples for importing and using these functions to get and show station data.

---
---

## `synoptic/`

### ⚙ `config.cfg`
A configuration file with your Synoptic API token. This token is required to make any data request from the Synoptic API.

### 🎟 `get_token.py`
This function performs a test on the token in the `config.cfg` file. If the token is valid, you are good to go. If not, then you will be prompted to edit the `config.cfg` file when you import any function from `synoptic.services`.

### 👨🏻‍💻 `services.py`
This is the main module you will interacti with. It contains functions for making API requests and returns the data as a Pandas DataFrame.

```python
# Import all functions
import synoptic.services as ss
```
or
```python
# Import a single function (prefered)
from synotpic.services import stations_timeseries
```

#### Available Functions
There is a separate function for each of the Synoptic Mesonet API services as described in the [Synotpic documentation](https://developers.synopticdata.com/mesonet/v2/).

1. `synoptic_api` - A generalized wrapper for making an API request and returns a `requests` object. You *could* access the raw JSON from this object, but the other functions will convert that JSON to a Pandas DataFrame. Generally, you won't use this function directly. The primary role of this function is to format parameter arguments to a string the request URL needs to retrieve data.
    - Converts datetime input to a string 
        - `datetime(2020,1,1)` >>> `"202001010000"`
    - Converts timedelta input to a string
        - `timedelta(hours=1)` >>> `"60"`
    - Converts lists (station IDs and variable names) to comma separated strings
        - `["WBB", "KSLC"]` >>> `"WBB,KSLC"`
        - `["air_temp", "wind_speed"]` >>> `"air_temp,wind_speed"`
1. `stations_metadata` - Returns metadata (information) about stations. [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/metadata/)
1. `stations_timeseries` - Return data for a period of time. [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/timeseries/)
1. `stations_nearesttime` - Return observation closest to the requested time. [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/nearesttime/)

1. `stations_latest` - Return the most recent observations [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/latest/)
1. 🏗 `stations_precipitation` - Return precipitation data (with derived quantities) [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/precipitation/) 
1. `networks` - Return information about networks of stations [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/networks/)
1. `networktypes` - Return network category information [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/information/)
1. `variables` - Return available variables [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/variables/)
1. `qctypes` - Return quality control information [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/qctypes/)`
1. `auth` - Manage tokens (you are better off doing this in the browser in your [Synoptic profile](https://developers.synopticdata.com/settings/)) [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/auth/)

1. ~~🏗 `stations_latency` - Latency information for a station [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/latency/)~~
1. ~~🏗 `stations_qcsegments` - Quality control for a period [Synoptic Docs 🔗](https://developers.synopticdata.com/mesonet/v2/stations/qcsegments/)~~

---
---

### 🧭 Function Parameters
Function arguments are stitched together to create a web query. The parameters you can use to filter the data depend on the API service. Synoptic's [API Explorer](https://developers.synopticdata.com/mesonet/explorer/) can help you determine what parameters can be used for each service.

If the Synoptic API is new to you, I recommend you become familiar with the [Station Selector arguments](https://developers.synopticdata.com/mesonet/v2/station-selectors/) first. These parameters key in on specific stations or a set of stations within an area of interest (`stid`, `radius`, `vars`, `state`, etc.).

### 🤹🏻‍♂️ Examples
Some things you should know first:
1. All lists are joined together into a comma separated string. For instance, if you are requesting three stations, you could do `stid=['WBB', 'KSLC', 'KMRY']`, and that will be converted to a comma separated list `stid='WBB,KSLC,KMRY'` required for the API request URL. 
1. Any input that is a datetime object (any datetime that can be parsed with f-string, `f'{DATE:%Y%m%d%H%M}'`) will be converted to a string required by the API (e.g., `start=datetime(2020,1,1)` will be converted to `start='YYYYmmddHHMM'` when the query is made.) 
1. For services that requires the `within` or `recent` arguments, these must be given in minutes. You may give integers for those arguments, but converting time to minutes is done automatically if you input a datetime.timedelta or a pandas datetime. For example, if you set `within=timedelta(hours=1)` or `recent=pd.to_timedelta('1d')`, the function will convert the value to minutes for you.

> #### ❓ What if I don't know a station's ID?
> MesoWest is your friend if you don't know what stations are available or what they are named: https://mesowest.utah.edu/.

To get a time series of air temperature and wind speed for the last 10 hours for the William Browning Building (WBB) you can do...

```python
from datetime import timedelta
from synotpic.services import stations_timeseries

df = stations_timeseries(stid='WBB', 
                        vars=['air_temp', 'wind_speed'],
                        recent=timedelta(hours=10))
```
![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/master/images/timeseries_df.png)

To get the latest air temperature and wind speed data for WBB (University of Utah) and KRMY (Monterey, CA airport) within one hour, we can also set the minutes as an integer instead as a timedelta.

```python
from synotpic.services import stations_latest

df = stations_latest(stid=['WBB', 'KMRY'],
                    vars=['air_temp', 'wind_speed'],
                    within=60)
```
![](./images/latest_df.png)

> Note: Parameters may be given as a list/datetime/timedelta, or as a string/integer interpreted by the Synoptic API. Thus, 
> ```python 
> stations_latest(stid='WBB,KMRY',
>                 vars='air_temp,wind_speed',
>                 within=60)
> ```
> is equivalent to the above example.

To get the air temperature and wind speed for WBB and KMRY nearest 00:00 UTC Jan 1, 2020 within one hour...

```python
from datetime import datetime
from synotpic.services import stations_nearesttime

df = stations_latest(stid=['WBB', 'KMRY'], 
                    vars=['air_temp', 'wind_speed'],
                    attime=datetime(2020,1,1),
                    within=60)
```
![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/master/images/nearesttime_df.png)

> Note: the string/integer alternative to the above example is
> ```python
> stations_nearesttime(stid='WBB,KMRY',
>                      vars='air_temp,wind_speed',
>                      attime='2020010100',
>                      within=60)
>```
> Use whichever is more convenient for you. I often use both methods. It depends on what I am doing.


### ♻ Returned Data: Variable Names
The raw data retrieved from the Synoptic API is converted from JSON to a Pandas DataFrame. 

If you look at the raw JSON returned, you will see that the observation values are returned as "sets" and "values", (e.g., `air_temp_set_1`, `pressure_set_1d`, `wind_speed_value_1`, etc.). This is because some stations have more than one sensor for a variable (e.g., wind at more than one level at a single site) or is reported at more than one interval (e.g., ozone at 1 hr and 15 min intervals). Time series requests return "sets" and nearest time requests return "values".

I don't really like dealing with the set and value labels. Almost always, I want the **set** or **value** with the _most_ data or the _most recent_ observation. **My functions, by default, will strip the `set_1` and `value_1` from the labels on the returned data. If there are more than one set or value, however, then the "set" and "value" labels will be retained for those extra sets.**

- If a query returns `air_temp_set_1` and `air_temp_set_2`, then the labels are renamed `air_temp` and `air_temp_set_2`.
- If a query returns `pressure_set_1` and `pressure_set_1d`, then the labels are renamed `pressure_set_1` and `pressure` _if **set_1d** has more observations than **set_1**_.
- If a query returns `dew_point_temperature_value_1` at 00:00 UTC and `dew_point_temperature_value_1d` at 00:15 UTC are both returned, then the labels are renamed `dew_point_temperature_value_1` and `dew_point_temperature` because the derived quantity is the most recent observation available.

In short, all sets and values are always returned, but column labels are simplified for the columns that I am most likely to use. 

For the renamed columns, it is up to the user to know if the data is a derived quantity and which set/value it is. To find out, look for attributes "SENSOR_VARIABLES" and "RENAME" in the DataFrame attributes (`df.attrs`), or look at the raw JSON.

Doing this makes sense to me, but if you are confused and don't trust what I'm doing, you can turn this "relabeling" off with `rename_set_1=False` and `rename_value_1=False` (for the appropriate function).

### 🌐 Latitude and Longitude
I should mention, `LATITUDE` and `LONGITUDE` in the raw JSON is renamed to `latitude` and `longitude` (lowercase) to match [CF convention](http://cfconventions.org/).

### 💨 U and V Wind Components
If the returned data contains variables for both `wind_speed` and `wind_direction`, then the DataFrame will compute and return the U and V wind components as `wind_u` and `wind_v`.

### ⏲ Timezone
The default timezone the data is returned is in UTC time. You may change the time to local time with the parameter `obtimezone=local`. Pandas will return the data with a timezone-aware index. However, I found that matplotlib plotting functions convert this time back to UTC. To plot by local time, you need to use the `tz_localize(None)` method to make it unaware of timezone and plot local time correctly. For example, compare the two plots created with the following:

```python
import matplotlib.pyplot as plt
from synoptic.services import stations_timeseries

df = stations_timeseries(stid='KSLC',
                        recent=1000,
                        obtimezone='local',
                        vars='air_temp')

plt.plot(df.index, df.air_temp, label='tz aware (plots in UTC)')
plt.plot(df.index.tz_localize(None), df.air_temp, label='tz unaware (as local time)')
plt.legend()
```
![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/master//images/tz_localize.png)

### ✅ How to set Synoptic's quality control checks
By default, only basic QC range checks are applied to the data before it is returned by the API. These basic checks remove physically implausible data like removing a 300 degree temperature instead of returning the value. 

You can add additional QC checks that more stringently remove "bad" data that might not be representative of the area or caused by a faulty sensor. However, you can't expect every bad observation will be removed (or every good observation will be retained).

- [Read about the QC checks](https://developers.synopticdata.com/about/qc/)
- [Read the QC section for a stations service (e.g., timeseries)](https://developers.synopticdata.com/mesonet/v2/stations/timeseries/)

Some tips:

- You can turn on more QC checks by Synoptic with the parameter `qc_checks='synopticlabs'`
- You can turn all QC checks on (includes synopiclab, mesowest, and madis checks) with the parameter `qc_checks='all'`.
- You can see the number of data point removed in the QC summary in the DataFrame attributes `df.attrs['QC_SUMMARY']`.
- Specific checks can be turned on (read the docs for more details).

For example:

```python
df = stations_timeseries(stid='UKBKB', recent=60, qc_checks='synopticlabs')
```
or
```python
df = stations_timeseries(stid='UKBKB', recent=60, qc_checks='all')
```

Look at the QC_SUMMARY in the DataFrame attributes to see some info about
what each QC check means and how many are flagged...
```python
df.attrs['QC_SUMMARY']
>>>{'QC_SHORTNAMES': {'18': 'ma_stat_cons_check', '16': 'ma_temp_cons_check'},
    'QC_CHECKS_APPLIED': ['all'],
    'PERCENT_OF_TOTAL_OBSERVATIONS_FLAGGED': 2.03,
    'QC_SOURCENAMES': {'18': 'MADIS', '16': 'MADIS'},
    'TOTAL_OBSERVATIONS_FLAGGED': 750.0,
    'QC_NAMES': {'18': 'MADIS Spatial Consistency Check', '16': 'MADIS Temporal Consistency Check'}}
```

You might be able to find a better way to mask out those QC'ed values, but here is one method for the QC check for *wind_speed_set_1*:

```python
# Identify which ones "passed" the QC checks (these have None in the QC array)
qc_mask = np.array([x is None for x in df.attrs['QC']['wind_speed_set_1']])
df = df.loc[qc_mask]
```

### 📈 `plots.py`
#### ***These are a work in progress***
Some helpers for plotting data from the Synoptic API. 

```python
# Import all functions
import synoptic.plots as sp
```
or
```python
# Import individual functions
from synoptic.plots import plot_timeseries
```

---

If you have stumbled across this package, I hope it is useful to you or at least gives you some ideas.

**Best of Luck 🍀**  
-Brian
