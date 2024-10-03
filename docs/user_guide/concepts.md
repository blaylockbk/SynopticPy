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

## What are these DataFrames?

SynopticPy organizes the Synoptic JSON data in long-format [Polars DataFrames](https://docs.pola.rs/). You're likely familiar with Pandas, but oh, boy, I'm in love with Polars. It took a minute to convert my brain to understand Polars after being a Pandas user, but it didn't take long before I started liking Polars syntax much more than Pandas. Plus, Polars is super fast.

The primary goal of SynopticPy is to unpack Synoptic's JSON data into a DataFrame that's ideal for archiving (e.g., saving the DataFrame to Parquet format). SynopticPy structures this data into a "long format" DataFrame, meaning each row represents a single observation. This format is flexible, allowing you to manipulate the data (e.g., pivoting or concatenating) as needed. I encourage you to explore and, ideally, master Polars to take full advantage of this data structure.

> If you prefer working with Pandas, you can easily convert a Polars DataFrame to a Pandas DataFrame using `df.to_pandas()`.


The [seaborn](https://seaborn.pydata.org/tutorial/data_structure.html) plotting library works really well for plotting long-format DataFrames, and you'll see me use seaborn to plot some of the examples in these docs.
