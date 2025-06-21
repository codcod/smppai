---
applyTo: "**/*.py"
---

# Copilot Instructions for Python Project

## Project Overview
This is an async SMPP (Short Message Peer-to-Peer) Protocol v3.4 implementation
in Python. The project follows modern Python packaging standards and uses a
clean modular architecture.

## Code Style & Standards

### **CORE PRINCIPLE: Absolute Minimal Changes**

- **ALWAYS prefer the smallest possible change that fixes the issue**
- **Never refactor existing working code unless specifically requested**
- **Only modify the exact lines/methods that need fixing**
- **Preserve existing code style, naming, and patterns**
- **Add code only when absolutely necessary to fix the specific issue**
- **When fixing bugs, change only what's broken, not what could be improved**

### Change Guidelines

```python
# ✅ GOOD: Minimal fix - only change the broken line
def broken_method(self, param: str) -> str:
    # ...existing code...
    return param.lower()  # Only change: was param.upper()

# ❌ BAD: Unnecessary refactoring while fixing
def broken_method(self, param: str) -> str:
    """Added unnecessary docstring."""
    # Reformatted existing code
    result = param.strip().lower()  # Added unnecessary .strip()
    return result
```

### Python Version & Compatibility
- **Target Python Version**: 3.13+
- **Type Hints**: Required for all public functions and methods
- **Async/Await**: Prefer async/await over callbacks for asynchronous operations

### Formatting & Linting
- **Formatter**: Ruff (configured in pyproject.toml)
- **Linter**: Ruff with E4, E7, E9, F, C90 rules
- **Line Length**: 88 characters
- **Quote Style**: Preserve existing quotes unless fixing syntax errors
- **Import Organization**: Fix only when addressing import-related issues

## Debugging & Problem Solving

### Minimal Fix Strategy
1. **Identify the exact error/issue**
2. **Find the minimal code change to fix it**
3. **Test that the fix works**
4. **Stop - don't improve unrelated code**

```python
# ✅ GOOD: Fix only the specific AttributeError
class Example:
    def __init__(self):
        self.value = None  # Only add this missing attribute

# ❌ BAD: Fix the error but also "improve" other things
class Example:
    """Added docstring while fixing AttributeError."""

    def __init__(self) -> None:  # Added type hint unnecessarily
        self.value: Optional[str] = None  # Added type hint unnecessarily
        self._internal_value = 0  # Added unrelated attribute
```

### Import Fixes
```python
# ✅ GOOD: Add only the missing import
from smpp.exceptions import SMPPTimeoutException  # Only add this

# ❌ BAD: Reorganize all imports while adding one
from smpp.exceptions import (  # Unnecessary reformatting
    SMPPConnectionException,
    SMPPException,
    SMPPTimeoutException,  # The only actually needed addition
)
```

### Exception Handling Fixes
```python
# ✅ GOOD: Fix only the specific exception issue
try:
    result = some_operation()
except ValueError as e:  # Only change: was bare except
    logger.error(f"Error: {e}")

# ❌ BAD: Rewrite entire error handling while fixing
try:
    result = some_operation()
except ValueError as e:
    logger.error(f"ValueError occurred: {e}")  # Unnecessary message change
except Exception as e:  # Added unnecessary catch-all
    logger.error(f"Unexpected error: {e}")
    raise
```

## Testing & Debugging

### Minimal Test Fixes
```python
# ✅ GOOD: Fix only the failing assertion
def test_example():
    result = function_under_test()
    assert result == "expected"  # Only fix: was wrong expected value

# ❌ BAD: Improve test while fixing
def test_example():
    """Added docstring while fixing assertion."""
    result = function_under_test()
    assert result == "expected", f"Got {result}"  # Added unnecessary message
    assert isinstance(result, str)  # Added unnecessary assertion
```

### Error Message Guidelines
- **Preserve existing error message format**
- **Change only the specific part that's incorrect**
- **Don't "improve" working error messages**

## Performance & Memory

### Minimal Performance Fixes
```python
# ✅ GOOD: Fix only the memory leak
async def cleanup_connections(self):
    for conn in self.connections:
        if not conn.is_alive():
            await conn.close()  # Only add this missing cleanup

# ❌ BAD: Optimize everything while fixing leak
async def cleanup_connections(self) -> None:  # Added type hint
    """Clean up dead connections."""  # Added docstring
    alive_connections = []  # Changed algorithm unnecessarily
    for conn in self.connections:
        if conn.is_alive():
            alive_connections.append(conn)
        else:
            await conn.close()
    self.connections = alive_connections
```

## Common Anti-Patterns to Avoid

### Don't "Fix" Working Code
```python
# ❌ BAD: Changing working code while fixing something else
# Original working code:
def working_method(self, data):
    return data.strip().upper()

# Don't change to:
def working_method(self, data: str) -> str:
    """Process data."""
    return data.strip().upper()
```

### Don't Consolidate Unrelated Changes
```python
# ❌ BAD: Multiple unrelated fixes in one change
# Fix import error AND format code AND add type hints

# ✅ GOOD: One focused fix
# Fix ONLY the import error, leave everything else unchanged
```

### Don't Anticipate Future Issues
```python
# ❌ BAD: Adding error handling "just in case"
def fix_method(self, value):
    try:  # Don't add this unless there's an actual error
        return self.process(value)
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

# ✅ GOOD: Fix only the actual reported issue
def fix_method(self, value):
    return self.process(value)  # Only fix what's broken
```

## Documentation Standards

### Minimal Documentation Changes
- **Add docstrings only when fixing documentation-related issues**
- **Update only incorrect/outdated information**
- **Don't add documentation to working undocumented code unless requested**

This project emphasizes making the smallest possible changes to achieve the
desired fix, preserving existing working code and patterns wherever possible.
