# How to publish a new release

> NOTE: These are Brian's personal notes.

Update version in
  - `CITATION.cff`

Create a tag and release in GitHub

Created a new conda environment with twine
```
conda create -n pypi python=3 twine pip -c conda-forge
```
```
conda activate pypi
cd SynopticPy
python setup.py sdist bdist_wheel

twine check dist/*
```

Upload to Test PyPI
```
twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*
```

Upload to PyPI
```
twine upload --skip-existing dist/*
```


## Conda release

TODO
