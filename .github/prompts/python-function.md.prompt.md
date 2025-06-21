---
mode: 'agent'
description: 'Python Function Design Prompt'
---

Create a Python function with the following structure:

## Requirements
- Type hints for all parameters and return value
- Comprehensive docstring with examples
- Input validation where appropriate
- Proper error handling
- Consider edge cases

## Template
```python
def function_name(
    param1: Type1,
    param2: Type2,
    optional_param: Optional[Type3] = None,
    **kwargs: Any
) -> ReturnType:
    """Brief description of what the function does.

    Detailed description if needed. Explain the algorithm,
    assumptions, or important behavior.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        optional_param: Description of optional parameter
        **kwargs: Additional keyword arguments

    Returns:
        Description of return value

    Raises:
        ValueError: When input validation fails
        TypeError: When wrong type is provided
        CustomError: When specific condition occurs

    Example:
        >>> result = function_name("value1", 42)
        >>> print(result)
        expected_output

        >>> # Edge case example
        >>> result = function_name("", 0)
        >>> print(result)
        edge_case_output
    """
    # Input validation
    if not param1:
        raise ValueError("param1 cannot be empty")

    if param2 < 0:
        raise ValueError("param2 must be non-negative")

    try:
        # Main logic here
        result = process_data(param1, param2)

        # Additional processing if optional_param provided
        if optional_param is not None:
            result = enhance_result(result, optional_param)

        return result

    except SpecificException as e:
        # Handle specific errors
        raise CustomError(f"Processing failed: {e}") from e
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in function_name: {e}")
        raise
```
