# Graph Report - smppai  (2026-09-22)

## Corpus Check
- 55 files · ~53,167 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 7, .lock 1)

## Summary
- 2297 nodes · 3873 edges · 170 communities (138 shown, 30 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 383 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `658a1810`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SMPPValidationException
- TestSMPPServerBindHandling
- SMPPServer
- TestSMPPClientSubmitSm
- TestCreatePDU
- SMPPPDUException
- SMPPClient
- PDU
- asyncio
- TestSMPPClientBinding
- base.py
- TLVParameter
- TestHelperFunctions
- TestStandardMessagePDU
- .decode
- SMSClient
- Set up Python with uv (composite action)
- test_server.py
- .stop
- SMSCServer
- test_validation.py
- ._handle_unbind_request
- TestMessagePDU
- CommandId
- TestAddressValidation
- ._handle_client_pdu
- TestCreateResponsePDU
- smpp/__init__.py
- TestEnquireLink
- TestOptionalParameterValidation
- test_base.py
- Outbind
- TestShutdownIntegration
- ClientSession
- protocol/__init__.py
- utils.py
- Exception
- TestMessageDecoding
- MockPDU
- DeliverSm
- TestRealWorldScenarios
- TestMessageEncoding
- TestEdgeCases
- TestQuerySm
- TestGenericNack
- TestAlertNotification
- .process_message
- TestQuerySmResp
- conftest.py
- TestEnquireLinkResp
- TestCStringDecoding
- TestIntegerEncoding
- TestIntegerDecoding
- TestCStringEncoding
- TestFieldValidation
- TestMessageLengthValidation
- TestPDUStructureValidation
- TestDataSmResp
- Any
- TestSMPPServerEdgeCases
- .test_set_event_handlers
- TestTLVPacking
- TestTLVUnpacking
- TestPDULengthCalculation
- TestSubmitSmParametersValidation
- exceptions.py
- TestBindParametersValidation
- rules
- SubmitSm
- TestBindingStates
- .decode
- examples/client.py
- UDH
- TestPDUReceiving
- TestRoundTripOperations
- TestSystemIdValidation
- test_factory.py
- ._handle_pdu_received
- TestSMPPServerPDUHandling
- SMPPConnection
- TestConnectionProperties
- TestSubmitSmResp
- TestSMPPClientContextManager
- TestRegisteredDeliveryValidation
- TestBindRequestPDU
- examples/server.py
- test_codec.py
- TestPasswordValidation
- TestSequenceNumberValidation
- TestSMPPServerClientConnection
- test_session.py
- BindTransmitterResp
- TestSMPPClientRepr
- TestSMPPClientPDUHandling
- BindTransmitter
- main
- test_message.py
- Exception
- TestUnbind
- TestSMPPClientInitialization
- decode_gsm7
- SMPPException
- .disconnect
- SubmitSmResp
- bind.py
- TestPriorityFlagValidation
- .handle_deliver_sm
- .test_set_event_handlers
- TestSMPPServerUnbindHandling
- .test_handle_connection_error_handler_exception
- PACKAGING.md
- .get_optional_parameter
- RELEASING.md
- ._handle_client_connection
- QuerySmResp
- TestSMPPClientWaitMethods
- TestCreateTypedPDU
- TestSequenceNumber
- TestSMPPClientEnquireLink
- SMPPException (base)
- test_connection.py
- ConcatenatedSMSHeader
- gsm_features_demo.py
- make_parts
- TestCreateRequestPDU
- Any
- TestSMPPServerGenericNack
- TestGetPDUClass
- UnbindResp
- gsm/__init__.py
- .get_message_encoding
- unit/__init__.py
- unit/protocol/pdu/__init__.py
- Dependabot Configuration
- Bug Report Issue Template
- Documentation Issue Template
- Feature Request Issue Template
- smppai
- TestServiceTypeValidation
- TestEsmClassValidation
- TestSMPPClientUnbinding
- TestSMPPConnectionInit
- TestContextManager
- TestBackgroundTasks
- .broadcast_message
- Enum
- protocol/constants.py
- StreamReader
- StreamWriter
- asyncio
- Exception
- asyncio
- DataSm
- TestSMPPClientConnection
- Enum
- Exception
- StreamReader
- StreamWriter
- TestSMPPClientProperties
- TestBindType
- TestMemoryManagement
- ValidationRule
- asyncio
- fixture
- TestPDUClasses
- Any
- Exception
- IntEnum

## God Nodes (most connected - your core abstractions)
1. `SMPPServer` - 148 edges
2. `SMPPClient` - 138 edges
3. `ClientSession` - 89 edges
4. `SMPPPDUException` - 89 edges
5. `CommandId` - 56 edges
6. `PDU` - 42 edges
7. `SMPPConnection` - 35 edges
8. `SMSCServer` - 31 edges
9. `BindTransmitter` - 31 edges
10. `SubmitSm` - 30 edges

## Surprising Connections (you probably didn't know these)
- `Pre-commit Hooks Configuration` --semantically_similar_to--> `Lint & Format Check Job`  [INFERRED] [semantically similar]
  .pre-commit-config.yaml → .github/workflows/ci.yml
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPClient (ESME)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md
- `CONTRIBUTING Guide` --semantically_similar_to--> `CI Workflow`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → .github/workflows/ci.yml
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPServer (SMSC)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md
- `connection()` --calls--> `SMPPConnection`  [INFERRED]
  tests/unit/transport/test_connection.py → src/smpp/transport/connection.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI Workflow Pipeline Stages** — github_workflows_ci_lint, github_workflows_ci_type_check, github_workflows_ci_security, github_workflows_ci_unit_tests, github_workflows_ci_integration_test, github_workflows_ci_build, github_workflows_ci_coverage_report, github_workflows_ci_all_checks [EXTRACTED 1.00]
- **Shared Quality-Check Toolchain (ruff/mypy/pytest/bandit)** — pre_commit_config, github_workflows_ci_lint, contributing, github_pull_request_template [INFERRED 0.85]
- **SMPP Exception Hierarchy** — readme_smppexception, readme_smppconnectionexception, readme_smppbindexception, readme_smpptimeoutexception, readme_smppmessageexception [INFERRED 0.85]

## Communities (170 total, 30 thin omitted)

### Community 0 - "SMPPValidationException"
Cohesion: 0.10
Nodes (34): Exception raised for validation errors., SMPPValidationException, Initialize TLV parameter. Args: tag: Parameter tag identifier value: Parameter…, SMPP Protocol Validation This module provides validation functions for SMPP…, Validate SMPP service type field. Args: service_type: Service type to validate…, Validate message length based on data coding. Args: message: Message bytes to…, Validate data coding scheme. Args: data_coding: Data coding value to validate…, Validate ESM class field. Args: esm_class: ESM class value to validate Raises:… (+26 more)

### Community 1 - "TestSMPPServerBindHandling"
Cohesion: 0.10
Nodes (11): Tests for bind request handling., Test successful bind transmitter request., Test successful bind receiver request., Test successful bind transceiver request., Test bind request when already bound., Test bind request with authentication failure., Test bind request with event handler., Test bind request when handler raises exception. (+3 more)

### Community 2 - "SMPPServer"
Cohesion: 0.04
Nodes (31): Event, Set the grace period for shutdown notifications, Set the delay after grace period before final shutdown, Initialize SMPP Server Args: host: Server bind address port: Server bind port…, Get current shutdown configuration, Configure all shutdown parameters with comprehensive validation. Args:…, Set the timeout for graceful shutdown. Args: timeout: Maximum time in seconds…, Default authentication - allows all connections (+23 more)

### Community 3 - "TestSMPPClientSubmitSm"
Cohesion: 0.07
Nodes (15): Tests for SMPPClient submit_sm operations., Test successful submit_sm as transmitter., Test successful submit_sm as transceiver., Test submit_sm when not bound., Test submit_sm with receiver bind type., Test submit_sm with no bind type., Test submit_sm with message too long., Test submit_sm when connection is None after being bound. (+7 more)

### Community 4 - "TestCreatePDU"
Cohesion: 0.17
Nodes (7): Test creating PDU with invalid command ID., Test creating PDU with invalid parameters., Test create_pdu function., Test creating BindTransmitter PDU., Test creating SubmitSm PDU., Test creating EnquireLink PDU., TestCreatePDU

### Community 5 - "SMPPPDUException"
Cohesion: 0.05
Nodes (45): Exception raised for PDU-related errors., SMPPPDUException, calculate_pdu_length(), decode_cstring(), decode_integer(), decode_message_with_encoding(), encode_cstring(), encode_integer() (+37 more)

### Community 6 - "SMPPClient"
Cohesion: 0.04
Nodes (30): ConnectionState, Check if client is connected to SMSC, Check if client is bound to SMSC, Get current bind type, Bind as transmitter (can send SMS), Bind as receiver (can receive SMS and delivery receipts), Bind as transceiver (can send and receive SMS), Send enquire_link to test connection Args: timeout: Response timeout Returns:… (+22 more)

### Community 7 - "PDU"
Cohesion: 0.07
Nodes (18): PDU, Abstract base class for all SMPP PDUs. This class provides the common…, Initialize PDU after creation., Encode PDU body to bytes. Must be implemented by subclasses to encode the PDU-…, Decode PDU body from bytes. Must be implemented by subclasses to decode the…, Encode complete PDU to bytes. Returns: The complete encoded PDU including…, Decode PDU from bytes. Args: data: The byte data to decode Returns: The decoded…, Add optional parameter. If a parameter with the same tag already exists, it… (+10 more)

### Community 8 - "asyncio"
Cohesion: 0.06
Nodes (26): asyncio, Tests for deliver_sm functionality., Test successful message delivery., Test message delivery when target not found., Test message delivery when target not bound., Test message delivery when target has wrong bind type., Test message delivery to transceiver., Tests for server start/stop functionality. (+18 more)

### Community 9 - "TestSMPPClientBinding"
Cohesion: 0.09
Nodes (12): Tests for SMPPClient binding operations., Test successful bind as transmitter., Test successful bind as receiver., Test successful bind as transceiver., Test bind when not connected., Test bind when already bound., Test bind when connection object is None., Test bind when no response received. (+4 more)

### Community 10 - "base.py"
Cohesion: 0.11
Nodes (17): ABC, Any, BindRequestPDU, BindResponsePDU, MessagePDU, SMPP PDU Base Classes and Utilities This module contains the base PDU class and…, Base class for request PDUs. Request PDUs are sent by SMPP clients to servers…, Base class for response PDUs. Response PDUs are sent by SMPP servers to clients… (+9 more)

### Community 11 - "TLVParameter"
Cohesion: 0.09
Nodes (16): Tag-Length-Value parameter for optional parameters. TLV parameters are used in…, Encode TLV parameter to bytes. Returns: The encoded TLV parameter as bytes, TLVParameter, Test TLV parameter string representation., Test TLVParameter class., Test TLV parameter equality., Test TLV parameter hashing., Test TLV parameter initialization with valid data. (+8 more)

### Community 12 - "TestHelperFunctions"
Cohesion: 0.17
Nodes (7): Test helper factory functions., Test create_bind_pdu helper., Test create_bind_pdu with invalid type., Test create_submit_sm_pdu helper., Test create_enquire_link_pdu helper., Test create_generic_nack_pdu helper., TestHelperFunctions

### Community 13 - "TestStandardMessagePDU"
Cohesion: 0.08
Nodes (22): Test decode with insufficient data for source address fields., Test decode with insufficient data for destination address fields., Test decode with insufficient data for message fields., Test delivery receipt request checking., Test StandardMessagePDU base class., Test setting delivery receipt request., Test Unicode message detection., Test StandardMessagePDU body encoding with basic data. (+14 more)

### Community 14 - ".decode"
Cohesion: 0.13
Nodes (8): Decode UDH element from bytes., Decode UDH from bytes. Args: data: Bytes to decode from offset: Starting offset…, Check if this message has User Data Header. Returns: True if UDH indicator is…, Extract UDH from short message if present. Returns: UDH object if present, None…, Get message content without UDH. Returns: Message content bytes (short_message…, Set UDH for this message. Args: udh: UDH object to set, Check if this is part of a concatenated SMS. Returns: True if this message has…, Get concatenated SMS information if present. Returns: ConcatenatedSMSHeader if…

### Community 15 - "SMSClient"
Cohesion: 0.11
Nodes (11): Exception, Handle connection lost event with enhanced shutdown awareness., Handle successful bind with enhanced logging., Handle unbind event with enhanced logging., Connect to SMSC and bind with enhanced shutdown awareness., Send a command to the server (for testing enhanced shutdown). Uses proper SMPP…, Send Unicode SMS message, Check if shutdown has been requested. (+3 more)

### Community 16 - "Set up Python with uv (composite action)"
Cohesion: 0.11
Nodes (28): CHANGELOG, CONTRIBUTING Guide, Conventional Commits, smppai Project Structure (client/server/protocol/transport/config), Semantic Release / Automated Versioning, Examples README, Set up Python with uv (composite action), Pull Request Template (+20 more)

### Community 17 - "test_server.py"
Cohesion: 0.07
Nodes (19): Unit tests for SMPP Server implementation This module contains tests for the…, Tests for enquire_link request handling., Test successful enquire_link request., Test enquire_link when exception occurs., Tests for server stop with client disconnect exceptions., Test server stop when client disconnect raises exception., Tests for custom authentication., Test custom authentication that succeeds. (+11 more)

### Community 18 - ".stop"
Cohesion: 0.11
Nodes (9): Async context manager entry, Async context manager exit with graceful shutdown, Start the SMPP server, Stop the SMPP server gracefully with enhanced shutdown sequence. This method is…, Stop the server and close connections., Reset shutdown state for potential restart., Set up signal handlers for graceful shutdown using proper async patterns., Unregister signal handlers to clean up on shutdown (+1 more)

### Community 19 - "SMSCServer"
Cohesion: 0.16
Nodes (8): Set up all server event handlers., Authenticate client credentials with enhanced logging. Args: system_id: Client…, Example SMSC server using SMPP with enhanced shutdown capabilities. Features: -…, Start the SMSC server., Stop the SMSC server with enhanced shutdown., Clean up all background tasks gracefully., Configure enhanced shutdown with reasonable timeouts for demonstration., SMSCServer

### Community 20 - "test_validation.py"
Cohesion: 0.14
Nodes (9): Unit tests for SMPP Protocol Validation functions. Tests all validation…, Tests for validate_data_coding function., Test validating valid data coding schemes., Test validating invalid data coding schemes., Tests for validate_command_id function., Test validating valid command IDs., Test validating invalid command IDs., TestCommandIdValidation (+1 more)

### Community 21 - "._handle_unbind_request"
Cohesion: 0.10
Nodes (11): Send shutdown notification to a client session with comprehensive error…, Send shutdown notification to all bound clients, Enhanced graceful shutdown with broadcast notifications and grace periods., Send notifications and wait for clients to disconnect gracefully., Wait for grace period and check if clients disconnect. Returns: True if all…, Force disconnect all remaining clients., Send unbind requests to all bound clients., Force disconnect all clients. (+3 more)

### Community 22 - "TestMessagePDU"
Cohesion: 0.20
Nodes (4): Test MessagePDU base class., Test MessagePDU default values., Test MessagePDU with custom values., TestMessagePDU

### Community 23 - "CommandId"
Cohesion: 0.11
Nodes (17): CommandId, SMPP Command IDs as defined in SMPP v3.4 specification, BindReceiverResp, BindTransceiverResp, BIND_RECEIVER_RESP PDU - Response to bind_receiver, BIND_TRANSCEIVER_RESP PDU - Response to bind_transceiver, Base class for standard bind responses with system_id only, Encode standard bind response body (+9 more)

### Community 24 - "TestAddressValidation"
Cohesion: 0.08
Nodes (13): Test validating a valid national ISDN address., Test validating a valid alphanumeric address., Test validating an address that's too long., Test validating an address with invalid TON., Test validating an address with invalid NPI., Test validating international ISDN address with invalid format., Test validating national ISDN address with invalid format., Test validating alphanumeric address with invalid format. (+5 more)

### Community 25 - "._handle_client_pdu"
Cohesion: 0.13
Nodes (10): CommandStatus, EnquireLink, Handle PDU received from client, Handle bind request from client, Handle submit_sm request from client, Send submit_sm response to client, Handle enquire_link request from client, Send generic_nack to client (+2 more)

### Community 26 - "TestCreateResponsePDU"
Cohesion: 0.20
Nodes (6): Test create_response_pdu function., Test creating response PDU successfully., Test creating response PDU with default status., Test creating response PDU from response command ID., Test creating response PDU for invalid command., TestCreateResponsePDU

### Community 27 - "smpp/__init__.py"
Cohesion: 0.10
Nodes (21): BindType, Perform bind operation, Submit SMS message Args: source_addr: Source address (sender) destination_addr:…, SMPP Client Module This module provides a comprehensive async SMPP client…, Exception raised for bind-related errors., Exception raised when operation is attempted in invalid state., Exception raised for message-related errors., SMPPBindException (+13 more)

### Community 28 - "TestEnquireLink"
Cohesion: 0.14
Nodes (8): Test EnquireLink PDU., Test EnquireLink initialization., Test that custom command_id is preserved., Test EnquireLink body encoding (should be empty)., Test EnquireLink body decoding (should handle empty body)., Test that sequence number stays 0 until send_pdu assigns it., Test custom sequence number., TestEnquireLink

### Community 29 - "TestOptionalParameterValidation"
Cohesion: 0.09
Nodes (12): Tests for validate_optional_parameter function., Test validating valid optional parameters., Test validating optional parameter with negative tag., Test validating optional parameter with tag too large., Test validating optional parameter with value too long., Test validating valid receipted message ID., Test validating receipted message ID with non-printable characters., Test validating receipted message ID with invalid ASCII. (+4 more)

### Community 30 - "test_base.py"
Cohesion: 0.13
Nodes (5): Unit tests for SMPP PDU base classes., Test that __post_init__ preserves non-zero sequence number., Test PDU default values., Test PDU with custom values., TestPDU

### Community 31 - "Outbind"
Cohesion: 0.12
Nodes (13): Outbind, OUTBIND PDU - SMSC initiated bind request, Encode outbind body with system_id and password only, Decode outbind body with system_id and password only, Validate outbind fields Raises: SMPPPDUException: If validation fails, Test Outbind initialization., Test Outbind body encoding., Test Outbind body decoding. (+5 more)

### Community 32 - "TestShutdownIntegration"
Cohesion: 0.12
Nodes (14): integration, performance, asyncio, fixture, Integration tests for SMPP Server and Client shutdown interaction These tests…, Test that client can reconnect after server restart., Integration tests for server-client shutdown interaction, Performance tests for shutdown operations (+6 more)

### Community 33 - "ClientSession"
Cohesion: 0.06
Nodes (27): Handle new client connection with enhanced logging., Handle client disconnection with enhanced logging., Handle successful client bind with enhanced logging., Handle SMS message from client with enhanced logging and commands., Send welcome message to newly bound clients., ClientSession, Get list of bound client sessions, Represents a connected SMPP client session (+19 more)

### Community 34 - "protocol/__init__.py"
Cohesion: 0.09
Nodes (43): SMPP Protocol Module This module contains the core SMPP protocol implementation…, EmptyBodyPDU, Base class for PDUs with empty body. Some SMPP PDUs like enquire_link and…, Decode empty body. Args: data: Raw PDU data (unused for empty body) offset:…, UNBIND PDU - Request to unbind from SMSC, Unbind, create_bind_pdu(), create_enquire_link_pdu() (+35 more)

### Community 35 - "utils.py"
Cohesion: 0.11
Nodes (19): calculate_message_length(), format_smpp_time(), generate_message_id(), is_valid_system_id(), mask_sensitive_data(), normalize_phone_number(), parse_smpp_time(), SMPP Utilities Module This module provides basic utility functions and helper… (+11 more)

### Community 36 - "Exception"
Cohesion: 0.15
Nodes (8): Exception, IntEnum, SMPP-specific error codes for better error categorization., SMPPErrorCode, Tests for SMPPClient connection lost handling., Test handling connection lost., Test handling connection lost when handler raises exception., TestSMPPClientConnectionLost

### Community 37 - "TestMessageDecoding"
Cohesion: 0.10
Nodes (11): Tests for decode_message_with_encoding function., Test decoding with default data coding., Test decoding with ASCII data coding., Test decoding with Latin-1 data coding., Test decoding with UCS2 data coding., Test decoding with octet unspecified data coding., Test decoding with unknown data coding (should fallback to UTF-8)., Test decoding Unicode with UTF-8 fallback. (+3 more)

### Community 38 - "MockPDU"
Cohesion: 0.14
Nodes (9): MockPDU, Test PDU sending functionality, Test sending PDU when not connected, Test sending PDU without waiting for response, Test sending PDU with response, Test PDU response timeout, Return mock encoded PDU, Test send data failure (+1 more)

### Community 39 - "DeliverSm"
Cohesion: 0.13
Nodes (11): DeliverSm, DELIVER_SM PDU - Deliver a short message or delivery receipt, Check if this is a delivery receipt Returns: bool: True if this is a delivery…, Check if this is a mobile originated message Returns: bool: True if this is a…, Parse delivery receipt message into structured data Returns: dict: Parsed…, Create a delivery receipt message Args: original_message_id: ID of the original…, Deliver SMS message to a specific client Args: target_system_id: Target client…, Test DeliverSm initialization. (+3 more)

### Community 40 - "TestRealWorldScenarios"
Cohesion: 0.17
Nodes (7): Tests for real-world usage scenarios., Test complete bind parameter validation flow., Test complete submit_sm parameter validation flow., Test alphanumeric addressing validation., Test Unicode message validation., Test that empty fields are allowed where appropriate., TestRealWorldScenarios

### Community 41 - "TestMessageEncoding"
Cohesion: 0.11
Nodes (10): Tests for encode_message_with_encoding function., Test encoding with default data coding., Test encoding with ASCII data coding., Test encoding with Latin-1 data coding., Test encoding with UCS2 data coding., Test encoding with octet unspecified data coding., Test encoding with unknown data coding (should fallback to UTF-8)., Test encoding Unicode with UTF-8 fallback. (+2 more)

### Community 42 - "TestEdgeCases"
Cohesion: 0.11
Nodes (10): Tests for edge cases and boundary conditions., Test system ID at exact boundary length., Test password at exact boundary length., Test address at exact boundary length., Test service type at exact boundary length., Test message at exact boundary length for GSM 7-bit., Test message at exact general boundary length., Test sequence number at boundary values. (+2 more)

### Community 43 - "TestQuerySm"
Cohesion: 0.22
Nodes (5): Test QuerySm initialization., Test QuerySm with custom values., Test QuerySm body encoding., Test QuerySm body decoding., TestQuerySm

### Community 44 - "TestGenericNack"
Cohesion: 0.17
Nodes (7): Test GenericNack body encoding (should be empty)., Test creating GenericNack for invalid PDU., Test creating GenericNack with error message., Test GenericNack PDU., Test GenericNack initialization., Test GenericNack with custom values., TestGenericNack

### Community 45 - "TestAlertNotification"
Cohesion: 0.17
Nodes (7): Test AlertNotification PDU., Test AlertNotification initialization., Test AlertNotification with custom values., Test AlertNotification body encoding., Test AlertNotification body decoding., Test decode with insufficient data., TestAlertNotification

### Community 46 - ".process_message"
Cohesion: 0.20
Nodes (5): Process received message with enhanced command support., Send a response back to the client., Demonstrate the enhanced shutdown feature., Send delivery receipt to client., Get comprehensive server statistics.

### Community 47 - "TestQuerySmResp"
Cohesion: 0.17
Nodes (7): Test QuerySmResp PDU., Test QuerySmResp initialization., Test QuerySmResp with custom values., Test QuerySmResp body encoding., Test QuerySmResp body decoding., Test decode with insufficient data., TestQuerySmResp

### Community 48 - "conftest.py"
Cohesion: 0.17
Nodes (14): event_loop(), mock_asyncio_sleep(), mock_logger(), mock_time(), fixture, Shared test fixtures and configuration for SMPP unit tests., Create an event loop for async tests., Mock asyncio.sleep to speed up tests. (+6 more)

### Community 49 - "TestEnquireLinkResp"
Cohesion: 0.20
Nodes (6): Test EnquireLinkResp PDU., Test EnquireLinkResp initialization., Test EnquireLinkResp with custom values., Test EnquireLinkResp body encoding (should be empty)., Test EnquireLinkResp body decoding., TestEnquireLinkResp

### Community 50 - "TestCStringDecoding"
Cohesion: 0.12
Nodes (9): Test decoding with invalid byte sequence., Tests for decode_cstring function., Test decoding a simple null-terminated string., Test decoding an empty string., Test decoding starting from a specific offset., Test decoding when offset is beyond data length., Test decoding when string is not null-terminated within max_length., Test decoding with custom character encoding. (+1 more)

### Community 51 - "TestIntegerEncoding"
Cohesion: 0.12
Nodes (9): Tests for encode_integer function., Test encoding 1-byte unsigned integer., Test encoding 1-byte signed integer., Test encoding 2-byte unsigned integer., Test encoding 4-byte unsigned integer., Test encoding 8-byte unsigned integer., Test encoding with invalid size., Test encoding value that's out of range for the size. (+1 more)

### Community 52 - "TestIntegerDecoding"
Cohesion: 0.12
Nodes (9): Tests for decode_integer function., Test decoding 1-byte unsigned integer., Test decoding 1-byte signed integer., Test decoding 2-byte unsigned integer., Test decoding 4-byte unsigned integer., Test decoding starting from a specific offset., Test decoding when there's insufficient data., Test decoding with invalid size. (+1 more)

### Community 53 - "TestCStringEncoding"
Cohesion: 0.12
Nodes (9): Tests for encode_cstring function., Test encoding a simple ASCII string., Test encoding an empty string., Test encoding a string that exactly fits the limit., Test encoding a string that exceeds the maximum length., Test encoding with custom character encoding., Test encoding with unsupported characters., Test when encoded bytes exceed limit even if string length is OK. (+1 more)

### Community 54 - "TestFieldValidation"
Cohesion: 0.12
Nodes (9): Tests for validate_field_length function., Test validation of a valid string field., Test validation of a valid bytes field., Test validation of field that's too short., Test validation of field that's too long., Test validation when no maximum length is specified., Test validation when field is exactly at minimum length., Test validation when field is exactly at maximum length. (+1 more)

### Community 55 - "TestMessageLengthValidation"
Cohesion: 0.12
Nodes (9): Tests for validate_message_length function., Test validating valid message length with default data coding., Test validating valid message length with UCS2 data coding., Test validating a message that exceeds the general maximum., Test validating a message that exceeds GSM 7-bit limit., Test validating a message that exceeds UCS2 limit., Test validating a message at the GSM 7-bit boundary., Test validating a message at the UCS2 boundary. (+1 more)

### Community 56 - "TestPDUStructureValidation"
Cohesion: 0.12
Nodes (9): Tests for validate_pdu_structure function., Test validating valid PDU structure for request., Test validating valid PDU structure for response., Test validating PDU structure with invalid command ID., Test validating PDU structure with invalid sequence number., Test validating PDU structure with command length too small., Test validating PDU structure with command length too large., Test validating PDU structure with invalid command status for response. (+1 more)

### Community 57 - "TestDataSmResp"
Cohesion: 0.22
Nodes (5): Test DataSmResp initialization., Test DataSmResp with custom values., Test DataSmResp body encoding., Test DataSmResp body decoding., TestDataSmResp

### Community 59 - "TestSMPPServerEdgeCases"
Cohesion: 0.20
Nodes (6): Tests for edge cases and error scenarios., Test client count after various operations., Test message ID counter behavior., Test getting bound clients with mixed session states., Test client connection when peer info is not available., TestSMPPServerEdgeCases

### Community 60 - ".test_set_event_handlers"
Cohesion: 0.20
Nodes (4): Tests for SMPPClient event handlers., Test that event handlers are initialized to None., Test setting event handlers., TestSMPPClientEventHandlers

### Community 61 - "TestTLVPacking"
Cohesion: 0.14
Nodes (8): Tests for pack_tlv_parameter function., Test packing a simple TLV parameter., Test packing TLV with empty value., Test packing TLV with maximum tag value., Test packing TLV with invalid negative tag., Test packing TLV with tag too large., Test packing TLV with value too long., TestTLVPacking

### Community 62 - "TestTLVUnpacking"
Cohesion: 0.14
Nodes (8): Tests for unpack_tlv_parameter function., Test unpacking a simple TLV parameter., Test unpacking TLV with empty value., Test unpacking TLV starting from a specific offset., Test unpacking when there's insufficient data for header., Test unpacking when there's insufficient data for value., Test unpacking when offset is at the end of data., TestTLVUnpacking

### Community 63 - "TestPDULengthCalculation"
Cohesion: 0.14
Nodes (8): Tests for calculate_pdu_length function., Test calculating basic PDU length., Test calculating PDU length without optional parameters., Test calculating PDU length with zero body size., Test calculating maximum allowed PDU length., Test calculating PDU length that exceeds maximum., Test calculating PDU length with large optional parameters., TestPDULengthCalculation

### Community 64 - "TestSubmitSmParametersValidation"
Cohesion: 0.14
Nodes (8): Tests for validate_submit_sm_parameters function., Test validating valid submit_sm parameters., Test validating submit_sm parameters with invalid source address., Test validating submit_sm parameters with invalid destination address., Test validating submit_sm parameters with message too long., Test validating submit_sm parameters with invalid data coding., Test validating submit_sm parameters with invalid priority flag., TestSubmitSmParametersValidation

### Community 65 - "exceptions.py"
Cohesion: 0.15
Nodes (12): Enum, SMPP Client (ESME) Implementation This module provides a comprehensive async…, SMPP Exception Classes This module defines all SMPP-specific exception classes…, SMPP Server (SMSC) Implementation This module provides a basic SMPP server…, ConnectionState, SMPP Connection Handling This module provides async TCP connection handling for…, SMPP Connection States, Get current connection state (+4 more)

### Community 66 - "TestBindParametersValidation"
Cohesion: 0.17
Nodes (7): Tests for validate_bind_parameters function., Test validating valid bind parameters., Test validating bind parameters with system type too long., Test validating bind parameters with invalid interface version., Test validating bind parameters with valid interface versions., Test validating bind parameters with invalid address range., TestBindParametersValidation

### Community 67 - "rules"
Cohesion: 0.15
Nodes (12): extends, rules, body-leading-blank, footer-leading-blank, header-max-length, scope-empty, scope-enum, subject-case (+4 more)

### Community 68 - "SubmitSm"
Cohesion: 0.15
Nodes (11): SUBMIT_SM PDU - Request to submit a short message, SubmitSm, Test integration with MessagePDU., Test SubmitSm PDU with UDH., Test SubmitSm PDU without UDH., TestMessagePDUIntegration, Test creating error response with message., Test SubmitSm initialization with defaults. (+3 more)

### Community 69 - "TestBindingStates"
Cohesion: 0.20
Nodes (6): Test connection binding state management, Test setting transmitter bound state, Test setting receiver bound state, Test setting transceiver bound state, Test setting invalid bound state, TestBindingStates

### Community 70 - ".decode"
Cohesion: 0.17
Nodes (6): Decode TLV parameter from bytes. Args: data: The byte data to decode from…, Test decoding with insufficient header data., Test decoding with insufficient value data., Test TLV parameter decoding., Test TLV parameter decoding with offset., Test decoding TLV with empty value.

### Community 71 - "examples/client.py"
Cohesion: 0.18
Nodes (9): interactive_client_example(), main(), monitor_messages_example(), SMPP Client Example This example demonstrates how to use the SMPP client to…, Main example function demonstrating enhanced shutdown handling. Features…, Simple example of sending one SMS with enhanced shutdown awareness., Example of monitoring incoming messages with enhanced shutdown handling. This…, Interactive client that can send commands to test enhanced shutdown. (+1 more)

### Community 72 - "UDH"
Cohesion: 0.13
Nodes (10): Get total UDH length including length header., User Data Header element. Attributes: iei: Information Element Identifier data:…, Convert to UDH element., Encode UDH element to bytes., User Data Header for SMS messages. Handles parsing and generation of UDH for…, Initialize UDH with optional elements., Get UDH element by IEI., Encode UDH to bytes. Returns: UDH bytes including length header (+2 more)

### Community 73 - "TestPDUReceiving"
Cohesion: 0.12
Nodes (9): Test PDU receiving functionality, Test successful PDU reception, Test PDU reception with no reader, Test PDU reception timeout, Test incomplete PDU read, Test PDU with invalid length, Test handling received PDU as response, Test handling received PDU as incoming (+1 more)

### Community 74 - "TestRoundTripOperations"
Cohesion: 0.17
Nodes (7): Tests for round-trip encoding/decoding operations., Test encoding and decoding C-strings., Test encoding and decoding integers., Test encoding and decoding messages with UTF-8., Test encoding and decoding messages with UCS2., Test packing and unpacking TLV parameters., TestRoundTripOperations

### Community 75 - "TestSystemIdValidation"
Cohesion: 0.17
Nodes (7): Tests for validate_system_id function., Test validating a valid system ID., Test validating an empty system ID., Test validating a system ID that's too long., Test validating a system ID with invalid characters., Test that underscores are allowed in system ID., TestSystemIdValidation

### Community 76 - "test_factory.py"
Cohesion: 0.12
Nodes (10): Unit tests for SMPP PDU factory., Test command utility functions., Test is_command_supported function., Test get_pdu_name function., Test get_pdu_name for unknown command., Test decode_pdu function., Test decoding EnquireLink PDU., Test decoding with invalid data. (+2 more)

### Community 77 - "._handle_pdu_received"
Cohesion: 0.20
Nodes (5): DeliverSm, Handle received PDU from connection, Handle deliver_sm PDU, Send enquire_link_resp, Handle unbind request from SMSC

### Community 78 - "TestSMPPServerPDUHandling"
Cohesion: 0.12
Nodes (9): Test PDU handling through _handle_client_pdu method., Test handling of BindTransmitter PDU through PDU handler., Test handling of BindReceiver PDU through PDU handler., Test handling of BindTransceiver PDU through PDU handler., Test handling of Unbind PDU through PDU handler., Test handling of SubmitSm PDU through PDU handler., Test handling of EnquireLink PDU through PDU handler., Test handling of unknown PDU through PDU handler. (+1 more)

### Community 79 - "SMPPConnection"
Cohesion: 0.07
Nodes (26): PDU, Connect to SMSC server, Exception raised when operations timeout., Exception raised for connection-related errors., SMPPConnectionException, SMPPTimeoutException, Check if connection is established, Check if connection is bound (+18 more)

### Community 80 - "TestConnectionProperties"
Cohesion: 0.18
Nodes (6): Test connection properties and state management, Test state property getter, Test is_connected property, Test is_bound property, Test state change with handler, TestConnectionProperties

### Community 81 - "TestSubmitSmResp"
Cohesion: 0.14
Nodes (8): Test SubmitSmResp PDU., Test SubmitSmResp initialization., Test SubmitSmResp with custom values., Test SubmitSmResp body encoding., Test SubmitSmResp body encoding with empty message_id., Test SubmitSmResp body decoding., Test SubmitSmResp body decoding with empty message_id., TestSubmitSmResp

### Community 82 - "TestSMPPClientContextManager"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient context manager., Test successful context manager usage., Test context manager when exception occurs., TestSMPPClientContextManager

### Community 83 - "TestRegisteredDeliveryValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_registered_delivery function., Test validating valid registered delivery values., Test validating registered delivery value below valid range., Test validating registered delivery value above valid range., TestRegisteredDeliveryValidation

### Community 84 - "TestBindRequestPDU"
Cohesion: 0.20
Nodes (4): Test BindRequestPDU base class., Test BindRequestPDU default values., Test BindRequestPDU with custom values., TestBindRequestPDU

### Community 85 - "examples/server.py"
Cohesion: 0.33
Nodes (4): SMPP Server Example This example demonstrates how to use the SMPP server with…, Simple server example showcasing async context manager with enhanced shutdown.…, simple_server_example(), SMPP Server Module This module provides a comprehensive async SMPP server…

### Community 86 - "test_codec.py"
Cohesion: 0.20
Nodes (6): Unit tests for SMPP Protocol Codec utilities. Tests all encoding/decoding…, Tests for edge cases and boundary conditions., Test handling of maximum values., Test handling of zero values., Test boundary length conditions., TestEdgeCases

### Community 87 - "TestPasswordValidation"
Cohesion: 0.20
Nodes (6): Tests for validate_password function., Test validating valid passwords., Test validating a password that's too long., Test validating a password with non-printable characters., Test that special printable characters are allowed., TestPasswordValidation

### Community 88 - "TestSequenceNumberValidation"
Cohesion: 0.20
Nodes (6): Tests for validate_sequence_number function., Test validating valid sequence numbers., Test validating sequence number zero., Test validating negative sequence number., Test validating sequence number that's too large., TestSequenceNumberValidation

### Community 89 - "TestSMPPServerClientConnection"
Cohesion: 0.14
Nodes (8): Tests for client connection handling., Test successful client connection handling., Test client connection rejected when max connections exceeded., Test client connection with event handler., Test client connection when handler raises exception., Test client disconnection handling., Test client disconnection when handler raises exception., TestSMPPServerClientConnection

### Community 90 - "test_session.py"
Cohesion: 0.29
Nodes (4): Unit tests for SMPP session PDUs., Test DataSm initialization., Test DataSm with custom values., TestDataSm

### Community 91 - "BindTransmitterResp"
Cohesion: 0.11
Nodes (13): BindTransmitterResp, BIND_TRANSMITTER_RESP PDU - Response to bind_transmitter, Test BindTransmitterResp PDU., Test BindTransmitterResp initialization., Test BindTransmitterResp with custom values., Test BindTransmitterResp body encoding., Test BindTransmitterResp body decoding., TestBindTransmitterResp (+5 more)

### Community 92 - "TestSMPPClientRepr"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient string representation., Test string representation., Test string representation when bound., TestSMPPClientRepr

### Community 93 - "TestSMPPClientPDUHandling"
Cohesion: 0.06
Nodes (19): patch, Test handling PDU when exception occurs., Test handling deliver_sm., Test handling deliver_sm when handler raises exception., Test that initialization creates SMPPConnection., Test sending deliver_sm_resp., Test sending deliver_sm_resp when exception occurs., Test sending enquire_link_resp. (+11 more)

### Community 94 - "BindTransmitter"
Cohesion: 0.20
Nodes (9): BindTransmitter, BIND_TRANSMITTER PDU - Request to bind as transmitter, Test decode with insufficient data., Test BindTransmitter PDU., Test BindTransmitter initialization with defaults., Test BindTransmitter with custom values., Test BindTransmitter body encoding., Test BindTransmitter body decoding. (+1 more)

### Community 95 - "main"
Cohesion: 0.25
Nodes (8): cleanup_background_tasks(), main(), Main server function demonstrating enhanced shutdown capabilities. Features…, Monitor and log server statistics periodically., Send periodic broadcast messages to demonstrate server capabilities., Clean up background tasks gracefully., run_broadcast_scheduler(), run_stats_monitor()

### Community 96 - "test_message.py"
Cohesion: 0.17
Nodes (7): Unit tests for SMPP message PDUs., Test DeliverSmResp PDU., Test DeliverSmResp initialization., Test DeliverSmResp with custom values., Test DeliverSmResp body encoding., Test DeliverSmResp body decoding., TestDeliverSmResp

### Community 98 - "TestUnbind"
Cohesion: 0.29
Nodes (4): Test Unbind initialization., Test Unbind body encoding (should be empty)., Test Unbind body decoding (should handle empty body)., TestUnbind

### Community 99 - "TestSMPPClientInitialization"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient initialization., Test SMPPClient initialization with default values., Test SMPPClient initialization with custom values., TestSMPPClientInitialization

### Community 100 - "decode_gsm7"
Cohesion: 0.14
Nodes (13): decode_gsm7(), encode_gsm7(), GSM 7-bit encoding implementation for SMS messages. Provides encoding and…, Encode text to GSM 7-bit format. Args: text: Unicode text to encode Returns:…, Decode GSM 7-bit encoded data to text. Args: data: GSM 7-bit encoded bytes…, Unit tests for GSM functionality., Test GSM 7-bit encoding and decoding., Test basic GSM 7-bit encoding. (+5 more)

### Community 101 - "SMPPException"
Cohesion: 0.18
Nodes (11): Exception raised for protocol violations., Exception raised for authentication failures., Exception raised when throttling limits are exceeded., Base exception for all SMPP-related errors., Exception raised for configuration-related errors., Enhanced string representation with context., SMPPAuthenticationException, SMPPConfigurationException (+3 more)

### Community 103 - "SubmitSmResp"
Cohesion: 0.13
Nodes (10): DeliverSmResp, SUBMIT_SM_RESP PDU - Response to submit_sm, Encode submit_sm_resp body Returns: bytes: Encoded PDU body, Decode submit_sm_resp body Args: data: Raw PDU data to decode offset: Starting…, Validate submit_sm_resp fields Raises: SMPPPDUException: If validation fails, DELIVER_SM_RESP PDU - Response to deliver_sm, Encode deliver_sm_resp body Returns: bytes: Encoded PDU body, Decode deliver_sm_resp body Args: data: Raw PDU data to decode offset: Starting… (+2 more)

### Community 104 - "bind.py"
Cohesion: 0.10
Nodes (15): BindReceiver, BindTransceiver, SMPP Bind PDU Implementations This module contains all bind-related PDU classes…, BIND_TRANSCEIVER PDU - Request to bind as transceiver, Base class for standard bind requests (transmitter, receiver, transceiver), BIND_RECEIVER PDU - Request to bind as receiver, StandardBindRequestPDU, Unit tests for SMPP bind PDUs. (+7 more)

### Community 105 - "TestPriorityFlagValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_priority_flag function., Test validating valid priority flag values., Test validating priority flag value below valid range., Test validating priority flag value above valid range., TestPriorityFlagValidation

### Community 106 - ".handle_deliver_sm"
Cohesion: 0.20
Nodes (5): Check if this message is a server shutdown notification., Handle server shutdown notifications with appropriate responses., Thread-safe graceful shutdown process., Disconnect from SMSC with enhanced shutdown handling., Handle incoming deliver_sm with enhanced shutdown notification detection.

### Community 107 - ".test_set_event_handlers"
Cohesion: 0.20
Nodes (4): Tests for server event handler initialization., Test that event handlers are initialized to None., Test setting custom event handlers., TestSMPPServerEventHandlers

### Community 108 - "TestSMPPServerUnbindHandling"
Cohesion: 0.33
Nodes (4): Tests for unbind request handling., Test successful unbind request., Test unbind request when exception occurs., TestSMPPServerUnbindHandling

### Community 109 - ".test_handle_connection_error_handler_exception"
Cohesion: 0.20
Nodes (5): Test state change handler exception handling, Test connection error handling, Test connection error handler exception, failing_handler(), TestErrorHandling

### Community 111 - ".get_optional_parameter"
Cohesion: 0.33
Nodes (3): Get optional parameter by tag. Args: tag: The parameter tag to search for…, Get optional parameter value by tag. Args: tag: The parameter tag to search for…, Check if optional parameter exists. Args: tag: The parameter tag to check for…

### Community 113 - "._handle_client_connection"
Cohesion: 0.25
Nodes (6): Handle new client connection, Handle client disconnection, handle_connection_lost(), Initialize SMPP connection Args: host: Remote host address port: Remote port…, StreamReader, StreamWriter

### Community 114 - "QuerySmResp"
Cohesion: 0.10
Nodes (13): MessageState, Message State values for delivery receipts, DataSmResp, QuerySmResp, Validate data_sm fields, DATA_SM_RESP PDU - Response to data_sm, Encode data_sm_resp body, Decode data_sm_resp body (+5 more)

### Community 115 - "TestSMPPClientWaitMethods"
Cohesion: 0.12
Nodes (8): Tests for SMPPClient wait methods., Test wait_for_connection when connection succeeds., Test wait_for_connection timeout., Test wait_for_connection when already connected., Test wait_for_bind when bind succeeds., Test wait_for_bind timeout., Test wait_for_bind when already bound., TestSMPPClientWaitMethods

### Community 116 - "TestCreateTypedPDU"
Cohesion: 0.25
Nodes (5): Test create_typed_pdu function., Test creating typed PDU successfully., Test creating typed PDU with type mismatch., Test creating typed PDU with invalid command ID., TestCreateTypedPDU

### Community 117 - "TestSequenceNumber"
Cohesion: 0.33
Nodes (4): Test sequence number generation, Test sequence number generation, Test sequence number wraparound, TestSequenceNumber

### Community 118 - "TestSMPPClientEnquireLink"
Cohesion: 0.12
Nodes (9): Tests for SMPPClient enquire_link operations., Test successful enquire_link., Test enquire_link when not connected., Test enquire_link when connection is None., Test enquire_link when no response received., Test enquire_link when error response received., Test enquire_link when exception occurs., Test enquire_link with custom timeout. (+1 more)

### Community 119 - "SMPPException (base)"
Cohesion: 0.40
Nodes (5): SMPPBindException, SMPPConnectionException, SMPPException (base), SMPPMessageException, SMPPTimeoutException

### Community 120 - "test_connection.py"
Cohesion: 0.16
Nodes (13): fixture, connected_connection(), connection(), mock_reader(), mock_writer(), MockEnquireLink, Unit tests for SMPP Connection module. Tests the async TCP connection handling,…, Mock asyncio StreamReader (+5 more)

### Community 121 - "ConcatenatedSMSHeader"
Cohesion: 0.23
Nodes (8): Get concatenated SMS information if this part has UDH. Returns:…, ConcatenatedSMSHeader, Concatenated SMS header information. Attributes: reference: Message reference…, Create from UDH element., Test 8-bit concatenated SMS UDH., Test 16-bit concatenated SMS UDH., Test UDH encoding and decoding., TestUDH

### Community 122 - "gsm_features_demo.py"
Cohesion: 0.17
Nodes (11): demo_compatibility(), demo_gsm7_encoding(), demo_message_segmentation(), demo_submit_sm_with_udh(), demo_udh_handling(), Demonstrate python-smpplib compatibility., Demo script showing GSM features usage. This demonstrates the new GSM 7-bit…, Demonstrate GSM 7-bit encoding. (+3 more)

### Community 123 - "make_parts"
Cohesion: 0.21
Nodes (8): make_parts(), Split a message into SMS parts for transmission. Args: message: Message text or…, Test message segmentation., Test message that fits in single SMS., Test GSM 7-bit message requiring multiple parts., Test binary message requiring multiple parts., Test UTF-16 encoding segmentation., TestMessageSegmentation

### Community 124 - "TestCreateRequestPDU"
Cohesion: 0.25
Nodes (5): Test create_request_pdu function., Test creating request PDU successfully., Test creating request PDU with response command ID., Test creating request PDU with invalid command ID., TestCreateRequestPDU

### Community 126 - "TestSMPPServerGenericNack"
Cohesion: 0.33
Nodes (4): Tests for generic_nack handling., Test successful generic_nack sending., Test generic_nack when exception occurs., TestSMPPServerGenericNack

### Community 127 - "TestGetPDUClass"
Cohesion: 0.25
Nodes (5): Test get_pdu_class function., Test getting PDU class for valid command ID., Test getting PDU class for invalid command ID., Test getting PDU class for zero command ID., TestGetPDUClass

### Community 128 - "UnbindResp"
Cohesion: 0.32
Nodes (5): UNBIND_RESP PDU - Response to unbind, UnbindResp, Test UnbindResp initialization., Test UnbindResp body encoding (should be empty)., TestUnbindResp

### Community 129 - "gsm/__init__.py"
Cohesion: 0.15
Nodes (10): GSM constants for compatibility with python-smpplib. Provides constants for…, GSM-specific functionality for SMPP implementation. This module provides GSM…, MessagePart, Message segmentation for SMS messages. Provides automatic message splitting for…, A single part of a segmented SMS message. Attributes: content: Message content…, Reassemble message parts into original message. Args: parts: List of…, Get the complete short message including UDH. Returns: Complete message bytes…, Get ESM class with UDH indicator if needed. Args: base_esm_class: Base ESM… (+2 more)

### Community 130 - ".get_message_encoding"
Cohesion: 0.33
Nodes (3): Get message text as string using specified or auto-detected encoding Args:…, Set message text from string using specified or auto-detected encoding Args:…, Get appropriate encoding for the message based on data_coding Returns: str:…

### Community 139 - "TestServiceTypeValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_service_type function., Test validating valid service types., Test validating a service type that's too long., Test validating a service type with non-printable characters., TestServiceTypeValidation

### Community 140 - "TestEsmClassValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_esm_class function., Test validating valid ESM class values., Test validating ESM class value below valid range., Test validating ESM class value above valid range., TestEsmClassValidation

### Community 141 - "TestSMPPClientUnbinding"
Cohesion: 0.33
Nodes (4): Tests for SMPPClient unbinding operations., Test unbind when exception occurs., Test unbind when handler raises exception., TestSMPPClientUnbinding

### Community 142 - "TestSMPPConnectionInit"
Cohesion: 0.33
Nodes (4): Test initialization with custom values, Test SMPPConnection initialization, Test initialization with default values, TestSMPPConnectionInit

### Community 143 - "TestContextManager"
Cohesion: 0.33
Nodes (4): Test async context manager functionality, Test successful context manager usage, Test context manager with exception, TestContextManager

### Community 144 - "TestBackgroundTasks"
Cohesion: 0.40
Nodes (3): Test background task functionality, Test enquire link loop, TestBackgroundTasks

### Community 148 - "protocol/constants.py"
Cohesion: 0.16
Nodes (17): CommandStatus, EsmClass, InterfaceVersion, NpiType, PriorityFlag, IntEnum, SMPP v3.4 Protocol Constants and Enumerations This module contains all the…, Numbering Plan Indicator (NPI) values (+9 more)

### Community 154 - "DataSm"
Cohesion: 0.14
Nodes (8): OptionalTag, Optional Parameter Tags for TLV (Tag-Length-Value) parameters, DataSm, DATA_SM PDU - Submit data using optional parameters, Get message payload from optional parameters, Set message payload as optional parameter, Get message text from payload, Set message text as payload

### Community 155 - "TestSMPPClientConnection"
Cohesion: 0.50
Nodes (3): Tests for SMPPClient connection management., Test disconnect when unbind fails., TestSMPPClientConnection

### Community 160 - "TestSMPPClientProperties"
Cohesion: 0.10
Nodes (11): Tests for SMPPClient properties., Test is_connected property when connected., Test is_connected property when no connection., Test is_connected property when connection exists but not connected., Test is_bound property when bound and connected., Test is_bound property when not bound., Test is_bound property when bound but not connected., Test bind_type property. (+3 more)

### Community 161 - "TestBindType"
Cohesion: 0.50
Nodes (3): Tests for BindType enum., Test BindType enum values., TestBindType

### Community 162 - "TestMemoryManagement"
Cohesion: 0.50
Nodes (3): Test memory management and limits, Test memory limit enforcement, TestMemoryManagement

### Community 168 - "TestPDUClasses"
Cohesion: 0.20
Nodes (6): Test PDU_CLASSES mapping., Test bind command mappings., Test message command mappings., Test session command mappings., Test that all mapped commands have valid classes., TestPDUClasses

## Knowledge Gaps
- **28 isolated node(s):** `smppai`, `Packaging`, `Releasing`, `body-leading-blank`, `footer-leading-blank` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1142 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SMPPPDUException` connect `SMPPPDUException` to `SMPPValidationException`, `TestCreatePDU`, `PDU`, `base.py`, `TestHelperFunctions`, `TestStandardMessagePDU`, `DataSm`, `smpp/__init__.py`, `TestCreateResponsePDU`, `Outbind`, `protocol/__init__.py`, `Exception`, `TestMessageDecoding`, `DeliverSm`, `TestMessageEncoding`, `TestCStringDecoding`, `TestIntegerEncoding`, `TestIntegerDecoding`, `TestCStringEncoding`, `TestFieldValidation`, `TestTLVPacking`, `TestTLVUnpacking`, `TestPDULengthCalculation`, `exceptions.py`, `.decode`, `test_factory.py`, `SMPPConnection`, `BindTransmitterResp`, `BindTransmitter`, `SMPPException`, `SubmitSmResp`, `bind.py`, `QuerySmResp`, `TestCreateTypedPDU`, `TestCreateRequestPDU`, `TestGetPDUClass`?**
  _High betweenness centrality (0.196) - this node is a cross-community bridge._
- **Why does `SMPPClient` connect `SMPPClient` to `TestSMPPClientSubmitSm`, `TestSMPPClientBinding`, `TestSMPPClientUnbinding`, `SMSClient`, `TestSMPPClientConnection`, `smpp/__init__.py`, `TestSMPPClientProperties`, `Exception`, `.test_set_event_handlers`, `exceptions.py`, `examples/client.py`, `._handle_pdu_received`, `SMPPConnection`, `TestSMPPClientContextManager`, `TestSMPPClientRepr`, `TestSMPPClientPDUHandling`, `TestSMPPClientInitialization`, `.disconnect`, `.handle_deliver_sm`, `TestSMPPClientWaitMethods`, `TestSMPPClientEnquireLink`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `SMPPServer` connect `SMPPServer` to `TestSMPPServerBindHandling`, `asyncio`, `test_server.py`, `.stop`, `SMSCServer`, `._handle_unbind_request`, `CommandId`, `._handle_client_pdu`, `smpp/__init__.py`, `ClientSession`, `DeliverSm`, `TestSMPPServerEdgeCases`, `exceptions.py`, `TestSMPPServerPDUHandling`, `examples/server.py`, `TestSMPPServerClientConnection`, `.test_set_event_handlers`, `TestSMPPServerUnbindHandling`, `._handle_client_connection`, `TestSMPPServerGenericNack`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `SMPPServer` (e.g. with `TestSMPPServerBindHandling` and `TestSMPPServerClientConnection`) actually correct?**
  _`SMPPServer` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SMPPClient` (e.g. with `TestSMPPClientBinding` and `TestSMPPClientConnection`) actually correct?**
  _`SMPPClient` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ClientSession` (e.g. with `TestShutdownPerformance` and `.test_shutdown_performance_with_many_clients()`) actually correct?**
  _`ClientSession` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `SMPPPDUException` (e.g. with `Outbind` and `StandardBindRequestPDU`) actually correct?**
  _`SMPPPDUException` has 34 INFERRED edges - model-reasoned connections that need verification._