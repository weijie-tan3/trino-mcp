"""Configuration for Trino connection."""

import os
from dataclasses import dataclass
from typing import Optional

import trino.auth
from dotenv import load_dotenv


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

    elif auth_method == "NONE":
        # No authentication
        auth = None

    else:
        raise ValueError(f"Unsupported AUTH_METHOD: {auth_method}")

    return TrinoConfig(
        host=host,
        port=port,
        user=user,
        catalog=catalog,
        schema=schema,
        http_scheme=http_scheme,
        auth=auth,
        additional_kwargs=additional_kwargs,
    )
