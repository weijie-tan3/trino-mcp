"""Configuration for Trino connection."""

import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Optional, Tuple

import trino.auth
from dotenv import load_dotenv
from requests import Session


class _BearerAuth:
    """Bearer token auth for requests."""

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: Any) -> Any:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class AzureAutoRefreshAuthentication(trino.auth.Authentication):
    """JWT authentication that auto-refreshes the token via an Azure credential.

    Unlike JWTAuthentication which holds a static token, this class stores
    the Azure credential and scope so it can fetch a fresh token on each
    request, avoiding expiry issues for long-running MCP servers.
    """

    def __init__(self, credential: Any, scope: str):
        self._credential = credential
        self._scope = scope

    def set_http_session(self, http_session: Session) -> Session:
        token = self._credential.get_token(self._scope).token
        http_session.auth = _BearerAuth(token)
        return http_session

    def get_exceptions(self) -> Tuple[Any, ...]:
        return ()


def _get_user_from_jwt(token: str) -> Optional[str]:
    """Extract the user identity (oid) from a JWT token payload."""
    try:
        payload = token.split(".")[1]
        # Add padding for base64 decoding
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        return data.get("oid") or data.get("sub")
    except Exception:
        return None


@dataclass
class TrinoConfig:
    """Trino connection configuration."""

    host: str
    port: int
    user: str
    catalog: Optional[str] = None
    schema: Optional[str] = None
    http_scheme: str = "http"
    auth: Optional[trino.auth.Authentication] = None
    additional_kwargs: Optional[dict] = None
    allow_write_queries: bool = False
    custom_watermark: Optional[dict] = None


def load_config() -> TrinoConfig:
    """Load configuration from environment variables."""
    load_dotenv()

    host = os.getenv("TRINO_HOST", "localhost")
    port = int(os.getenv("TRINO_PORT", "8080"))
    user = os.getenv("TRINO_USER", "trino")
    catalog = os.getenv("TRINO_CATALOG")
    schema = os.getenv("TRINO_SCHEMA")
    http_scheme = os.getenv("TRINO_HTTP_SCHEME", "http")

    # Setup authentication based on available credentials
    auth = None
    additional_kwargs = {}

    auth_method = os.getenv("AUTH_METHOD", "PASSWORD").upper()
    if auth_method == "PASSWORD":
        password = os.getenv("TRINO_PASSWORD")
        if not (user and password):
            raise ValueError(
                "TRINO_USER and TRINO_PASSWORD must be set for password authentication"
            )
        auth = trino.auth.BasicAuthentication(user, password)

    elif auth_method == "OAUTH2":
        auth = trino.auth.OAuth2Authentication()
        http_scheme = "https"
        port = 443
        additional_kwargs["http_headers"] = {"X-Client-Info": "secured"}

    elif auth_method == "AZURE_SPN":
        try:
            from azure.identity import (
                AzureCliCredential,
                ClientSecretCredential,
                DefaultAzureCredential,
            )
        except ImportError:
            raise ImportError(
                "azure-identity is required for AZURE_SPN authentication. "
                "Install it with: pip install trino-mcp[azure]"
            )
        scope = os.getenv("AZURE_SCOPE")
        if not scope:
            raise ValueError(
                "AZURE_SCOPE must be set for Azure SPN authentication "
                "(e.g. api://<trino-app-id>/.default)"
            )

        token = None
        working_credential = None

        # 1. Try AzureCliCredential (works after `az login --service-principal`)
        try:
            credential = AzureCliCredential()
            token = credential.get_token(scope).token
            working_credential = credential
        except Exception:
            pass

        # 2. Try ClientSecretCredential if env vars are set
        if token is None:
            client_id = os.getenv("AZURE_CLIENT_ID")
            client_secret = os.getenv("AZURE_CLIENT_SECRET")
            tenant_id = os.getenv("AZURE_TENANT_ID")
            if client_id and client_secret and tenant_id:
                try:
                    credential = ClientSecretCredential(
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client_secret=client_secret,
                    )
                    token = credential.get_token(scope).token
                    working_credential = credential
                except Exception:
                    pass

        # 3. Fallback to DefaultAzureCredential (managed identity, etc.)
        if token is None:
            try:
                credential = DefaultAzureCredential()
                token = credential.get_token(scope).token
                working_credential = credential
            except Exception:
                pass

        if token is None or working_credential is None:
            raise ValueError(
                "Failed to acquire Azure token. Either run "
                "'az login --service-principal' or set AZURE_CLIENT_ID, "
                "AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables."
            )

        # Extract user identity (oid) from the JWT token to avoid
        # impersonation errors — Trino expects the SPN's OID, not a username.
        user = _get_user_from_jwt(token) or user

        # Use auto-refreshing auth so the token is refreshed before each
        # request, avoiding expiry issues for long-running MCP servers.
        auth = AzureAutoRefreshAuthentication(working_credential, scope)
        http_scheme = "https"
        port = 443

    elif auth_method == "NONE":
        # No authentication
        auth = None

    else:
        raise ValueError(f"Unsupported AUTH_METHOD: {auth_method}")

    # Query execution permissions
    allow_write_queries = os.getenv("ALLOW_WRITE_QUERIES", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    # Custom watermark configuration
    custom_watermark = None
    custom_watermark_raw = os.getenv("TRINO_MCP_CUSTOM_WATERMARK")
    if custom_watermark_raw:
        try:
            watermark_config = json.loads(custom_watermark_raw)
            if not isinstance(watermark_config, dict):
                raise ValueError("TRINO_MCP_CUSTOM_WATERMARK must be a JSON object")
            custom_watermark = {}
            for key, env_var_name in watermark_config.items():
                if not isinstance(env_var_name, str):
                    raise ValueError(
                        f"TRINO_MCP_CUSTOM_WATERMARK values must be strings "
                        f"(environment variable names), got {type(env_var_name).__name__} for key '{key}'"
                    )
                env_value = os.getenv(env_var_name, "")
                custom_watermark[key] = env_value
        except json.JSONDecodeError as e:
            raise ValueError(
                f"TRINO_MCP_CUSTOM_WATERMARK must be valid JSON: {e}"
            )

    return TrinoConfig(
        host=host,
        port=port,
        user=user,
        catalog=catalog,
        schema=schema,
        http_scheme=http_scheme,
        auth=auth,
        additional_kwargs=additional_kwargs,
        allow_write_queries=allow_write_queries,
        custom_watermark=custom_watermark,
    )
