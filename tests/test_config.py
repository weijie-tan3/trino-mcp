"""Tests for configuration module."""

import os
from unittest.mock import patch, MagicMock

import pytest

from trino_mcp.config import TrinoConfig, load_config


def test_trino_config_defaults():
    """Test TrinoConfig with default values."""
    config = TrinoConfig(
        host="localhost",
        port=8080,
        user="trino",
    )

    assert config.host == "localhost"
    assert config.port == 8080
    assert config.user == "trino"
    assert config.catalog is None
    assert config.schema is None
    assert config.http_scheme == "http"
    assert config.auth is None


def test_trino_config_with_catalog_schema():
    """Test TrinoConfig with catalog and schema."""
    config = TrinoConfig(
        host="trino.example.com",
        port=443,
        user="admin",
        catalog="hive",
        schema="default",
        http_scheme="https",
    )

    assert config.host == "trino.example.com"
    assert config.port == 443
    assert config.user == "admin"
    assert config.catalog == "hive"
    assert config.schema == "default"
    assert config.http_scheme == "https"


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "test-host",
        "TRINO_PORT": "9999",
        "TRINO_USER": "test-user",
        "TRINO_HTTP_SCHEME": "https",
        "AUTH_METHOD": "NONE",
    },
)
def test_load_config_basic():
    """Test loading basic configuration from environment."""
    config = load_config()

    assert config.host == "test-host"
    assert config.port == 9999
    assert config.user == "test-user"
    assert config.http_scheme == "https"
    assert config.auth is None


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "TRINO_CATALOG": "hive",
        "TRINO_SCHEMA": "default",
        "AUTH_METHOD": "NONE",
    },
)
def test_load_config_with_defaults():
    """Test loading configuration with catalog and schema defaults."""
    config = load_config()

    assert config.catalog == "hive"
    assert config.schema == "default"


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "admin",
        "TRINO_PASSWORD": "secret123",
        "AUTH_METHOD": "PASSWORD",
    },
)
def test_load_config_with_basic_auth():
    """Test loading configuration with basic authentication."""
    config = load_config()

    assert config.auth is not None
    assert hasattr(config.auth, "_username")
    assert hasattr(config.auth, "_password")


@patch("trino_mcp.config.load_dotenv")
@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
    },
    clear=True,
)
def test_load_config_defaults(mock_load_dotenv):
    """Test default values when environment variables are not set."""
    config = load_config()

    assert config.host == "localhost"
    assert config.port == 8080
    assert config.user == "trino"
    assert config.http_scheme == "http"
    assert config.catalog is None
    assert config.schema is None
