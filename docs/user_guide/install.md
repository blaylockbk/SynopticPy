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

Import SynopticPy by importing `synoptic` or importing the classes for individual services. 

```python
import synoptic
```

```python
from synoptic import TimeSeries, Precipitation # etc.
```

For a general overview of how these services are called, refer to the usage of each of the services in the `tests/` directory.

Refer to the [Setup](./setup.md) page for instructions on getting and configuring your Synoptic API token.
