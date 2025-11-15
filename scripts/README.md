# Scripts

This directory contains utility scripts for the Trino MCP project.

## generate_tool_docs.py

Automatically generates tool documentation from the MCP server implementation.

### Purpose

This script extracts tool information from `src/trino_mcp/server.py` using AST parsing and generates comprehensive documentation in multiple formats. This eliminates the need to manually maintain tool documentation in the README.

### Usage

```bash
# From repository root
python3 scripts/generate_tool_docs.py
```

### Output

The script generates two files in the repository root:

1. **TOOLS.md** - Human-readable markdown documentation with:
   - Tool names and descriptions
   - Parameter details (name, type, required/optional status)
   - Usage examples

2. **tools.json** - Machine-readable JSON metadata with:
   - Structured tool information
   - Parameter specifications
   - Suitable for programmatic consumption

### CI Integration

This script runs automatically in the CI pipeline (see `.github/workflows/ci.yml`):
- Executes on every push and pull request
- Uploads generated documentation as artifacts
- Artifacts retained for 90 days
- Ensures documentation stays in sync with code

### Testing

Tests for this script are in `tests/test_generate_docs.py`:
- Validates AST parsing correctness
- Checks parameter extraction (required vs optional)
- Verifies markdown generation
- Confirms JSON structure

### Design

The script uses AST (Abstract Syntax Tree) parsing to analyze the server code without importing it, avoiding the need for a Trino connection or environment setup. It specifically looks for:
- Functions decorated with `@mcp.tool()`
- Function docstrings and parameter descriptions
- Pydantic Field annotations to determine required/optional status
