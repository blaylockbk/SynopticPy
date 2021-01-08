# 🔨 Setup

Before you can retrieve data from the Synoptic API, **you need to register as a Synoptic user and obtain a _token_**. Follow the instructions at the [Getting Started Page](https://developers.synopticdata.com/mesonet/v2/getting-started/). When you have a token, edit `synoptic/config.cfg` with your personal API **token**, _not your API key_. The config file should look should look something like this:
    
```
[Synoptic]
token = 1234567890abcdefg
```

If you don't do this step, don't worry. When you import `synoptic.services`,
a quick check will make sure the token in the config file is valid. If not,
you will be prompted to update the token in the config file.