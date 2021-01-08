# 🔨 Setup

## Register for a Synoptic developers account and obtain a token
Before you can retrieve data from the Synoptic API, **you need to register as a Synoptic user and obtain a _token_**. Follow the instructions at the [Getting Started Page](https://developers.synopticdata.com/mesonet/v2/getting-started/). 
1. Go to the [Get Started](https://developers.synopticdata.com/mesonet/v2/getting-started/) page and click **Sign Up Now!** to register for an account.
2. After registering for your account, go to your [profile settings](https://developers.synopticdata.com/settings/) and locate your public token. You may also generate a new token in the "Manage Tokens" tab, if desired.
3. Copy a public token (not your key!).

## Configure SynopticPy with your token
SynopticPy needs to know your token. The first time you import `synoptic.services` it will help you setup your token in its config file.

1. Open python in a terminal and type the following:
```python
import synoptic.services
```

2. You will be prompted with instructions for aquiring an API token, and then it will ask you to input your token. Remember to enter you API **token** and _not your API key_.

```
What is your Synoptic API token? >>>
```

3. The script updates a config file located at `~/.config/SynopticPy/config.cfg`. If you are having problems, that file should look something like this:
    
```
[Synoptic]
token = 1234567890abcdefg
```

Every time you import a `synoptic.services` function it does a quick check to make sure the token in that file is valid. If everything looks good, the next time you import the module you won't be asked for the token because it is saved in that config file.