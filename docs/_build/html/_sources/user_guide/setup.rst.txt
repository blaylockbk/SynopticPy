===========
🔨 Setup
===========

Register for a Synoptic developers account and obtain a token
-------------------------------------------------------------
Before you can retrieve data from the Synoptic API, **you need to register as a Synoptic user and obtain a *token***. Follow the instructions at the `Getting Started Page <https://developers.synopticdata.com/mesonet/v2/getting-started/>`_.

1. Go to the `Get Started <https://developers.synopticdata.com/mesonet/v2/getting-started/>`_ page and click **Sign Up Now!** to register for an account.
2. After registering for your account, go to your `profile settings <https://developers.synopticdata.com/settings/>`_ and locate your public token. You may also generate a new token in the "Manage Tokens" tab, if desired.
3. Copy a public token (not your key!).

Configure SynopticPy with your token
------------------------------------
SynopticPy needs to know your token. The first time you import ``synoptic.services`` it will help you setup your token in its config file.

1. Open python in a terminal and type the following:

.. code-block:: python

    import synoptic.services

2. You will be prompted with instructions for acquiring an API token, and then it will ask you to input your token. Remember to enter you API **token** and *not your API key*.

.. code-block::

    What is your Synoptic API token? >>>

3. The script updates a config file located at ``~/.config/SynopticPy/config.toml``. 
    
Every time you import a ``synoptic.services`` function it does a quick check to make sure the token in that file is valid. If everything looks good, the next time you import the module you won't be asked for the token because it is saved in that config file.

Configure Settings
------------------

The first time you import ``synoptic.services``, a new config file is created here: ``~/.config/SynopticPy/config.toml``

Is should look something like this:

.. code-block::

    [default]
    verbose = true
    hide_token = true
    rename_value_1 = true
    rename_set_1 = true
    token = "1234567890abcdefghijklmnopqrstuvwxyz"

verbose
    Print extra info to the screen during the API request.

hide_token
    If true, hide the API token from being printed to the screen.
    If false, your token will be displayed

rename_value_1
    If true, strip "_value_1" and "_value_1d" from the columns variable name. I prefer that the column names strips this part of the string to more easily key in on the variables I want. For situations where there are both
    "_value_1" and "_value_1d" for a variable, only the most recent value will be renamed. 
    
    If false, preserve original column names.

    *Valid for **stations.latest** and **stations.nearesttime**.*

rename_set_1
    If true, strip "_set_1" and "_set_1d" from the columns variable name. I prefer that the column names strips this part of the string to more easily key in on the variables I want. For situations where there are both "_set_1" and "_set_1d" for a variable, only the column with the most non-NaN values will be renamed. 

    If false, preserve original column names.

    *Valid for **stations.timeseries**.*

token
    Your Synoptic API token. 
