## Brian Blaylock
## September 11, 2020
"""
==================
Synoptic API Token
==================
The first time you import a synoptic.services function, it will check
the API token in the config file. You can manually update that file, or
let this script help you update it.
"""
import configparser
from pathlib import Path
import requests

# Directory of this file:
BASE = Path(__file__).parent

# Brian's has a special configuration file that is not passed to GitHub.
# If that doesn't exist, then the default config file is used.
brians_config = BASE / 'BB_config.cfg'
default_config = BASE / 'config.cfg'

if brians_config.is_file():
    _config_path = brians_config.resolve()
else:
    _config_path = default_config.resolve()


msg = f'''
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
'''

def test_token(verbose=True, configure_on_fail=True):
    """
    Test that the token in ``./config.cfg`` can get data from Synoptic.
    
    If the test fails, the user is prompted with instructions to acquire
    a valid token. The user will be asked what the token is, and will
    save that info into the config file.
    
    Parameters
    ----------
    configure_on_fail : bool
        True - Help the user update the config file with ``config_token``
        False - Don't update (prevents infinant loop if user keeps
                adding an invalid token).
    verbose : bool
        True - Print lots of details as this function runs.
        False - Don't print anything if the token check passes.

    Returns
    -------
    A valid API token
    """
    
    # Get the token from config.cfg
    config = configparser.ConfigParser()
    config.read(_config_path)
    token = config.get('API', 'token')
    if token == '':
        # There isn't an API token defined, so configure one.
        return config_token()
    
    if verbose: print(f"🧪 Testing your token: {token}")
    
    # Test with a quick metadata request for a single station
    URL = f'https://api.synopticdata.com/v2/stations/metadata?'
    params = dict(stid='WBB', token=token)
    json = requests.get(URL, params).json()
    response = json['SUMMARY']['RESPONSE_MESSAGE']
    
    if response == 'OK':
        if verbose: print(f"👨🏻‍🎓 Passed. Response is {response}.")
        return token
    else:
        print(f"🤦🏻‍♂️ Failed: {token} is not valid. {response}")
        print()
        print('----------------------------')
        print('Token Configuration Required')
        print('----------------------------')
        if configure_on_fail:
            config_token()
        else:
            print(f'⚠')
            print(f'⚠ Please update {_config_path} with a valid token.')
            print(f'⚠')

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
    A valid API token if it passes test_token. Else, None.
    """
    # Get the current token value to display
    config = configparser.ConfigParser()
    config.read(_config_path)
    token = config.get('API', 'token')

    print(f"Config File: {_config_path}")
    if token == '':
        print(f"Current Token: 🕵🏻‍♂️ NOT ASSIGNED")
    else:
        print(f"Current Token: {token}")

    if new_token is None:
        print(msg)
        new_token = input('What is your Synoptic API token? >>> ')

    # Save the new_token to the config.cfg file
    config['API']['token'] = new_token
    with open(_config_path, 'w') as configfile:
        config.write(configfile)

    print(f'\nThanks! I will do a quick test...')
    # Don't want to run into an infinite loop, so set config_on_fail=False
    token = test_token(configure_on_fail=False) 
    return token

#####################################
# Get the token from the config file.
#####################################
token = test_token(verbose=False)
