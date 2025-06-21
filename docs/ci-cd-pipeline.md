# CI/CD Pipeline Documentation

This document describes the comprehensive GitHub Actions CI/CD pipeline for the smppai project.

## 🚀 Overview

The CI/CD pipeline implements automated testing, code quality checks, semantic versioning, and publishing workflows that follow modern DevOps best practices.

## 📋 Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:** Push to any branch, Pull requests to `main`

**Jobs:**

#### Lint & Format Check
- Runs `ruff check` for linting
- Runs `ruff format --check` for formatting validation
- Ensures code follows project style guidelines

#### Type Check
- Runs `mypy` type checking on source code
- Validates type annotations and catches type-related issues

#### Security Check
- Runs `bandit` security scanner
- Generates security report artifacts
- Non-blocking but provides security insights

#### Test
- Runs comprehensive test suite with `pytest`
- Matrix strategy (currently Python 3.13, easily expandable)
- Generates coverage reports (XML, HTML, terminal)
- Uploads coverage to Codecov (if token configured)
- Uploads test artifacts for analysis

#### Build Package
- Builds source and wheel distributions with `uv build`
- Validates package with `twine check`
- Runs only after lint, type-check, and test jobs pass
- Uploads build artifacts

#### Integration Tests
- Tests example code execution
- Validates import statements work correctly
- Ensures real-world usage scenarios function

#### All Checks Status
- Summary job that validates all other jobs passed
- Provides clear CI status for PR requirements

### 2. Release Pipeline (`.github/workflows/release.yml`)

**Triggers:** Push to `main` branch, Manual workflow dispatch

**Jobs:**

#### Semantic Release
- Analyzes conventional commits since last release
- Automatically determines version bump (major/minor/patch)
- Generates CHANGELOG.md
- Creates GitHub release with release notes
- Tags the release with semantic version

#### Publish to PyPI
- Runs only if a new release was created
- Uses PyPI trusted publishing (no API tokens needed)
- Publishes both source and wheel distributions
- Includes attestations for supply chain security

### 3. Commit Validation (`.github/workflows/validate-commits.yml`)

**Triggers:** Pull requests to `main`

**Purpose:**
- Validates PR commits follow conventional commit format
- Ensures semantic versioning can work correctly
- Provides helpful feedback on commit message format

## 🔧 Configuration Files

### `.commitlintrc.json`
- Configures conventional commit validation
- Defines allowed types: feat, fix, perf, docs, style, refactor, test, build, ci, chore
- Defines allowed scopes: client, server, protocol, transport, config, examples, tests, deps
- Sets formatting rules and limits

### `.github/dependabot.yml`
- Automated dependency updates
- Monitors Python dependencies (weekly)
- Monitors GitHub Actions (weekly)
- Creates PRs with conventional commit messages

### GitHub Issue Templates
- Bug report template (`.github/ISSUE_TEMPLATE/bug_report.md`)
- Feature request template (`.github/ISSUE_TEMPLATE/feature_request.md`)
- Documentation issue template (`.github/ISSUE_TEMPLATE/documentation.md`)

### Pull Request Template
- Guides contributors on conventional commits
- Includes checklists for code quality
- Encourages proper testing and documentation

## 📝 Conventional Commits

The project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types and Version Impact
- `feat`: New feature → Minor version bump (0.x.0)
- `fix`: Bug fix → Patch version bump (0.0.x)
- `perf`: Performance improvement → Patch version bump (0.0.x)
- `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`: No version bump

### Breaking Changes
- Add `!` after type: `feat!: breaking change`
- Add `BREAKING CHANGE:` in footer
- Results in major version bump (x.0.0)

### Examples
```bash
feat(client): add connection pooling support
fix(server): resolve memory leak in PDU handling
feat(protocol)!: redesign PDU structure

BREAKING CHANGE: PDU class constructors now require explicit parameters
```

## 🛠️ Development Workflow

### Local Development
```bash
# Setup
uv sync --all-extras --dev

# Quality checks
uv run ruff check src tests
uv run ruff format src tests
uv run mypy src
uv run pytest

# Security check
uv run bandit -r src/
```

### Pull Request Process
1. Create feature branch: `git checkout -b feat/your-feature`
2. Make changes following conventional commits
3. Run local quality checks
4. Push and create PR
5. CI automatically validates all checks
6. Merge to main triggers release process

### Release Process
1. **Automatic**: Merging PRs to main with conventional commits
2. **Manual**: Trigger release workflow manually if needed

Releases are fully automated:
- Version determination based on commit types
- CHANGELOG.md generation
- GitHub release creation
- PyPI package publishing

## 🔒 Security

### Supply Chain Security
- PyPI trusted publishing (no API keys stored)
- Package attestations for verification
- Dependabot for vulnerability monitoring
- Bandit security scanning

### Access Control
- Branch protection on `main`
- Required status checks
- No direct pushes to main (PRs only)
- Required conventional commit validation

## 📊 Monitoring & Reporting

### Code Coverage
- Automated coverage reporting
- Codecov integration (if configured)
- Coverage artifacts in CI runs
- Current server module: 98% coverage

### Quality Metrics
- Linting violations tracked
- Type checking errors reported
- Security scan results available
- Test results and artifacts preserved

## 🎯 Benefits

### For Developers
- ✅ Automated quality checks catch issues early
- ✅ Clear feedback on code standards
- ✅ Conventional commits guide contribution style
- ✅ Comprehensive testing ensures reliability

### For Maintainers
- ✅ Automated releases reduce manual work
- ✅ Semantic versioning enables API compatibility tracking
- ✅ Automated changelog generation documents changes
- ✅ Security scanning identifies vulnerabilities

### For Users
- ✅ Consistent, tested releases
- ✅ Clear version semantics for API changes
- ✅ Regular security updates
- ✅ Comprehensive documentation and examples

## 🔧 Customization

The pipeline is highly configurable:

- **Python versions**: Update matrix in ci.yml
- **Additional checks**: Add new jobs to ci.yml
- **Release channels**: Configure additional branches in semantic-release config
- **Commit validation**: Modify .commitlintrc.json rules
- **Dependencies**: Update dependabot.yml schedule

## 📚 Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)

This CI/CD pipeline ensures high code quality, automated releases, and excellent developer experience while maintaining security and reliability standards.
