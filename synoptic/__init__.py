## Brian Blaylock
## September 11, 2020

"""
============
Synoptic API
============

Retrieve and plot mesonet data from thousands of stations via the Synoptic Data
Mesonet API: https://developers.synopticdata.com/mesonet/.

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

__author__ = 'Brian Blaylock'
__email__ = 'blaylockbk@gmail.com'
__url__ = 'https://github.com/blaylockbk/Synoptic_API'

try:
    from synoptic.accessors import *
except:
    warnings.warn('Could not import synoptic.accessors')
    pass

# 🙋🏻‍♂️ Thank you for using SynopticPy!")
