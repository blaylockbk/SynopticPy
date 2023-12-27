"""Synoptic API for Python.

Retrieve and plot mesonet data from thousands of stations via the
Synoptic Data Weather API:
https://docs.synopticdata.com/services/weather-data-api.

Usage
-----
There are two recommended ways to import SynopticPy.

``` python
# Method 1: Import full module
import synoptic.services as ss
import synoptic.plots as sp
```

``` python
# Method 2: Import individual functions
from synoptic.services import stations_timeseries
```
"""

__author__ = "Brian K. Blaylock"
__email__ = "blaylockbk@gmail.com"
__url__ = "https://github.com/blaylockbk/SynopticPy"

import os
import re
import warnings
from pathlib import Path

import toml

from synoptic.token import TOKEN_HELP, Token
from synoptic.utils import ANSI

try:
    ## TODO: Will the `_version.py` file *always* be present?
    ## TODO: What if the person doesn't do "pip install"
    from ._version import __version__, __version_tuple__
except Exception as e:
    warnings.warn(
        f"Could not import version. Maybe you haven't done a pip install. {e}"
    )
    __version__ = "unknown"
    __version_tuple__ = (999, 999, 999)

# try:
#    from synoptic.accessors import *
# except Exception as e:
#    warnings.warn(f"Could not import synoptic.accessors. {e}")


########################################################################
# Overload Path object with my custom expand method so user can use
# environment variables in the config file (e.g., ${HOME}).
def _expand(self):
    """
    Fully expand and resolve the Path with the given environment variables.

    Example
    -------
    >>> Path('$HOME').expand()
    PosixPath('/p/home/blaylock')
    """
    return Path(os.path.expandvars(self)).expanduser().resolve()


Path.expand = _expand


########################################################################
# Location of SynopticPy's configuration file
_config_path = os.getenv("SYNOPTICPY_CONFIG_PATH", "~/.config/SynopticPy")
_config_path = Path(_config_path).expand()
_config_file = _config_path / "config.toml"

# Default TOML Configuration Values
default_toml = """# SynopticPy defaults
['default']
verbose = true
hide_token = true
rename_value_1 = true
rename_set_1 = true
token = ""

# ======================================================================
# The first time you import SynopticPy, you will be asked to input your
# Synoptic API token. If you have issues, you can edit this file with
# your valid token directly. For example:
#
# Or, if you have an environment variable SYNOPTIC_TOKEN set, then
# SynopticPy will use that token instead.
"""


def configure_token(token=None, config_file=_config_file):
    """Update the SynopticPy config file with a new Synoptic API token.

    Parameters
    ----------
    token : str or Token
        A valid Synoptic API token
    config_file : str or Path
        Path to the config file.
    """
    if not isinstance(token, Token):
        token = Token(token)

    if not token.is_valid():
        raise ValueError(
            f"\n"
            f"╭─SynopticPy ERROR────────────────────────────────────╮\n"
            f"│ Invalid Token.                                      │\n"
            f"│ {ANSI.text(token, ANSI.GREEN):<52s}│\n"
            f"│ Please manually update the config file:             │\n"
            f"│ {str(config_file):^52s}│\n"
            f"╰─────────────────────────────────────────────────────╯"
            f"{TOKEN_HELP}"
        )

    with open(config_file) as file:
        file_content = file.read()

    new_content = re.sub(r"""token\s?=\s?\".*\"""", f'token = "{token}"', file_content)

    with open(config_file, "w") as file:
        file.write(new_content)

    print(
        f"╭─SynopticPy INFO──────────────────────────────────────╮\n"
        f"│ Updated config file with new token.                  │\n"
        f"│ {str(config_file):^53s}│\n"
        f"╰──────────────────────────────────────────────────────╯"
    )


########################################################################
# Load config file (create one if needed)
try:
    # Load the SynopticPy config file if possible
    config = toml.load(_config_file)

    if os.getenv("SYNOPTIC_TOKEN"):
        config["default"]["token"] = os.getenv("SYNOPTIC_TOKEN")
    elif config["default"].get("token") in [None, ""]:
        configure_token()
        config = toml.load(_config_file)

except Exception:
    try:
        # Create the SynopticPy config file
        _config_path.mkdir(parents=True, exist_ok=True)
        with open(_config_file, "w", encoding="utf-8") as f:
            f.write(default_toml)

        print(
            f"╭─SynopticPy INFO──────────────────────────────────────╮\n"
            f"│ Created a default config file.                       │\n"
            f"│ You may view/edit SynopticPys's configuration here:  │\n"
            f"│ {str(_config_file):^53s}│\n"
            f"│ but it still needs your Synoptic API token.          │\n"
            f"╰──────────────────────────────────────────────────────╯"
        )

        # Ask user for their token and put it in the configure file.
        configure_token()

        # Load the new SynopticPy config file
        config = toml.load(_config_file)

    except (OSError, FileNotFoundError, PermissionError):
        print(
            f"╭─SynopticPy WARNING──────────────────────────────────╮\n"
            f"│ Failed to create the config file                    │\n"
            f"│ {str(_config_file):^52s}│\n"
            f"│                                                     │\n"
            f"│ SynopticPy will use standard default settings,      │\n"
            f"│ just be sure to give your API token when request.   │\n"
            f"│                                                     │\n"
            f"│ You could try setting the environment variable      │\n"
            f"│ {ANSI.text('SYNOPTICPY_CONFIG_PATH', ANSI.CYAN)} to write the conf file to a  │\n"
            f"│ different path, or you can use these default        │\n"
            f"│ settings and set the env variable {ANSI.text('SYNOPTIC_TOKEN', ANSI.CYAN)}.   │\n"
            f"╰─────────────────────────────────────────────────────╯"
        )
        config = toml.loads(default_toml)

if os.getenv("SYNOPTIC_TOKEN"):
    print(
        "╭─SynopticPy INFO──────────────────────────────────────╮\n"
        "│ Overriding the configured token because the          │\n"
        "│ environment variable SYNOPTIC_TOKEN is set.          │\n"
        "╰──────────────────────────────────────────────────────╯"
    )
    config["default"]["token"] = os.getenv("SYNOPTIC_TOKEN")

# Make the token item a Token object
TOKEN = Token(config["default"]["token"])
config["default"]["token"] = TOKEN

if not TOKEN.is_valid(verbose=False):
    print(
        f"╭─SynopticPy ERROR─────────────────────────────────────╮\n"
        f"│ Sorry, {ANSI.text(TOKEN, ANSI.GREEN):42s} │\n"
        f"│ is not a valid token. Edit the config file manually  │\n"
        f"│ {str(_config_file):^53s}│\n"
        f"│ or set the environment variable SYNOPTIC_TOKEN.      │\n"
        f"╰──────────────────────────────────────────────────────╯"
    )

