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

import tomllib
import os
import re
from pathlib import Path
import requests

# Default TOML Configuration Values
DEFAULT_TOML = """# SynopticPy needs to know your public Synoptic API token.
# That token can be stored in this file or set as
# an environment variable SYNOPTIC_TOKEN.

token = ""
hide_token = true
verbose = false
"""

TOKEN_WELCOME = """
    ╭─SynopticPy:WELCOME─────────────────────────────────────────────────────╮
    │                                                                        │
    │ Welcome to SynopticPy.                                                 │
    │                                                                        │
    │ Before you get started, you need a Synoptic account and valid Synoptic │
    │ API token. To get started with the open-access datasets,               │
    │                                                                        │
    │ 1) Go to https://customer.synopticdata.com/signup/                     │
    │    and create a new account or log into your account.                  │
    │                                                                        │
    │ 2) You can view, create, and manage your API tokens at                 │
    │    https://customer.synopticdata.com/credentials/.                     │
    │                                                                        │
    ╰────────────────────────────────────────────────────────────────────────╯
"""

TOKEN_HELP = f"""
    ╭─SynopticPy:HELP────────────────────────────────────────────────────────╮
    │                                                                        │
    │ A valid Synoptic token is required.                                    │
    │                                                                        │
    │ You can sign up for a free open-access acount at                       │
    │ https://customer.synopticdata.com/signup/                              │
    │                                                                        │
    ├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
    │                                                                        │
    │ Do one of the following:                                               │
    │                                                                        │
    │  1) Specify {ANSI.text('token="YoutTokenHere"', ANSI.GREEN)} in your request.                     │
    │                                                                        │
    │  2) Set the environment variable {ANSI.text('SYNOPTIC_TOKEN', ANSI.BOLD)}.                       │
    │                                                                        │
    │  3) Configure a token in {ANSI.text('~/.config/SynopticPy/config.toml', ANSI.MAGENTA)}              │
    │                                                                        │
    ╰────────────────────────────────────────────────────────────────────────╯
"""


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

        Examples
        --------
        >>> print(f"Color {ANSI.text('me', ANSI.GREEN)}.")
        """
        return f"{color}{text}{ANSI.RESET}"


class Token:
    """Synoptic API Token for validating and storing API access credentials.

    A Synoptic API public token is 32-characters string. You can create
    a new token or find existing tokens in your Synoptic account at
    https://customer.synopticdata.com/credentials/

    Parameters
    ----------
    token : str
        A Synoptic API token.

    Examples
    --------
    >>> myToken = Token("123abc")
    >>> myToken.is_valid()
    False
    """

    CONFIG_PATH = Path(
        os.getenv("SYNOPTICPY_CONFIG_PATH", "~/.config/SynopticPy")
    ).expanduser()
    CONFIG_FILE = CONFIG_PATH / "config.toml"

    def __init__(self, token: str | None = None):
        """Initialize Token instance, attempting to retrieve token if not provided."""
        self.source = "user"
        self.token = token or self._retrieve_token()

    def __str__(self):  # noqa: D105
        return self.token

    def __repr__(self):  # noqa: D105
        return f"🎫 Synoptic API token: {ANSI.text(self.token, ANSI.GREEN)} ({self.source})"

    def _retrieve_token(self):
        """Retrieve token from environment, config, or prompt user for input."""
        self.source = "environment variable"
        return (
            os.getenv("SYNOPTIC_TOKEN")
            or self._get_token_from_config()
            or self._prompt_user_for_token()
        )

    def _get_token_from_config(self):
        """Retrieve token from configuration file, if available."""
        if self.CONFIG_PATH.exists():
            with open(self.CONFIG_FILE, "rb") as f:
                self.source = "config file"
                return tomllib.load(f).get("token")
        return None

    def _prompt_user_for_token(self):
        """Prompt user to enter a token if not found in environment or config."""
        print(TOKEN_WELCOME)
        self.source = "user input"
        return input("Enter your Synoptic API token: ").strip()

    def is_valid(self, *, configure_on_fail=False, verbose=False) -> bool:
        """Check if the token is valid by making a test request to the API."""
        if verbose:
            print(f"🧪 Testing token={ANSI.text(self.token, ANSI.GREEN)}")

        # Make an simple API request to test token validity.
        URL = "https://api.synopticdata.com/v2/stations/metadata"
        params = dict(stid="WBB", token=self.token)
        response = requests.get(URL, params).json()
        response = response["SUMMARY"]["RESPONSE_MESSAGE"]

        if response == "OK":
            if verbose:
                print("🔓 Token is valid.")
            return True
        else:
            print(
                f"Token '{ANSI.text(self.token, ANSI.RED)}' is invalid.\n"
                f"Response: {ANSI.text(response, ANSI.RED)}.\n"
                "Please update your token or sign up at: https://customer.synopticdata.com/signup/"
            )
            if configure_on_fail:
                self.token = self._prompt_user_for_token()
                if self.is_valid():
                    self.update_config_file()
            else:
                print(TOKEN_HELP)
            return False

    def update_config_file(self, verbose=True):
        """Update the config file with the current token if it's valid."""
        if not self.is_valid():
            raise ValueError("Cannot save an invalid token.")

        content = self._read_config_file()
        updated_content = re.sub(r'token=".*?"', f'token="{self.token}"', content)

        with open(self.CONFIG_FILE, "w") as file:
            file.write(updated_content)

        if verbose:
            print(f"📝 Token updated in {self.CONFIG_FILE}.")

    def _read_config_file(self):
        """Read the config file, returning default content if not found."""
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE) as f:
                return f.read()
        return DEFAULT_TOML
