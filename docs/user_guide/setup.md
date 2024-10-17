# 🔨 Setup

You will need a Synoptic account and API token to request data.

1. Visit Synoptic's [Welcome](https://docs.synopticdata.com/services/welcome-to-synoptic-data-s-web-services) page to register for an account.
2. Navigate to your [Synoptic Data Credentials](https://customer.synopticdata.com/credentials/) and find your public tokens. You can generate a new token under the "Manage Tokens" tab, if needed.
3. Copy a **_public token_** (not your key!).

## Using Your Token in SynopticPy

Whenever you query data from Synoptic's Weather API, you need to provide your public token. You can specify this token in SynopticPy in three ways, listed in order of priority:

1. Set the `token=` argument when using a SynopticPy function;
2. Define the `SYNOPTIC_TOKEN` environment variable;
3. Configure a `~/.config/SynopticPy/config.toml` file.

### 1. Provide the token as an argument

You can directly provide the token when instantiating any `synoptic.services` class:

```python
import synoptic
df = synoptic.Metadata(
    stid='WBB',
    token="yourToken123456789"
).df()
```

If `token` is not provided, then SynopticPy looks for the token from an environment variable and then the config file.

### 2. Environment Variable

If you don't provide the token as an argument, SynopticPy will look for the `SYNOPTIC_TOKEN` environment variable.

For Linux users, you can add the following line to your `.bashrc`, `.profile`, or another shell configuration file:

```bash
export SYNOPTIC_TOKEN="yourToken123456789"
```

### 3. SynopticPy config file

Lastly, SynopticPy checks for the token in the `~/.config/SynopticPy/config.toml` file.

Your config file should look like this:

```toml
token = "yourToken123456789"
```

If no token is found when making an API query, SynopticPy will prompt you to enter your token and will create the `config.toml` file for you automatically.
