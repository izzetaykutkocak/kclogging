# Contributing to Immutable Log Widget

Thank you for your interest in contributing! This document provides guidelines
for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/immutable-log-widget/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Relevant code snippets or logs

### Suggesting Features

1. Check [Issues](https://github.com/yourusername/immutable-log-widget/issues) for existing suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest tests/ -v`
6. Format code: `black immutable_log_widget/ tests/`
7. Check linting: `flake8 immutable_log_widget/`
8. Update documentation if needed
9. Commit with clear messages: `git commit -m "Add feature: description"`
10. Push to your fork: `git push origin feature/your-feature-name`
11. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/immutable-log-widget.git
cd immutable-log-widget

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use type hints where appropriate
- Write docstrings for all public APIs
- Keep functions focused and small

## Testing

- Write tests for all new features
- Maintain >80% code coverage
- Test edge cases and error conditions
- Use pytest fixtures for setup

## Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Add docstrings to all public functions
- Include examples for new features

## Commit Messages

Use clear, descriptive commit messages:

```
Add feature: brief description

Longer explanation of what changed and why.

Fixes #123
```

## Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, your PR will be merged

## Questions?

Open an issue or start a discussion!

Thank you for contributing! 🎉
