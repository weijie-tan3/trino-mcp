"""Configuration for Trino connection."""

import base64
import json
import logging
import os
import sys
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple

import trino.auth
from dotenv import load_dotenv
from requests import Session

logger = logging.getLogger(__name__)


class _AutoRefreshBearerAuth:
    """Bearer token auth that fetches a fresh token on every HTTP request.

    The Azure SDK caches tokens internally and only performs a real refresh
    when the cached token is near expiry, so calling ``get_token()`` on
    every request is both correct and efficient.
    """

    def __init__(self, credential: Any, scope: str):
        self._credential = credential
        self._scope = scope

    def __call__(self, r: Any) -> Any:
        token = self._credential.get_token(self._scope).token
        r.headers["Authorization"] = f"Bearer {token}"
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
        http_session.auth = _AutoRefreshBearerAuth(self._credential, self._scope)
        return http_session

    def get_exceptions(self) -> Tuple[Any, ...]:
        return ()


def _sanitize_watermark_str(s: str) -> str:
    """Strip characters that could break out of a SQL line comment."""
    return s.replace("\n", "").replace("\r", "")


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


def _make_github_actions_oidc_fetcher(
    audience: str = "api://AzureADTokenExchange",
) -> Optional[Callable[[], str]]:
    """Return a callable that fetches a fresh OIDC token from GitHub Actions.

    GitHub Actions sets ``ACTIONS_ID_TOKEN_REQUEST_URL`` and
    ``ACTIONS_ID_TOKEN_REQUEST_TOKEN`` when a workflow has
    ``permissions: id-token: write``.  The callable returned here hits
    that endpoint to obtain a fresh JWT assertion each time it is called,
    which ``ClientAssertionCredential`` then exchanges for an Azure AD
    token.

    Returns ``None`` if the required environment variables are not set
    (i.e. we are not running inside GitHub Actions with OIDC enabled).
    """
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not request_url or not request_token:
        return None

    def _fetch() -> str:
        url = f"{request_url}&audience={audience}"
        req = urllib.request.Request(
            url, headers={"Authorization": f"bearer {request_token}"}
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())["value"]

    return _fetch


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
    request_timeout: float = 300.0
    async_progress: bool = True


def load_config(overrides: Optional[dict] = None) -> TrinoConfig:
    """Load configuration from environment variables, with optional overrides.

    Resolution order (highest priority first):
    1. ``overrides`` dict (e.g. from CLI flags)
    2. Shell environment variables
    3. ``.env`` file (loaded by python-dotenv, which never overwrites existing vars)

    Args:
        overrides: Optional dict mapping environment variable names
                   (e.g. ``"TRINO_HOST"``) to values. Non-None values
                   take precedence over env vars and ``.env``.
    """
    load_dotenv()

    if overrides is None:
        overrides = {}

    def _get(env_var: str, default: Optional[str] = None) -> Optional[str]:
        """Return the override value if set, otherwise fall back to env."""
        value = overrides.get(env_var)
        if value is not None:
            return value
        return os.getenv(env_var, default)

    host = _get("TRINO_HOST", "localhost")
    port = int(_get("TRINO_PORT", "8080"))
    user = _get("TRINO_USER", "trino")
    catalog = _get("TRINO_CATALOG")
    schema = _get("TRINO_SCHEMA")
    http_scheme = _get("TRINO_HTTP_SCHEME", "http")

    # Setup authentication based on available credentials
    auth = None
    additional_kwargs = {}

    auth_method = _get("AUTH_METHOD", "PASSWORD").upper()
    if auth_method == "PASSWORD":
        password = _get("TRINO_PASSWORD")
        if not (user and password):
            raise ValueError(
                "TRINO_USER and TRINO_PASSWORD must be set for password authentication"
            )
        auth = trino.auth.BasicAuthentication(user, password)

    elif auth_method == "OAUTH2":
        # Use a custom redirect handler that writes to stderr instead of stdout.
        # The default ConsoleRedirectHandler uses print() which writes to stdout,
        # corrupting the MCP stdio transport protocol.
        def _stderr_redirect_handler(url: str) -> None:
            print(
                f"Open the following URL in browser for the external authentication:\n{url}",
                file=sys.stderr,
                flush=True,
            )

        auth = trino.auth.OAuth2Authentication(
            redirect_auth_url_handler=trino.auth.CompositeRedirectHandler([
                trino.auth.WebBrowserRedirectHandler(),
                _stderr_redirect_handler,
            ])
        )
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
        scope = _get("AZURE_SCOPE")
        if not scope:
            raise ValueError(
                "AZURE_SCOPE must be set for Azure SPN authentication "
                "(e.g. api://<trino-app-id>/.default)"
            )

        token = None
        working_credential = None

        # 0. Try GitHub Actions OIDC (federated credential via
        #    ACTIONS_ID_TOKEN_REQUEST_URL / ACTIONS_ID_TOKEN_REQUEST_TOKEN).
        #    This is preferred in CI because it can fetch fresh OIDC tokens
        #    indefinitely, whereas AzureCliCredential only holds a
        #    short-lived token that cannot be refreshed in OIDC flows.
        oidc_fetcher = _make_github_actions_oidc_fetcher()
        if oidc_fetcher is not None:
            client_id = _get("AZURE_CLIENT_ID")
            tenant_id = _get("AZURE_TENANT_ID")
            if client_id and tenant_id:
                try:
                    from azure.identity import ClientAssertionCredential

                    credential = ClientAssertionCredential(
                        tenant_id=tenant_id,
                        client_id=client_id,
                        func=oidc_fetcher,
                    )
                    token = credential.get_token(scope).token
                    working_credential = credential
                    logger.info(
                        "Using GitHub Actions OIDC federated credential "
                        "(ClientAssertionCredential)"
                    )
                except Exception as exc:
                    logger.debug(
                        "GitHub Actions OIDC credential failed: %s", exc
                    )

        # 1. Try AzureCliCredential (works after `az login --service-principal`)
        if token is None:
            try:
                credential = AzureCliCredential()
                token = credential.get_token(scope).token
                working_credential = credential
            except Exception:
                pass

        # 2. Try ClientSecretCredential if env vars are set
        if token is None:
            client_id = _get("AZURE_CLIENT_ID")
            client_secret = _get("AZURE_CLIENT_SECRET")
            tenant_id = _get("AZURE_TENANT_ID")
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
                "'az login --service-principal', set AZURE_CLIENT_ID, "
                "AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables, "
                "or use GitHub Actions OIDC with AZURE_CLIENT_ID and "
                "AZURE_TENANT_ID (requires id-token: write permission)."
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

    # Trino HTTP request timeout (per individual HTTP request, not per query)
    request_timeout = float(_get("TRINO_REQUEST_TIMEOUT", "300.0"))

    # Async progress heartbeats (keeps MCP connection alive during long queries)
    async_progress = _get("TRINO_MCP_ASYNC_PROGRESS", "true").lower() in (
        "true",
        "1",
        "yes",
    )

    # Query execution permissions
    allow_write_queries = _get("ALLOW_WRITE_QUERIES", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    # Custom watermark configuration
    # Values can be either:
    #   - A literal string (used as-is), e.g. "my-app"
    #   - An env: prefixed string to resolve from env vars, e.g. "env:MY_APP_ID"
    custom_watermark = None
    custom_watermark_raw = _get("TRINO_MCP_CUSTOM_WATERMARK")
    if custom_watermark_raw:
        try:
            watermark_config = json.loads(custom_watermark_raw)
            if not isinstance(watermark_config, dict):
                raise ValueError("TRINO_MCP_CUSTOM_WATERMARK must be a JSON object")
            for key, value in watermark_config.items():
                if not isinstance(value, str):
                    raise ValueError(
                        f"TRINO_MCP_CUSTOM_WATERMARK values must be strings, "
                        f"got {type(value).__name__} for key '{key}'"
                    )
            custom_watermark = {}
            for key, value in watermark_config.items():
                if value.startswith("env:"):
                    resolved = os.getenv(value[4:], "")
                else:
                    resolved = value
                custom_watermark[_sanitize_watermark_str(key)] = (
                    _sanitize_watermark_str(resolved)
                )
        except json.JSONDecodeError as e:
            raise ValueError(f"TRINO_MCP_CUSTOM_WATERMARK must be valid JSON: {e}")

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
        request_timeout=request_timeout,
        async_progress=async_progress,
    )
