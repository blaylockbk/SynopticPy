import os
from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README = (HERE / 'README.md').read_text()

setup(
    name = 'SynopticPy',   # I have to use 'SynopticPy' because 'synoptic' is used
    version = '0.0.2',
    author = 'Brian K. Blaylock',
    author_email = "blaylockbk@gmail.com",
    description = 'SynopticPy - Load mesonet data from the Synoptic API into a Pandas Dataframe',
    long_description = README,
    long_description_content_type = 'text/markdown',
    project_urls = {
        'Source Code': 'https://github.com/blaylockbk/SynopticPy',
    },
    license = "MIT",
    packages = find_packages(),
    package_data = {
        "": ['*.cfg'],
    },
    install_requires = ['numpy', 'pandas', 'requests', 'matplotlib', 'cartopy'],
    keywords = ['mesonet', 'weather', 'synoptic', 'pandas'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    zip_safe = False,
)

###############################################################################
## Brian's Note: How to upload a new version to PyPI
## -------------------------------------------------
# Created a new conda environment with twine
# conda create -n pypi python=3 twine pip -c conda-forge
'''
conda activate pypi
python setup.py sdist bdist_wheel

twine check dist/*

# Test PyPI
twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*

# PyPI
twine upload --skip-existing dist/*
'''