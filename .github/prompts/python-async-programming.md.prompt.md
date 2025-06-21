---
mode: 'agent'
description: 'Async Python Programming Prompt'
---

You are an expert in Python asyncio programming. Write async code that:

## Best Practices
- Use `async def` and `await` properly
- Handle cancellation gracefully
- Implement proper resource cleanup
- Use connection pooling for I/O operations
- Handle timeouts appropriately
- Avoid blocking operations in async functions

## Common Patterns
- Use `asyncio.gather()` for concurrent operations
- Implement backpressure for high-throughput scenarios
- Use `asyncio.Queue` for producer-consumer patterns
- Create async context managers for resources
- Use `asyncio.create_task()` for fire-and-forget operations

## Error Handling
- Wrap operations in try-except blocks
- Use `asyncio.wait_for()` for timeouts
- Handle `asyncio.CancelledError` appropriately
- Log errors with proper context

## Template Structure
```python
import asyncio
from typing import Optional, AsyncIterator, AsyncContextManager
from contextlib import asynccontextmanager

class AsyncService:
    async def __aenter__(self):
        # Initialize resources
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup resources
        pass

    async def process_item(self, item: Any) -> Any:
        """Process a single item asynchronously."""
        try:
            # Async processing logic
            pass
        except asyncio.CancelledError:
            # Handle cancellation
            raise
        except Exception as e:
            # Handle other errors
            pass

    async def process_batch(self, items: List[Any]) -> List[Any]:
        """Process multiple items concurrently."""
        tasks = [self.process_item(item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)
```
