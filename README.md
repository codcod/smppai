# SMPP AI - Async SMPP Protocol v3.4 Implementation

A comprehensive, async implementation of the SMPP (Short Message Peer-to-Peer) protocol v3.4 in Python, built with modern asyncio patterns.

## Features

**Complete SMPP v3.4 Implementation**
- Full protocol support according to SMPP v3.4 specification
- All PDU types implemented with proper encoding/decoding
- Comprehensive error handling and status codes

**Modern Async Architecture**
- Built with Python's asyncio for high performance
- Non-blocking I/O operations
- Concurrent connection handling
- Async context manager support

**SMPP Client (ESME)**
- Transmitter, Receiver, and Transceiver binding modes
- SMS sending with delivery receipts
- Connection management with automatic enquire_link
- Event-driven message handling

**SMPP Server (SMSC)**
- Multi-client connection support
- Authentication and authorization
- Message routing capabilities
- Configurable for testing and production

**Advanced Features**
- Optional parameters (TLV) support
- Unicode message handling
- Connection resilience and reconnection
- Comprehensive logging and debugging

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd smppai

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Quick Start

### Simple SMS Client

```python
import asyncio
from smpp import SMPPClient

async def send_sms():
    client = SMPPClient(
        host="localhost",
        port=2775,
        system_id="test_client",
        password="password"
    )

    async with client:
        # Bind as transmitter
        await client.bind_transmitter()

        # Send SMS
        message_id = await client.submit_sm(
            source_addr="1234",
            destination_addr="5678",
            short_message="Hello World!"
        )

        print(f"Message sent with ID: {message_id}")

asyncio.run(send_sms())
```

### SMS Server (SMSC)

```python
import asyncio
from smpp import SMPPServer

async def run_server():
    server = SMPPServer(
        host="localhost",
        port=2775,
        system_id="TEST_SMSC"
    )

    async with server:
        print("SMSC server running on localhost:2775")
        # Keep server running
        await asyncio.sleep(3600)  # Run for 1 hour

asyncio.run(run_server())
```

## Comprehensive Examples

### Advanced Client Usage

```python
import asyncio
from smpp import SMPPClient, DeliverSm, RegisteredDelivery, DataCoding

class SMSHandler:
    def __init__(self):
        self.client = SMPPClient(
            host="localhost",
            port=2775,
            system_id="my_client",
            password="my_password",
            system_type="SMS_APP",
            enquire_link_interval=30.0
        )

    async def start(self):
        """Start the SMS handler"""
        await self.client.connect()
        await self.client.bind_transceiver()

        # Set up PDU handler
        self.client.on_pdu_received = self.handle_incoming_pdu
        self.client.on_connection_lost = self.handle_connection_lost

        print("SMS handler started")

    def handle_incoming_pdu(self, pdu):
        """Handle incoming PDUs"""
        if isinstance(pdu, DeliverSm):
            message = pdu.short_message.decode('utf-8', errors='ignore')
            if pdu.esm_class & 0x04:  # Delivery receipt
                print(f"Delivery receipt: {message}")
            else:  # Regular SMS
                print(f"SMS from {pdu.source_addr}: {message}")

    def handle_connection_lost(self, error):
        """Handle connection failures"""
        print(f"Connection lost: {error}")
        # Implement reconnection logic here

    async def send_sms(self, to_number: str, message: str, request_receipt: bool = True):
        """Send SMS with optional delivery receipt"""
        try:
            message_id = await self.client.submit_sm(
                source_addr="12345",
                destination_addr=to_number,
                short_message=message,
                registered_delivery=RegisteredDelivery.SUCCESS_FAILURE if request_receipt else RegisteredDelivery.NO_RECEIPT,
                data_coding=DataCoding.DEFAULT
            )
            print(f"SMS sent to {to_number}, ID: {message_id}")
            return message_id
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return None

    async def send_unicode_sms(self, to_number: str, message: str):
        """Send Unicode SMS"""
        try:
            message_id = await self.client.submit_sm(
                source_addr="12345",
                destination_addr=to_number,
                short_message=message.encode('utf-8'),
                data_coding=DataCoding.UCS2
            )
            print(f"Unicode SMS sent to {to_number}, ID: {message_id}")
            return message_id
        except Exception as e:
            print(f"Failed to send Unicode SMS: {e}")
            return None

    async def stop(self):
        """Stop the SMS handler"""
        await self.client.disconnect()
        print("SMS handler stopped")

# Usage
async def main():
    handler = SMSHandler()
    try:
        await handler.start()

        # Send messages
        await handler.send_sms("67890", "Hello World!")
        await handler.send_unicode_sms("67890", "Hello World!")

        # Keep running to receive messages
        await asyncio.sleep(60)

    finally:
        await handler.stop()

asyncio.run(main())
```

### Custom SMSC Server

```python
import asyncio
from smpp import SMPPServer, SubmitSm

class CustomSMSC:
    def __init__(self):
        self.server = SMPPServer(
            host="0.0.0.0",
            port=2775,
            system_id="CUSTOM_SMSC",
            max_connections=100
        )

        # Set up authentication handler
        self.server.authenticate = self.authenticate_client

        # Set up event handlers
        self.server.on_message_received = self.handle_message
        self.server.on_client_connected = self.handle_client_connected
        self.server.on_client_bound = self.handle_client_bound

        # Message store
        self.messages = []

    def authenticate_client(self, system_id: str, password: str, system_type: str) -> bool:
        """Authenticate connecting clients"""
        # Implement your authentication logic
        valid_clients = {
            "client1": "password1",
            "client2": "password2"
        }
        return valid_clients.get(system_id) == password

    def handle_client_connected(self, server, session):
        """Handle new client connections"""
        print(f"Client connected from {session.address}")

    def handle_client_bound(self, server, session):
        """Handle successful client binding"""
        print(f"Client {session.system_id} bound")

    def handle_message(self, server, session, pdu: SubmitSm) -> str:
        """Handle incoming SMS messages"""
        message = pdu.short_message.decode('utf-8', errors='ignore')

        print(f"Message from {session.system_id}: {pdu.source_addr} -> {pdu.destination_addr}")
        print(f"Content: {message}")

        # Store message
        self.messages.append({
            'id': len(self.messages) + 1,
            'from': pdu.source_addr,
            'to': pdu.destination_addr,
            'message': message,
            'client': session.system_id
        })

        # Return message ID
        return f"MSG_{len(self.messages):06d}"

    async def start(self):
        """Start the SMSC"""
        await self.server.start()
        print(f"Custom SMSC started on {self.server.host}:{self.server.port}")

    async def stop(self):
        """Stop the SMSC"""
        await self.server.stop()
        print("Custom SMSC stopped")

    async def send_message_to_client(self, client_id: str, from_addr: str, to_addr: str, message: str):
        """Send message to a specific client"""
        success = await self.server.deliver_sm(
            target_system_id=client_id,
            source_addr=from_addr,
            destination_addr=to_addr,
            short_message=message
        )

        if success:
            print(f"Message delivered to {client_id}")
        else:
            print(f"Failed to deliver message to {client_id}")

        return success

# Usage
async def main():
    smsc = CustomSMSC()
    try:
        await smsc.start()

        # Keep server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await smsc.stop()

asyncio.run(main())
```

## API Reference

### SMPPClient

The main client class for connecting to SMSC servers.

#### Constructor

```python
SMPPClient(
    host: str,
    port: int,
    system_id: str,
    password: str,
    system_type: str = "",
    interface_version: int = 0x34,
    addr_ton: int = TonType.UNKNOWN,
    addr_npi: int = NpiType.UNKNOWN,
    address_range: str = "",
    bind_timeout: float = 30.0,
    enquire_link_interval: float = 60.0,
    response_timeout: float = 30.0
)
```

#### Properties

- `is_connected: bool` - Connection status
- `is_bound: bool` - Binding status
- `bind_type: Optional[BindType]` - Current bind type
- `connection_state: ConnectionState` - Current connection state

#### Methods

- `async connect()` - Connect to SMSC
- `async disconnect()` - Disconnect from SMSC
- `async bind_transmitter()` - Bind as transmitter
- `async bind_receiver()` - Bind as receiver
- `async bind_transceiver()` - Bind as transceiver
- `async unbind()` - Unbind from SMSC
- `async submit_sm(...)` - Send SMS message
- `async enquire_link(timeout=None)` - Test connection

#### Event Handlers

Set these as callable attributes on the client instance:

- `on_pdu_received` - Called when any PDU is received
- `on_connection_lost` - Called when connection is lost

### SMPPServer

Server implementation for creating SMSC-like services.

#### Constructor

```python
SMPPServer(
    host: str = "localhost",
    port: int = 2775,
    system_id: str = "SMSC",
    interface_version: int = 0x34,
    max_connections: int = 100
)
```

#### Properties

- `is_running: bool` - Server running status
- `client_count: int` - Number of connected clients

#### Methods

- `async start()` - Start the server
- `async stop()` - Stop the server
- `async deliver_sm(...)` - Send message to client
- `get_client_sessions()` - Get all client sessions
- `get_bound_clients()` - Get bound client sessions

#### Event Handlers

Set these as callable attributes on the server instance:

- `authenticate` - Client authentication function
- `on_client_connected` - Called when client connects
- `on_client_disconnected` - Called when client disconnects
- `on_client_bound` - Called when client binds
- `on_message_received` - Called when message is received

## Protocol Support

### Supported PDU Types

- **Session Management**
  - bind_transmitter / bind_transmitter_resp
  - bind_receiver / bind_receiver_resp
  - bind_transceiver / bind_transceiver_resp
  - unbind / unbind_resp
  - outbind

- **Message Operations**
  - submit_sm / submit_sm_resp
  - deliver_sm / deliver_sm_resp

## Protocol Support

### Supported PDU Types

- **Session Management**
  - bind_transmitter / bind_transmitter_resp
  - bind_receiver / bind_receiver_resp
  - bind_transceiver / bind_transceiver_resp
  - unbind / unbind_resp
  - outbind

- **Message Operations**
  - submit_sm / submit_sm_resp
  - deliver_sm / deliver_sm_resp

- **Auxiliary Operations**
  - enquire_link / enquire_link_resp
  - generic_nack

### Optional Parameters (TLV)

The library supports SMPP optional parameters through the TLV (Tag-Length-Value) mechanism:

```python
from smpp import OptionalTag, TLVParameter

# Create TLV parameter
tlv = TLVParameter(OptionalTag.MESSAGE_PAYLOAD, b"additional data")

# Add to PDU optional parameters
pdu.optional_parameters.append(tlv)
```

### Data Coding Schemes

Supported data coding schemes:
- Default SMSC alphabet (7-bit)
- IA5/ASCII
- Latin-1 (ISO-8859-1)
- UCS2 (UTF-16)
- UTF-8

## Error Handling

The library provides comprehensive error handling with specific exception types:

```python
from smpp import (
    SMPPException,
    SMPPConnectionException,
    SMPPBindException,
    SMPPTimeoutException,
    SMPPMessageException
)

try:
    await client.submit_sm("1234", "5678", "Hello!")
except SMPPBindException as e:
    print(f"Bind error: {e}")
except SMPPTimeoutException as e:
    print(f"Timeout: {e}")
except SMPPMessageException as e:
    print(f"Message error: {e}")
except SMPPException as e:
    print(f"General SMPP error: {e}")
```

## Logging

The library uses Python's standard logging module. Configure logging to see detailed protocol information:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific loggers
logging.getLogger('smpp').setLevel(logging.INFO)
```

## Testing

Run the test suite to verify the implementation:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/smpp

# Run specific test files
uv run pytest tests/unit/
uv run pytest tests/integration/
```

Run the examples to test functionality:

```bash
# Run client example
PYTHONPATH=src python examples/client.py

# Run server example
PYTHONPATH=src python examples/server.py
```

## Examples Directory

The `examples/` directory contains comprehensive usage examples:

- `client.py` - Complete client implementation with all features
- `server.py` - Full-featured SMSC server implementation
- `README.md` - Detailed examples documentation

## Performance Considerations

- **Async Operations**: All network operations are non-blocking
- **Connection Pooling**: Server supports multiple concurrent connections
- **Memory Efficient**: Streaming PDU processing without buffering large amounts of data
- **Configurable Timeouts**: All operations have configurable timeouts

## Production Deployment

For production use, consider:

1. **Security**: Implement proper authentication and encryption
2. **Monitoring**: Add comprehensive logging and metrics
3. **Error Handling**: Implement retry logic and circuit breakers
4. **Configuration**: Use environment variables for configuration
5. **Testing**: Thoroughly test with your SMSC provider

## Contributing

Contributions are welcome! This project uses modern CI/CD practices:

### Automated CI/CD Pipeline
- **Comprehensive Testing**: Automated linting, type checking, security scanning, and test suite
- **Semantic Versioning**: Automated releases based on [Conventional Commits](https://www.conventionalcommits.org/)
- **Code Quality**: Automated formatting with `ruff`, type checking with `mypy`
- **Security**: Automated security scanning with `bandit`

### Development Guidelines
1. **Follow Conventional Commits**: Use conventional commit format for automated versioning
   ```bash
   feat(client): add connection pooling support
   fix(server): resolve memory leak in PDU handling
   ```

2. **Quality Standards**:
   - Code follows Python standards (PEP 8)
   - All tests pass with >95% coverage
   - Type hints for all public APIs
   - Security best practices

3. **Development Workflow**:
   ```bash
   # Setup development environment
   uv sync --all-extras --dev

   # Run quality checks
   uv run ruff check src tests
   uv run ruff format src tests
   uv run mypy src
   uv run pytest
   ```

4. **Pull Request Process**:
   - Create feature branch with descriptive name
   - Follow conventional commit format
   - All CI checks must pass
   - Include tests for new features
   - Update documentation as needed

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines and [CI/CD Pipeline Documentation](docs/ci-cd-pipeline.md) for technical details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

- [SMPP v3.4 Specification](https://smpp.org/SMPP_v3_4_Issue1_2.pdf)
- [SMPP Protocol Overview](https://smpp.org/)
- [SMS Forum](https://www.smsforum.net/)

## Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the examples for common usage patterns
- Review the SMPP v3.4 specification for protocol details

---

**SMPP AI** - Modern async SMPP implementation for Python
