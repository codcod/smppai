# Graph Report - smppai  (2026-09-22)

## Corpus Check
- 53 files · ~50,300 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 6, .lock 1)

## Summary
- 2203 nodes · 3941 edges · 139 communities (124 shown, 13 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 414 edges (avg confidence: 0.93)
- Token cost: 98,393 input · 0 output

## Community Hubs (Navigation)
- SMPP Client & Server Examples
- Server Session & EnquireLink Tests
- SMPP Server Shutdown Config
- Client Connect/Disconnect Tests
- Bind Response PDUs
- PDU Factory Functions
- SMPP Client Bind & Send
- PDU Base Encode/Decode
- PDU Codec (Encode/Decode Helpers)
- Protocol Validation & Data Coding
- Server SubmitSm Handling
- TLV Parameter Tests
- Client Deliver/Unbind Handling Tests
- Message PDU Decode Edge Cases
- Bind Request/Response PDU Classes
- Client Example - Enhanced Shutdown
- Project Docs & CI Meta
- Server Auth & Context Manager Tests
- BindTransmitter PDU Tests
- Server Example - Event Handlers
- Validation: Data Coding & Command ID
- Server PDU Dispatch Tests
- Protocol Constants (Enums)
- PDU Class Mapping Tests
- Validation: Address Formats
- Client Bind Operation Tests
- Connection PDU Send Tests
- SMPP Error Handling Decorators
- EnquireLink PDU & Decode Tests
- Validation: Optional Params & Payload
- PDU Sequence Number Generation
- Outbind PDU
- Shutdown Integration Tests
- Bind Request PDU Variants
- DataSm Session PDU
- SMPP Utility Functions
- Client Property Tests
- Codec: Message Encoding Variants
- Connection Establishment Tests
- DeliverSm & Delivery Receipts
- Server Graceful Shutdown Logic
- Codec: Message Encoding Tests
- Validation: Boundary Conditions
- PDU Body Encoding Helpers
- Unbind PDU
- Standard Message PDU Base
- SubmitSmResp PDU
- QuerySmResp PDU
- Shared Test Fixtures (conftest)
- Client Wait-For Methods
- Codec: C-String Decoding
- Codec: Integer Encoding
- Codec: Integer Decoding
- Codec: C-String Encoding
- Codec: Field Length Validation
- Validation: Message Length
- Validation: PDU Structure
- DataSmResp PDU
- Field Validator with Caching
- DeliverSmResp PDU
- AlertNotification PDU
- Codec: TLV Packing
- Codec: TLV Unpacking
- Codec: PDU Length Calculation
- Validation: SubmitSm Parameters
- Connection Test Fixtures
- Connection PDU Receiving Tests
- Commitlint Config
- Server Example - Message Handling
- QuerySm PDU
- TLV Decode Tests
- PDU Base MessagePDU Tests
- PDU Factory Creation Tests
- PDU Factory Helper Tests
- Codec: Round-Trip Tests
- Validation: System ID
- Validation: Real-World Scenarios
- Server Client Connection Tests
- Client Example - Interactive
- SMPP Connection Init
- Connection State Property Tests
- Session PDU Field Validation
- Client Event Handler Tests
- Client Edge Case Tests
- PDU Base BindRequest Tests
- PDU Factory Response Creation Tests
- Codec Edge Case Tests
- Validation: Password
- Validation: Sequence Number
- Server Property Tests
- Server Start/Stop Tests
- Server Edge Case Tests
- Server Event Handler Init Tests
- Connection Error Handling Tests
- Connection Binding State Tests
- Server Example - Background Tasks
- Connection Send & Sequence
- Server Client Connection Handling
- Connection Memory/Cleanup Tasks
- PDU Factory Typed Creation Tests
- PDU Factory Request Creation Tests
- PDU Factory Command Utility Tests
- Validation: Service Type
- Validation Rule Registry Tests
- Validation: ESM Class
- Validation: Priority Flag
- Validation: Registered Delivery
- FieldValidator Class Tests
- Server Message Handling Tests
- Connection State & Bind Setters
- PDU Field Validate Methods
- PDU Optional Parameter Getters
- Client Connection Lost Tests
- Client Context Manager Tests
- Client Repr Tests
- Client Init Tests
- Connection Init Tests
- Connection Sequence Number Tests
- Connection Context Manager Tests
- SMPP Exception Hierarchy (README)
- Connection EnquireLink Loop
- Connection PDU Receive Loop
- Message PDU Resp Validation
- SMPP Connection Init Fields
- BindType Enum Tests
- PDU Default Values Test
- PDU Factory Unknown Command Test
- Connection Memory Limit Tests
- Client Connection Lost Handler
- Exception String Repr
- Unit Test Package Init
- PDU Test Package Init
- Dependabot Configuration
- Bug Report Issue Template
- Documentation Issue Template
- Feature Request Issue Template
- Package Root (smppai)

## God Nodes (most connected - your core abstractions)
1. `SMPPServer` - 149 edges
2. `SMPPClient` - 143 edges
3. `SMPPPDUException` - 101 edges
4. `ClientSession` - 89 edges
5. `CommandId` - 69 edges
6. `PDU` - 53 edges
7. `SMPPValidationException` - 42 edges
8. `SMPPConnection` - 42 edges
9. `SubmitSm` - 39 edges
10. `BindTransmitter` - 33 edges

## Surprising Connections (you probably didn't know these)
- `Absolute Minimal Changes Principle` --semantically_similar_to--> `CONTRIBUTING Guide`  [INFERRED] [semantically similar]
  .github/copilot-instructions.md → CONTRIBUTING.md
- `CONTRIBUTING Guide` --semantically_similar_to--> `CI Workflow`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → .github/workflows/ci.yml
- `Pre-commit Hooks Configuration` --semantically_similar_to--> `Lint & Format Check Job`  [INFERRED] [semantically similar]
  .pre-commit-config.yaml → .github/workflows/ci.yml
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPClient (ESME)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPServer (SMSC)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI Workflow Pipeline Stages** — github_workflows_ci_lint, github_workflows_ci_type_check, github_workflows_ci_security, github_workflows_ci_unit_tests, github_workflows_ci_integration_test, github_workflows_ci_build, github_workflows_ci_coverage_report, github_workflows_ci_all_checks [EXTRACTED 1.00]
- **SMPP Exception Hierarchy** — readme_smppexception, readme_smppconnectionexception, readme_smppbindexception, readme_smpptimeoutexception, readme_smppmessageexception [INFERRED 0.85]
- **Shared Quality-Check Toolchain (ruff/mypy/pytest/bandit)** — pre_commit_config, github_workflows_ci_lint, contributing, github_pull_request_template [INFERRED 0.85]

## Communities (139 total, 13 thin omitted)

### Community 0 - "SMPP Client & Server Examples"
Cohesion: 0.06
Nodes (49): SMPP Server Example This example demonstrates how to use the SMPP server with…, BindType, Enum, SMPP Client (ESME) Implementation This module provides a comprehensive async…, Connect to SMSC server, Perform bind operation, Submit SMS message Args: source_addr: Source address (sender) destination_addr:…, SMPP Client Module This module provides a comprehensive async SMPP client… (+41 more)

### Community 1 - "Server Session & EnquireLink Tests"
Cohesion: 0.06
Nodes (36): ClientSession, Get list of all client sessions, Get list of bound client sessions, Represents a connected SMPP client session, asyncio, Tests for enquire_link request handling., Test successful enquire_link request., Test enquire_link when exception occurs. (+28 more)

### Community 2 - "SMPP Server Shutdown Config"
Cohesion: 0.04
Nodes (33): Event, Simple server example showcasing async context manager with enhanced shutdown.…, simple_server_example(), create_simple_server(), Create a simple SMPP server with minimal configuration. Args: host: Server bind…, Set the grace period for shutdown notifications, Initialize SMPP Server Args: host: Server bind address port: Server bind port…, Set the delay after grace period before final shutdown (+25 more)

### Community 3 - "Client Connect/Disconnect Tests"
Cohesion: 0.04
Nodes (29): asyncio, Test successful connection., Test connect when no connection object., Test connect when already connected., Test successful disconnection., Test disconnect when not connected., Test disconnect when unbind fails., Test successful unbind. (+21 more)

### Community 4 - "Bind Response PDUs"
Cohesion: 0.06
Nodes (28): BindReceiverResp, BindTransceiverResp, BindTransmitterResp, SMPP Bind PDU Implementations This module contains all bind-related PDU classes…, BIND_RECEIVER_RESP PDU - Response to bind_receiver, BIND_TRANSCEIVER_RESP PDU - Response to bind_transceiver, UNBIND_RESP PDU - Response to unbind, Base class for standard bind responses with system_id only (+20 more)

### Community 5 - "PDU Factory Functions"
Cohesion: 0.07
Nodes (38): create_bind_pdu(), create_enquire_link_pdu(), create_error_response(), create_generic_nack_pdu(), create_pdu(), create_request_pdu(), create_response_pdu(), create_submit_sm_pdu() (+30 more)

### Community 6 - "SMPP Client Bind & Send"
Cohesion: 0.05
Nodes (22): Check if client is connected to SMSC, Check if client is bound to SMSC, Get current bind type, Disconnect from SMSC server, Bind as transmitter (can send SMS), Bind as receiver (can receive SMS and delivery receipts), Bind as transceiver (can send and receive SMS), Send enquire_link to test connection Args: timeout: Response timeout Returns:… (+14 more)

### Community 7 - "PDU Base Encode/Decode"
Cohesion: 0.06
Nodes (21): PDU, Abstract base class for all SMPP PDUs. This class provides the common…, Encode PDU body to bytes. Must be implemented by subclasses to encode the PDU-…, Decode PDU body from bytes. Must be implemented by subclasses to decode the…, Encode complete PDU to bytes. Returns: The complete encoded PDU including…, Decode PDU from bytes. Args: data: The byte data to decode Returns: The decoded…, Add optional parameter. If a parameter with the same tag already exists, it…, Remove optional parameter by tag. Args: tag: The parameter tag to remove… (+13 more)

### Community 8 - "PDU Codec (Encode/Decode Helpers)"
Cohesion: 0.07
Nodes (29): Exception raised for PDU-related errors., SMPPPDUException, calculate_pdu_length(), decode_cstring(), decode_integer(), decode_message_with_encoding(), encode_integer(), encode_message_with_encoding() (+21 more)

### Community 9 - "Protocol Validation & Data Coding"
Cohesion: 0.11
Nodes (38): Exception raised for validation errors., SMPPValidationException, DataCoding, is_response_command(), Data Coding Scheme values, Check if a command ID represents a response PDU, SMPP Protocol Module This module contains the core SMPP protocol implementation…, SMPP Protocol Validation This module provides validation functions for SMPP… (+30 more)

### Community 10 - "Server SubmitSm Handling"
Cohesion: 0.08
Nodes (20): SUBMIT_SM PDU - Request to submit a short message, SubmitSm, Handle submit_sm request from client, Send submit_sm response to client, Generate next message ID, Test creating error response with message., Test SubmitSm initialization with defaults., Test SubmitSm with custom values. (+12 more)

### Community 11 - "TLV Parameter Tests"
Cohesion: 0.08
Nodes (17): Tag-Length-Value parameter for optional parameters. TLV parameters are used in…, Initialize TLV parameter. Args: tag: Parameter tag identifier value: Parameter…, Encode TLV parameter to bytes. Returns: The encoded TLV parameter as bytes, TLVParameter, Test TLV parameter string representation., Test TLV parameter equality., Test TLVParameter class., Test TLV parameter hashing. (+9 more)

### Community 12 - "Client Deliver/Unbind Handling Tests"
Cohesion: 0.06
Nodes (17): Test handling deliver_sm when handler raises exception., Test sending deliver_sm_resp., Test sending deliver_sm_resp when exception occurs., Test sending enquire_link_resp., Test sending enquire_link_resp when exception occurs., Test handling unbind request., Test handling unbind request when exception occurs., Test handling unbind request when handler raises exception. (+9 more)

### Community 13 - "Message PDU Decode Edge Cases"
Cohesion: 0.08
Nodes (22): Test decode with insufficient data for source address fields., Test decode with insufficient data for destination address fields., Test decode with insufficient data for message fields., Test delivery receipt request checking., Test StandardMessagePDU base class., Test setting delivery receipt request., Test Unicode message detection., Test StandardMessagePDU body encoding with basic data. (+14 more)

### Community 14 - "Bind Request/Response PDU Classes"
Cohesion: 0.11
Nodes (21): ABC, CommandStatus, SMPP Command Status codes as defined in SMPP v3.4 specification, BindRequestPDU, BindResponsePDU, EmptyBodyPDU, MessagePDU, Any (+13 more)

### Community 15 - "Client Example - Enhanced Shutdown"
Cohesion: 0.08
Nodes (16): Exception, Check if this message is a server shutdown notification., Handle server shutdown notifications with appropriate responses., Thread-safe graceful shutdown process., Handle connection lost event with enhanced shutdown awareness., Handle successful bind with enhanced logging., Handle unbind event with enhanced logging., Connect to SMSC and bind with enhanced shutdown awareness. (+8 more)

### Community 16 - "Project Docs & CI Meta"
Cohesion: 0.11
Nodes (29): CHANGELOG, CONTRIBUTING Guide, Conventional Commits, smppai Project Structure (client/server/protocol/transport/config), Semantic Release / Automated Versioning, Examples README, Set up Python with uv (composite action), Absolute Minimal Changes Principle (+21 more)

### Community 17 - "Server Auth & Context Manager Tests"
Cohesion: 0.07
Nodes (19): Unit tests for SMPP Server implementation This module contains tests for the…, Tests for server stop with client disconnect exceptions., Test server stop when client disconnect raises exception., Tests for custom authentication., Test custom authentication that succeeds., Test when authentication is disabled., Tests for server async context manager., Test successful context manager usage. (+11 more)

### Community 18 - "BindTransmitter PDU Tests"
Cohesion: 0.09
Nodes (18): BindTransmitter, BIND_TRANSMITTER PDU - Request to bind as transmitter, Test decode with insufficient data., Test BindTransmitter PDU., Test BindTransmitter initialization with defaults., Test BindTransmitter with custom values., Test BindTransmitter body encoding., Test BindTransmitter body decoding. (+10 more)

### Community 19 - "Server Example - Event Handlers"
Cohesion: 0.09
Nodes (14): Set up all server event handlers., Authenticate client credentials with enhanced logging. Args: system_id: Client…, Handle new client connection with enhanced logging., Handle client disconnection with enhanced logging., Handle successful client bind with enhanced logging., Example SMSC server using SMPP with enhanced shutdown capabilities. Features: -…, Start the SMSC server., Stop the SMSC server with enhanced shutdown. (+6 more)

### Community 20 - "Validation: Data Coding & Command ID"
Cohesion: 0.08
Nodes (16): Unit tests for SMPP Protocol Validation functions. Tests all validation…, Tests for validate_data_coding function., Test validating valid data coding schemes., Test validating invalid data coding schemes., Tests for validate_command_id function., Test validating valid command IDs., Test validating invalid command IDs., Tests for validate_bind_parameters function. (+8 more)

### Community 21 - "Server PDU Dispatch Tests"
Cohesion: 0.10
Nodes (15): patch, Test that initialization creates SMPPConnection., Test PDU handling through _handle_client_pdu method., Test handling of BindTransmitter PDU through PDU handler., Test handling of BindReceiver PDU through PDU handler., Test handling of BindTransceiver PDU through PDU handler., Test handling of Unbind PDU through PDU handler., Test handling of SubmitSm PDU through PDU handler. (+7 more)

### Community 22 - "Protocol Constants (Enums)"
Cohesion: 0.11
Nodes (23): EsmClass, get_request_command_id(), get_response_command_id(), InterfaceVersion, MessageState, NpiType, OptionalTag, PriorityFlag (+15 more)

### Community 23 - "PDU Class Mapping Tests"
Cohesion: 0.11
Nodes (16): CommandId, SMPP Command IDs as defined in SMPP v3.4 specification, EnquireLinkResp, ENQUIRE_LINK_RESP PDU - Response to enquire_link, Test PDU_CLASSES mapping., Test bind command mappings., Test message command mappings., Test session command mappings. (+8 more)

### Community 24 - "Validation: Address Formats"
Cohesion: 0.08
Nodes (13): Tests for validate_address function., Test validating a valid international ISDN address., Test validating a valid national ISDN address., Test validating a valid alphanumeric address., Test validating an address that's too long., Test validating an address with invalid TON., Test validating an address with invalid NPI., Test validating international ISDN address with invalid format. (+5 more)

### Community 25 - "Client Bind Operation Tests"
Cohesion: 0.09
Nodes (12): Tests for SMPPClient binding operations., Test successful bind as transmitter., Test successful bind as receiver., Test successful bind as transceiver., Test bind when not connected., Test bind when already bound., Test bind when connection object is None., Test bind when no response received. (+4 more)

### Community 26 - "Connection PDU Send Tests"
Cohesion: 0.11
Nodes (11): MockEnquireLink, MockPDU, Test PDU sending functionality, Test sending PDU when not connected, Test sending PDU without waiting for response, Test sending PDU with response, Test PDU response timeout, Return mock encoded PDU (+3 more)

### Community 27 - "SMPP Error Handling Decorators"
Cohesion: 0.14
Nodes (10): async_handle_smpp_error(), handle_smpp_error(), wrapper(), Any, Exception, IntEnum, SMPP-specific error codes for better error categorization., Decorator to handle SMPP errors with consistent logging and context. Args:… (+2 more)

### Community 28 - "EnquireLink PDU & Decode Tests"
Cohesion: 0.12
Nodes (14): EnquireLink, ENQUIRE_LINK PDU - Keepalive request to test connection, Test decode_pdu function., Test decoding EnquireLink PDU., Test decoding with invalid data., TestDecodePDU, Test EnquireLink PDU., Test EnquireLink initialization. (+6 more)

### Community 29 - "Validation: Optional Params & Payload"
Cohesion: 0.09
Nodes (12): Tests for validate_optional_parameter function., Test validating valid optional parameters., Test validating optional parameter with negative tag., Test validating optional parameter with tag too large., Test validating optional parameter with value too long., Test validating valid receipted message ID., Test validating receipted message ID with non-printable characters., Test validating receipted message ID with invalid ASCII. (+4 more)

### Community 30 - "PDU Sequence Number Generation"
Cohesion: 0.10
Nodes (8): Initialize PDU after creation., Generate a unique sequence number. Returns: A unique sequence number between 1…, Test sequence number generation., Test sequence number is within valid bounds., Test that __post_init__ generates sequence number when 0., Test that __post_init__ preserves non-zero sequence number., Test PDU with custom values., TestPDU

### Community 31 - "Outbind PDU"
Cohesion: 0.13
Nodes (12): Outbind, OUTBIND PDU - SMSC initiated bind request, Decode outbind body with system_id and password only, Validate outbind fields Raises: SMPPPDUException: If validation fails, Test Outbind initialization., Test Outbind body encoding., Test Outbind body decoding., Test Outbind validation success. (+4 more)

### Community 32 - "Shutdown Integration Tests"
Cohesion: 0.12
Nodes (14): integration, performance, asyncio, fixture, Integration tests for SMPP Server and Client shutdown interaction These tests…, Test that client can reconnect after server restart., Integration tests for server-client shutdown interaction, Performance tests for shutdown operations (+6 more)

### Community 33 - "Bind Request PDU Variants"
Cohesion: 0.12
Nodes (14): BindReceiver, BindTransceiver, BIND_TRANSCEIVER PDU - Request to bind as transceiver, Base class for standard bind requests (transmitter, receiver, transceiver), Encode standard bind request body with all fields, BIND_RECEIVER PDU - Request to bind as receiver, StandardBindRequestPDU, Test BindReceiver PDU. (+6 more)

### Community 34 - "DataSm Session PDU"
Cohesion: 0.13
Nodes (9): DataSm, DATA_SM PDU - Submit data using optional parameters, Get message payload from optional parameters, Set message payload as optional parameter, Get message text from payload, Set message text as payload, Test DataSm initialization., Test DataSm with custom values. (+1 more)

### Community 35 - "SMPP Utility Functions"
Cohesion: 0.11
Nodes (19): calculate_message_length(), format_smpp_time(), generate_message_id(), is_valid_system_id(), mask_sensitive_data(), normalize_phone_number(), parse_smpp_time(), SMPP Utilities Module This module provides basic utility functions and helper… (+11 more)

### Community 36 - "Client Property Tests"
Cohesion: 0.10
Nodes (11): Tests for SMPPClient properties., Test is_connected property when connected., Test is_connected property when no connection., Test is_connected property when connection exists but not connected., Test is_bound property when bound and connected., Test is_bound property when not bound., Test is_bound property when bound but not connected., Test bind_type property. (+3 more)

### Community 37 - "Codec: Message Encoding Variants"
Cohesion: 0.10
Nodes (11): Tests for decode_message_with_encoding function., Test decoding with default data coding., Test decoding with ASCII data coding., Test decoding with Latin-1 data coding., Test decoding with UCS2 data coding., Test decoding with octet unspecified data coding., Test decoding with unknown data coding (should fallback to UTF-8)., Test decoding Unicode with UTF-8 fallback. (+3 more)

### Community 38 - "Connection Establishment Tests"
Cohesion: 0.13
Nodes (12): asyncio, Test connection establishment and teardown, Test successful connection, Test connect when already connected, Test connection timeout, Test connection failure, Test disconnect when not connected, Test successful disconnection (+4 more)

### Community 39 - "DeliverSm & Delivery Receipts"
Cohesion: 0.13
Nodes (11): DeliverSm, DELIVER_SM PDU - Deliver a short message or delivery receipt, Check if this is a delivery receipt Returns: bool: True if this is a delivery…, Check if this is a mobile originated message Returns: bool: True if this is a…, Parse delivery receipt message into structured data Returns: dict: Parsed…, Create a delivery receipt message Args: original_message_id: ID of the original…, Deliver SMS message to a specific client Args: target_system_id: Target client…, Test DeliverSm initialization. (+3 more)

### Community 40 - "Server Graceful Shutdown Logic"
Cohesion: 0.11
Nodes (9): Send shutdown notification to a client session with comprehensive error…, Send shutdown notification to all bound clients, Enhanced graceful shutdown with broadcast notifications and grace periods., Send notifications and wait for clients to disconnect gracefully., Wait for grace period and check if clients disconnect. Returns: True if all…, Force disconnect all remaining clients., Send unbind requests to all bound clients., Force disconnect all clients. (+1 more)

### Community 41 - "Codec: Message Encoding Tests"
Cohesion: 0.11
Nodes (10): Tests for encode_message_with_encoding function., Test encoding with default data coding., Test encoding with ASCII data coding., Test encoding with Latin-1 data coding., Test encoding with UCS2 data coding., Test encoding with octet unspecified data coding., Test encoding with unknown data coding (should fallback to UTF-8)., Test encoding Unicode with UTF-8 fallback. (+2 more)

### Community 42 - "Validation: Boundary Conditions"
Cohesion: 0.11
Nodes (10): Tests for edge cases and boundary conditions., Test system ID at exact boundary length., Test password at exact boundary length., Test address at exact boundary length., Test service type at exact boundary length., Test message at exact boundary length for GSM 7-bit., Test message at exact general boundary length., Test sequence number at boundary values. (+2 more)

### Community 43 - "PDU Body Encoding Helpers"
Cohesion: 0.12
Nodes (9): encode_cstring(), Encode a string as a C-style null-terminated string with length validation.…, Encode outbind body with system_id and password only, Encode standard bind response body, Encode submit_sm_resp body Returns: bytes: Encoded PDU body, Encode deliver_sm_resp body Returns: bytes: Encoded PDU body, Encode data_sm_resp body, Encode query_sm_resp body (+1 more)

### Community 44 - "Unbind PDU"
Cohesion: 0.15
Nodes (11): UNBIND PDU - Request to unbind from SMSC, Unbind, Handle unbind request from client, Test Unbind initialization., Test Unbind body encoding (should be empty)., Test Unbind body decoding (should handle empty body)., TestUnbind, Tests for unbind request handling. (+3 more)

### Community 45 - "Standard Message PDU Base"
Cohesion: 0.14
Nodes (9): Get message text as string using specified or auto-detected encoding Args:…, Set message text from string using specified or auto-detected encoding Args:…, Check if delivery receipt is requested Returns: bool: True if delivery receipt…, Set delivery receipt request flag Args: requested: Whether to request delivery…, Check if message uses Unicode encoding Returns: bool: True if message uses…, Base class for standard message PDUs (SubmitSm, DeliverSm) with identical…, Get appropriate encoding for the message based on data_coding Returns: str:…, Encode standard message PDU body Returns: bytes: Encoded PDU body Raises:… (+1 more)

### Community 46 - "SubmitSmResp PDU"
Cohesion: 0.17
Nodes (10): SUBMIT_SM_RESP PDU - Response to submit_sm, SubmitSmResp, Test SubmitSmResp PDU., Test SubmitSmResp initialization., Test SubmitSmResp with custom values., Test SubmitSmResp body encoding., Test SubmitSmResp body encoding with empty message_id., Test SubmitSmResp body decoding. (+2 more)

### Community 47 - "QuerySmResp PDU"
Cohesion: 0.17
Nodes (10): QuerySmResp, QUERY_SM_RESP PDU - Response to query_sm, Get human-readable message state name Returns: str: Human-readable message…, Test QuerySmResp PDU., Test QuerySmResp initialization., Test QuerySmResp with custom values., Test QuerySmResp body encoding., Test QuerySmResp body decoding. (+2 more)

### Community 48 - "Shared Test Fixtures (conftest)"
Cohesion: 0.17
Nodes (14): event_loop(), mock_asyncio_sleep(), mock_logger(), mock_time(), fixture, Shared test fixtures and configuration for SMPP unit tests., Create an event loop for async tests., Mock asyncio.sleep to speed up tests. (+6 more)

### Community 49 - "Client Wait-For Methods"
Cohesion: 0.12
Nodes (8): Tests for SMPPClient wait methods., Test wait_for_connection when connection succeeds., Test wait_for_connection timeout., Test wait_for_connection when already connected., Test wait_for_bind when bind succeeds., Test wait_for_bind timeout., Test wait_for_bind when already bound., TestSMPPClientWaitMethods

### Community 50 - "Codec: C-String Decoding"
Cohesion: 0.12
Nodes (9): Test decoding with invalid byte sequence., Tests for decode_cstring function., Test decoding a simple null-terminated string., Test decoding an empty string., Test decoding starting from a specific offset., Test decoding when offset is beyond data length., Test decoding when string is not null-terminated within max_length., Test decoding with custom character encoding. (+1 more)

### Community 51 - "Codec: Integer Encoding"
Cohesion: 0.12
Nodes (9): Tests for encode_integer function., Test encoding 1-byte unsigned integer., Test encoding 1-byte signed integer., Test encoding 2-byte unsigned integer., Test encoding 4-byte unsigned integer., Test encoding 8-byte unsigned integer., Test encoding with invalid size., Test encoding value that's out of range for the size. (+1 more)

### Community 52 - "Codec: Integer Decoding"
Cohesion: 0.12
Nodes (9): Tests for decode_integer function., Test decoding 1-byte unsigned integer., Test decoding 1-byte signed integer., Test decoding 2-byte unsigned integer., Test decoding 4-byte unsigned integer., Test decoding starting from a specific offset., Test decoding when there's insufficient data., Test decoding with invalid size. (+1 more)

### Community 53 - "Codec: C-String Encoding"
Cohesion: 0.12
Nodes (9): Tests for encode_cstring function., Test encoding a simple ASCII string., Test encoding an empty string., Test encoding a string that exactly fits the limit., Test encoding a string that exceeds the maximum length., Test encoding with custom character encoding., Test encoding with unsupported characters., Test when encoded bytes exceed limit even if string length is OK. (+1 more)

### Community 54 - "Codec: Field Length Validation"
Cohesion: 0.12
Nodes (9): Tests for validate_field_length function., Test validation of a valid string field., Test validation of a valid bytes field., Test validation of field that's too short., Test validation of field that's too long., Test validation when no maximum length is specified., Test validation when field is exactly at minimum length., Test validation when field is exactly at maximum length. (+1 more)

### Community 55 - "Validation: Message Length"
Cohesion: 0.12
Nodes (9): Tests for validate_message_length function., Test validating valid message length with default data coding., Test validating valid message length with UCS2 data coding., Test validating a message that exceeds the general maximum., Test validating a message that exceeds GSM 7-bit limit., Test validating a message that exceeds UCS2 limit., Test validating a message at the GSM 7-bit boundary., Test validating a message at the UCS2 boundary. (+1 more)

### Community 56 - "Validation: PDU Structure"
Cohesion: 0.12
Nodes (9): Tests for validate_pdu_structure function., Test validating valid PDU structure for request., Test validating valid PDU structure for response., Test validating PDU structure with invalid command ID., Test validating PDU structure with invalid sequence number., Test validating PDU structure with command length too small., Test validating PDU structure with command length too large., Test validating PDU structure with invalid command status for response. (+1 more)

### Community 57 - "DataSmResp PDU"
Cohesion: 0.18
Nodes (7): DataSmResp, DATA_SM_RESP PDU - Response to data_sm, Test DataSmResp initialization., Test DataSmResp with custom values., Test DataSmResp body encoding., Test DataSmResp body decoding., TestDataSmResp

### Community 58 - "Field Validator with Caching"
Cohesion: 0.16
Nodes (11): FieldValidator, get_validation_rule(), Any, Clear validation cache., Register a custom validation rule for a field. Args: field_name: Name of the…, Get validation rule for a field. Args: field_name: Name of the field Returns:…, Enhanced field validator with caching and custom rules., Validate field with result caching. Args: field_name: Name of the field value:… (+3 more)

### Community 59 - "DeliverSmResp PDU"
Cohesion: 0.19
Nodes (9): DeliverSmResp, DELIVER_SM_RESP PDU - Response to deliver_sm, Unit tests for SMPP message PDUs., Test DeliverSmResp PDU., Test DeliverSmResp initialization., Test DeliverSmResp with custom values., Test DeliverSmResp body encoding., Test DeliverSmResp body decoding. (+1 more)

### Community 60 - "AlertNotification PDU"
Cohesion: 0.20
Nodes (9): AlertNotification, ALERT_NOTIFICATION PDU - Notification of message availability, Test AlertNotification PDU., Test AlertNotification initialization., Test AlertNotification with custom values., Test AlertNotification body encoding., Test AlertNotification body decoding., Test decode with insufficient data. (+1 more)

### Community 61 - "Codec: TLV Packing"
Cohesion: 0.14
Nodes (8): Tests for pack_tlv_parameter function., Test packing a simple TLV parameter., Test packing TLV with empty value., Test packing TLV with maximum tag value., Test packing TLV with invalid negative tag., Test packing TLV with tag too large., Test packing TLV with value too long., TestTLVPacking

### Community 62 - "Codec: TLV Unpacking"
Cohesion: 0.14
Nodes (8): Tests for unpack_tlv_parameter function., Test unpacking a simple TLV parameter., Test unpacking TLV with empty value., Test unpacking TLV starting from a specific offset., Test unpacking when there's insufficient data for header., Test unpacking when there's insufficient data for value., Test unpacking when offset is at the end of data., TestTLVUnpacking

### Community 63 - "Codec: PDU Length Calculation"
Cohesion: 0.14
Nodes (8): Tests for calculate_pdu_length function., Test calculating basic PDU length., Test calculating PDU length without optional parameters., Test calculating PDU length with zero body size., Test calculating maximum allowed PDU length., Test calculating PDU length that exceeds maximum., Test calculating PDU length with large optional parameters., TestPDULengthCalculation

### Community 64 - "Validation: SubmitSm Parameters"
Cohesion: 0.14
Nodes (8): Tests for validate_submit_sm_parameters function., Test validating valid submit_sm parameters., Test validating submit_sm parameters with invalid source address., Test validating submit_sm parameters with invalid destination address., Test validating submit_sm parameters with message too long., Test validating submit_sm parameters with invalid data coding., Test validating submit_sm parameters with invalid priority flag., TestSubmitSmParametersValidation

### Community 65 - "Connection Test Fixtures"
Cohesion: 0.18
Nodes (12): connected_connection(), connection(), mock_reader(), mock_writer(), fixture, Unit tests for SMPP Connection module. Tests the async TCP connection handling,…, Mock asyncio StreamReader, Mock asyncio StreamWriter (+4 more)

### Community 66 - "Connection PDU Receiving Tests"
Cohesion: 0.14
Nodes (8): Test PDU receiving functionality, Test successful PDU reception, Test PDU reception with no reader, Test PDU reception timeout, Test incomplete PDU read, Test PDU with invalid length, Test handling received PDU as response, TestPDUReceiving

### Community 67 - "Commitlint Config"
Cohesion: 0.15
Nodes (12): extends, rules, body-leading-blank, footer-leading-blank, header-max-length, scope-empty, scope-enum, subject-case (+4 more)

### Community 68 - "Server Example - Message Handling"
Cohesion: 0.17
Nodes (6): Handle SMS message from client with enhanced logging and commands., Process received message with enhanced command support., Send a response back to the client., Demonstrate the enhanced shutdown feature., Send delivery receipt to client., Get comprehensive server statistics.

### Community 69 - "QuerySm PDU"
Cohesion: 0.21
Nodes (8): QuerySm, QUERY_SM PDU - Query status of a submitted message, Unit tests for SMPP session PDUs., Test QuerySm initialization., Test QuerySm with custom values., Test QuerySm body encoding., Test QuerySm body decoding., TestQuerySm

### Community 70 - "TLV Decode Tests"
Cohesion: 0.17
Nodes (6): Decode TLV parameter from bytes. Args: data: The byte data to decode from…, Test decoding with insufficient header data., Test decoding with insufficient value data., Test TLV parameter decoding., Test TLV parameter decoding with offset., Test decoding TLV with empty value.

### Community 71 - "PDU Base MessagePDU Tests"
Cohesion: 0.17
Nodes (5): Unit tests for SMPP PDU base classes., Test MessagePDU base class., Test MessagePDU default values., Test MessagePDU with custom values., TestMessagePDU

### Community 72 - "PDU Factory Creation Tests"
Cohesion: 0.17
Nodes (7): Test creating PDU with invalid command ID., Test creating PDU with invalid parameters., Test create_pdu function., Test creating BindTransmitter PDU., Test creating SubmitSm PDU., Test creating EnquireLink PDU., TestCreatePDU

### Community 73 - "PDU Factory Helper Tests"
Cohesion: 0.17
Nodes (7): Test helper factory functions., Test create_bind_pdu helper., Test create_bind_pdu with invalid type., Test create_submit_sm_pdu helper., Test create_enquire_link_pdu helper., Test create_generic_nack_pdu helper., TestHelperFunctions

### Community 74 - "Codec: Round-Trip Tests"
Cohesion: 0.17
Nodes (7): Tests for round-trip encoding/decoding operations., Test encoding and decoding C-strings., Test encoding and decoding integers., Test encoding and decoding messages with UTF-8., Test encoding and decoding messages with UCS2., Test packing and unpacking TLV parameters., TestRoundTripOperations

### Community 75 - "Validation: System ID"
Cohesion: 0.17
Nodes (7): Test validating a system ID that's too long., Test validating a system ID with invalid characters., Test that underscores are allowed in system ID., Tests for validate_system_id function., Test validating a valid system ID., Test validating an empty system ID., TestSystemIdValidation

### Community 76 - "Validation: Real-World Scenarios"
Cohesion: 0.17
Nodes (7): Tests for real-world usage scenarios., Test complete bind parameter validation flow., Test complete submit_sm parameter validation flow., Test alphanumeric addressing validation., Test Unicode message validation., Test that empty fields are allowed where appropriate., TestRealWorldScenarios

### Community 77 - "Server Client Connection Tests"
Cohesion: 0.17
Nodes (7): Tests for client connection handling., Test successful client connection handling., Test client connection with event handler., Test client connection when handler raises exception., Test client disconnection handling., Test client disconnection when handler raises exception., TestSMPPServerClientConnection

### Community 78 - "Client Example - Interactive"
Cohesion: 0.18
Nodes (9): interactive_client_example(), main(), monitor_messages_example(), SMPP Client Example This example demonstrates how to use the SMPP client to…, Main example function demonstrating enhanced shutdown handling. Features…, Simple example of sending one SMS with enhanced shutdown awareness., Example of monitoring incoming messages with enhanced shutdown handling. This…, Interactive client that can send commands to test enhanced shutdown. (+1 more)

### Community 79 - "SMPP Connection Init"
Cohesion: 0.18
Nodes (6): Initialize SMPP Client Args: host: SMSC server hostname or IP port: SMSC server…, Check if connection is established, Check if connection is bound, Async SMPP Connection Handler Manages TCP connection, PDU encoding/decoding,…, Get current connection state, SMPPConnection

### Community 80 - "Connection State Property Tests"
Cohesion: 0.18
Nodes (6): Test connection properties and state management, Test state property getter, Test is_connected property, Test is_bound property, Test state change with handler, TestConnectionProperties

### Community 81 - "Session PDU Field Validation"
Cohesion: 0.22
Nodes (5): Validate alert_notification fields, Validate data_sm fields, Validate data_sm_resp fields, Validate query_sm fields, Validate query_sm_resp fields

### Community 82 - "Client Event Handler Tests"
Cohesion: 0.20
Nodes (4): Tests for SMPPClient event handlers., Test that event handlers are initialized to None., Test setting event handlers., TestSMPPClientEventHandlers

### Community 83 - "Client Edge Case Tests"
Cohesion: 0.20
Nodes (6): Tests for edge cases and boundary conditions., Test submit_sm with Unicode message., Test submit_sm with message at boundary length., Test connection state property during state transitions., Test binding sequence (bind, unbind, rebind)., TestSMPPClientEdgeCases

### Community 84 - "PDU Base BindRequest Tests"
Cohesion: 0.20
Nodes (4): Test BindRequestPDU base class., Test BindRequestPDU default values., Test BindRequestPDU with custom values., TestBindRequestPDU

### Community 85 - "PDU Factory Response Creation Tests"
Cohesion: 0.20
Nodes (6): Test create_response_pdu function., Test creating response PDU successfully., Test creating response PDU with default status., Test creating response PDU from response command ID., Test creating response PDU for invalid command., TestCreateResponsePDU

### Community 86 - "Codec Edge Case Tests"
Cohesion: 0.20
Nodes (6): Unit tests for SMPP Protocol Codec utilities. Tests all encoding/decoding…, Tests for edge cases and boundary conditions., Test handling of maximum values., Test handling of zero values., Test boundary length conditions., TestEdgeCases

### Community 87 - "Validation: Password"
Cohesion: 0.20
Nodes (6): Tests for validate_password function., Test validating valid passwords., Test validating a password that's too long., Test validating a password with non-printable characters., Test that special printable characters are allowed., TestPasswordValidation

### Community 88 - "Validation: Sequence Number"
Cohesion: 0.20
Nodes (6): Tests for validate_sequence_number function., Test validating valid sequence numbers., Test validating sequence number zero., Test validating negative sequence number., Test validating sequence number that's too large., TestSequenceNumberValidation

### Community 89 - "Server Property Tests"
Cohesion: 0.20
Nodes (6): Tests for SMPPServer properties., Test that server is not running initially., Test that server reports running when started., Test client count when no clients connected., Test client count with connected clients., TestSMPPServerProperties

### Community 90 - "Server Start/Stop Tests"
Cohesion: 0.20
Nodes (6): Tests for server start/stop functionality., Test successful server start., Test starting server when already running raises exception., Test successful server stop., Test stopping server when not running., TestSMPPServerStartStop

### Community 91 - "Server Edge Case Tests"
Cohesion: 0.20
Nodes (6): Tests for edge cases and error scenarios., Test client count after various operations., Test message ID counter behavior., Test getting bound clients with mixed session states., Test client connection when peer info is not available., TestSMPPServerEdgeCases

### Community 92 - "Server Event Handler Init Tests"
Cohesion: 0.20
Nodes (4): Tests for server event handler initialization., Test that event handlers are initialized to None., Test setting custom event handlers., TestSMPPServerEventHandlers

### Community 93 - "Connection Error Handling Tests"
Cohesion: 0.20
Nodes (5): Test state change handler exception handling, Test connection error handling, Test connection error handler exception, failing_handler(), TestErrorHandling

### Community 94 - "Connection Binding State Tests"
Cohesion: 0.20
Nodes (6): Test connection binding state management, Test setting transmitter bound state, Test setting receiver bound state, Test setting transceiver bound state, Test setting invalid bound state, TestBindingStates

### Community 95 - "Server Example - Background Tasks"
Cohesion: 0.25
Nodes (8): cleanup_background_tasks(), main(), Main server function demonstrating enhanced shutdown capabilities. Features…, Monitor and log server statistics periodically., Send periodic broadcast messages to demonstrate server capabilities., Clean up background tasks gracefully., run_broadcast_scheduler(), run_stats_monitor()

### Community 96 - "Connection Send & Sequence"
Cohesion: 0.29
Nodes (5): Exception raised for connection-related errors., SMPPConnectionException, Get next sequence number, Send PDU and optionally wait for response Args: pdu: PDU to send wait_response:…, Send raw data over connection

### Community 97 - "Server Client Connection Handling"
Cohesion: 0.25
Nodes (6): Exception, StreamReader, StreamWriter, Handle new client connection, Handle client disconnection, handle_connection_lost()

### Community 98 - "Connection Memory/Cleanup Tasks"
Cohesion: 0.25
Nodes (4): Establish TCP connection, Background task to clean up stale pending PDUs, Check and enforce memory limits for pending PDUs, Async context manager entry

### Community 99 - "PDU Factory Typed Creation Tests"
Cohesion: 0.25
Nodes (5): Test create_typed_pdu function., Test creating typed PDU successfully., Test creating typed PDU with type mismatch., Test creating typed PDU with invalid command ID., TestCreateTypedPDU

### Community 100 - "PDU Factory Request Creation Tests"
Cohesion: 0.25
Nodes (5): Test create_request_pdu function., Test creating request PDU successfully., Test creating request PDU with response command ID., Test creating request PDU with invalid command ID., TestCreateRequestPDU

### Community 101 - "PDU Factory Command Utility Tests"
Cohesion: 0.25
Nodes (5): Test command utility functions., Test is_command_supported function., Test get_pdu_name function., Test get_pdu_name for unknown command., TestCommandUtilities

### Community 102 - "Validation: Service Type"
Cohesion: 0.25
Nodes (5): Tests for validate_service_type function., Test validating valid service types., Test validating a service type that's too long., Test validating a service type with non-printable characters., TestServiceTypeValidation

### Community 103 - "Validation Rule Registry Tests"
Cohesion: 0.25
Nodes (5): Tests for validation rule registry functions., Test registering a custom validation rule., Test getting a non-existent validation rule., Test overwriting an existing validation rule., TestValidationRuleRegistry

### Community 104 - "Validation: ESM Class"
Cohesion: 0.25
Nodes (5): Tests for validate_esm_class function., Test validating valid ESM class values., Test validating ESM class value below valid range., Test validating ESM class value above valid range., TestEsmClassValidation

### Community 105 - "Validation: Priority Flag"
Cohesion: 0.25
Nodes (5): Tests for validate_priority_flag function., Test validating valid priority flag values., Test validating priority flag value below valid range., Test validating priority flag value above valid range., TestPriorityFlagValidation

### Community 106 - "Validation: Registered Delivery"
Cohesion: 0.25
Nodes (5): Tests for validate_registered_delivery function., Test validating valid registered delivery values., Test validating registered delivery value below valid range., Test validating registered delivery value above valid range., TestRegisteredDeliveryValidation

### Community 107 - "FieldValidator Class Tests"
Cohesion: 0.25
Nodes (5): Tests for FieldValidator class., Test FieldValidator initialization., Test validation with caching., Test clearing validation cache., TestFieldValidator

### Community 108 - "Server Message Handling Tests"
Cohesion: 0.25
Nodes (5): Tests for server message handling., Test message ID generation., Test getting all client sessions., Test getting only bound client sessions., TestSMPPServerMessageHandling

### Community 109 - "Connection State & Bind Setters"
Cohesion: 0.29
Nodes (3): Set connection state and trigger state change event, Set bound state based on bind type, Async context manager exit

### Community 110 - "PDU Field Validate Methods"
Cohesion: 0.40
Nodes (3): Validate bind request fields. Raises: SMPPPDUException: If validation fails, Validate bind response fields. Raises: SMPPPDUException: If validation fails, Validate message PDU fields. Raises: SMPPPDUException: If validation fails

### Community 111 - "PDU Optional Parameter Getters"
Cohesion: 0.33
Nodes (3): Get optional parameter by tag. Args: tag: The parameter tag to search for…, Get optional parameter value by tag. Args: tag: The parameter tag to search for…, Check if optional parameter exists. Args: tag: The parameter tag to check for…

### Community 112 - "Client Connection Lost Tests"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient connection lost handling., Test handling connection lost., Test handling connection lost when handler raises exception., TestSMPPClientConnectionLost

### Community 113 - "Client Context Manager Tests"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient context manager., Test successful context manager usage., Test context manager when exception occurs., TestSMPPClientContextManager

### Community 114 - "Client Repr Tests"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient string representation., Test string representation., Test string representation when bound., TestSMPPClientRepr

### Community 115 - "Client Init Tests"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient initialization., Test SMPPClient initialization with default values., Test SMPPClient initialization with custom values., TestSMPPClientInitialization

### Community 116 - "Connection Init Tests"
Cohesion: 0.33
Nodes (4): Test initialization with custom values, Test SMPPConnection initialization, Test initialization with default values, TestSMPPConnectionInit

### Community 117 - "Connection Sequence Number Tests"
Cohesion: 0.33
Nodes (4): Test sequence number generation, Test sequence number generation, Test sequence number wraparound, TestSequenceNumber

### Community 118 - "Connection Context Manager Tests"
Cohesion: 0.33
Nodes (4): Test async context manager functionality, Test successful context manager usage, Test context manager with exception, TestContextManager

### Community 119 - "SMPP Exception Hierarchy (README)"
Cohesion: 0.40
Nodes (5): SMPPBindException, SMPPConnectionException, SMPPException (base), SMPPMessageException, SMPPTimeoutException

### Community 120 - "Connection EnquireLink Loop"
Cohesion: 0.40
Nodes (3): Exception, Background task to send periodic enquire_link PDUs, Handle connection errors

### Community 124 - "SMPP Connection Init Fields"
Cohesion: 0.50
Nodes (3): StreamReader, StreamWriter, Initialize SMPP connection Args: host: Remote host address port: Remote port…

### Community 125 - "BindType Enum Tests"
Cohesion: 0.50
Nodes (3): Tests for BindType enum., Test BindType enum values., TestBindType

### Community 128 - "Connection Memory Limit Tests"
Cohesion: 0.50
Nodes (3): Test memory management and limits, Test memory limit enforcement, TestMemoryManagement

## Knowledge Gaps
- **26 isolated node(s):** `@commitlint/config-conventional`, `type-enum`, `scope-enum`, `scope-empty`, `subject-case` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1088 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SMPPPDUException` connect `PDU Codec (Encode/Decode Helpers)` to `SMPP Client & Server Examples`, `Bind Response PDUs`, `PDU Factory Functions`, `PDU Base Encode/Decode`, `TLV Parameter Tests`, `Message PDU Decode Edge Cases`, `Bind Request/Response PDU Classes`, `BindTransmitter PDU Tests`, `SMPP Error Handling Decorators`, `EnquireLink PDU & Decode Tests`, `Outbind PDU`, `Bind Request PDU Variants`, `DataSm Session PDU`, `Codec: Message Encoding Variants`, `DeliverSm & Delivery Receipts`, `Codec: Message Encoding Tests`, `PDU Body Encoding Helpers`, `Standard Message PDU Base`, `SubmitSmResp PDU`, `QuerySmResp PDU`, `Codec: C-String Decoding`, `Codec: Integer Encoding`, `Codec: Integer Decoding`, `Codec: C-String Encoding`, `Codec: Field Length Validation`, `DataSmResp PDU`, `DeliverSmResp PDU`, `AlertNotification PDU`, `Codec: TLV Packing`, `Codec: TLV Unpacking`, `Codec: PDU Length Calculation`, `Connection PDU Receiving Tests`, `QuerySm PDU`, `TLV Decode Tests`, `PDU Factory Creation Tests`, `PDU Factory Helper Tests`, `SMPP Connection Init`, `Session PDU Field Validation`, `PDU Factory Response Creation Tests`, `PDU Factory Typed Creation Tests`, `PDU Factory Request Creation Tests`, `PDU Factory Command Utility Tests`, `PDU Field Validate Methods`, `Connection PDU Receive Loop`, `Message PDU Resp Validation`?**
  _High betweenness centrality (0.211) - this node is a cross-community bridge._
- **Why does `SMPPClient` connect `SMPP Client Bind & Send` to `SMPP Client & Server Examples`, `Client Connection Lost Handler`, `Connection Send & Sequence`, `Client Connect/Disconnect Tests`, `Client Property Tests`, `Client Deliver/Unbind Handling Tests`, `Client Example - Interactive`, `SMPP Connection Init`, `Client Example - Enhanced Shutdown`, `Client Connection Lost Tests`, `Client Context Manager Tests`, `Client Edge Case Tests`, `Client Event Handler Tests`, `Client Init Tests`, `Server PDU Dispatch Tests`, `Client Repr Tests`, `Client Wait-For Methods`, `Client Bind Operation Tests`?**
  _High betweenness centrality (0.209) - this node is a cross-community bridge._
- **Why does `SMPPServer` connect `SMPP Server Shutdown Config` to `SMPP Client & Server Examples`, `Server Session & EnquireLink Tests`, `Bind Response PDUs`, `PDU Base Encode/Decode`, `Server SubmitSm Handling`, `Server Auth & Context Manager Tests`, `Server Example - Event Handlers`, `Server PDU Dispatch Tests`, `DeliverSm & Delivery Receipts`, `Server Graceful Shutdown Logic`, `Unbind PDU`, `Server Example - Message Handling`, `Server Client Connection Tests`, `Server Property Tests`, `Server Start/Stop Tests`, `Server Edge Case Tests`, `Server Event Handler Init Tests`, `Server Client Connection Handling`, `Server Message Handling Tests`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `SMPPServer` (e.g. with `SMPPException` and `TestSMPPServerBindHandling`) actually correct?**
  _`SMPPServer` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `SMPPClient` (e.g. with `SMPPBindException` and `SMPPConnectionException`) actually correct?**
  _`SMPPClient` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `SMPPPDUException` (e.g. with `BindRequestPDU` and `BindResponsePDU`) actually correct?**
  _`SMPPPDUException` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ClientSession` (e.g. with `TestShutdownPerformance` and `.test_shutdown_performance_with_many_clients()`) actually correct?**
  _`ClientSession` has 14 INFERRED edges - model-reasoned connections that need verification._