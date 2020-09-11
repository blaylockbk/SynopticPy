## Brian Blaylock
## September 11, 2020
"""
==================
Synoptic API Token
==================

.. note::
    Dear fellow weather enthusiast,

    Thanks for trying this package to retrieve data from the Synoptic Data API.
    To get started, you must set up a Synoptic account and create a "token". 
    This is done on the Synoptic Data website: 
    https://developers.synopticdata.com/mesonet/v2/getting-started/.
    After you create a token, edit the variable below with your token.

    I import my token from a file hidden from GitHub. You don't need to worry 
    about those lines of code below the `token` assignment. Those are just for
    me.

    Good luck! 🍀 
    Brian Blaylock
"""

token = 'YOUR_TOKEN_HERE'

##=============================================================================
## You can ignore the following. It's just Brian loading his token.
##=============================================================================
if token == 'YOUR_TOKEN_HERE':
    try:
        from synoptic.get_credentials import get_MW_token
        token = get_MW_token()['token']
    except:
        # whoops, you haven't set your token yet.
        print("🎺 Please edit the file`synoptic.mytoken.py` with your token.")
##=============================================================================