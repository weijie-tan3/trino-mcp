# Contributing to Documentation

This guide explains how to work with the documentation for Trino MCP Server.

## Building Documentation Locally

### Prerequisites

Install documentation dependencies:

```bash
# Using pip
pip install mkdocs mkdocs-material

# Or using uv
uv pip install mkdocs mkdocs-material
```

### Build Documentation

Build the static documentation site:

```bash
# From the repository root
mkdocs build

# Build with strict mode (fails on warnings)
mkdocs build --strict
```

The built site will be in the `site/` directory.

### Serve Documentation Locally

Start a local development server:

```bash
mkdocs serve
```

The documentation will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

The server automatically reloads when you make changes to the documentation files.

## Documentation Structure

```
docs/
├── index.md              # Home page
├── installation.md       # Installation guide
├── configuration.md      # Configuration reference
├── quickstart.md         # Quick start guide
├── tools.md             # Available MCP tools
├── authentication.md     # Authentication methods
├── examples.md          # Usage examples
├── api.md               # API reference
├── contributing.md       # Contributing guidelines
└── license.md           # License information
```

## Writing Documentation

### Adding a New Page

1. Create a new `.md` file in the `docs/` directory
2. Add the page to the `nav` section in `mkdocs.yml`
3. Write your content using Markdown

### Markdown Extensions

The documentation supports several Markdown extensions:

- **Code blocks with syntax highlighting**:
  ````markdown
  ```python
  def hello():
      print("Hello, world!")
  ```
  ````

- **Admonitions**:
  ```markdown
  !!! note "This is a note"
      This is the content of the note.

  !!! warning "This is a warning"
      This is important information.
  ```

- **Tabs**:
  ````markdown
  === "Tab 1"
      Content for tab 1

  === "Tab 2"
      Content for tab 2
  ````

- **Tables**:
  ```markdown
  | Column 1 | Column 2 |
  |----------|----------|
  | Value 1  | Value 2  |
  ```

### Style Guide

- Use clear, concise language
- Include code examples where appropriate
- Use admonitions for important notes, warnings, and tips
- Keep line length reasonable (around 100 characters)
- Use proper headings hierarchy (H1 for title, H2 for sections, etc.)

## Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

The deployment is handled by the `.github/workflows/docs.yml` GitHub Actions workflow.

### Manual Deployment

To manually deploy documentation:

```bash
# Build and deploy to GitHub Pages
mkdocs gh-deploy
```

## Configuration

Documentation configuration is in `mkdocs.yml` at the repository root.

Key configuration sections:

- `site_name`: Site title
- `theme`: Theme configuration (Material theme)
- `nav`: Navigation structure
- `plugins`: Enabled plugins
- `markdown_extensions`: Enabled Markdown extensions

## Links

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
