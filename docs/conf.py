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
import datetime
import os
import sys

import pydata_sphinx_theme

import synoptic

sys.path.insert(0, os.path.abspath("../.."))

# The full version, including alpha/beta/rc/post tags
release = synoptic.__version__

# The version, excluding alpha/beat/rc/tags
version = ".".join([str(i) for i in synoptic.__version_tuple__])


# -- Project information -----------------------------------------------------
# ---- Project information -----------------------------------------------------
utc_now = datetime.datetime.now(datetime.UTC).strftime("%H:%M UTC %d %b %Y")

project = "SynopticPy"
author = "Brian K. Blaylock"
copyright = f"{datetime.datetime.now(datetime.UTC).strftime('%Y')}, {author}.    ♻ Updated: {utc_now}"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx.ext.todo",
    "sphinx_design",
    "autodocsumm",
    "sphinx_markdown_tables",
    "myst_parser",
]


autosummary_generate = True  # Turn on sphinx.ext.autosummary

# MyST Docs: https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Set up mapping for other projects' docs
intersphinx_mapping = {
    "metpy": ("https://unidata.github.io/MetPy/latest/", None),
    "matplotlib": ("https://matplotlib.org/", None),
    "python": ("https://docs.python.org/3/", None),
    "polars": ("https://docs.pola.rs/api/python/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".ipynb_checkpoints",
    ".vscode",
]

# --- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_favicon = "_static/logo_SynopticPy_blue.svg"

html_theme_options = {
    "external_links": [
        {
            "name": "Herbie",
            "url": "https://herbie.readthedocs.io/",
        },
        {
            "name": "GOES-2-go",
            "url": "https://goes2go.readthedocs.io/",
        },
    ],
    "header_links_before_dropdown": 4,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/blaylockbk/SynopticPy",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/SynopticPy",
            "icon": "fa-custom fa-pypi",
        },
    ],
    "logo": {
        "test": "SynopticPy",
        "image_light": "_static/logo_SynopticPy_blue.svg",
        "image_dark": "_static/logo_SynopticPy_white.svg",
    },
    "use_edit_page_button": True,
    "show_toc_level": 1,
    "navbar_align": "left",
    "show_version_warning_banner": True,
    "navbar_center": ["version-switcher", "navbar-nav"],
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "switcher": {
        "json_url": "https://synopticpy.readthedocs.io/en/latest/_static/switcher.json",
        "version_match": os.environ.get("READTHEDOCS_VERSION"),
    },
}


html_sidebars = {}


html_context = {
    "github_user": "blaylockbk",
    "github_repo": "SynopticPy",
    "github_version": "main",
    "doc_path": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static", "../images"]
html_css_files = ["brian_style.css"]
html_js_files = []
todo_include_todos = True

# ---- Options for autosummary/autodoc output ---------------------------------

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "groupwise"

## Set autodoc defaults
autodoc_default_options = {
    #"autosummary": True,  # Include a members "table of contents"
    "members": True,  # Document all functions/members
    #"special-members": "__init__",
}

autodoc_mock_imports = [
    "numpy",
    "matplotlib",
    "polars",
    "cartopy",
]
