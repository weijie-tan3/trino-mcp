# Authentication

Trino MCP Server supports multiple authentication methods to connect to your Trino cluster securely.

## Authentication Methods

### Basic Authentication

The simplest authentication method using username and password.

#### Configuration

```bash
TRINO_HOST=trino.example.com
TRINO_PORT=8443
TRINO_USER=your_username
TRINO_PASSWORD=your_password
TRINO_HTTP_SCHEME=https
```

#### Use Case

- Development environments
- Testing
- Simple deployments without OAuth infrastructure

!!! warning "Security Best Practice"
    Always use HTTPS when using password authentication to protect credentials in transit.

---

### OAuth2 Authentication

Enterprise-grade authentication using OAuth2 without requiring explicit JWT token management.

#### Configuration

```bash
TRINO_HOST=trino.example.com
TRINO_PORT=8443
TRINO_USER=your_username
TRINO_OAUTH_TOKEN=your_oauth_token
TRINO_HTTP_SCHEME=https
AUTH_METHOD=OAuth2
```

#### How OAuth Works

The Trino MCP Server uses the Trino Python client's OAuth2 support, which:

1. Handles the OAuth2 authentication flow automatically
2. Manages token refresh transparently
3. Supports standard OAuth2 identity providers

#### Trino Server Configuration

Your Trino server must be configured for OAuth2. See the [Trino OAuth2 documentation](https://trino.io/docs/current/security/oauth2.html) for server-side setup.

Example Trino `config.properties`:

```properties
http-server.authentication.type=oauth2
http-server.authentication.oauth2.issuer=https://your-idp.com
http-server.authentication.oauth2.client-id=your-client-id
http-server.authentication.oauth2.client-secret=your-client-secret
```

#### Use Case

- Production environments
- Enterprise deployments
- SSO integration
- Fine-grained access control

---

### No Authentication

For development or testing against unsecured Trino instances.

#### Configuration

```bash
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_HTTP_SCHEME=http
```

Simply omit `TRINO_PASSWORD` and `TRINO_OAUTH_TOKEN`.

!!! danger "Not for Production"
    Never use unauthenticated connections in production environments.

---

## SSL/TLS Configuration

### Enable SSL

Use HTTPS for encrypted connections:

```bash
TRINO_HTTP_SCHEME=https
TRINO_VERIFY_SSL=true
```

### Custom SSL Certificate

If using self-signed certificates or custom CA:

```bash
TRINO_HTTP_SCHEME=https
TRINO_SSL_CERT=/path/to/cert.pem
TRINO_VERIFY_SSL=true
```

### Disable SSL Verification (Development Only)

!!! danger "Development Only"
    Never disable SSL verification in production.

```bash
TRINO_HTTP_SCHEME=https
TRINO_VERIFY_SSL=false
```

---

## Authentication Examples

### Example 1: Development Environment

Local Trino without authentication:

```bash
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=trino
TRINO_HTTP_SCHEME=http
```

### Example 2: Production with Basic Auth

Secure connection with password:

```bash
TRINO_HOST=trino.prod.example.com
TRINO_PORT=8443
TRINO_USER=data_analyst
TRINO_PASSWORD=SecurePassword123!
TRINO_HTTP_SCHEME=https
TRINO_VERIFY_SSL=true
```

### Example 3: Production with OAuth2

Enterprise OAuth2 setup:

```bash
TRINO_HOST=trino.prod.example.com
TRINO_PORT=8443
TRINO_USER=data_analyst@example.com
TRINO_OAUTH_TOKEN=eyJhbGciOiJSUzI1NiIs...
TRINO_HTTP_SCHEME=https
AUTH_METHOD=OAuth2
TRINO_VERIFY_SSL=true
```

---

## Troubleshooting Authentication

### Authentication Failed

**Symptom:** Error message "Authentication failed" or "401 Unauthorized"

**Solutions:**
1. Verify username and password are correct
2. Check that authentication method matches Trino server configuration
3. Ensure user has proper permissions in Trino
4. Check Trino server logs for detailed error messages

### OAuth Token Expired

**Symptom:** Error message about expired token or "401 Unauthorized"

**Solutions:**
1. Obtain a fresh OAuth token from your identity provider
2. Update `TRINO_OAUTH_TOKEN` environment variable
3. Restart the MCP server
4. Implement token refresh mechanism if needed

### SSL Certificate Errors

**Symptom:** SSL certificate verification failed

**Solutions:**
1. Verify certificate is valid: `openssl s_client -connect trino.example.com:8443`
2. Ensure `TRINO_SSL_CERT` points to correct certificate file
3. Check certificate is not expired
4. For development only: Temporarily set `TRINO_VERIFY_SSL=false`

### Connection Refused

**Symptom:** "Connection refused" error

**Solutions:**
1. Verify Trino server is running
2. Check firewall rules allow connection
3. Ensure correct host and port configuration
4. Test connectivity: `curl -v https://trino.example.com:8443/v1/status`

---

## Security Best Practices

### 1. Use Strong Authentication

- ✅ Use OAuth2 for production environments
- ✅ Use strong passwords for basic auth
- ✅ Rotate credentials regularly
- ❌ Don't use no-auth in production

### 2. Encrypt Connections

- ✅ Always use HTTPS in production
- ✅ Verify SSL certificates
- ✅ Use TLS 1.2 or higher
- ❌ Don't disable SSL verification in production

### 3. Credential Management

- ✅ Store credentials in environment variables or secret managers
- ✅ Never commit `.env` files to version control
- ✅ Use read-only or limited-permission users when possible
- ❌ Don't hardcode credentials in configuration files

### 4. Network Security

- ✅ Use VPNs or private networks for Trino access
- ✅ Implement firewall rules
- ✅ Use network segmentation
- ❌ Don't expose Trino directly to the internet

### 5. Access Control

- ✅ Use Trino's authorization features
- ✅ Implement least-privilege principle
- ✅ Audit access regularly
- ❌ Don't use admin credentials for applications

---

## OAuth2 Implementation Details

The Trino Python client supports OAuth2 through a redirect handler mechanism. Here's how it works:

1. **Initial Request**: Client attempts to connect to Trino
2. **Redirect**: Trino redirects to OAuth provider if needed
3. **Authentication**: User authenticates with OAuth provider
4. **Token**: OAuth provider issues token
5. **Connection**: Client uses token to connect to Trino

The MCP server provides the foundation for OAuth2 integration. For production use with OAuth2, you may need to:

- Configure your OAuth2 identity provider (Okta, Auth0, Azure AD, etc.)
- Set up Trino server with OAuth2 authentication
- Implement custom OAuth2 redirect handler if needed
- Configure token refresh logic

---

## Next Steps

- [Configuration](configuration.md) - Complete configuration reference
- [Quick Start](quickstart.md) - Get started quickly
- [Available Tools](tools.md) - Explore available MCP tools
