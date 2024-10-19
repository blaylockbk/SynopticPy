"""
🎫 Configure Synoptic API Token.

SynopticPy needs to know your public Synoptic API token.

It looks for your token in this order:

1. The class constructor argument ``token='...'``
2. The environment variable ``SYNOPTIC_TOKEN``
3. The SynopticPy config file ``~/.config/SynopticPy/config.toml``

The first time you `import synoptic`, it will
ask for your API token and store that information in
``~/.config/SynopticPy/config.cfg``. You may edit that config file if
you need.

"""

import os
from pathlib import Path

import requests
import toml

# Location of SynopticPy's configuration file
_config_path = os.getenv("SYNOPTICPY_CONFIG_PATH", "~/.config/SynopticPy")
_config_path = Path(_config_path).expanduser()
_config_file = _config_path / "config.toml"

# Default TOML Configuration Values
DEFAULT_TOML = """# SynopticPy needs to know your public Synoptic API token.
# That token can be stored in this file or set as
# an environment variable SYNOPTIC_TOKEN.

token = ""
verbose = false
"""

MESSAGE = f"""
    ╭─SynopticPy───────────────────────────────────────────────────────────────╮
    │ Dear SynopticPy User,                                                    │
    │                                                                          │
    │ Thanks for installing SynopticPy. Before you get started, you            │
    │ need to register for a free Synoptic Data account and obtain an          │
    │ API token. Follow these instructions:                                    │
    │                                                                          │
    │ 1) Go to https://customer.synopticdata.com/activate/                     │
    │    and create a new account or log into your account.                    │
    │                                                                          │
    │ 2) Go to your profile settings and locate your public token at           │
    │    https://customer.synopticdata.com/credentials/.                       │
    │    You may also generate a new token in the "Public Tokens" section.     │
    │                                                                          │
    │ 3) Copy a public token (not your key!), and paste into this input        │
    │    dialogue. Or exit out of this dialog and edit the file                │
    │    {str(_config_file):^70s}│
    │    with your token.                                                      │
    │                                                                          │
    │ Good luck and happy programming! 🍀                                      │
    │ Brian Blaylock                                                           │
    ╰──────────────────────────────────────────────────────────────────────────╯\n
"""


def test_token(
    token: str,
    verbose: bool = True,
) -> bool:
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
    if token in [None, ""]:
        return False

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
        return True
    else:
        print(f"🤦🏻‍♂️ Failed: {token} is not valid. {response}")
        print(
            f" ╭─SynopticPy──────────────────────────────────────────╮\n"
            f" │ ERROR: Please update config file with a valid token:│\n"
            f" │ {str(_config_file):^52s}│\n"
            f" ╰─────────────────────────────────────────────────────╯\n"
        )
        return False


def config_token(config_file: Path, token=None):
    """Update the config.toml file with your Synoptic API token.

    Parameters
    ----------
    config_file : Path
    token : None or str
        If None, the user will be asked to input the token (default).
        Else, the config file will be updated with `token`.

    Returns
    -------
    A valid API token, if it passes `test_token`. Else, None.
    """
    print(f"Config File: {config_file}")
    token = config.get("token")

    if token is None:
        print(MESSAGE)
        token = input("What is your Synoptic API token? >>> ")

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
# Load config file (create one if needed)

# Check if SYNOPTIC_TOKEN is set and valid
if test_token(os.getenv("SYNOPTIC_TOKEN")):
    print("Valid token set by SYNOPTIC_TOKEN.")
elif test_token(toml.load(_config_file)["token"]):
    print(f"Valid token set in {_config_file}.")
else:
    try:
        # Create the SynopticPy config file
        _config_path.mkdir(parents=True, exist_ok=True)
        with open(_config_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_TOML)

        print(
            f" ╭─SynopticPy───────────────────────────────────────────╮\n"
            f" │ INFO: Created a default config file.                 │\n"
            f" │ You may view/edit SynopticPys's configuration here:  │\n"
            f" │ {str(_config_file):^53s}│\n"
            f" ╰──────────────────────────────────────────────────────╯\n"
        )

        config_token(_config_file)

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
        config = toml.loads(DEFAULT_TOML)
