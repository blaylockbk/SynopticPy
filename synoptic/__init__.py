## Brian Blaylock
## September 11, 2020

"""
============
Synoptic API
============

Retrieve and plot mesonet data from thousands of stations via the
Synoptic Data Mesonet API: https://developers.synopticdata.com/mesonet/.

Usage
-----
There are two recommended ways to import these functions.

``` python
# Method 1: Import full module
import synoptic.services as ss
import synoptic.plots as sp
```

``` python
# Method 2: Import individual functions
from synoptic.services import stations_timeseries
```
"""

__author__ = "Brian K. Blaylock"
__email__ = "blaylockbk@gmail.com"
__url__ = "https://github.com/blaylockbk/SynopticPy"


try:
    ## TODO: Will the `_version.py` file *always* be present?
    ## TODO: What if the person doesn't do "pip install"
    from ._version import __version__, __version_tuple__
except:
    __version__ = "unknown"
    __version_tuple__ = (999, 999, 999)

# Note to self: Synoptic's config file is created by the get_token.py script

try:
    from synoptic.accessors import *
except:
    warnings.warn("Could not import synoptic.accessors")
    pass

# 🙋🏻‍♂️ Thank you for using SynopticPy!")
