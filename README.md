<div
    align='center'
>

![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/main/images/SynopticPy_logo.png)

# ☁ Synoptic API for Python (_unofficial_)

<!-- Badges -->

[![PyPI](https://img.shields.io/pypi/v/SynopticPy)](https://pypi.python.org/pypi/SynopticPy/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/synopticpy.svg)](https://anaconda.org/conda-forge/synopticpy)
[![DOI](https://zenodo.org/badge/288617886.svg)](https://zenodo.org/badge/latestdoi/288617886)

![License](https://img.shields.io/github/license/blaylockbk/SynopticPy)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests (Python)](https://github.com/blaylockbk/SynopticPy/actions/workflows/tests-python.yml/badge.svg)](https://github.com/blaylockbk/SynopticPy/actions/workflows/tests-python.yml)
[![Documentation Status](https://readthedocs.org/projects/synopticpy/badge/?version=latest)](https://synopticpy.readthedocs.io/?badge=latest)
[![Python](https://img.shields.io/pypi/pyversions/SynopticPy.svg)](https://pypi.org/project/SynopticPy/)
[![Conda Recipe](https://img.shields.io/badge/recipe-synopticpy-green.svg)](https://anaconda.org/conda-forge/synopticpy)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/synopticpy.svg)](https://anaconda.org/conda-forge/synopticpy)
[![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/synopticpy.svg)](https://anaconda.org/conda-forge/synopticpy)

<!-- (Badges) -->

</div>

The [Synoptic Weather API](https://synopticdata.com/weatherapi) gives you access to real-time and historical surface-based weather and environmental observations for thousands of stations.

Synoptic open-access data is [_free_](https://synopticdata.com/pricing/open-access-pricing/). More data and enhances services are available through a [commercial option](https://synopticdata.com/pricing) (available through Synoptic, not me).

| <H2>📘 [SynopticPy Documentation](https://synopticpy.readthedocs.io/)</H2>    | <h2>📈 [SynopticPy Web App](https://blaylockbk.github.io/SynopticPy)</h2>   |
| :---: | :---: |
| SynopticPy is a Python package that helps you get mesonet data from the Synoptic API and load the data into Pandas Dataframes.    |  The SynopticPy web app lets you plot station data from Synoptic in your browser powered by pyscript!    |


# SynopticPy

I wrote these functions to conveniently access data from the Synoptic API and convert the JSON data to a **[Pandas DataFrame](https://pandas.pydata.org/docs/)**. This may be helpful to others who are getting started with the Synoptic API and Python. The idea is loosely based on the obsolete [MesoPy](https://github.com/mesowx/MesoPy) python wrapper, but returning the data as a Pandas DataFrame instead of a simple dictionary, making the retrieved data more _ready-to-use_.

> ### 🌐 Register for a free account at the Synoptic API Webpage
>
> > https://docs.synopticdata.com/account/
>
> You will need to obtain an API token before using this python package.

If you have stumbled across this package, I hope it is useful to you or at least gives you some ideas.

**Best of Luck 🍀**  
-Brian

- [👨🏻‍🏭 Contributing Guidelines and Disclaimer](https://synopticpy.readthedocs.io/en/latest/user_guide/contribute.html)
- [💬 Discussions](https://github.com/blaylockbk/SynopticPy/discussions)
- [🐛 Issues](https://github.com/blaylockbk/SynopticPy/issues)

<hr>

<br><br><br>

# 🐍 Installation

## Install with conda

If conda environments are new to you, I suggest you become familiar with [managing conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

```bash
conda install -c conda-forge synopticpy
```

## Install with pip

Install the last published version from PyPI.

```bash
# Install latest release
pip install SynopticPy
```

```bash
# Install latest main branch
pip install git+https://github.com/blaylockbk/SynopticPy.git
```

```bash
# Install latest main branch, editable (for development)
git clone https://github.com/blaylockbk/SynopticPy.git
cd SynopticPy
pip install -e .
```

## Optional Dependencies

It's optional, but you will likely want `cartopy` too. You may also want https://github.com/blaylockbk/carpenter_workshop.git

# 🔨 Setup

After following the setup instructions in the [documentation](https://synopticpy.readthedocs.io/en/latest/user_guide/setup.html), you should either have an environmental variable named `SYNOPTIC_TOKEN` or a file at `~/.config/SynopticPy/config.toml` that looks something like this:

```toml
[default]
verbose = true
hide_token = true
rename_value_1 = true
rename_set_1 = true
token = "1234567890abcdefghijklmnopqrstuvwxyz"
```

If you don't do this step, don't worry. When you import `synoptic.services`,
a quick check will make sure the token in the config file is valid. If not,
you will be prompted to update the token in the config file.

# Quick Examples

- [User Guide Examples](https://synopticpy.readthedocs.io/en/latest/user_guide/examples.html)
- [Reference Guide](https://synopticpy.readthedocs.io/en/latest/reference_guide/index.html)
- [Jupyter Notebooks](https://github.com/blaylockbk/SynopticPy/tree/main/notebooks)

> TODO: Move these notebooks to the docs.

```python
# Import all functions
import synoptic.services as ss
```

or

```python
# Import a single function (prefered)
from synoptic.services import stations_timeseries
```

Get a timeseries of air temperature and wind speed at the station WBB for the last 10 hours:

```python
from datetime import timedelta
from synoptic.services import stations_timeseries

df = stations_timeseries(
    stid='WBB',
    vars=['air_temp', 'wind_speed'],
    recent=timedelta(hours=10)
)
```

![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/main/images/timeseries_df.png)

Get the latest air temperature and wind speed data for WBB (University of Utah) and KRMY (Monterey, CA airport) within one hour (with `windin` given as an interger in minutes, this may also be a timedelta object instead).

```python
from synoptic.services import stations_latest

df = stations_latest(
    stid=['WBB', 'KMRY'],
    vars=['air_temp', 'wind_speed'],
    within=60
)
```

![](./images/latest_df.png)

Get the air temperature and wind speed for WBB and KMRY nearest 00:00 UTC Jan 1, 2020 within one hour...

```python
from datetime import datetime
from synoptic.services import stations_nearesttime

df = stations_latest(
    stid=['WBB', 'KMRY'],
    vars=['air_temp', 'wind_speed'],
    attime=datetime(2020,1,1),
    within=60
)
```

![](https://raw.githubusercontent.com/blaylockbk/SynopticPy/main/images/nearesttime_df.png)

# How to Cite and Acknowledge

If SynopticPy played an important role in your work, please [tell me about it](https://github.com/blaylockbk/SynopticPY/discussions/categories/show-and-tell)! Also, consider including a citation or acknowledgement in your article or product.

**_Suggested Citation_**

> Blaylock, B. K. (2023). SynopticPy: Synoptic API for Python (Version 2023.3.0) [Computer software]. https://github.com/blaylockbk/SynopticPy

**_Suggested Acknowledgment_**

> A portion of this work used code generously provided by Brian Blaylock's SynopticPy python package (https://github.com/blaylockbk/SynopticPy)
