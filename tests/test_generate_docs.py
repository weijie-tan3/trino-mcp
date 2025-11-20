"""Tests for the tool documentation generation script."""

import ast
import json
from pathlib import Path

import pytest


def test_generate_tool_docs_script_exists():
    """Test that the generate_tool_docs.py script exists."""
    script_path = Path(__file__).parent.parent / "scripts" / "generate_tool_docs.py"
    assert script_path.exists(), "generate_tool_docs.py script should exist"
    assert script_path.is_file(), "generate_tool_docs.py should be a file"


def test_extract_tools_from_ast():
    """Test extracting tools from AST."""
    from scripts.generate_tool_docs import extract_tools_from_ast
    
    server_file = Path(__file__).parent.parent / "src" / "trino_mcp" / "server.py"
    tools = extract_tools_from_ast(server_file)
    
    # Should extract all 8 tools
    assert len(tools) == 8, f"Expected 8 tools, got {len(tools)}"
    
    # Check tool names
    tool_names = [tool['name'] for tool in tools]
    expected_names = [
        'list_catalogs',
        'list_schemas',
        'list_tables',
        'describe_table',
        'execute_query_read_only',
        'execute_query',
        'show_create_table',
        'get_table_stats'
    ]
    assert tool_names == expected_names, f"Tool names mismatch: {tool_names}"


def test_list_catalogs_extracted_correctly():
    """Test list_catalogs tool extraction."""
    from scripts.generate_tool_docs import extract_tools_from_ast
    
    server_file = Path(__file__).parent.parent / "src" / "trino_mcp" / "server.py"
    tools = extract_tools_from_ast(server_file)
    
    list_catalogs = next(t for t in tools if t['name'] == 'list_catalogs')
    assert 'List all available Trino catalogs' in list_catalogs['description']
    assert len(list_catalogs['parameters']) == 0, "list_catalogs should have no parameters"


def test_list_schemas_extracted_correctly():
    """Test list_schemas tool extraction."""
    from scripts.generate_tool_docs import extract_tools_from_ast
    
    server_file = Path(__file__).parent.parent / "src" / "trino_mcp" / "server.py"
    tools = extract_tools_from_ast(server_file)
    
    list_schemas = next(t for t in tools if t['name'] == 'list_schemas')
    assert 'catalog' in list_schemas['parameters']
    assert list_schemas['parameters']['catalog']['required'] is True, "catalog should be required"


def test_describe_table_extracted_correctly():
    """Test describe_table tool extraction with optional parameters."""
    from scripts.generate_tool_docs import extract_tools_from_ast
    
    server_file = Path(__file__).parent.parent / "src" / "trino_mcp" / "server.py"
    tools = extract_tools_from_ast(server_file)
    
    describe_table = next(t for t in tools if t['name'] == 'describe_table')
    assert 'table' in describe_table['parameters']
    assert 'catalog' in describe_table['parameters']
    assert 'schema' in describe_table['parameters']
    
    # table should be required, catalog and schema should be optional
    assert describe_table['parameters']['table']['required'] is True
    assert describe_table['parameters']['catalog']['required'] is False
    assert describe_table['parameters']['schema']['required'] is False


def test_generate_markdown():
    """Test markdown generation."""
    from scripts.generate_tool_docs import generate_markdown
    
    # Create sample tool data
    tools = [
        {
            'name': 'test_tool',
            'description': 'Test tool description',
            'parameters': {
                'param1': {
                    'name': 'param1',
                    'description': 'Required parameter',
                    'required': True,
                    'type': 'string'
                },
                'param2': {
                    'name': 'param2',
                    'description': 'Optional parameter',
                    'required': False,
                    'type': 'string'
                }
            }
        }
    ]
    
    markdown = generate_markdown(tools)
    
    # Check structure
    assert '## Available Tools' in markdown
    assert '### `test_tool`' in markdown
    assert 'Test tool description' in markdown
    assert 'param1' in markdown
    assert 'param2' in markdown
    assert 'required' in markdown
    assert 'optional' in markdown
    assert '**Example**:' in markdown


def test_script_runs_without_errors(tmp_path):
    """Test that the script runs without errors."""
    import subprocess
    import sys
    
    script_path = Path(__file__).parent.parent / "scripts" / "generate_tool_docs.py"
    
    # Run the script
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    
    # Check exit code
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"
    
    # Check outputs
    assert "Tool documentation written to" in result.stderr
    assert "Tool metadata written to" in result.stderr


def test_generated_files_exist():
    """Test that generated files exist after running script."""
    import subprocess
    import sys
    
    script_path = Path(__file__).parent.parent / "scripts" / "generate_tool_docs.py"
    repo_root = Path(__file__).parent.parent
    
    # Run the script
    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=repo_root,
        capture_output=True
    )
    
    # Check files exist
    tools_md = repo_root / "TOOLS.md"
    tools_json = repo_root / "tools.json"
    
    assert tools_md.exists(), "TOOLS.md should be generated"
    assert tools_json.exists(), "tools.json should be generated"
    
    # Verify JSON is valid
    with open(tools_json, 'r') as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 8  # Should have 8 tools


def test_json_structure():
    """Test the structure of generated JSON."""
    import subprocess
    import sys
    
    script_path = Path(__file__).parent.parent / "scripts" / "generate_tool_docs.py"
    repo_root = Path(__file__).parent.parent
    
    # Run the script
    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=repo_root,
        capture_output=True
    )
    
    # Load JSON
    tools_json = repo_root / "tools.json"
    with open(tools_json, 'r') as f:
        tools = json.load(f)
    
    # Check structure of first tool
    for tool in tools:
        assert 'name' in tool
        assert 'description' in tool
        assert 'parameters' in tool
        assert isinstance(tool['name'], str)
        assert isinstance(tool['description'], str)
        assert isinstance(tool['parameters'], dict)
        
        # Check parameter structure
        for param_name, param_info in tool['parameters'].items():
            assert 'name' in param_info
            assert 'description' in param_info
            assert 'required' in param_info
            assert 'type' in param_info
            assert isinstance(param_info['required'], bool)
