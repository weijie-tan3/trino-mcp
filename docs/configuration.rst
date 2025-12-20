Configuration
=============

Trino MCP Server can be configured using environment variables or a ``.env`` file.

Basic Configuration
-------------------

Create a ``.env`` file in your working directory or set environment variables:

.. code-block:: bash

   # Basic Configuration
   TRINO_HOST=localhost
   TRINO_PORT=8080
   TRINO_USER=trino
   TRINO_HTTP_SCHEME=http

Environment Variables Reference
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 20 10

   * - Variable
     - Description
     - Default
     - Required
   * - ``TRINO_HOST``
     - Trino server hostname
     - ``localhost``
     - Yes
   * - ``TRINO_PORT``
     - Trino server port
     - ``8080``
     - Yes
   * - ``TRINO_USER``
     - Username for authentication
     - ``trino``
     - Yes
   * - ``TRINO_PASSWORD``
     - Password (for basic auth)
     - -
     - No
   * - ``TRINO_OAUTH_TOKEN``
     - OAuth token (for OAuth2)
     - -
     - No
   * - ``TRINO_HTTP_SCHEME``
     - HTTP scheme (http/https)
     - ``http``
     - No
   * - ``TRINO_CATALOG``
     - Default catalog
     - -
     - No
   * - ``TRINO_SCHEMA``
     - Default schema
     - -
     - No
   * - ``AUTH_METHOD``
     - Authentication method (PASSWORD/OAUTH2/NONE)
     - ``PASSWORD``
     - No

Authentication Methods
----------------------

Basic Authentication
~~~~~~~~~~~~~~~~~~~~

Use username and password authentication:

.. code-block:: bash

   TRINO_HOST=localhost
   TRINO_PORT=8080
   TRINO_USER=trino
   TRINO_PASSWORD=your_password
   TRINO_HTTP_SCHEME=https
   AUTH_METHOD=PASSWORD

.. warning::
   Always use HTTPS when using password authentication to protect credentials in transit.

OAuth2 Authentication
~~~~~~~~~~~~~~~~~~~~~

Use OAuth2 authentication:

.. code-block:: bash

   TRINO_HOST=localhost
   TRINO_PORT=8443
   TRINO_USER=your_username
   TRINO_OAUTH_TOKEN=your_oauth_token
   TRINO_HTTP_SCHEME=https
   AUTH_METHOD=OAUTH2

.. note::
   The Trino Python client handles OAuth2 flows automatically. You don't need to manually manage JWT tokens.

Configuration File Example
--------------------------

Here's a complete ``.env`` file example:

.. code-block:: bash

   # Trino Connection
   TRINO_HOST=trino.example.com
   TRINO_PORT=8443
   TRINO_HTTP_SCHEME=https

   # Authentication
   TRINO_USER=data_analyst
   TRINO_PASSWORD=secure_password_here
   AUTH_METHOD=PASSWORD

   # Defaults
   TRINO_CATALOG=hive
   TRINO_SCHEMA=default
