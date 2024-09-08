# Notes

```Python
import synoptic

df = synoptic.TimeSeries(...).df
df.synoptic.pivot()
```

The default DataFrame is in long format; one row for each unique observation


## Timezone
Requesting a `obtimezone='local'` still returns column of dataframe in UTC time. This is because Polars datetime type is timezone aware, so you can't have multiple timezones in the same column.

If you need all data in their local timezone, then use `df.partition_by('stid')`

## Elevation and Position units

- Station elevation has units of _feet_.
- Sensor position has units in _meters_.

## Precipitation

I don't allow the use of the legacy API behavior by not letting the user omit the `pmode` argument. Its default is "totals"

## Quality control

The QC column is always provided, but does not mean QC checks were performed.

## DataFrame

- Data is provided in long format; one unique observation per row.

- Only float values are parse. The following variables are dropped because they cannot be floats:

  - wind_cardinal_direction
  - weather_condition
  - weather_summary
  - cloud_layer
  - metar

- All column names are changed to **lower case**.

- Don't do anything with `"SENSOR_VARIABLES"`. This tells us what variables are used to derive other variables, but I don't see how it is useful when doing any analysis.


### QC
- The presence of the `qc_flags` column means that some QC checks were applied. 

