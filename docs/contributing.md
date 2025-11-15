# Contributing

Thank you for your interest in contributing to Trino MCP Server! This guide will help you get started.

## Ways to Contribute

- 🐛 **Report Bugs**: Open an issue describing the bug
- 💡 **Suggest Features**: Propose new features or improvements
- 📝 **Improve Documentation**: Fix typos, clarify instructions, add examples
- 🔧 **Submit Code**: Fix bugs or implement new features
- ⭐ **Star the Project**: Show your support on GitHub

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- uv (recommended) or pip
- A Trino server for testing (optional)

### Setting Up Development Environment

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/trino-mcp.git
cd trino-mcp
```

2. **Install dependencies:**

```bash
# Using uv (recommended)
uv sync --all-extras --dev

# Or using pip
pip install -e ".[dev]"
```

3. **Create a `.env` file for testing:**

```bash
cp .env.example .env
# Edit .env with your Trino connection details
```

## Development Workflow

### Making Changes

1. **Create a new branch:**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

2. **Make your changes:**

Edit the relevant files in `src/trino_mcp/`

3. **Test your changes:**

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/trino_mcp --cov-report=term
```

4. **Format your code:**

```bash
# Format with black
black src/ tests/

# Check formatting
black --check src/ tests/
```

5. **Type check:**

```bash
mypy src/trino_mcp --ignore-missing-imports
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src/trino_mcp --cov-report=html
```

### Testing with a Real Trino Instance

If you have access to a Trino server:

```bash
# Set up environment variables
export TRINO_HOST=localhost
export TRINO_PORT=8080
export TRINO_USER=trino

# Run the server
python -m trino_mcp.server
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) style guide with some modifications:

- **Line length**: 100 characters (enforced by black)
- **Imports**: Organized with `isort`
- **Type hints**: Required for all public functions
- **Docstrings**: Google style docstrings

### Example Code Style

```python
"""Module docstring."""

import logging
from typing import Optional

from pydantic import Field

logger = logging.getLogger(__name__)


class MyClass:
    """Class docstring.
    
    Attributes:
        name: The name of the object.
        value: The value of the object.
    """
    
    def __init__(self, name: str, value: int) -> None:
        """Initialize MyClass.
        
        Args:
            name: The name to set.
            value: The value to set.
        """
        self.name = name
        self.value = value
    
    def process(self, input_data: str) -> Optional[str]:
        """Process input data.
        
        Args:
            input_data: The data to process.
            
        Returns:
            The processed result, or None if processing failed.
            
        Raises:
            ValueError: If input_data is empty.
        """
        if not input_data:
            raise ValueError("input_data cannot be empty")
        return input_data.upper()
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(client): add support for query timeout configuration
fix(server): handle connection errors gracefully
docs(readme): update installation instructions
test(client): add tests for list_catalogs method
```

## Submitting Changes

### Pull Request Process

1. **Ensure your code passes all checks:**

```bash
# Run tests
pytest

# Format code
black src/ tests/

# Type check
mypy src/trino_mcp
```

2. **Update documentation:**

- Update docstrings for new/modified functions
- Update relevant `.md` files in `docs/`
- Add examples if introducing new features

3. **Update CHANGELOG:**

Add an entry describing your changes (if applicable)

4. **Push your branch:**

```bash
git push origin feature/your-feature-name
```

5. **Open a Pull Request:**

- Go to GitHub and open a PR from your branch
- Fill out the PR template
- Link related issues
- Request review

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted with black
- [ ] Type hints are added
- [ ] Docstrings are updated
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if applicable)
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete

## Reporting Issues

### Bug Reports

Include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Exact steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, package version
- **Logs**: Relevant error messages or logs

**Template:**

```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 14.1]
- Python: [e.g., 3.12.0]
- Package Version: [e.g., 0.1.0]
- Trino Version: [e.g., 435]

## Additional Context
Any other relevant information
```

### Feature Requests

Include:
- **Use Case**: Describe the problem you're trying to solve
- **Proposed Solution**: Your suggested approach
- **Alternatives**: Other solutions you've considered
- **Additional Context**: Any other relevant information

## Code Review Process

1. **Automated Checks**: CI runs tests, linting, and type checking
2. **Manual Review**: Maintainers review code for quality and correctness
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR will be merged
5. **Release**: Changes included in next release

## Project Structure

```
trino-mcp/
├── .github/           # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml     # CI configuration
├── docs/              # Documentation
│   ├── index.md
│   ├── installation.md
│   └── ...
├── examples/          # Example configurations
├── src/               # Source code
│   └── trino_mcp/
│       ├── __init__.py
│       ├── client.py
│       ├── config.py
│       └── server.py
├── tests/             # Tests
│   ├── test_client.py
│   ├── test_config.py
│   └── test_server.py
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore rules
├── LICENSE            # MIT License
├── README.md          # Project README
├── mkdocs.yml         # Documentation configuration
├── pyproject.toml     # Project metadata and dependencies
└── pytest.ini         # Pytest configuration
```

## Getting Help

- **GitHub Issues**: Open an issue for questions
- **GitHub Discussions**: For general questions and discussions
- **Documentation**: Check the [documentation](https://weijie-tan3.github.io/trino-mcp/)
- **Trino Docs**: [Trino documentation](https://trino.io/docs/)
- **MCP Docs**: [MCP documentation](https://modelcontextprotocol.io/)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes
- Project documentation

Thank you for contributing! 🎉
