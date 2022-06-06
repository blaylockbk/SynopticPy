# 🤹🏻‍♂️ Usage Examples

## Import Functions

There is a separate function for each of the Synoptic Mesonet API services as described in the [Synoptic documentation](https://developers.synopticdata.com/mesonet/v2/).

Import all the functions with

```python
import synoptic.services as ss
```

or import a specific function like

```python
from synoptic.services import stations_timeseries
```

## 📝 Jupyter Notebook Examples

I have provided a number of [notebooks on GitHub](https://github.com/blaylockbk/SynopticPy/tree/main/notebooks) that contain some practical examples for importing and using these functions to get and show station data.

[![Binder](https://binder.pangeo.io/badge_logo.svg)](https://binder.pangeo.io/v2/gh/blaylockbk/SynopticPy/master)

## 🧭 Function Parameters
Function arguments are stitched together to create a web query. The parameters you can use to filter the data depend on the API service. Synoptic's [API Explorer](https://developers.synopticdata.com/mesonet/explorer/) can help you determine what parameters can be used for each service.

If the Synoptic API is new to you, I recommend you become familiar with the [Station Selector arguments](https://developers.synopticdata.com/mesonet/v2/station-selectors/) first. These parameters key in on specific stations or a set of stations within an area of interest (`stid`, `radius`, `vars`, `state`, etc.).

Some things you should know when specifying a parameter:
1. All lists are joined together into a comma separated string. For instance, if you are requesting three stations, you could do `stid=['WBB', 'KSLC', 'KMRY']`, and that will be converted to a comma separated list `stid='WBB,KSLC,KMRY'` required for the API request URL. Both inputs are accepted by the functions.
1. Any input that is a datetime object (any datetime that can be parsed with f-string, `f'{DATE:%Y%m%d%H%M}'`) will be converted to a string required by the API. For example, `start=datetime(2020,1,1)` will be converted to `start='YYYYmmddHHMM'` when the query is made. Both inputs are accepted by the functions.
1. For services that requires the `within` or `recent` arguments, the API required these given in **minutes**. You may give integers for those arguments, but converting time to minutes is done automatically by the function if you input a `datetime.timedelta` or a `pandas timedelta`. For example, if you set `within=timedelta(hours=1)` or `recent=pd.to_timedelta('1d')`, the function will convert the value to minutes for you.

> **❓ What if I don't know a station's ID?**  
> MesoWest is your friend if you don't know what stations are available or what they are named: https://mesowest.utah.edu/.

### Query Timeseries Data
To get a time series of air temperature and wind speed for the last 10 hours for the William Browning Building (WBB) you can do...

```python
from datetime import timedelta
from synoptic.services import stations_timeseries

df = stations_timeseries(stid='WBB', 
                         vars=['air_temp', 'wind_speed'],
                         recent=timedelta(hours=10))
```
![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/main/images/timeseries_df.png)

### Query Latest Data
To get the latest air temperature and wind speed data for WBB (University of Utah) and KRMY (Monterey, CA airport) within one hour, we can also set the minutes as an integer instead as a timedelta.

```python
from synoptic.services import stations_latest

df = stations_latest(stid=['WBB', 'KMRY'],
                    vars=['air_temp', 'wind_speed'],
                    within=60)
```
![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/main/images/latest_df.png)

Parameters may be given as a list/datetime/timedelta, or as a string/integer interpreted by the Synoptic API. Thus, 
```python 
stations_latest(stid='WBB,KMRY',
                vars='air_temp,wind_speed',
                within=60)
```
is equivalent to the above example.


### Query Nearesttime Data

To get the air temperature and wind speed for WBB and KMRY nearest 00:00 UTC Jan 1, 2020 within one hour...

```python
from datetime import datetime
from synoptic.services import stations_nearesttime

df = stations_nearesttime(stid=['WBB', 'KMRY'], 
                          vars=['air_temp', 'wind_speed'],
                          attime=datetime(2020,1,1),
                          within=60)
```
![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/main/images/nearesttime_df.png)

**Note:** the string/integer alternative to the above example is
```python
stations_nearesttime(stid='WBB,KMRY',
                     vars='air_temp,wind_speed',
                     attime='2020010100',
                     within=60)
```
Use whichever is more convenient for you. I often use both methods. It depends on what I am doing.


## ♻ Returned Data: Variable Names
The raw data retrieved from the Synoptic API is converted from JSON to a Pandas DataFrame. 

If you look at the raw JSON returned, you will see that the observation values are returned as "sets" and "values", (e.g., `air_temp_set_1`, `pressure_set_1d`, `wind_speed_value_1`, etc.). This is because some stations have more than one sensor for a variable (e.g., wind at more than one level at a single site) or is reported at more than one interval (e.g., ozone at 1 hr and 15 min intervals). Time series requests return "sets" and nearest time requests return "values".

I don't really like dealing with the set and value labels. Almost always, I want the **set** or **value** with the _most_ data or the _most recent_ observation. **My functions, by default, will strip the `set_1` and `value_1` from the labels on the returned data. If there are more than one set or value, however, then the "set" and "value" labels will be retained for those extra sets.**

- If a query returns `air_temp_set_1` and `air_temp_set_2`, then the labels are renamed `air_temp` and `air_temp_set_2`.
- If a query returns `pressure_set_1` and `pressure_set_1d`, then the labels are renamed `pressure_set_1` and `pressure` _if **set_1d** has more observations than **set_1**_.
- If a query returns `dew_point_temperature_value_1` at 00:00 UTC and `dew_point_temperature_value_1d` at 00:15 UTC are both returned, then the labels are renamed `dew_point_temperature_value_1` and `dew_point_temperature` because the derived quantity is the most recent observation available.

In short, all sets and values are always returned, but column labels are simplified for the columns that I am most likely to use. 

For the renamed columns, it is up to the user to know if the data is a derived quantity and which set/value it is. To find out, look for attributes "SENSOR_VARIABLES" and "RENAME" in the DataFrame attributes (`df.attrs`), or look at the raw JSON.

Doing this makes sense to me, but if you are confused and don't trust what I'm doing, you can turn this "relabeling" off with `rename_set_1=False` and `rename_value_1=False` (for the appropriate function).

## 🌐 Latitude and Longitude
I should mention, `LATITUDE` and `LONGITUDE` in the raw JSON is renamed to `latitude` and `longitude` (lowercase) to match [CF convention](http://cfconventions.org/).

## 💨 U and V Wind Components
If the returned data contains variables for both `wind_speed` and `wind_direction`, then the DataFrame will compute and return the U and V wind components as `wind_u` and `wind_v`.

## ⏲ Timezone
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
![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/main//images/tz_localize.png)

## ✅ Quality Control Checks
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

# Contains the following
{'QC_SHORTNAMES': {'18': 'ma_stat_cons_check', '16': 'ma_temp_cons_check'},
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

## 📈 `plots.py` ***These are a work in progress***
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
