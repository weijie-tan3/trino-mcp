#!/usr/bin/env python3
"""Validate the Trino MCP server installation and configuration."""

import sys
import os
from pathlib import Path


def validate_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment configuration...")

    required = ["TRINO_HOST", "TRINO_PORT", "TRINO_USER"]
    optional = ["TRINO_CATALOG", "TRINO_SCHEMA", "TRINO_PASSWORD", "TRINO_HTTP_SCHEME"]

    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("   Please set them in your .env file or environment")
        return False

    print("✅ Required environment variables are set")

    for var in optional:
        value = os.getenv(var)
        if value:
            print(f"   ℹ️  {var} = {value}")

    return True


def validate_dependencies():
    """Check if required Python packages are installed."""
    print("\n🔍 Checking dependencies...")

    required_packages = {
        "mcp": "MCP SDK",
        "trino": "Trino Python client",
        "dotenv": "python-dotenv",
    }

    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {name} is installed")
        except ImportError:
            missing.append(name)
            print(f"   ❌ {name} is not installed")

    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("   Install with: uv pip install .")
        return False

    return True


def validate_trino_connection():
    """Test connection to Trino server."""
    print("\n🔍 Testing Trino connection...")

    try:
        from trino_mcp.config import load_config
        from trino_mcp.client import TrinoClient

        config = load_config()
        print(f"   Connecting to {config.host}:{config.port}...")

        client = TrinoClient(config)
        catalogs = client.list_catalogs()

        print(f"   ✅ Successfully connected to Trino!")
        print(f"   ℹ️  Found {len(catalogs)} catalog(s): {', '.join(catalogs[:5])}")
        if len(catalogs) > 5:
            print(f"      ... and {len(catalogs) - 5} more")

        return True
    except Exception as e:
        print(f"   ❌ Failed to connect to Trino: {e}")
        print("   Please check your connection settings and ensure Trino is running")
        return False


def validate_mcp_server():
    """Validate MCP server can be imported."""
    print("\n🔍 Validating MCP server...")

    try:
        from trino_mcp.server import mcp

        print(f"   ✅ MCP server is properly configured")
        print(f"   ℹ️  MCP server name: {mcp.name}")

        return True
    except Exception as e:
        print(f"   ❌ Failed to validate MCP server: {e}")
        return False


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("Trino MCP Server - Validation Script")
    print("=" * 60)

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  No .env file found. Using environment variables only.")
        print("   Consider creating .env from .env.example")
    else:
        print("\n✅ Found .env file")

    # Run validation checks
    checks = [
        ("Environment", validate_environment),
        ("Dependencies", validate_dependencies),
        ("MCP Server", validate_mcp_server),
        ("Trino Connection", validate_trino_connection),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Unexpected error during {name} check: {e}")
            results[name] = False

    # Print summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Your Trino MCP server is ready to use.")
        print("\nTo run the server:")
        print("  uvx --from . trino-mcp")
        print("\nOr see QUICKSTART.md for more options.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
