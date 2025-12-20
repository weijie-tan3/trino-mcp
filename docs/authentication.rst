Authentication
==============

Trino MCP Server supports multiple authentication methods to connect to your Trino cluster securely.

Authentication Methods
----------------------

Basic Authentication
~~~~~~~~~~~~~~~~~~~~

The simplest authentication method using username and password.

**Configuration:**

.. code-block:: bash

   TRINO_HOST=trino.example.com
   TRINO_PORT=8443
   TRINO_USER=your_username
   TRINO_PASSWORD=your_password
   TRINO_HTTP_SCHEME=https
   AUTH_METHOD=PASSWORD

**Use Case:**

* Development environments
* Testing
* Simple deployments without OAuth infrastructure

.. warning::
   Always use HTTPS when using password authentication to protect credentials in transit.

OAuth2 Authentication
~~~~~~~~~~~~~~~~~~~~~

Enterprise-grade authentication using OAuth2 without requiring explicit JWT token management.

**Configuration:**

.. code-block:: bash

   TRINO_HOST=trino.example.com
   TRINO_PORT=8443
   TRINO_USER=your_username
   TRINO_OAUTH_TOKEN=your_oauth_token
   TRINO_HTTP_SCHEME=https
   AUTH_METHOD=OAUTH2

**How OAuth Works:**

The Trino MCP Server uses the Trino Python client's OAuth2 support, which:

1. Handles the OAuth2 authentication flow automatically
2. Manages token refresh transparently
3. Supports standard OAuth2 identity providers

**Use Case:**

* Production environments
* Enterprise deployments
* SSO integration
* Fine-grained access control

No Authentication
~~~~~~~~~~~~~~~~~

For development or testing against unsecured Trino instances.

**Configuration:**

.. code-block:: bash

   TRINO_HOST=localhost
   TRINO_PORT=8080
   TRINO_USER=trino
   TRINO_HTTP_SCHEME=http
   AUTH_METHOD=NONE

Simply omit ``TRINO_PASSWORD`` and ``TRINO_OAUTH_TOKEN``.

.. danger::
   Never use unauthenticated connections in production environments.

Security Best Practices
-----------------------

1. Use Strong Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ✅ Use OAuth2 for production environments
* ✅ Use strong passwords for basic auth
* ✅ Rotate credentials regularly
* ❌ Don't use no-auth in production

2. Encrypt Connections
~~~~~~~~~~~~~~~~~~~~~~

* ✅ Always use HTTPS in production
* ✅ Verify SSL certificates
* ✅ Use TLS 1.2 or higher
* ❌ Don't disable SSL verification in production

3. Credential Management
~~~~~~~~~~~~~~~~~~~~~~~~

* ✅ Store credentials in environment variables or secret managers
* ✅ Never commit ``.env`` files to version control
* ✅ Use read-only or limited-permission users when possible
* ❌ Don't hardcode credentials in configuration files
