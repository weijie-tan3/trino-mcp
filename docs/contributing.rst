Contributing
============

Thank you for your interest in contributing to Trino MCP Server!

Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.10 or higher
* Git
* uv (recommended) or pip
* A Trino server for testing (optional)

Setting Up Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Fork and clone the repository:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/trino-mcp.git
      cd trino-mcp

2. Install dependencies:

   .. code-block:: bash

      # Using uv (recommended)
      uv sync --all-extras --dev

      # Or using pip
      pip install -e ".[dev]"

3. Create a ``.env`` file for testing:

   .. code-block:: bash

      cp .env.example .env
      # Edit .env with your Trino connection details

Development Workflow
--------------------

Making Changes
~~~~~~~~~~~~~~

1. Create a new branch:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. Make your changes and test them:

   .. code-block:: bash

      # Run tests
      pytest tests/ -v

      # Format code
      black src/ tests/

      # Type check
      mypy src/trino_mcp --ignore-missing-imports

3. Commit your changes:

   .. code-block:: bash

      git commit -m "feat: add new feature"

Code Style
----------

We follow PEP 8 style guide with these modifications:

* Line length: 100 characters (enforced by black)
* Type hints: Required for all public functions
* Docstrings: Google style docstrings

Commit Messages
~~~~~~~~~~~~~~~

Follow Conventional Commits format:

.. code-block:: text

   <type>(<scope>): <description>

   [optional body]

   [optional footer]

**Types:**

* ``feat``: New feature
* ``fix``: Bug fix
* ``docs``: Documentation changes
* ``style``: Code style changes
* ``refactor``: Code refactoring
* ``test``: Adding or updating tests
* ``chore``: Maintenance tasks

Submitting Changes
------------------

1. Ensure your code passes all checks
2. Update documentation if needed
3. Push your branch and open a Pull Request
4. Fill out the PR template
5. Request review

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.
