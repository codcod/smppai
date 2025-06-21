---
mode: 'ask'
description: 'Python Class Design Prompt'
---

You are a Python architecture expert. Design classes that follow these principles:

## Design Principles
- Single Responsibility Principle
- Open/Closed Principle
- Dependency Injection
- Composition over Inheritance
- Immutability where appropriate

## Requirements
- Use dataclasses or pydantic models for data structures
- Implement proper `__init__`, `__repr__`, `__eq__` methods
- Add type hints for all methods and attributes
- Include comprehensive docstrings
- Handle edge cases and validation
- Consider thread safety if applicable

## Class Structure Template
```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ExampleClass:
    """Brief description of the class purpose.

    Attributes:
        attribute_name: Description of attribute

    Example:
        >>> obj = ExampleClass(param1="value")
        >>> obj.method_name()
        "expected_result"
    """

    def __post_init__(self):
        """Validation and setup after initialization."""
        pass

    def public_method(self) -> ReturnType:
        """Public method with clear purpose."""
        pass

    def _private_method(self) -> ReturnType:
        """Private helper method."""
        pass
```

## Additional Considerations
- Factory methods for complex initialization
- Context managers for resource management
- Property decorators for computed attributes
- Class methods for alternative constructors
