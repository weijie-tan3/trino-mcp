# Contributing to Documentation

This guide explains how to work with the documentation for Trino MCP Server.

## Documentation Architecture

The documentation uses **Sphinx** with automatic API generation:

- **API Reference** (`docs/api.rst`): Auto-generated from Python docstrings using Sphinx autodoc
- **Manual Pages**: Installation, configuration, examples, etc. are manually written in RST format

This approach ensures:
- API documentation stays in sync with code
- Guides and examples are carefully crafted for clarity
- Documentation builds fail if docstrings are missing or malformed

## Building Documentation Locally

### Prerequisites

Install documentation dependencies:

```bash
# Using pip
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Or using uv
uv pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Install the package in editable mode (required for autodoc)
pip install -e .
```

### Build Documentation

Build the static documentation site:

```bash
# From the repository root
sphinx-build -b html docs docs/_build/html

# With warnings treated as errors (recommended)
sphinx-build -b html docs docs/_build/html -W --keep-going
```

The built site will be in the `docs/_build/html/` directory.

### Serve Documentation Locally

You can use Python's built-in HTTP server to view the docs:

```bash
cd docs/_build/html
python -m http.server 8000
```

The documentation will be available at [http://localhost:8000](http://localhost:8000)

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Home page
├── installation.rst     # Installation guide
├── configuration.rst    # Configuration reference
├── quickstart.rst       # Quick start guide
├── tools.rst           # Available MCP tools
├── authentication.rst   # Authentication methods
├── examples.rst        # Usage examples
├── api.rst             # API reference (auto-generated)
├── contributing.rst     # Contributing guidelines
├── license.rst         # License information
├── _static/            # Static files (CSS, images, etc.)
└── _templates/         # Custom templates
```

## Writing Documentation

### Auto-Generated API Documentation

The API documentation in `docs/api.rst` uses Sphinx autodoc directives:

```rst
.. automodule:: trino_mcp.client
   :members:
   :undoc-members:
   :show-inheritance:
```

This automatically extracts:
- Module docstrings
- Class docstrings
- Method/function docstrings
- Parameter types and return types

**To improve API docs, update the Python docstrings in the source code**, not the RST file.

### Manual Pages

Manual pages are written in reStructuredText (RST) format.

#### Adding a New Page

1. Create a new `.rst` file in the `docs/` directory
2. Add the page to the `toctree` in `docs/index.rst`
3. Write your content using RST syntax

#### RST Syntax Examples

**Code blocks:**

```rst
.. code-block:: python

   def hello():
       print("Hello, world!")
```

**Admonitions:**

```rst
.. note::
   This is an informational note.

.. warning::
   This is a warning.

.. danger::
   This is a danger notice.
```

**Tables:**

```rst
.. list-table::
   :header-rows: 1

   * - Column 1
     - Column 2
   * - Value 1
     - Value 2
```

### Style Guide

- Use clear, concise language
- Include code examples where appropriate
- Use admonitions for important notes, warnings, and tips
- Keep line length reasonable (around 100 characters)
- Use proper headings hierarchy (= for title, - for sections, ~ for subsections)

## Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

The deployment is handled by the `.github/workflows/docs.yml` GitHub Actions workflow, which:
1. Installs Sphinx and dependencies
2. Installs the package (required for autodoc)
3. Builds the documentation with `sphinx-build`
4. Deploys to GitHub Pages

### Manual Deployment

To manually deploy documentation:

```bash
# Build the docs
sphinx-build -b html docs docs/_build/html

# Deploy to GitHub Pages (requires gh CLI or manual push)
# Note: Automated via GitHub Actions
```

## Configuration

Documentation configuration is in `docs/conf.py`.

Key configuration sections:

- `extensions`: Enabled Sphinx extensions (autodoc, napoleon, etc.)
- `html_theme`: Theme configuration (using Read the Docs theme)
- `autodoc_default_options`: Default options for autodoc
- `napoleon_*`: Settings for Google-style docstrings

## Links

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
