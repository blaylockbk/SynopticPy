# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.abspath('../..'))

#import sphinx_rtd_theme
import pydata_sphinx_theme


# -- Project information -----------------------------------------------------

project = 'SynopticPy Docs'
copyright = f'{datetime.utcnow():%Y}, Brian K. Blaylock'
author = 'Brian K. Blaylock'

release = '0.1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    #'sphinx_rtd_theme',     # I'm not using this theme, use pydata_sphinx_theme
    'nbsphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.napoleon',
    #'sphinx.ext.jsmath',    # Can't seem to get the math function to work
    'recommonmark', 
    'autodocsumm',
    'sphinx_markdown_tables'
]

# Set up mapping for other projects' docs
intersphinx_mapping = {
    'metpy': ('https://unidata.github.io/MetPy/latest/', None),
    'pint': ('https://pint.readthedocs.io/en/stable/', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    'xarray': ('https://xarray.pydata.org/en/stable/', None)
}

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 
                    '.ipynb_checkpoints', '.vscode']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = "sphinx_rtd_theme"
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    'github_url': 'https://github.com/blaylockbk/SynopticPy',
    'twitter_url': "https://twitter.com/blaylockbk",
    "navbar_end": ["navbar-icon-links.html", "search-field.html"],
    "google_analytics_id": "G-HBCJD6ZZKM",
    "use_edit_page_button": True,
    "show_toc_level": 1,
    "external_links": [
      {"name": "GOES-2-go", "url": "https://blaylockbk.github.io/goes2go/_build/html/"},
      {"name": "HRRR-B", "url": "https://blaylockbk.github.io/HRRR_archive_download/_build/html/"}
  ]
}

html_sidebars = {
}

html_logo = "_static/SynopticPy_logo.png"
html_favicon = "_static/wxicon.png"

html_context = {
    'github_user': 'blaylockbk',
    'github_repo': 'SynopticPy',
    'github_version': 'master',  # Make changes to the master branch
    "doc_path": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', '../images']

html_css_files = [
    # 'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',  # the pydata theme already does this DO NOT LOAD IT AGAIN!
    'brian_style.css'
]

html_js_files = [
    'https://kit.fontawesome.com/f6cc126dcc.js',
]

# Set autodoc defaults
autodoc_default_options = {
    'autosummary': True,        # Include a members "table of contents"
    'members': True,            # Document all functions/members  
}

autodoc_mock_imports = ["xesmf", "siphon", "imageio"]

# -- Auto-convert markdown pages to demo --------------------------------------
import recommonmark
from recommonmark.transform import AutoStructify


def setup(app):
    app.add_transform(AutoStructify)

# ^^I actually don't know what the above did, if it did anything