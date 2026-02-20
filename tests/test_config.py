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


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "ALLOW_WRITE_QUERIES": "false",
    },
)
def test_load_config_write_queries_false():
    """Test loading configuration with write queries disabled."""
    config = load_config()

    assert config.allow_write_queries is False


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "ALLOW_WRITE_QUERIES": "true",
    },
)
def test_load_config_write_queries_true():
    """Test loading configuration with write queries enabled."""
    config = load_config()

    assert config.allow_write_queries is True


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "ALLOW_WRITE_QUERIES": "1",
    },
)
def test_load_config_write_queries_one():
    """Test loading configuration with write queries enabled using '1'."""
    config = load_config()

    assert config.allow_write_queries is True


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "ALLOW_WRITE_QUERIES": "yes",
    },
)
def test_load_config_write_queries_yes():
    """Test loading configuration with write queries enabled using 'yes'."""
    config = load_config()

    assert config.allow_write_queries is True


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "ALLOW_WRITE_QUERIES": "FALSE",
    },
)
def test_load_config_write_queries_false_uppercase():
    """Test loading configuration with write queries disabled using uppercase."""
    config = load_config()

    assert config.allow_write_queries is False


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
    },
)
def test_load_config_write_queries_default():
    """Test default value for write queries when not specified."""
    config = load_config()

    assert config.allow_write_queries is False


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "AZURE_SPN",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_CLIENT_SECRET": "test-client-secret",
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_SCOPE": "api://test-scope/.default",
    },
)
@patch("trino_mcp.config._get_user_from_jwt", return_value="mock-oid-12345")
@patch("azure.identity.AzureCliCredential")
@patch("azure.identity.ClientSecretCredential")
def test_load_config_azure_spn(mock_spn_cls, mock_cli_cls, mock_get_user):
    """Test loading configuration with Azure SPN authentication."""
    # AzureCliCredential fails, falls through to ClientSecretCredential
    mock_cli = MagicMock()
    mock_cli.get_token.side_effect = Exception("az login not available")
    mock_cli_cls.return_value = mock_cli

    mock_spn = MagicMock()
    mock_token = MagicMock()
    mock_token.token = "test-jwt-token"
    mock_spn.get_token.return_value = mock_token
    mock_spn_cls.return_value = mock_spn

    config = load_config()

    mock_spn_cls.assert_called_once_with(
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-client-secret",
    )
    mock_spn.get_token.assert_called_once_with("api://test-scope/.default")
    assert config.auth is not None
    assert config.http_scheme == "https"
    assert config.port == 443
    assert config.user == "mock-oid-12345"


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "AZURE_SPN",
        "AZURE_SCOPE": "api://test-scope/.default",
    },
)
@patch("azure.identity.AzureCliCredential")
def test_load_config_azure_spn_via_az_cli(mock_cli_cls):
    """Test Azure SPN auth works via AzureCliCredential (az login)."""
    mock_cli = MagicMock()
    mock_token = MagicMock()
    mock_token.token = "test-jwt-token"
    mock_cli.get_token.return_value = mock_token
    mock_cli_cls.return_value = mock_cli

    with patch("trino_mcp.config._get_user_from_jwt", return_value="cli-oid"):
        config = load_config()

    mock_cli.get_token.assert_called_once_with("api://test-scope/.default")
    assert config.auth is not None
    assert config.user == "cli-oid"


@patch("trino_mcp.config.load_dotenv")
@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "AZURE_SPN",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_CLIENT_SECRET": "test-client-secret",
        "AZURE_TENANT_ID": "test-tenant-id",
    },
    clear=True,
)
def test_load_config_azure_spn_missing_scope(mock_load_dotenv):
    """Test Azure SPN authentication fails when AZURE_SCOPE is missing."""
    with pytest.raises(ValueError, match="AZURE_SCOPE"):
        load_config()


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "AZURE_SPN",
        "AZURE_SCOPE": "api://test-scope/.default",
    },
    clear=True,
)
@patch("azure.identity.DefaultAzureCredential")
@patch("azure.identity.AzureCliCredential")
def test_load_config_azure_spn_no_creds_all_fail(mock_cli_cls, mock_default_cls):
    """Test Azure SPN authentication fails when no credential method works."""
    mock_cli_cls.return_value.get_token.side_effect = Exception("no az login")
    mock_default_cls.return_value.get_token.side_effect = Exception("no managed identity")

    with pytest.raises(ValueError, match="Failed to acquire Azure token"):
        load_config()
