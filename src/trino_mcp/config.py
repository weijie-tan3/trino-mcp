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
    password = os.getenv("TRINO_PASSWORD")

    if password:
        # Basic authentication
        auth = trino.auth.BasicAuthentication(user, password)

    # Note: For OAuth2, you need to provide a redirect handler
    # This is a simplified version - for production use, implement proper OAuth2 flow
    # Example: auth = trino.auth.OAuth2Authentication()

    return TrinoConfig(
        host=host,
        port=port,
        user=user,
        catalog=catalog,
        schema=schema,
        http_scheme=http_scheme,
        auth=auth,
    )
