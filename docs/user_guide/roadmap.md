# 🛣️ Roadmap

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
