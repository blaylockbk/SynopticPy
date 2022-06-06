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
import toml
from pathlib import Path
import requests

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
# SynopticPy configuration file
# Configuration file is save in `~/config/SynopticPy/config.toml`
_config_path = Path("~/.config/SynopticPy/config.toml").expand()

########################################################################
# Default TOML Configuration
# (we will ask the user to input their API token interactively)
default_toml = f"""
['default']
verbose = true
hide_token = true
rename_value_1 = true
rename_set_1 = true
"""

########################################################################
# If a config file isn't found, make one
if not _config_path.exists():
    print(
        f" ╭─────────────────────────────────────────────────╮\n"
        f" │ I'm building SynopticPy's default config file.  │\n"
        f" ╰╥────────────────────────────────────────────────╯\n"
        f" 👷🏻‍♂️"
    )
    _config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(_config_path, "w") as f:
        toml_string = toml.dump(toml.loads(default_toml), f)
    print(f"⚙ Created config file [{_config_path}] with default values.")

msg = f"""
    | Dear SynopticPy User,
    |
    | Thanks for installing SynopticPy. Before you get started, you
    | need to register for a free Synoptic Data account and obtain an
    | API token. Follow these instructions:
    |
    | 1) Go to https://developers.synopticdata.com/mesonet/v2/getting-started/
    |    and click "Sign Up Now!" to register for an account.
    |
    | 2) Go to your profile settings and locate your public token at
    |    https://developers.synopticdata.com/settings/.
    |    You may also generate a new token in the "Manage Tokens" tab,
    |    if desired.
    |
    | 3) Copy a public token (not your key!), and paste into this input
    |    dialogue. Or exit out of this dialog and edit the file
    |    {_config_path} with your token.
    |
    | Good luck and happy programing! 🍀
    | Brian Blaylock
"""


def test_token(verbose=True, configure_on_fail=True):
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
        - False: Do not update (prevents infinant loop if user keeps adding an invalid token).

    verbose : bool

        - True: Print details as this function runs.
        - False: Do not print anything if the token check passes.

    Returns
    -------
    A valid API token

    """
    # Read the config file and get the token
    config = toml.load(_config_path)
    token = config["default"].get("token")

    if token is None:
        # There isn't an API token defined, so configure one.
        return config_token()

    if verbose:
        print(f"🧪 Testing your token: {token}")

    # Test with a quick metadata request for a single station
    URL = f"https://api.synopticdata.com/v2/stations/metadata?"
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
            config_token()
        else:
            print(f"⚠")
            print(f"⚠ Please update {_config_path} with a valid token.")
            print(f"⚠")


def config_token(new_token=None):
    """
    Update the config.cfg file with your Synoptic API token

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
    config = toml.load(_config_path)
    token = config["default"].get("token")

    print(f"Config File: {_config_path}")
    if token is None:
        print(f"Current Token: 🕵🏻‍♂️ NOT ASSIGNED")
    else:
        print(f"Current Token: {token}")

    if new_token is None:
        print(msg)
        new_token = input("What is your Synoptic API token? >>> ")

    # Save the new_token to the config.toml file
    config["default"] = {**config["default"], **{"token": new_token}}

    with open(_config_path, "w") as f:
        toml.dump(config, f)

    print(f"\nThanks! I will do a quick test...")

    # Don't want to run into an infinite loop, so set config_on_fail=False
    config = test_token(configure_on_fail=False)
    return config


#####################################
# Get the token from the config file.
#####################################

config = test_token(verbose=False)
