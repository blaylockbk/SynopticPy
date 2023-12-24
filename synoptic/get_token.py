## Brian Blaylock
## January 8, 2020

"""
======================
🎫 Synoptic API Token
======================
SynopticPy needs to know your public Synoptic API token.

You likely wont need to do anything with these functions.

The first time you import a ``synoptic.services`` function, it will
ask you for your API token and store that information in
``~/.config/SynopticPy/config.cfg``. You may edit that config file if
you need. Please refer to the :ref:`User Guide`. for more info.

"""

import os
from pathlib import Path

import requests
import toml


########################################################################
# Append Path object with my custom expand method so user can use
# environment variables in the config file (e.g., ${HOME}).
def _expand(self):
    """
    Fully expand and resolve the Path with the given environment variables.

    Example
    -------
    >>> Path('$HOME').expand()
    >>> PosixPath('/p/home/blaylock')
    """
    return Path(os.path.expandvars(self)).expanduser().resolve()


Path.expand = _expand


########################################################################
def test_token(config, verbose=True, configure_on_fail=True):
    """
    Test that the token can get data from Synoptic.

    If the test fails, the user is prompted with instructions to acquire
    a valid token. The user will be asked what the token is, and will
    save that info into the config file located at
    ``~/.config/SynopticPy/config.cfg``.

    Parameters
    ----------
    configure_on_fail : bool

        - True: Help the user update the config file with ``config_token``
        - False: Do not update (prevents infinite loop if user keeps adding an invalid token).

    verbose : bool

        - True: Print details as this function runs.
        - False: Do not print anything if the token check passes.

    Returns
    -------
    A valid API token

    """
    token = config["default"].get("token")

    if token in [None, ""]:
        # There isn't an API token defined, so configure one.
        return config_token(config)

    if verbose:
        print(f"🧪 Testing your token: {token}")

    # Test token with a quick metadata request for a single station
    URL = "https://api.synopticdata.com/v2/stations/metadata?"
    params = dict(stid="WBB", token=token)
    json = requests.get(URL, params).json()
    response = json["SUMMARY"]["RESPONSE_MESSAGE"]

    if response == "OK":
        if verbose:
            print(f"🔓 API Access Enabled. Response is [{response}].")
        return config
    else:
        print(f"🤦🏻‍♂️ Failed: {token} is not valid. {response}")
        print()
        print("----------------------------")
        print("Token Configuration Required")
        print("----------------------------")
        if configure_on_fail:
            config_token(config)
        else:
            print(
                f" ╭─SynopticPy──────────────────────────────────────────╮\n"
                f" │ ERROR: Please update config file with a valid token:│\n"
                f" │ {str(_config_file):^52s}│\n"
                f" ╰─────────────────────────────────────────────────────╯\n"
            )


def config_token(config, new_token=None):
    """Update the config.cfg file with your Synoptic API token.

    Parameters
    ----------
    new_token : None or str
        If None, the user will be asked to input the token (default).
        Else, the config file will be updated with `new_token`.

    Returns
    -------
    A valid API token, if it passes ``test_token``. Else, None.

    """
    # Read the config file and get the token
    token = config["default"].get("token")

    print(f"Config File: {_config_path}")
    if token is None:
        print("Current Token: 🕵🏻‍♂️ NOT ASSIGNED")
    else:
        print(f"Current Token: {token}")

    if new_token is None:
        print(msg)
        new_token = input("What is your Synoptic API token? >>> ")

    # Save the new_token to the config.toml file
    config["default"] = {**config["default"], **{"token": new_token}}

    try:
        with open(_config_file, "w") as f:
            toml.dump(config, f)

        print("\nThanks! I will do a quick test...")

        # Don't want to run into an infinite loop, so set configure_on_fail=False
        config = test_token(config, configure_on_fail=False)
        return config
    except:
        raise ValueError(
            f"\n"
            f" ╭─SynopticPy──────────────────────────────────────────╮\n"
            f" │ ERROR: Please update config file with a valid token:│\n"
            f" │ {str(_config_file):^52s}│\n"
            f" ╰─────────────────────────────────────────────────────╯\n"
        )


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
# token="1234567890abcdefghijklm"
#
# Or, if you have an environment variable SYNOPTIC_TOKEN set, then
# SynopticPy will use that token instead.
"""

msg = f"""
    ╭─SynopticPy───────────────────────────────────────────────────────────────╮
    │ Dear SynopticPy User,                                                    │
    │                                                                          │
    │ Thanks for installing SynopticPy. Before you get started, you            │
    │ need to register for a free Synoptic Data account and obtain an          │
    │ API token. Follow these instructions:                                    │
    │                                                                          │
    │ 1) Go to https://developers.synopticdata.com/mesonet/v2/getting-started/ │
    │    and click "Sign Up Now!" to register for an account.                  │
    │                                                                          │
    │ 2) Go to your profile settings and locate your public token at           │
    │    https://developers.synopticdata.com/settings/.                        │
    │    You may also generate a new token in the "Manage Tokens" tab,         │
    │    if desired.                                                           │
    │                                                                          │
    │ 3) Copy a public token (not your key!), and paste into this input        │
    │    dialogue. Or exit out of this dialog and edit the file                │
    │    {str(_config_file):^70s}│
    │    with your token.                                                      │
    │                                                                          │
    │ Good luck and happy programing! 🍀                                       │
    │ Brian Blaylock                                                           │
    ╰──────────────────────────────────────────────────────────────────────────╯\n
"""

########################################################################
# Load config file (create one if needed)
try:
    # Load the SynopticPy config file
    config = toml.load(_config_file)

    # Test the token.
    config = test_token(config, verbose=False)

except:
    try:
        # Create the SynopticPy config file
        _config_path.mkdir(parents=True, exist_ok=True)
        with open(_config_file, "w", encoding="utf-8") as f:
            f.write(default_toml)

        print(
            f" ╭─SynopticPy───────────────────────────────────────────╮\n"
            f" │ INFO: Created a default config file.                 │\n"
            f" │ You may view/edit SynopticPys's configuration here:  │\n"
            f" │ {str(_config_file):^53s}│\n"
            f" ╰──────────────────────────────────────────────────────╯\n"
        )

        # Load the new SynopticPy config file
        config = toml.load(_config_file)
    except (OSError, FileNotFoundError, PermissionError):
        print(
            f" ╭─SynopticPy──────────────────────────────────────────╮\n"
            f" │ WARNING: Unable to create config file               │\n"
            f" │ {str(_config_file):^53s}│\n"
            f" │ SynopticPy will use standard default settings.      │\n"
            f" │ Or, you may set env variable SYNOPTICPY_CONFIG_PATH.│\n"
            f" ╰─────────────────────────────────────────────────────╯\n"
        )
        config = toml.loads(default_toml)

# Test the token.
config = test_token(config, verbose=False)


if os.getenv("SYNOPTIC_TOKEN"):
    config["default"]["token"] = os.getenv("SYNOPTIC_TOKEN")
    print(
        " ╭─SynopticPy───────────────────────────────────────────╮\n"
        " │ INFO: Overriding the configured token because the    │\n"
        " │ environment variable SYNOPTIC_TOKEN is set.          │\n"
        " ╰──────────────────────────────────────────────────────╯\n"
    )
