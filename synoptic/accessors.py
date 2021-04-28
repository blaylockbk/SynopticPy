## Brian Blaylock
## April 27, 2021

"""
=====================================
Custom Pandas Accessor for SynopticPy
=====================================

So, I recently learned a cool trick--using Pandas custom accessors
to extend Pandas DataFrames with custom methods. Look more about them
here:
https://pandas.pydata.org/pandas-docs/stable/development/extending.html

This is work in progress, but will be useful for making quick map and
timeseries plots of data returned from the API.

"""
import warnings

import pandas as pd
import matplotlib.pyplot as plt

try:
    from toolbox.cartopy_tools import common_features, pc
except:
    warnings.warn('map making not available with cartopy_tools')

@pd.api.extensions.register_dataframe_accessor("synoptic")
class SynopticAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        # verify there is a column latitude and a column longitude
        if "latitude" not in obj.columns or "longitude" not in obj.columns:
            raise AttributeError("Must have 'latitude' and 'longitude'.")

    @property
    def center(self):
        # return the geographic center point of this DataFrame
        lat = self._obj.latitude
        lon = self._obj.longitude
        return (float(lon.mean()), float(lat.mean()))

    def get_stn_column(self):
        """Get df as just STATIONS columns"""
        return self._obj[a._obj.attrs['STATIONS']]

    def get_dt_column(self):
        """Get df as just DATETIME columns"""
        return self._obj[a._obj.attrs['DATETIMES']]

    def plot(self, ax=None):
        # plot this array's data on a map, e.g., using Cartopy

        df = self._obj

        if ax is None:
            ax = common_features()
        
        ax.scatter()

        return ax