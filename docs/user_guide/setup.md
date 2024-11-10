# 🔨 Setup

You will need a Synoptic account and API token to request data.

1. Visit Synoptic's [Welcome](https://docs.synopticdata.com/services/welcome-to-synoptic-data-s-web-services) page to register for an account.
2. Navigate to your [Synoptic Data Credentials](https://customer.synopticdata.com/credentials/) and find your public tokens. You can generate a new token under the "Manage Tokens" tab, if needed.
3. Copy a **_public token_** (not your key!).

## Using Your Token in SynopticPy

Whenever you query data from Synoptic's Weather API, you need to provide your public token. You can specify this token in SynopticPy in three ways, listed in order of priority:

1. Set the `SYNOPTIC_TOKEN` environment variable with your token;
1. Configure a `~/.config/SynopticPy/config.toml` file with your token;
1. Set the `token=` argument when using any `synoptic.services` class.

### 1. Environment Variable

SynopticPy first looks for your token in the `SYNOPTIC_TOKEN` environment variable.

For Linux users, you can add the following line to your `.bashrc`, `.profile`, or another shell configuration file:

```bash
export SYNOPTIC_TOKEN="yourToken123456789"
```

### 2. SynopticPy config file

You can create a SynopticPy configuration file and set your token with the following Python code:

```python
import synoptic
synoptic.configure(token="yourToken123456789")
```

This creates a new file `~/.config/SynopticPy/config.toml` file with your token. Restart your Python instance, and the next time you `import synoptic` it will use the token value stored in the `config.toml` file.

### 3. Provide the token as an argument

Lastly, you can directly provide the token when instantiating any `synoptic.services` class:

```python
import synoptic
df = synoptic.Metadata(
    stid='WBB',
    token="yourToken123456789"
).df()
```

## How to check the default token value

You can check the default token SynopticPy is using with the following:

```python
import synoptic
synoptic.services.TOKEN
```

Which will print your token and the source. It will look like one of the following:

```
🎫 Synoptic API token: yourToken123456789 (environment variable)
```

```
🎫 Synoptic API token: yourToken123456789 (config file)
```

```
🎫 Synoptic API token: None (not configured)
```
