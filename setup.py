import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'synoptic',
    version = '0.0.2',
    author = 'Brian K. Blaylock',
    author_email = "blaylockbk@gmail.com",
    description = 'SynopticPy - Load mesonet data from the Synoptic API into a Pandas Dataframe',
    long_description = read('README.md'),
    url = 'https://github.com/blaylockbk/SynopticPy',
    license = "MIT",
    packages = ['synoptic'],
    include_package_data = True,
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
    zip_safe = False
)
