# 🐍 Installation and Conda Environment
### Option 1: pip
Install the last published version from PyPI. This requires the following are already installed:  
`numpy`, `pandas`, `requests`. It's optional, but you will want `matplotlib`, and `cartopy`, too.

```bash
pip install SynopticPy
```

### Option 2: conda
If conda environments are new to you, I suggest you become familiar with [managing conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

I have provided a sample Anaconda [environment.yml](https://github.com/blaylockbk/SynopticPy/blob/master/environment.yml) file that lists the minimum packages required plus some extras that might be useful when working with other types of weather data. Look at the bottom lines of that yaml file...there are two ways to install SynopticPy with pip. Comment out the lines you don't want.

For the latest development code:
```yaml
- pip:
    - git+https://github.com/blaylockbk/SynopticPy.git
```
For the latest published version
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

> ### Alternative "Install" Method
> There are several other ways to "install" a python package so you can import them. One alternatively is you can `git clone https://github.com/blaylockbk/SynopticPy.git` this repository to any directory. To import the package, you will need to update your PYTHONPATH environment variable to find the directory you put this package or add the line `sys.path.append("/path/to/SynotpicPy")` at the top of your python script.