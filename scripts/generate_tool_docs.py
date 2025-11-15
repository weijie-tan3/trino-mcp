#!/usr/bin/env python3
"""Generate tool documentation from MCP server definitions.

This script extracts tool information from the Trino MCP server and generates
markdown documentation automatically, avoiding manual maintenance.
"""

import ast
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def extract_tools_from_ast(server_file: Path) -> List[Dict[str, Any]]:
    """Extract tool information from server.py using AST parsing.
    
    This avoids importing the module which would require Trino connection.
    """
    with open(server_file, 'r') as f:
        tree = ast.parse(f.read())
    
    tools = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if function has @mcp.tool() decorator
            has_tool_decorator = any(
                isinstance(dec, ast.Call) and 
                isinstance(dec.func, ast.Attribute) and
                dec.func.attr == 'tool'
                for dec in node.decorator_list
            )
            
            if not has_tool_decorator:
                continue
            
            # Extract function name
            tool_name = node.name
            
            # Extract docstring
            docstring = ast.get_docstring(node) or ""
            
            # Split docstring into description and args
            description = ""
            args_section = {}
            
            if docstring:
                lines = docstring.split('\n')
                desc_lines = []
                in_args = False
                current_arg = None
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('Args:'):
                        in_args = True
                        continue
                    
                    if not in_args:
                        if stripped:
                            desc_lines.append(stripped)
                    else:
                        # Parse args section
                        if ':' in stripped and not stripped.startswith(' '):
                            parts = stripped.split(':', 1)
                            arg_name = parts[0].strip()
                            arg_desc = parts[1].strip() if len(parts) > 1 else ""
                            args_section[arg_name] = arg_desc
                
                description = ' '.join(desc_lines)
            
            # Extract parameters from function signature
            parameters = {}
            for arg in node.args.args:
                if arg.arg == 'self':
                    continue
                    
                param_info = {
                    'name': arg.arg,
                    'description': args_section.get(arg.arg, ""),
                    'required': True,
                    'type': 'string'
                }
                
                # Check if parameter has default value
                defaults_offset = len(node.args.args) - len(node.args.defaults)
                arg_index = node.args.args.index(arg)
                if arg_index >= defaults_offset:
                    default_index = arg_index - defaults_offset
                    if default_index < len(node.args.defaults):
                        default_value = node.args.defaults[default_index]
                        # Check if default is empty string
                        if isinstance(default_value, ast.Constant) and default_value.value == "":
                            param_info['required'] = False
                        # Check if it's a Field() call with 'default' keyword argument
                        elif isinstance(default_value, ast.Call):
                            # Check if Field has 'default' keyword argument
                            has_default = any(
                                kw.arg == 'default' for kw in default_value.keywords
                            )
                            if has_default:
                                param_info['required'] = False
                            # If Field() without default, it's still required
                
                parameters[arg.arg] = param_info
            
            tools.append({
                'name': tool_name,
                'description': description,
                'parameters': parameters
            })
    
    return tools


def generate_markdown(tools: List[Dict[str, Any]]) -> str:
    """Generate markdown documentation for tools."""
    lines = ["## Available Tools\n"]
    
    for tool in tools:
        # Tool name as heading
        lines.append(f"### `{tool['name']}`")
        
        # Description
        if tool['description']:
            lines.append(tool['description'] + "\n")
        
        # Parameters
        if tool['parameters']:
            lines.append("**Parameters**:")
            for param_name, param_info in tool['parameters'].items():
                required = "required" if param_info['required'] else "optional"
                desc = param_info['description']
                lines.append(f"- `{param_name}` ({param_info['type']}, {required}): {desc}")
        else:
            lines.append("**Parameters**: None")
        
        lines.append("")
        
        # Example
        lines.append("**Example**:")
        lines.append("```")
        
        # Generate example call
        if tool['parameters']:
            example_params = []
            for param_name, param_info in tool['parameters'].items():
                if param_info['required']:
                    example_params.append(f'{param_name}="..."')
            if example_params:
                lines.append(f"{tool['name']}({', '.join(example_params)})")
            else:
                lines.append(f"{tool['name']}()")
        else:
            lines.append(f"{tool['name']}()")
        
        lines.append("```")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    # Get the server.py file path
    repo_root = Path(__file__).parent.parent
    server_file = repo_root / "src" / "trino_mcp" / "server.py"
    
    if not server_file.exists():
        print(f"Error: {server_file} not found", file=sys.stderr)
        sys.exit(1)
    
    # Extract tools
    tools = extract_tools_from_ast(server_file)
    
    # Generate markdown
    markdown = generate_markdown(tools)
    
    # Output to stdout
    print(markdown)
    
    # Also save to a file
    output_file = repo_root / "TOOLS.md"
    with open(output_file, 'w') as f:
        f.write(markdown)
    
    print(f"\n✓ Tool documentation written to {output_file}", file=sys.stderr)
    
    # Also generate JSON for programmatic use
    json_file = repo_root / "tools.json"
    with open(json_file, 'w') as f:
        json.dump(tools, f, indent=2)
    
    print(f"✓ Tool metadata written to {json_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
