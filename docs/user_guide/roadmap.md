# 🛣️ Roadmap

Previous versions of SynopticPy used Pandas. Pandas is popular, but is starting to be antiquated. I have been using Polars for over a year and love it! These are the reasons why I re-wrote SynopticPy from the ground up using [Polars](https://docs.pola.rs/user-guide/getting-started/).

1. **_Personal learning exercise:_** I wanted to get better at using Polars, and rewriting SynopticPy was a great chance to do that. I'm also using class inheritance, which is not something I have used before, so I'm experimenting with that too.

1. **_Improve maintainability:_** Older versions of SynopticPy had some quirks I wanted to fix. The best way to fix those quicks was to re-write the package.

1. **_Locally Archiving Synoptic Data:_** SynopticPy limits the amount of data you can request in one API request. Also, in a research setting I need to use and re-use data lots of times as I'm experimenting. It doesn't make sense to keep getting data from the API every time I need to use the data. Instead, I should store the data locally after I got it from Synoptic. A long-format Polars DataFrame can be written to Parquet format, which has much smaller file sizes than JSON files.


Below is my running TODO list for this package.

## Questions

- Are derived variables flagged if the variables used to derive its value also flagged?

## TODO

- [ ] Close all legacy GitHub issues and discussions.

- [ ] Implement logging. Include log level in config file.

### Documentation

- [ ] Convert all old gallery notebooks I want to keep.

- [ ] Tutorials for each service.

- [ ] Show how to write to Parquet and tell user they should if they will be requesting the same data multiple times (i.e., case study research).

- [ ] Show how to convert timezones because because `obtimezone='local'` is IGNORED (because Polars can't have multiple timezones in same column)

## Features

- [ ] Latest/NearstTime: unnest minmax column

- [ ] Metadata: parsing sensor_variables column when `sensorvars=1`

- [ ] Latency: unnest statistics column if present and cast to appropriate datetime and duration types

- [ ] Timeseries: could have argument `with_latency` and make a latency request and join to data.

- [ ] Not all columns are parsed (complex stucts)

## Polars Custom Namespace

- [ ] Provide helper to properly use rolling and resample windows (https://docs.pola.rs/user-guide/transformations/time-series/resampling/)

- [ ] Add some quick, standardized plots (leverage seaborn, altair, cartopy optional)
