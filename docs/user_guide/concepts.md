# 🌳 Concepts

## Preferred Import

You can import SynopticPy either by importing the entire `synoptic` module

```python
import synoptic
```

or by importing individual service classes

```python
from synoptic import TimeSeries, Latest # ... etc.
```

## Available Services

All of Synoptic's Weather API services are available in SynopticPy (with the exception of `qcsegments`, which I have never needed).

The names of these service classes are listed in the following table:

| Class           | Description                                                 |
| --------------- | ----------------------------------------------------------- |
| `TimeSeries`    | Get time series data for one or more stations.              |
| `Latest`        | Get the most recent data from one or more stations.         |
| `NearestTime`   | Get data nearest a specified time for one or more stations. |
| `Precipitation` | Get derived precipitation total or intervals.               |
| `Latency`       | Get station latency.                                        |
| `Metadata`      | Get metadata for one or moe stations.                       |
| `QCTypes`       | Table of all QC types and names.                            |
| `Variables`     | Table of all available variables.                           |
| `Networks`      | Table of all available networks.                            |
| `NetworkTypes`  | Table of all available network types.                       |

## Constructor arguments

Constructor arguments (class input parameters) are stitched together to create a web query. The parameters used to specify the data you want depends on the API service. Synoptic's Weather API [Documentation](https://docs.synopticdata.com/services/weather-data-api) and [Query Builder](https://demos.synopticdata.com/query-builder/index.html) can help you determine what parameters can be used for each service.

:::{tip}

**I highly recommend you become familiar with [Synoptic's Weather API documentation](https://docs.synopticdata.com/services/weather-data-api).**
:::

In SynopticPy,

```python
from datetime import datetime
import synoptic

S = synoptic.TimeSeries(
    stid="wbb",
    start=datetime(2024, 1, 1),
    end=datetime(2024, 1, 5),
    vars=["air_temp","wind_speed","wind_direction"],
)
```

makes the following API request: <https://api.synopticdata.com/v2/stations/timeseries?stid=wbb&start=202401010000&end=202401050000&vars=air_temp,wind_speed,wind_direction&token=YourTokenHere>

Notice that SynopticPy allows you to use more _Pythonic_ input for these parameters. Pay attention to these extended input conventions used by SynopticPy when requesting data:

1. **Lists and tuples are accepted**, and will be converted to comma- separated strings. For example:

   When selecting stations, both are acceptable:

   ```python
   stid="WBB,KSLC,KMRY"
   ```

   ```python
   stid=["WBB", "KSLC", "KMRY"]
   ```

   When selecting variables, both are acceptable:

   ```python
   vars="air_temp,wind_speed"
   ```

   ```python
   vars=["air_temp","wind_speed"]
   ```

   When using the radius parameter, both are acceptable:

   ```python
   radius="wbb,20"
   ```

   ```python
   radius=("wbb", 20)
   ```

1. **Datetime objects are accepted** and will be converted to a string required by the Synoptic API. For example:

   While both are acceptable, using datetime objects is preferred to reduce room for errors.

   ```python
   start=datetime.datetime(2020, 1, 1)
   ```

   ```python
   start="202001010000"
   ```

   The parameter `obrange` is a special case which can be provided as a tuple of datetimes `obrange=(datetime_start, datetime_end)`.

1. **Timedetla or Polars-style duration strings are accepted** and will be converted to a value required by the Synoptic API. For example:

   While Synoptic expects the `within` and `recent` arguments to be integer minutes, SynopticPy lets you use a timedelta object or a Polars-style duration string.

   The following are equivalent:

   ```python
   within=datetime.timedelta(hours=1)
   ```

   ```python
   within="1h"
   ```

   ```python
   within=60
   ```

1. **Boolean values are accepted** for parameters where Synoptic expects values of `0`, `1`, `"on"`, or `"off"`. For example:

   ```python
   showemptystations=False,
   qc=True
   ```

   can be used in place of

   ```python
   showemptystations=0,
   qc="on"
   ```

## What if I don't know a station's ID?

Use these two amazing resources:

- [Syonptic's Data Viewer](https://viewer.synopticdata.com/)
- [MesoWest](https://mesowest.utah.edu/)

## Data as a Polars DataFrame

SynopticPy is built with Polars, and converts Synoptic's JSON data to a long-form Polars DataFrame. Use the `.df()` method on a service class to get the data.

```python
from synoptic import TimeSeries

df = TimeSeries(stid='wbb', recent=30, vars='air_temp,wind_speed').df()
```

## What is included in a Services Class instance?

In general, most instances return the following attributes:

1. Capitalized attributes like `.SUMMARY`, `.STATION`, `.UNITS`, and `.QC_SUMMARY` are copied dictionaries attached from the returned JSON. These are for convenience.

1. `.df()` is the long-format **Polars DataFrame** of the `STATION` data.

1. `.endpoint` is the URL for the requested API service.

1. `.help_url` is the website for the documentation for the service.

1. `.json` is the returned JSON from the API request loaded into a Python dictionary.

1. `.params` are the user-specified parameters used to make the request.

1. `.response` is the object from the requests library, `requests.get(...)`.

1. `.service` is the requested Synoptic API service type.

1. `.url` is the full URL used to make the API request.

Let's take a look at the attributes of Metadata service instance...

## What are these DataFrames?

SynopticPy organizes the Synoptic JSON data in _long form_ [Polars DataFrames](https://docs.pola.rs/). A _long form_ dataframe means that each row in the DataFrame represents a single, unique observations. This makes it easy to archive the data locally (i.e., saving to a Parquet file). This format is flexible, allowing you to manipulate the data (e.g., pivoting or concatenating) as needed.

```{admonition} Polars!
:class: sidebar note
I'm a big Polars user now. It took a minute to convert my brain to understand Polars after being a Pandas user, but it didn't take long before I started liking Polars syntax much more than Pandas. Plus, Polars is super efficient for large datasets.

I encourage you to get comfortable with Polars, but if you prefer working with Pandas, you can easily convert a Polars DataFrame to a Pandas DataFrame using `df.to_pandas()`.
```

## Why are all Timezones in UTC?

The `date_time` column and timezones for other DateTime columns are _always_ returned in UTC, even if you set `obtimezone="local"`. This is because SynopticPy organizes the data in long-form DataFrames where all the observation times are in a single column. All datetimes in the date-time column must be in the same time zone.

It is possible to convert data to a specific timezone using Polars. If you have multiple stations, you will probably want to partition the DataFrame by the `date_time` column.

> "Note that, because a Datetime can only have a single time zone, it is impossible to have a column with multiple time zones."
> - [Polars Docs: Timezones](https://docs.pola.rs/user-guide/transformations/time-series/timezones/)

## Plotting

Throughout these docs, I use many different plotting tools.

- Matplotlib
- [Seaborn](https://seaborn.pydata.org/tutorial/data_structure.html) - Works really well for plotting long-form DataFrames.
- Cartopy - When I use Cartopy, and I typically use my shortcut `EasyMap` tool included in [Herbie](https://github.com/blaylockbk/Herbie) to create those cartopy maps.
- Altair - Built-in plotting support for Polars.
