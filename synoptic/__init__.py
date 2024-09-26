"""
Synoptic API for Python Polars.

Retrieve and plot mesonet data from thousands of stations via the
Synoptic Data Weather Data API.

https://docs.synopticdata.com/services/weather-data-api.
"""

__author__ = "Brian K. Blaylock"
__email__ = "blaylockbk@gmail.com"
__url__ = "https://github.com/blaylockbk/SynopticPy"


try:
    ## TODO: Will the `_version.py` file *always* be present?
    ## TODO: What if the person doesn't do "pip install"?
    from ._version import __version__, __version_tuple__
except:
    __version__ = "unknown"
    __version_tuple__ = (999, 999, 999)
