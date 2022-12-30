from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf8")

setup(
    name="SynopticPy",  # I have to use 'SynopticPy' because 'synoptic' is used
    version="0.0.7",
    author="Brian K. Blaylock",
    author_email="blaylockbk@gmail.com",
    description="Load mesonet weather and environmental data from the Synoptic API into a Pandas Dataframe",
    long_description=README,
    long_description_content_type="text/markdown",
    project_urls={
        "Source Code": "https://github.com/blaylockbk/SynopticPy",
        "Documentation": "https://github.com/blaylockbk/SynopticPy/blob/main/README.md",
        "Official Synoptic Docs": "https://developers.synopticdata.com/mesonet/",
    },
    license="MIT",
    packages=find_packages(),
    package_data={
        "": ["*.cfg"],
    },
    install_requires=["numpy", "pandas", "requests", "toml"],
    keywords=["pandas", "meteorology", "weather", "mesonet", "Synoptic", "MesoWest"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    zip_safe=False,
)

###############################################################################
## Brian's Note: How to upload a new version to PyPI
## -------------------------------------------------
# Update version in
#  - setup.py
#  - CITATION.cff
#  - Create a tag and release in GitHub
# Created a new conda environment with twine
# conda create -n pypi python=3 twine pip -c conda-forge
"""
conda activate pypi
cd SynopticPy
python setup.py sdist bdist_wheel

twine check dist/*

# Test PyPI
twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*

# PyPI
twine upload --skip-existing dist/*
"""


#######################################################
## On May 12, 2022 I changed the default branch to main
## You can change your local clone default name with
## The following
"""
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
"""
