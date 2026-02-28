"""Tests for configuration module."""

import base64
import json
import os
from unittest.mock import patch, MagicMock

import pytest

from trino_mcp.config import (
    AzureAutoRefreshAuthentication,
    TrinoConfig,
    _BearerAuth,
    _get_user_from_jwt,
    load_config,
)


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
    assert isinstance(config.auth, AzureAutoRefreshAuthentication)
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
    assert isinstance(config.auth, AzureAutoRefreshAuthentication)
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


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": '{"wtm_key": "MY_APP_ID"}',
        "MY_APP_ID": "my-cool-app",
    },
)
def test_load_config_custom_watermark():
    """Test loading configuration with custom watermark."""
    config = load_config()

    assert config.custom_watermark == {"wtm_key": "my-cool-app"}


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": '{"key1": "ENV_VAR1", "key2": "ENV_VAR2"}',
        "ENV_VAR1": "value1",
        "ENV_VAR2": "value2",
    },
)
def test_load_config_custom_watermark_multiple_keys():
    """Test loading configuration with multiple custom watermark keys."""
    config = load_config()

    assert config.custom_watermark == {"key1": "value1", "key2": "value2"}


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": '{"wtm_key": "MISSING_ENV_VAR"}',
    },
    clear=True,
)
def test_load_config_custom_watermark_missing_env_var():
    """Test custom watermark with missing environment variable defaults to empty string."""
    config = load_config()

    assert config.custom_watermark == {"wtm_key": ""}


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": "not-valid-json",
    },
)
def test_load_config_custom_watermark_invalid_json():
    """Test custom watermark with invalid JSON raises error."""
    with pytest.raises(ValueError, match="TRINO_MCP_CUSTOM_WATERMARK must be valid JSON"):
        load_config()


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
    },
)
def test_load_config_no_custom_watermark():
    """Test loading configuration without custom watermark."""
    config = load_config()

    assert config.custom_watermark is None


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": '{"key\\ninjected": "MY_VAR"}',
        "MY_VAR": "value\ninjected",
    },
)
def test_load_config_custom_watermark_strips_newlines():
    """Test that newlines are stripped from custom watermark keys and values."""
    config = load_config()

    assert config.custom_watermark == {"keyinjected": "valueinjected"}


# ---------------------------------------------------------------------------
# _get_user_from_jwt — JWT payload extraction
# ---------------------------------------------------------------------------


def test_get_user_from_jwt_extracts_oid():
    """Test that _get_user_from_jwt correctly extracts the 'oid' claim.

    Azure SPN tokens carry the service principal's object ID in the 'oid' claim.
    Trino uses this value as the user identity to avoid impersonation errors.
    """
    payload = base64.urlsafe_b64encode(
        json.dumps({"oid": "abc-123-def", "sub": "should-not-be-used"}).encode()
    ).decode().rstrip("=")
    token = f"header.{payload}.signature"

    assert _get_user_from_jwt(token) == "abc-123-def"


def test_get_user_from_jwt_falls_back_to_sub():
    """Test that _get_user_from_jwt uses 'sub' when 'oid' is absent.

    Some token types (e.g. v1 tokens) may not include 'oid'.
    The function should fall back to the 'sub' claim.
    """
    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": "fallback-sub-id"}).encode()
    ).decode().rstrip("=")
    token = f"header.{payload}.signature"

    assert _get_user_from_jwt(token) == "fallback-sub-id"


def test_get_user_from_jwt_returns_none_for_invalid_token():
    """Test that _get_user_from_jwt returns None for malformed tokens.

    When the token cannot be decoded, the function must return None so the
    caller falls back to the configured TRINO_USER rather than crashing.
    """
    assert _get_user_from_jwt("not-a-jwt") is None
    assert _get_user_from_jwt("") is None
    assert _get_user_from_jwt("a.!!!invalid-base64.c") is None


def test_get_user_from_jwt_returns_none_when_no_identity_claims():
    """Test that _get_user_from_jwt returns None when neither 'oid' nor 'sub' exist."""
    payload = base64.urlsafe_b64encode(
        json.dumps({"name": "some-user", "email": "x@y.com"}).encode()
    ).decode().rstrip("=")
    token = f"header.{payload}.signature"

    assert _get_user_from_jwt(token) is None


# ---------------------------------------------------------------------------
# _BearerAuth — Authorization header injection
# ---------------------------------------------------------------------------


def test_bearer_auth_sets_authorization_header():
    """Test that _BearerAuth sets the correct Authorization header on a request.

    This is the mechanism by which Azure tokens are attached to every
    Trino HTTP request. A wrong header format would cause auth failures.
    """
    auth = _BearerAuth("my-token-value")
    request = MagicMock()
    request.headers = {}

    result = auth(request)

    assert result is request
    assert request.headers["Authorization"] == "Bearer my-token-value"


# ---------------------------------------------------------------------------
# AzureAutoRefreshAuthentication — token refresh on each request
# ---------------------------------------------------------------------------


def test_azure_auto_refresh_auth_refreshes_token_on_each_call():
    """Test that set_http_session fetches a fresh token on every invocation.

    This is the core value of AzureAutoRefreshAuthentication over a static
    JWTAuthentication: long-running MCP servers must refresh tokens before
    they expire. Each call to set_http_session should obtain a new token.
    """
    mock_credential = MagicMock()
    mock_credential.get_token.return_value.token = "fresh-token-1"

    auth = AzureAutoRefreshAuthentication(mock_credential, "api://scope/.default")
    session = MagicMock()

    result = auth.set_http_session(session)

    # Verify it called get_token with the correct scope
    mock_credential.get_token.assert_called_once_with("api://scope/.default")
    # Verify the session was returned with auth set
    assert result is session
    assert session.auth is not None

    # Simulate a second request — token should be fetched again
    mock_credential.get_token.return_value.token = "fresh-token-2"
    auth.set_http_session(session)
    assert mock_credential.get_token.call_count == 2


def test_azure_auto_refresh_auth_get_exceptions_returns_empty():
    """Test get_exceptions returns an empty tuple.

    The trino library calls get_exceptions() to determine which exceptions
    should trigger authentication retry. Returning () means no retries,
    which is correct since we refresh the token proactively.
    """
    auth = AzureAutoRefreshAuthentication(MagicMock(), "scope")

    assert auth.get_exceptions() == ()


# ---------------------------------------------------------------------------
# load_config — OAuth2 auth method
# ---------------------------------------------------------------------------


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "trino.example.com",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "OAUTH2",
    },
)
def test_load_config_oauth2_enforces_https_and_port():
    """Test that OAuth2 auth forces HTTPS on port 443 with required headers.

    OAuth2 requires HTTPS. The config should override any user-supplied
    port/scheme to ensure the connection is secure.
    """
    config = load_config()

    assert config.http_scheme == "https"
    assert config.port == 443
    assert config.additional_kwargs["http_headers"] == {"X-Client-Info": "secured"}
    assert config.auth is not None


# ---------------------------------------------------------------------------
# load_config — error cases
# ---------------------------------------------------------------------------


@patch("trino_mcp.config.load_dotenv")
@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "PASSWORD",
    },
    clear=True,
)
def test_load_config_password_missing_password(mock_load_dotenv):
    """Test that PASSWORD auth without TRINO_PASSWORD raises a clear error.

    PASSWORD is the default AUTH_METHOD, so a new user who forgets to set
    TRINO_PASSWORD should get a helpful error message rather than a crash.
    """
    with pytest.raises(ValueError, match="TRINO_USER and TRINO_PASSWORD must be set"):
        load_config()


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "KERBEROS",
    },
)
def test_load_config_unsupported_auth_method():
    """Test that an unsupported AUTH_METHOD raises a clear error.

    Users who typo the auth method (e.g. KERBEROS instead of a supported
    value) should get an error naming the unsupported method.
    """
    with pytest.raises(ValueError, match="Unsupported AUTH_METHOD: KERBEROS"):
        load_config()


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": '["not", "a", "dict"]',
    },
)
def test_load_config_custom_watermark_non_dict_rejected():
    """Test that TRINO_MCP_CUSTOM_WATERMARK rejects non-dict JSON.

    A JSON array is valid JSON but not a valid watermark config. The error
    should fire before the server starts, not at query time.
    """
    with pytest.raises(ValueError, match="TRINO_MCP_CUSTOM_WATERMARK must be a JSON object"):
        load_config()


@patch.dict(
    os.environ,
    {
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "trino",
        "AUTH_METHOD": "NONE",
        "TRINO_MCP_CUSTOM_WATERMARK": '{"key": 42}',
    },
)
def test_load_config_custom_watermark_non_string_value_rejected():
    """Test that TRINO_MCP_CUSTOM_WATERMARK rejects non-string values.

    Values must be environment variable names (strings). Passing an int
    or other type indicates a misconfigured watermark and should fail early.
    """
    with pytest.raises(ValueError, match="values must be strings"):
        load_config()


# ---------------------------------------------------------------------------
# load_config — Azure DefaultAzureCredential fallback
# ---------------------------------------------------------------------------


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
def test_load_config_azure_spn_falls_back_to_default_credential(mock_cli_cls, mock_default_cls):
    """Test Azure SPN auth falls through to DefaultAzureCredential.

    When running on Azure (e.g. managed identity), AzureCliCredential will
    fail but DefaultAzureCredential should succeed. This tests the full
    fallback chain: CLI fails → no client secret env vars → DefaultAzureCredential succeeds.
    """
    mock_cli_cls.return_value.get_token.side_effect = Exception("no az login")

    mock_default = MagicMock()
    mock_default.get_token.return_value.token = "managed-identity-token"
    mock_default_cls.return_value = mock_default

    with patch("trino_mcp.config._get_user_from_jwt", return_value="managed-id-oid"):
        config = load_config()

    mock_default.get_token.assert_called_once_with("api://test-scope/.default")
    assert isinstance(config.auth, AzureAutoRefreshAuthentication)
    assert config.user == "managed-id-oid"
    assert config.http_scheme == "https"
    assert config.port == 443
