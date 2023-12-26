## Brian Blaylock
## January 8, 2020

"""🎫 Synoptic API Token.

SynopticPy needs to know your public Synoptic API token.

The first time you import a `synoptic.services` function, it will
ask you for your API token and store that information in
`~/.config/SynopticPy/config.cfg`. You may edit that config file if
you need.
"""

import os
import re
from pathlib import Path

import requests
import toml


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


TOKEN_HELP = """
   ╭─SynopticPy HELP──────────────────────────────────────────────────────────╮
   │ Dear SynopticPy User,                                                    │
   │                                                                          │
   │ Thanks for installing SynopticPy. Before you get started, you            │
   │ need a valid Synoptic API token. To use the open-access datasets:        │
   │                                                                          │
   │ 1) Go to https://synopticdata.com/pricing/open-access-pricing/ and       │
   │    select 'Get Started' to create your new, free account.                │
   │                                                                          │
   │ 2) When logged in, you can manage your API credentials at                │
   │    https://customer.synopticdata.com/credentials/                        │
   │    Here you can view and generate new public tokens.                     │
   ╰──────────────────────────────────────────────────────────────────────────╯
"""

########################################################################


class ANSI:
    """ANSI color and escape codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"

    # Text color codes
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background color codes
    BLACK_BG = "\033[40m"
    RED_BG = "\033[41m"
    GREEN_BG = "\033[42m"
    YELLOW_BG = "\033[43m"
    BLUE_BG = "\033[44m"
    MAGENTA_BG = "\033[45m"
    CYAN_BG = "\033[46m"
    WHITE_BG = "\033[47m"

    @staticmethod
    def text(text, color):
        """Show ANSI-colored text.

        Usage
        -----
        >>> print(f"Color {ANSI.text('me', ANSI.GREEN)}.")
        """
        return f"{color}{text}{ANSI.RESET}"


class Token:
    """Synoptic API Token.

    A Synoptic API public token is 32-characters string. You can create
    a new token or find existing tokens at your Synoptic account at
    https://customer.synopticdata.com/credentials/

    Parameters
    ----------
    token : str
        Your Synoptic API token.

    Usage
    -----
    >>> myToken = Token("123abc")
    >>> myToken.is_valid
    False
    """

    def __init__(self, token=None):
        if token is None:
            print(TOKEN_HELP)
            self.token = input("What is your Synoptic API token? >>> ").strip()
        else:
            self.token = token.strip()

    def __str__(self):
        """Token's string representation."""
        return self.token

    def __repr__(self):
        """Representation of the Token class."""
        return f"🎫 Synoptic API token: {ANSI.text(self.token, ANSI.GREEN)}"

    def is_valid(self, verbose=True):
        """Test that the token is valid."""
        if verbose:
            print(f"🧪 Testing token {ANSI.text(self.token, ANSI.GREEN)}")

        # Test token with a quick metadata request for a single station
        URL = "https://api.synopticdata.com/v2/stations/metadata?"
        params = dict(stid="WBB", token=self.token)
        json = requests.get(URL, params).json()
        response = json["SUMMARY"]["RESPONSE_MESSAGE"]

        if response == "OK":
            if verbose:
                print(f"🔓 Access with token is {ANSI.text(response, ANSI.GREEN)}.")
            return True

        else:
            print(
                f"🤦🏻‍♂️ ERROR: {ANSI.text(self.token, ANSI.GREEN)} is not a valid Synoptic API token. {ANSI.text(response, ANSI.RED)}"
            )
            return False


def configure_token(token=None):
    """Update the SynopticPy config file with a new Synoptic API token."""
    if token is None:
        print(TOKEN_HELP)
        token = input("What is your Synoptic API token? >>> ")

    if not isinstance(token, Token):
        token = Token(token)

    if not token.is_valid():
        raise ValueError(
            f"\n"
            f"╭─SynopticPy ERROR────────────────────────────────────╮\n"
            f"│ Invalid Token.                                      │\n"
            f"│ {ANSI.text(token, ANSI.GREEN):<52s}│\n"
            f"│ Will not update config.                             │\n"
            f"│ Please update config file with a valid token:       │\n"
            f"│ {str(_config_file):^52s}│\n"
            f"╰─────────────────────────────────────────────────────╯\n"
            f"{TOKEN_HELP}"
        )

    # Read the contents of the config file
    with open(_config_file) as file:
        file_content = file.read()

    # Replace the token in the content with the new token
    updated_content = re.sub(r"token\s?=\s?.*", f'token = "{token}"', file_content)

    # Write the updated content back to the file
    with open(_config_file, "w") as file:
        file.write(updated_content)

    print(f"Updated {str(_config_file)} with new token.")


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


########################################################################
# Load config file (create one if needed)
try:
    # Load the SynopticPy config file
    config = toml.load(_config_file)

except:
    try:
        # Create the SynopticPy config file
        _config_path.mkdir(parents=True, exist_ok=True)
        with open(_config_file, "w", encoding="utf-8") as f:
            f.write(default_toml)

        print(
            f" ╭─SynopticPy INFO──────────────────────────────────────╮\n"
            f" │ Created a default config file.                       │\n"
            f" │ You may view/edit SynopticPys's configuration here:  │\n"
            f" │ {str(_config_file):^53s}│\n"
            f" ╰──────────────────────────────────────────────────────╯\n"
        )

        # Ask user for their token and put it in the configure file.
        configure_token()

        # Load the new SynopticPy config file
        config = toml.load(_config_file)
    except (OSError, FileNotFoundError, PermissionError):
        print(
            f" ╭─SynopticPy WARNING──────────────────────────────────╮\n"
            f" │ Unable to create config file                        │\n"
            f" │ {str(_config_file):^53s}│\n"
            f" │ SynopticPy will use standard default settings.      │\n"
            f" │ Or, you may set env variable SYNOPTICPY_CONFIG_PATH.│\n"
            f" ╰─────────────────────────────────────────────────────╯\n"
        )
        config = toml.loads(default_toml)

if os.getenv("SYNOPTIC_TOKEN"):
    config["default"]["token"] = os.getenv("SYNOPTIC_TOKEN")
    print(
        " ╭─SynopticPy INFO──────────────────────────────────────╮\n"
        " │ Overriding the configured token because the          │\n"
        " │ environment variable SYNOPTIC_TOKEN is set.          │\n"
        " ╰──────────────────────────────────────────────────────╯\n"
    )

# Test the token is valid
if not Token(config["default"]["token"]).is_valid():
    print(
        "ERROR: Config file's token is not valid."
        "Maybe you can edit the config file manually to correct the issue."
    )

# =============================================================================
# That's all. You should have access to the config variable with a valid token.
