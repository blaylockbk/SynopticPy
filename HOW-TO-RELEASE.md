# _Note to self_
# How to publish a new release of the `synopticpy` package on PyPI and conda-forge

## Pre-step

Update SynopticPy version number in

- ~~setup.py~~
- ~~./docs/conf.py~~
- ~~Build the docs (one last time before release)~~
- ./CITATION.cff
- Make sure all leftover changes on main are committed that you want. 
- **Create a tag and release in GitHub**. 

> Note: The tag name should be `YYYY.MM.00` with _no leading zeros for the month_ (PyPI doesn't care about leading zeros).


## 📦 Publish to PyPI

On my local copy, do a `git fetch` and then checkout the tag. DO NOT EDIT ANY FILES (else you will get a `_post#` in the version name.)

Created a new conda environment with twine, pip, and build

```bash
# To create an environment for publishing to PyPI
conda create -n pypi python=3 twine pip build -c conda-forge

# To update that conda environment
conda update -n pypi -c conda-forge --all
python3 -m pip install --upgrade build  --user # Needed to get the latest version of build (0.10+)
python3 -m pip install --upgrade twine --user
```

Use the [build](https://github.com/pypa/build) tool to build my package following the steps from [here](https://towardsdatascience.com/how-to-package-your-python-code-df5a7739ab2e)

```bash
conda activate pypi
cd SynopticPy
python -m build
twine check dist/*
```

### Upload Package PyPI

```bash
# Upload to TEST PyPI site
twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*

# followed by username and password
```

```bash
# Upload to REAL PyPI site
twine upload --skip-existing dist/*

```
Enter username and password. _Note to self: I get a warning because I'm not using keyring_

Now confirm the file was uploaded to PyPI at <https://pypi.org/project/SynopticPy/>

## 🐍 Publish to Conda

Go to SynopticPy feedstock, update the version in the `meta.yml` file.

- Fork the [SynopticPy Conda feedstock](https://github.com/conda-forge/SynopticPy-feedstock)
- Follow the instructions in the README to update the build
    - Update version
    - Update sha256 has for the `SynopticPy-{version}.tar.gz` file (found on PyPI) in the "Download files" tab.
    - Set build to 0 for releasing a new version.
- Create pull request.
- Follow instructions in the pull request template.

---

# Miscellaneous

See PyPI download statistics at: https://pepy.tech/project/SynopticPy

Check import time with

```bash
python -X importtime synoptic/services.py > importtime.txt 2>&1
```
