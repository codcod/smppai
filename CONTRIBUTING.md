# Contributing to smppai

Thank you for your interest in contributing to smppai! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/smppai.git
   cd smppai
   ```

2. **Install uv (if not already installed)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up development environment**
   ```bash
   uv sync --all-extras --dev
   ```

4. **Run tests to ensure everything works**
   ```bash
   uv run pytest
   ```

## 📝 Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) for consistent and semantic commit messages. This enables automated versioning and changelog generation.

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | New feature | Minor (0.x.0) |
| `fix` | Bug fix | Patch (0.0.x) |
| `perf` | Performance improvement | Patch (0.0.x) |
| `docs` | Documentation only | None |
| `style` | Code style changes | None |
| `refactor` | Code refactoring | None |
| `test` | Adding/updating tests | None |
| `build` | Build system changes | None |
| `ci` | CI configuration changes | None |
| `chore` | Maintenance tasks | None |

### Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or use `!` after the type:

```bash
feat!: remove deprecated API endpoints

BREAKING CHANGE: The legacy v1 API has been removed. Use v2 endpoints instead.
```

### Examples

```bash
# Feature addition
feat(client): add connection pooling support

# Bug fix
fix(server): resolve memory leak in PDU handling

# Breaking change
feat(protocol)!: redesign PDU structure for better performance

BREAKING CHANGE: PDU class constructors now require explicit parameters

# Documentation
docs: update installation instructions

# Refactoring
refactor(transport): simplify connection state management
```

### Scopes

Common scopes in this project:
- `client` - SMPP client functionality
- `server` - SMPP server functionality
- `protocol` - SMPP protocol implementation
- `transport` - Connection and transport layer
- `config` - Configuration management
- `examples` - Example code
- `tests` - Test suite

## 🔧 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Write code following the project's coding standards
- Add tests for new functionality
- Update documentation as needed

### 3. Run Quality Checks

```bash
# Format code
uv run ruff format src tests

# Check linting
uv run ruff check src tests

# Type checking
uv run mypy src

# Run tests
uv run pytest

# Security check
uv run bandit -r src/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat(scope): add new feature description"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request through GitHub.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/smpp

# Run specific test file
uv run pytest tests/unit/test_specific.py

# Run specific test
uv run pytest tests/unit/test_specific.py::TestClass::test_method
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Use descriptive test names
- Follow the existing test patterns
- Ensure good test coverage
- Mock external dependencies

## 📋 Code Style

### Python Style

- Follow PEP 8 with our Ruff configuration
- Use type hints for all public functions
- Maximum line length: 88 characters
- Use single quotes for strings
- Follow the existing code patterns

### Documentation

- Use Google-style docstrings
- Document all public APIs
- Include examples in docstrings when helpful
- Keep README.md up to date

## 🚀 Release Process

Releases are automated using semantic-release:

1. **Merge to main**: When PRs are merged to main with conventional commits
2. **Automated versioning**: semantic-release analyzes commits and determines version bump
3. **Changelog generation**: Automatic changelog based on conventional commits
4. **GitHub release**: Automated release creation
5. **PyPI publishing**: Automatic package publishing (if configured)

### Manual Release

If needed, maintainers can trigger a manual release:

```bash
# Dry run
uv run semantic-release version --print

# Create release
uv run semantic-release publish
```

## 📊 Project Structure

```
smppai/
├── src/smpp/           # Main package
│   ├── client/         # SMPP client implementation
│   ├── server/         # SMPP server implementation
│   ├── protocol/       # SMPP protocol definitions
│   ├── transport/      # Connection and transport
│   └── config/         # Configuration management
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── examples/           # Usage examples
├── docs/               # Documentation
└── .github/            # GitHub workflows and templates
```

## 🤝 Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the README and docs/ directory

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)
- CHANGELOG.md

Thank you for contributing to smppai! 🎉
