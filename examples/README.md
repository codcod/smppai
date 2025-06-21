# SMPP Examples

This directory contains comprehensive examples demonstrating how to use the SMPP library.

## Overview

The examples demonstrate:
- Clean imports from the main `smpp` package
- Practical usage patterns for common scenarios
- Modern async/await patterns
- Error handling and connection management
- Event-driven programming

## Available Examples

### 1. `client.py` - Comprehensive Client Example
Demonstrates a full-featured SMPP client with:
- Connection management and binding
- SMS sending (regular and Unicode)
- Event handling for delivery receipts
- Multiple bind types (transmitter, receiver, transceiver)
- Error handling and reconnection

**Usage:**
```bash
PYTHONPATH=src python examples/client.py
```

### 2. `server.py` - SMSC Server Example
Shows how to create an SMSC-like server with:
- Client authentication
- Multi-client session management
- Message routing and processing
- Event handling for client connections
- Message ID generation

**Usage:**
```bash
PYTHONPATH=src python examples/server.py
## Running Examples

### Prerequisites
1. Install the library in development mode:
   ```bash
   uv sync
   ```

2. Or run with PYTHONPATH:
   ```bash
   PYTHONPATH=src python examples/client.py
   PYTHONPATH=src python examples/server.py
   ```

## Key Features Demonstrated

### Client Example Features
- **Connection Management**: Proper connect/disconnect handling
- **Multiple Bind Types**: Transmitter, receiver, and transceiver modes
- **Message Sending**: Regular SMS and Unicode message support
- **Event Handling**: Processing delivery receipts and incoming messages
- **Error Handling**: Robust error handling and reconnection logic
- **Context Managers**: Clean resource management with async context managers

### Server Example Features
- **Multi-Client Support**: Handle multiple simultaneous client connections
- **Authentication**: Customizable client authentication
- **Message Routing**: Process and route messages between clients
- **Event-Driven Architecture**: Handle client lifecycle events
- **Message ID Generation**: Automatic message ID assignment
- **Session Management**: Track client binding states and capabilities

## Implementation Notes

### Import Patterns
All examples use clean imports from the main `smpp` package:

```python
from smpp import (
    SMPPClient,
    SMPPServer,
    BindType,
    DataCoding,
    RegisteredDelivery,
    DeliverSm,
    SubmitSm
)
```

### Error Handling
Examples demonstrate proper exception handling:

```python
from smpp import (
    SMPPException,
    SMPPConnectionException,
    SMPPBindException,
    SMPPTimeoutException
)

try:
    await client.submit_sm(source, dest, message)
except SMPPTimeoutException:
    print("Message send timed out")
except SMPPBindException:
    print("Client not properly bound")
except SMPPException as e:
    print(f"SMPP error: {e}")
```

### Async Context Managers
Examples show proper resource management:

```python
async with SMPPClient(...) as client:
    await client.bind_transmitter()
    # Client automatically disconnects on exit
```

## Testing the Examples

1. **Start the Server**:
   ```bash
   PYTHONPATH=src python examples/server.py
   ```

2. **Run the Client** (in another terminal):
   ```bash
   PYTHONPATH=src python examples/client.py
   ```

The client will connect to the server, send test messages, and demonstrate various SMPP operations. The server will log all client activities and message processing.
   ```

### For Client Examples
You need a running SMSC server. You can:
1. Use the server example: `python3 examples/server.py`
2. Use a commercial SMSC simulator
3. Use an online SMSC testing service

### Configuration
Most examples use these default connection settings:
- Host: `localhost`
- Port: `2775`
- System ID: `test_client` / `test_server`
- Password: `password`

Modify the connection parameters in each example as needed for your setup.

## Example Scenarios

### Sending SMS
```python
# Simple SMS
message_id = await client.submit_sm(
    source_addr='1234',
    destination_addr='5678',
    short_message='Hello World!'
)

# Unicode SMS with delivery receipt
message_id = await client.submit_sm(
    source_addr='1234',
    destination_addr='5678',
    short_message='Hello World!'.encode('utf-8'),
    data_coding=DataCoding.UCS2,
    registered_delivery=RegisteredDelivery.SUCCESS_FAILURE
)
```

### Receiving Messages
```python
def handle_pdu(pdu):
    if isinstance(pdu, DeliverSm):
        message = pdu.short_message.decode('utf-8', errors='ignore')
        print(f'Received: {message}')

client.on_pdu_received = handle_pdu
await client.bind_receiver()
```

### Server Setup
```python
server = SMPPServer(host='localhost', port=2775)

def authenticate(system_id, password, system_type):
    return system_id == 'test' and password == 'pass'

server.authenticate = authenticate
await server.start()
```

## Error Handling

All examples include comprehensive error handling patterns:
```python
try:
    await client.connect()
    await client.bind_transmitter()
    message_id = await client.submit_sm('1234', '5678', 'Test')
except SMPPConnectionException as e:
    print(f'Connection error: {e}')
except SMPPBindException as e:
    print(f'Bind error: {e}')
except SMPPException as e:
    print(f'SMPP error: {e}')
finally:
    await client.disconnect()
```

## Performance Tips

1. **Use Transceiver Mode**: More efficient than separate transmitter/receiver connections
2. **Configure Timeouts**: Adjust timeouts based on your network conditions
3. **Handle Enquire Links**: Implement proper keepalive handling
4. **Connection Pooling**: For high-volume applications, consider connection pooling
5. **Async Operations**: Always use async/await for non-blocking operations

## Troubleshooting

- **Connection Refused**: Check if server is running and port is correct
- **Bind Failures**: Verify credentials and system_id
- **Message Failures**: Check message encoding and SMSC limits
- **Timeouts**: Adjust timeout values for your network conditions

1. **Use connection pooling** for high-throughput applications
2. **Bind as transceiver** when you need both send and receive capability
3. **Handle events asynchronously** to avoid blocking the main thread
4. **Use proper encoding** (UCS2 for Unicode, default for ASCII)
5. **Implement reconnection logic** for production deployments

## Next Steps

After reviewing these examples:
1. Start with `simple_examples.py` to understand the new APIs
2. Study `client.py` for comprehensive client usage patterns
3. Review `server.py` if you need to implement server functionality
4. Check the main README for deployment and production considerations

## Support

For questions about the examples or the library:
1. Check the main project documentation
2. Review the inline comments in each example
3. Examine the test files for additional usage patterns
