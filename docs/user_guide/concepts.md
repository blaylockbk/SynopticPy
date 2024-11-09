# 🌳 Concepts

## Preferred Import

You can import SynopticPy either by importing the entire `synoptic` module or by importing individual service classes.

```python
import synoptic
```

or

```python
from synoptic import TimeSeries, Latest # ... etc.
```

The available services are listed in the following table.

| Synoptic Services | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| `TimeSeries`      | Get time series data for one or more stations.              |
| `Latest`          | Get the most recent data from one or more stations.         |
| `NearestTime`     | Get data nearest a specified time for one or more stations. |
| `Precipitation`   | Get derived precipitation total or intervals.               |
| `Latency`         | Get station latency.                                        |
| `Metadata`        | Get metadata for one or moe stations.                       |
| `QCTypes`         | Table of all QC types and names.                            |
| `Variables`       | Table of all available variables.                           |
| `Networks`        | Table of all available networks.                            |
| `NetworkTypes`    | Table of all available network types.                       |

## Data as a Polars DataFrame

SynopticPy is built with Polars, and converts Synoptic's JSON data to a long-form Polars DataFrame. Use the `.df()` method on a service class to get the data.

```python
from synoptic import TimeSeries

df = TimeSeries(stid='wbb', recent=30, vars='air_temp,wind_speed').df()
```

## Constructor arguments

Constructor arguments (class input parameters) are stitched together to create a web query. The parameters used to specify the data you want depends on the API service. Synoptic's Weather API [Documentation](https://docs.synopticdata.com/services/weather-data-api) and [Query Builder](https://demos.synopticdata.com/query-builder/index.html) can help you determine what parameters can be used for each service.

:::{tip}
**If the Synoptic API is new to you, I highly recommend you become familiar with its [documentation](https://docs.synopticdata.com/services/weather-data-api).**
:::

SynopticPy allows you to use more "Pythonic" input for these parameters. Pay attention to these SynopticPy extensions when requesting data:

1. Parameters may be given as lists or tuples, which are joined together into a comma separated string. One example where this is useful is in selecting multiple stations. While you can request `stid='WBB,KSLC,KMRY`, you may also request `stid=["WBB", "KSLC", "KMRY"]`. Both inputs are acceptable. Another example is `radius=("wbb", 20)` is equivalent to `radius="wbb,20"`

1. Datetime objects (any datetime that can be parsed with f-string, `f'{DATE:%Y%m%d%H%M}'`) will be converted to a string required by the API. For example, `start=datetime.datetime(2020,1,1)` will be converted to `start='202001010000'` when the query is made. Both inputs are accepted, but using a datetime object is preferred. A special case is `obrange` which can be provided as a tuple of datetimes `obrange=(datetime_start, datetime_end)`.

1. While Synoptic expects the `within` and `recent` arguments to be integer minutes, SynopticPy lets you use a timedelta object or polar-style duration string. The following are equivalent `within=datetime.timedelta(hours=1)` or `within='1h'` or `within=60`.

1. When Synoptic expects values of `0`, `1`, `'on'`, or `'off'`, SynopticPy lets you give these as booleans. For example `showemptystations=False` is the same as `showemptystations=0`, and `qc=True` is the same as `qc='on'`.

## What if I don't know a station's ID?

Use these two amazing resources:

- [Syonptic's Data Viewer](https://viewer.synopticdata.com/)
- [MesoWest](https://mesowest.utah.edu/)

## What are these DataFrames?

SynopticPy organizes the Synoptic JSON data in long-format [Polars DataFrames](https://docs.pola.rs/). You're likely familiar with Pandas, but oh, boy, I'm in love with Polars. It took a minute to convert my brain to understand Polars after being a Pandas user, but it didn't take long before I started liking Polars syntax much more than Pandas. Plus, Polars is super fast.

The primary goal of SynopticPy is to unpack Synoptic's JSON data into a DataFrame that's ideal for archiving (e.g., saving the DataFrame to Parquet format). SynopticPy structures this data into a "long format" DataFrame, meaning each row represents a single observation. This format is flexible, allowing you to manipulate the data (e.g., pivoting or concatenating) as needed. I encourage you to explore and, ideally, master Polars to take full advantage of this data structure.

> If you prefer working with Pandas, you can easily convert a Polars DataFrame to a Pandas DataFrame using `df.to_pandas()`.

## Why are all Timezones in UTC?

Timezone is _always_ returned in UTC, even if you set `obtimezone=local`. This is because SynopticPy organizes the data in long-form DataFrames where all the observation times are in a single column. All datetimes in the date-time column must be in the same time zone.

It is possible to convert data to a specific timezone using Polars. If you have multiple stations, you will probably want to partition the DataFrame by the `date-time` column.

## Plotting

Throughout these docs, I use many different plotting tools.

- Matplotlib
- [Seaborn](https://seaborn.pydata.org/tutorial/data_structure.html) - Works really well for plotting long-form DataFrames.
- Cartopy - When I use Cartopy, and I typically use my shortcut `EasyMap` tool included in [Herbie](https://github.com/blaylockbk/Herbie) to create those cartopy maps.
- Altair - Built-in plotting support for Polars.
