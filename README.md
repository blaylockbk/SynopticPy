<div
    align='center'
>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/blaylockbk/SynopticPy/refs/heads/56-rewrite-using-polars/docs/_static/SynopticPy_white.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/blaylockbk/SynopticPy/refs/heads/56-rewrite-using-polars/docs/_static/SynopticPy_blue.svg">
  <img alt="Shows a black logo in light color mode and a white one in dark color mode." src="https://raw.githubusercontent.com/blaylockbk/SynopticPy/refs/heads/56-rewrite-using-polars/docs/_static/SynopticPy_blue.svg" width=300>
</picture>

## ☁ Synoptic API for Python (_unofficial_)

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

Synoptic's [Weather API](https://synopticdata.com/weatherapi/) gives you access to real-time and historical surface-based weather and environmental observations for thousands of stations. Synoptic's [open access data](https://synopticdata.com/pricing/open-access-pricing/) is _free_. More data and enhanced services are also available.

I wrote these functions to conveniently request data from [Synoptic's Weather API](https://docs.synopticdata.com/services/weather-data-api) and convert the JSON data to a **[Polars DataFrame](https://docs.pola.rs/user-guide/getting-started/)**. I'm sharing this as an open source project because I think these might be helpful to others who are getting started using the Synoptic API with Python. I also wrote this package to get more experimence using Polars DataFrames.


> ### 🎟️ You will need an API token before using SynopticPy: [Register for a free Synoptic account](https://customer.synopticdata.com/).

If you have stumbled across this package, I hope it is useful to you or at least gives you some ideas.

**Best of Luck 🍀**  
-Brian

<div align=center>

# 📘 [SynopticPy Documentation](https://synopticpy.readthedocs.io/)

## [👨🏻‍🏭 Contributing](https://synopticpy.readthedocs.io/en/latest/user_guide/contribute.html) | [💬 Discussions](https://github.com/blaylockbk/SynopticPy/discussions) | [🐛 Issues](https://github.com/blaylockbk/SynopticPy/issues)

</div>


# 🐍 Install

```bash
pip install SynopticPy
```

```bash
conda install -c conda-forge SynopticPy
```

# How to Cite and Acknowledge

If SynopticPy played an important role in your work, please [tell me about it](https://github.com/blaylockbk/SynopticPY/discussions/categories/show-and-tell)! Also, consider including a citation or acknowledgement in your article or product.

**_Suggested Citation_**

> Blaylock, B. K. (2024). SynopticPy: Synoptic API for Python (Version 2024.10.0) [Computer software]. https://github.com/blaylockbk/SynopticPy

**_Suggested Acknowledgment_**

> A portion of this work used code generously provided by Brian Blaylock's SynopticPy python package (https://github.com/blaylockbk/SynopticPy)


|                           <H2>📘 [SynopticPy Documentation](https://synopticpy.readthedocs.io/)</H2>                           |              <h2>📈 [SynopticPy Web App](https://blaylockbk.github.io/SynopticPy)</h2>               |
| :----------------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------: |
| SynopticPy is a Python package that helps you get mesonet data from the Synoptic API and load the data into Pandas Dataframes. | The SynopticPy web app lets you plot station data from Synoptic in your browser powered by pyscript! |
