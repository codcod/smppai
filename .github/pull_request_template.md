## 📋 Description
<!-- Describe your changes in detail -->

## 🏷️ Type of Change
<!-- Mark with "x" all that apply -->
- [ ] 🐛 **fix**: Bug fix (patch)
- [ ] ✨ **feat**: New feature (minor)
- [ ] 💥 **BREAKING CHANGE**: Breaking change (major)
- [ ] 📝 **docs**: Documentation only changes
- [ ] 🎨 **style**: Changes that do not affect the meaning of the code
- [ ] ♻️ **refactor**: Code change that neither fixes a bug nor adds a feature
- [ ] ⚡ **perf**: Performance improvement
- [ ] ✅ **test**: Adding missing tests or correcting existing tests
- [ ] 🔧 **build**: Changes that affect the build system or external dependencies
- [ ] 🔄 **ci**: Changes to CI configuration files and scripts
- [ ] 🧹 **chore**: Other changes that don't modify src or test files

## 🧪 Testing
<!-- Describe the tests you ran to verify your changes -->
- [ ] Tests pass locally with `uv run pytest`
- [ ] Linting passes with `uv run ruff check`
- [ ] Type checking passes with `uv run ty check src`
- [ ] Added tests for new functionality
- [ ] Updated documentation if needed

## 📝 Commit Message
<!--
Follow conventional commits format:
<type>[optional scope]: <description>

Examples:
- feat(server): add connection pooling support
- fix(client): resolve memory leak in PDU handling
- docs: update installation instructions
- refactor(protocol): simplify PDU encoding logic
-->

**Suggested commit message:**
```
type(scope): brief description

- Detailed change 1
- Detailed change 2
```

## 📚 Related Issues
<!-- Link any related issues -->
Closes #

## 📋 Checklist
- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
