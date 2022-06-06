# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/main/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../.."))

# import sphinx_rtd_theme
import pydata_sphinx_theme
from datetime import datetime

# -- Project information -----------------------------------------------------
utc_now = datetime.utcnow().strftime("%H:%M UTC %d %b %Y")

project = "SynopticPy Docs"
copyright = f"{datetime.utcnow():%Y}, Brian K. Blaylock.    ♻ Updated: {utc_now}"
author = "Brian K. Blaylock"

release = "0.1"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx_panels",
    "autodocsumm",
    "sphinx_markdown_tables",
    "myst_parser",
]

# MyST Docs: https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "linkify",  # Autodetects URL links in Markdown files
]

# Set up mapping for other projects' docs
intersphinx_mapping = {
    "metpy": ("https://unidata.github.io/MetPy/latest/", None),
    "pint": ("https://pint.readthedocs.io/en/stable/", None),
    "matplotlib": ("https://matplotlib.org/", None),
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
    "xarray": ("https://xarray.pydata.org/en/stable/", None),
}

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".ipynb_checkpoints", ".vscode"]


# --- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/blaylockbk/goes2go",
    "twitter_url": "https://twitter.com/blaylockbk",
    "navbar_end": ["navbar-icon-links.html", "search-field.html"],
    "google_analytics_id": "G-NWK8MJNNGX",
    "use_edit_page_button": True,
    "show_toc_level": 1,
    "external_links": [
        {
            "name": "GOES-2-go",
            "url": "https://blaylockbk.github.io/goes2go/_build/html/",
        },
        {"name": "Herbie", "url": "https://blaylockbk.github.io/Herbie/_build/html/"},
    ],
}

html_sidebars = {}

html_logo = "_static/SynopticPy_logo.png"
html_favicon = "_static/wxicon.png"

html_context = {
    "github_user": "blaylockbk",
    "github_repo": "SynopticPy",
    "github_version": "master",  # Make changes to the master branch
    "doc_path": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static", "../images"]

fontawesome_included = True
panels_add_bootstrap_css = False  # False, because pydata theme already loads it

html_css_files = ["brian_style.css"]

html_js_files = [
    "https://kit.fontawesome.com/f6cc126dcc.js",
]

# Set autodoc defaults
autodoc_default_options = {
    "autosummary": True,  # Include a members "table of contents"
    "members": True,  # Document all functions/members
    "special-members": "__init__",
}

autodoc_mock_imports = [
    "xesmf",
    "numpy",
    "matplotlib",
    "pandas",
    "xarray",
    "cartopy",
    "cfgrib",
    "imageio",
    "siphon",
]


"""
IMPORTANT NOTES ABOUT PUBLISHING TO GITHUB PAGES
-----------------------------------------------
1. Must have an empty file called .nojekell in this directory.

2. Include an index.html file to redirect to the actual html build
   Something like this in that file (yes, only one line)...
        <meta http-equiv="Refresh" content="0;url=_build/html/"/>

3.
"""
