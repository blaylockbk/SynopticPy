# Concepts

## Import and Basic Usage

You can import SynopticPy either by importing the entire `synoptic` module or by importing individual services. You can then retrieve data as a DataFrame using the `.df` attribute. For example:

```python
import synoptic

df = synoptic.Latest(stid='wbb').df
```

or

```python
from synoptic import Latest

df = Latest(stid='wbb').df
```

## Function parameters

Function arguments are stitched together to create a web query. The parameters you can use to filter the data depend on the API service. Synoptic's [API Explorer](https://developers.synopticdata.com/mesonet/explorer/) can help you determine what parameters can be used for each service.

If the Synoptic API is new to you, I recommend you become familiar with the [Station Selector arguments](https://developers.synopticdata.com/mesonet/v2/station-selectors/) first. These parameters key in on specific stations or a set of stations within an area of interest (`stid`, `radius`, `vars`, `state`, etc.).

Some things you should know when specifying a parameter:
1. All lists are joined together into a comma separated string. For instance, if you are requesting three stations, you could do `stid=['WBB', 'KSLC', 'KMRY']`, and that will be converted to a comma separated list `stid='WBB,KSLC,KMRY'` required for the API request URL. Both inputs are accepted by the functions.
1. Any input that is a datetime object (any datetime that can be parsed with f-string, `f'{DATE:%Y%m%d%H%M}'`) will be converted to a string required by the API. For example, `start=datetime(2020,1,1)` will be converted to `start='YYYYmmddHHMM'` when the query is made. Both inputs are accepted by the functions.
1. For services that requires the `within` or `recent` arguments, the API required these given in **minutes**. You may give integers for those arguments, but converting time to minutes is done automatically by the function if you input a `datetime.timedelta` or a `pandas timedelta`. For example, if you set `within=timedelta(hours=1)` or `recent=pd.to_timedelta('1d')`, the function will convert the value to minutes for you.

> **❓ What if I don't know a station's ID?**  
> MesoWest is your friend if you don't know what stations are available or what they are named: https://mesowest.utah.edu/.

## 💨 U and V Wind Components

TODO: Convert wind speed and directionto U and V components.

## ⏲ Timezone
Timezone is _always_ returned in UTC, even if you set `obtimezone=local`.

TODO: Example

## What are these DataFrames?

SynopticPy organizes the Synoptic JSON data in long-format [Polars DataFrames](https://docs.pola.rs/). You're likely familiar with Pandas, but oh, boy, I'm in love with Polars. It took a minute to convert my brain to understand Polars after being a Pandas user, but it didn't take long before I started liking Polars syntax much more than Pandas. Plus, Polars is super fast.

The primary goal of SynopticPy is to unpack Synoptic's JSON data into a DataFrame that's ideal for archiving (e.g., saving the DataFrame to Parquet format). SynopticPy structures this data into a "long format" DataFrame, meaning each row represents a single observation. This format is flexible, allowing you to manipulate the data (e.g., pivoting or concatenating) as needed. I encourage you to explore and, ideally, master Polars to take full advantage of this data structure.

> If you prefer working with Pandas, you can easily convert a Polars DataFrame to a Pandas DataFrame using `df.to_pandas()`.


The [seaborn](https://seaborn.pydata.org/tutorial/data_structure.html) plotting library works really well for plotting long-format DataFrames, and you'll see me use seaborn to plot some of the examples in these docs.

