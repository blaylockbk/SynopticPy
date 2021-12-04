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
    from paint.standard2 import cm_tmp
except:
    warnings.warn("map making not available without Brian's cartopy_tools")


@pd.api.extensions.register_dataframe_accessor("synoptic")
class SynopticAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if obj.attrs["service"] in ["stations_latest", "stations_nearesttime"]:
            # verify there is a latitude and a longitude index.
            if "latitude" not in obj.index or "longitude" not in obj.index:
                raise AttributeError("Must have 'latitude' and 'longitude'.")
        else:
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
        return self._obj[a._obj.attrs["STATIONS"]]

    def get_dt_column(self):
        """Get df as just DATETIME columns"""
        return self._obj[a._obj.attrs["DATETIMES"]]

    def plot_map(
        self,
        ax=None,
        color_by=None,
        show_label="STID",
        cbar_kw={},
        common_features_kw={},
        **kw,
    ):
        """
        Parameters
        ----------
        show_label : {None, 'STID', 'NAME', 'ELEVATION', etc.}
            What value to show for the label.
        """
        # plot this array's data on a map, e.g., using Cartopy

        df = self._obj

        if ax is None:
            ax = common_features(**common_features_kw).ax

        stations = df.attrs["STATIONS"]

        kw.setdefault("transform", pc)
        kw.setdefault("edgecolor", "k")
        kw.setdefault("linewidth", 0.5)

        cbar_kw.setdefault("fraction", 0.046)
        cbar_kw.setdefault("pad", 0.01)

        if color_by is not None:
            kw["c"] = df[stations].loc[color_by]
        else:
            kw["c"] = "tab:blue"

        if color_by == "air_temp":
            kw = {**cm_tmp().cmap_kwargs, **kw}
            cbar_kw = {**cm_tmp().cbar_kwargs, **cbar_kw}

        for stid, info in df[stations].iteritems():

            if color_by is not None:
                kw["c"] = info[color_by]

            art = ax.scatter(info.longitude, info.latitude, **kw)
            if show_label or show_label is not None:
                ax.text(
                    info.longitude,
                    info.latitude,
                    f" {info[show_label]}",
                    va="center",
                    ha="left",
                    transform=pc,
                    fontfamily="monospace",
                    clip_on=True,
                )

        if color_by is not None:
            plt.colorbar(art, ax=ax, **cbar_kw)

        ax.adjust_extent()

        return ax
