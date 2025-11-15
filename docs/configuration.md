# Configuration

Trino MCP Server can be configured using environment variables or a `.env` file.

## Basic Configuration

Create a `.env` file in your working directory or set environment variables:

```bash
# Basic Configuration
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_HTTP_SCHEME=http
```

## Optional Configuration

### Default Catalog and Schema

Set default catalog and schema to avoid specifying them in every query:

```bash
TRINO_CATALOG=my_catalog
TRINO_SCHEMA=my_schema
```

### Session Properties

Configure Trino session properties:

```bash
# Example session properties
TRINO_SESSION_PROPERTIES=query_max_memory=10GB,query_max_execution_time=30m
```

## Authentication Methods

### Basic Authentication

Use username and password authentication:

```bash
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_PASSWORD=your_password
TRINO_HTTP_SCHEME=https
```

!!! warning "Security"
    Always use HTTPS when using password authentication to protect credentials in transit.

### OAuth2 Authentication

Use OAuth2 authentication (without explicit JWT):

```bash
TRINO_HOST=localhost
TRINO_PORT=8443
TRINO_USER=your_username
TRINO_OAUTH_TOKEN=your_oauth_token
TRINO_HTTP_SCHEME=https
AUTH_METHOD=OAuth2
```

!!! info "OAuth Token Management"
    The Trino Python client handles OAuth2 flows automatically. You don't need to manually manage JWT tokens.

## Connection Options

### SSL/TLS Configuration

For secure connections:

```bash
TRINO_HTTP_SCHEME=https
TRINO_VERIFY_SSL=true
TRINO_SSL_CERT=/path/to/cert.pem
```

### Timeout Settings

Configure connection and query timeouts:

```bash
# Connection timeout in seconds
TRINO_TIMEOUT=300

# Query timeout in seconds
TRINO_QUERY_TIMEOUT=600
```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TRINO_HOST` | Trino server hostname | `localhost` | Yes |
| `TRINO_PORT` | Trino server port | `8080` | Yes |
| `TRINO_USER` | Username for authentication | `trino` | Yes |
| `TRINO_PASSWORD` | Password (for basic auth) | - | No |
| `TRINO_OAUTH_TOKEN` | OAuth token (for OAuth2) | - | No |
| `TRINO_HTTP_SCHEME` | HTTP scheme (http/https) | `http` | No |
| `TRINO_CATALOG` | Default catalog | - | No |
| `TRINO_SCHEMA` | Default schema | - | No |
| `TRINO_VERIFY_SSL` | Verify SSL certificates | `true` | No |
| `TRINO_SSL_CERT` | Path to SSL certificate | - | No |
| `TRINO_TIMEOUT` | Connection timeout (seconds) | `300` | No |
| `AUTH_METHOD` | Authentication method | `Basic` | No |

## Configuration File Example

Here's a complete `.env` file example:

```bash
# Trino Connection
TRINO_HOST=trino.example.com
TRINO_PORT=8443
TRINO_HTTP_SCHEME=https

# Authentication
TRINO_USER=data_analyst
TRINO_PASSWORD=secure_password_here

# Defaults
TRINO_CATALOG=hive
TRINO_SCHEMA=default

# SSL Configuration
TRINO_VERIFY_SSL=true

# Timeouts
TRINO_TIMEOUT=300
TRINO_QUERY_TIMEOUT=600
```

## Using Configuration in Code

The configuration is automatically loaded when the server starts:

```python
from trino_mcp.config import load_config

# Load configuration from environment
config = load_config()

# Access configuration values
print(f"Host: {config.host}")
print(f"Port: {config.port}")
print(f"User: {config.user}")
```

## Best Practices

### Security

1. **Never commit `.env` files** to version control
2. **Use HTTPS** for production environments
3. **Rotate credentials** regularly
4. **Use OAuth2** when available for better security
5. **Limit user permissions** in Trino to minimum required

### Performance

1. **Set appropriate timeouts** based on your query complexity
2. **Use default catalog/schema** to reduce query overhead
3. **Configure session properties** for optimal query performance
4. **Monitor connection pool** usage

### Reliability

1. **Test connectivity** before deploying
2. **Use health checks** to monitor Trino availability
3. **Configure retry logic** for transient failures
4. **Log configuration** (without sensitive data) for debugging

## Troubleshooting

### Connection Refused

- Verify Trino is running: `curl http://localhost:8080/v1/status`
- Check firewall rules
- Ensure correct host and port

### Authentication Failed

- Verify credentials are correct
- Check authentication method matches Trino configuration
- For OAuth, ensure token is valid and not expired

### SSL Errors

- Verify certificate is valid: `openssl s_client -connect trino.example.com:8443`
- Check certificate path in `TRINO_SSL_CERT`
- Try disabling SSL verification for testing (not recommended for production)

## Next Steps

- [Quick Start](quickstart.md) - Start using the server
- [Authentication](authentication.md) - Learn more about authentication
- [Available Tools](tools.md) - Explore available MCP tools
