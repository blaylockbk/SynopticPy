"""🎫 Synoptic API Token.

SynopticPy needs to know your public Synoptic API token.

Note that the first time you import a `synoptic.services` function,
SynopticPy will ask you for your API token and store that information in
`~/.config/SynopticPy/config.cfg`. You may edit that config file if
needed.
"""

import requests

from synoptic.utils import ANSI

TOKEN_HELP = (
    "╭─SynopticPy HELP──────────────────────────────────────────────────────────╮\n"
    "│                                                                          │\n"
    "│ Welcome to SynopticPy.                                                   │\n"
    "│                                                                          │\n"
    "│ Before you get started, you need a Synoptic account and valid Synoptic   │\n"
    "│ API token. To get started with the open-access datasets,                 │\n"
    "│                                                                          │\n"
    "│ 1) Go to https://synopticdata.com/pricing/open-access-pricing/ and       │\n"
    "│    select 'Get Started' to create your new, free Synoptic account.       │\n"
    "│                                                                          │\n"
    "│ 2) When logged into your account, you can view and manage your API       │\n"
    "│    credentials at https://customer.synopticdata.com/credentials/.        │\n"
    "│                                                                          │\n"
    "╰──────────────────────────────────────────────────────────────────────────╯"
)


class Token:
    """Synoptic API Token.

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

    def __init__(self, token=None):
        if token in [None, ""]:
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
                print(
                    f"🔓 Synoptic API access with token is {ANSI.text(response, ANSI.GREEN)}."
                )
            return True

        else:
            print(
                f"🤦🏻‍♂️ ERROR: {ANSI.text(self.token, ANSI.GREEN)} is not a valid Synoptic API token. "
                f"{ANSI.text(response, ANSI.RED)}."
            )
            print(
                "Try a different token or create a new one at https://customer.synopticdata.com/credentials/."
            )
            return False
