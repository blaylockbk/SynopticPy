# 🐍 Install

Install with conda:

```bash
conda install -c conda-forge SynopticPy
```

Install with pip:

```bash
pip install SynopticPy
```

Install latest from GitHub:

```bash
pip install git+https://github.com/blaylockbk/SynopticPy.git
```

For developers:

```bash
git clone https://github.com/blaylockbk/SynopticPy.git
cd SynopticPy
pip install -e .
```

## Quick Start

Refer to the [Setup](./setup.md) page for additional instructions on getting and configuring your Synoptic API token.

Import SynopticPy by importing the `synoptic` module or importing the classes for individual services.

```python
import synoptic
```
or
```python
from synoptic import TimeSeries, Precipitation # etc.
```

You retrieve data as a DataFrame using the `.df()` method. For example:

```python
import synoptic

df = synoptic.Latest(stid='wbb').df()
```

or

```python
from synoptic import Latest

df = Latest(stid='wbb').df()
```
