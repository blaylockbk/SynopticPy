# 🐍 Installation and Conda Environment

## Option 1 (*recommended*): conda environment
If conda environments are new to you, I suggest you become familiar with [managing conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

I have provided a sample Anaconda [environment.yml](https://github.com/blaylockbk/SynopticPy/blob/main/environment.yml) file that lists the minimum packages required plus some extras that might be useful when working with other types of weather data. Look at the bottom lines of that yaml file--there are two ways to install SynopticPy with pip. Comment out the lines you don't want.

For the latest version of the code, use:

```yaml
- pip:
    - git+https://github.com/blaylockbk/SynopticPy.git
```
or use this for the latest version published to PyPI

```yaml
- pip:
    - SynopticPy
```

First, create the virtual environment with 

```bash
conda env create -f environment.yml
```

Then, activate the `synoptic` environment. Don't confuse this _environment_ name with the _package_ name.

```bash
conda activate synoptic
```

Occasionally, you might want to update all the packages in the environment.

```bash
conda env update -f environment.yml
```

## Option 2: pip
**SynopticPy is my first [PyPI](https://pypi.org/project/SynopticPy/) package.** You may install the last published version from PyPI. This requires the following are already installed:  
`numpy`, `pandas`, `requests`, `matplotlib`, and `cartopy`.

```bash
pip install SynopticPy
```

Note that installing with pip will not give you the latest version from github.

## Option 3: Alternative "Install" Method
There are several other ways to "install" a python package so you can import them. One alternative is to clone the repository into any directory.

```bash
git clone https://github.com/blaylockbk/SynopticPy.git
```
To import the SynopticPy functions, you will need to update your `PYTHONPATH` environment variable to find the directory you cloned the package into, or you can add the line the following line to the top of your python scripts:
```python 
sys.path.append("/path/to/SynopticPy")
```
