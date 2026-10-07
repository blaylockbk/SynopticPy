"""Tests for API token configuration."""

import tomllib

import synoptic
import synoptic.services as services
import synoptic.token as token_module


def test_configure_creates_missing_config_directory(tmp_path, monkeypatch):
    """Create the config directory when saving the initial configuration."""
    config_file = tmp_path / "config" / "SynopticPy" / "config.toml"
    monkeypatch.setattr(token_module, "CONFIG_FILE", config_file)
    monkeypatch.setattr(token_module.Token, "is_valid", lambda self: True)
    monkeypatch.delenv("SYNOPTIC_TOKEN", raising=False)
    existing_token = services.TOKEN

    token_module.configure(token="test-token", verbose=False)

    with config_file.open("rb") as file:
        config = tomllib.load(file)

    assert config["token"] == "test-token"
    assert services.TOKEN is existing_token
    assert synoptic.TOKEN is existing_token
    assert services.TOKEN.token == "test-token"
    assert services.TOKEN.source == "config file"
