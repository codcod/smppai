# Graph Report - smppai  (2026-09-22)

## Corpus Check
- 55 files · ~53,741 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 6, .lock 1)

## Summary
- 2208 nodes · 3936 edges · 145 communities (118 shown, 25 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 409 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6615d8a3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SMPPValidationException
- asyncio
- SMPPServer
- asyncio
- TestBindTransmitter
- protocol/__init__.py
- SMPPClient
- PDU
- constants.py
- SMPPPDUException
- TestSMPPServerSubmitSmHandling
- TLVParameter
- TestSMPPClientPDUHandling
- TestStandardMessagePDU
- .__init__
- SMSClient
- Set up Python with uv (composite action)
- test_server.py
- test_factory.py
- SMSCServer
- test_validation.py
- patch
- test_base.py
- .test_bind_commands
- TestAddressValidation
- ClientSession
- MockPDU
- exceptions.py
- TestEnquireLink
- TestOptionalParameterValidation
- TestPDU
- Outbind
- TestShutdownIntegration
- TestSMPPClientProperties
- QuerySm
- utils.py
- TestSMPPClientUnbinding
- TestMessageDecoding
- asyncio
- test_message.py
- ._force_disconnect_remaining_clients
- TestMessageEncoding
- TestEdgeCases
- test_session.py
- TestGenericNack
- .parse_delivery_receipt
- TestSubmitSmResp
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
- DataSmResp
- FieldValidator
- TestSMPPClientConnection
- TestAlertNotification
- TestTLVPacking
- TestTLVUnpacking
- TestPDULengthCalculation
- TestSubmitSmParametersValidation
- test_connection.py
- TestBindParametersValidation
- rules
- .process_message
- DataSm
- .decode
- .test_handle_connection_error_handler_exception
- TestCreateRequestPDU
- TestHelperFunctions
- TestRoundTripOperations
- TestSystemIdValidation
- TestRealWorldScenarios
- TestCreateErrorResponse
- examples/client.py
- SMPPConnection
- TestConnectionProperties
- test_bind.py
- test_client.py
- BindType
- TestBindRequestPDU
- TestCreateResponsePDU
- test_codec.py
- TestPasswordValidation
- TestSequenceNumberValidation
- TestSMPPServerProperties
- TestCommandUtilities
- TestContextManager
- .test_set_event_handlers
- TestSubmitSm
- TestBindingStates
- examples/server.py
- TestDeliverSmResp
- ._handle_client_pdu
- TestUnbind
- TestSMPPClientEdgeCases
- .__init__
- TestBindTransmitterResp
- TestServiceTypeValidation
- TestValidationRuleRegistry
- TestEsmClassValidation
- TestPriorityFlagValidation
- TestRegisteredDeliveryValidation
- TestFieldValidator
- TestSMPPServerEdgeCases
- .test_default_values
- PACKAGING.md
- .get_optional_parameter
- RELEASING.md
- TestBindTransceiver
- TestBindTransceiverResp
- .decode_body
- ConnectionState
- TestSequenceNumber
- TestSMPPServerInitialization
- SMPPException (base)
- TestSMPPServerMessageHandling
- .test_decode_body_insufficient_data_dest
- .test_decode_body_insufficient_data_message
- .create_for_invalid_pdu
- TestBindReceiver
- .test_get_message_encoding
- TestSMPPServerEnquireLinkHandling
- .test_create_error_response_unknown_request
- .test_decode_body_basic
- asyncio
- fixture
- unit/__init__.py
- unit/protocol/pdu/__init__.py
- Dependabot Configuration
- Bug Report Issue Template
- Documentation Issue Template
- Feature Request Issue Template
- smppai
- TestUnbindResp
- .validate
- .test_message_commands
- .test_session_commands
- .test_all_commands_have_classes

## God Nodes (most connected - your core abstractions)
1. `SMPPServer` - 149 edges
2. `SMPPClient` - 143 edges
3. `SMPPPDUException` - 101 edges
4. `ClientSession` - 88 edges
5. `CommandId` - 69 edges
6. `PDU` - 53 edges
7. `SMPPConnection` - 42 edges
8. `SMPPValidationException` - 42 edges
9. `SubmitSm` - 39 edges
10. `BindTransmitter` - 33 edges

## Surprising Connections (you probably didn't know these)
- `Pre-commit Hooks Configuration` --semantically_similar_to--> `Lint & Format Check Job`  [INFERRED] [semantically similar]
  .pre-commit-config.yaml → .github/workflows/ci.yml
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPClient (ESME)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md
- `CONTRIBUTING Guide` --semantically_similar_to--> `CI Workflow`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → .github/workflows/ci.yml
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPServer (SMSC)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md
- `TestSMPPClientBinding` --uses--> `SMPPInvalidStateException`  [INFERRED]
  tests/unit/client/test_client.py → src/smpp/exceptions.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI Workflow Pipeline Stages** — github_workflows_ci_lint, github_workflows_ci_type_check, github_workflows_ci_security, github_workflows_ci_unit_tests, github_workflows_ci_integration_test, github_workflows_ci_build, github_workflows_ci_coverage_report, github_workflows_ci_all_checks [EXTRACTED 1.00]
- **Shared Quality-Check Toolchain (ruff/mypy/pytest/bandit)** — pre_commit_config, github_workflows_ci_lint, contributing, github_pull_request_template [INFERRED 0.85]
- **SMPP Exception Hierarchy** — readme_smppexception, readme_smppconnectionexception, readme_smppbindexception, readme_smpptimeoutexception, readme_smppmessageexception [INFERRED 0.85]

## Communities (145 total, 25 thin omitted)

### Community 0 - "SMPPValidationException"
Cohesion: 0.09
Nodes (36): Exception raised for validation errors., SMPPValidationException, is_response_command(), Check if a command ID represents a response PDU, SMPP Protocol Validation This module provides validation functions for SMPP…, Validate SMPP system ID field. Args: system_id: System ID to validate Raises:…, Validate SMPP password field. Args: password: Password to validate Raises:…, Validate SMPP address field with TON and NPI. Args: address: Address to… (+28 more)

### Community 1 - "asyncio"
Cohesion: 0.06
Nodes (26): asyncio, Tests for deliver_sm functionality., Test successful message delivery., Test message delivery when target not found., Test message delivery when target not bound., Test message delivery when target has wrong bind type., Test message delivery to transceiver., Tests for server start/stop functionality. (+18 more)

### Community 2 - "SMPPServer"
Cohesion: 0.04
Nodes (32): Event, create_simple_server(), Create a simple SMPP server with minimal configuration. Args: host: Server bind…, Set the grace period for shutdown notifications, Initialize SMPP Server Args: host: Server bind address port: Server bind port…, Set the delay after grace period before final shutdown, Get current shutdown configuration, Configure all shutdown parameters with comprehensive validation. Args:… (+24 more)

### Community 3 - "asyncio"
Cohesion: 0.04
Nodes (38): Exception raised when operations timeout., SMPPTimeoutException, asyncio, Tests for SMPPClient binding operations., Test successful bind as transmitter., Test successful bind as receiver., Test successful bind as transceiver., Test bind when not connected. (+30 more)

### Community 4 - "TestBindTransmitter"
Cohesion: 0.17
Nodes (7): Test decode with insufficient data., Test BindTransmitter PDU., Test BindTransmitter initialization with defaults., Test BindTransmitter with custom values., Test BindTransmitter body encoding., Test BindTransmitter body decoding., TestBindTransmitter

### Community 5 - "protocol/__init__.py"
Cohesion: 0.07
Nodes (75): SMPP AI - Async SMPP Protocol v3.4 Implementation A comprehensive, async…, CommandId, MessageState, SMPP Command IDs as defined in SMPP v3.4 specification, Message State values for delivery receipts, SMPP Protocol Module This module contains the core SMPP protocol implementation…, EmptyBodyPDU, Base class for response PDUs. Response PDUs are sent by SMPP servers to clients… (+67 more)

### Community 6 - "SMPPClient"
Cohesion: 0.04
Nodes (29): Exception, Check if client is connected to SMSC, Check if client is bound to SMSC, Disconnect from SMSC server, Bind as transmitter (can send SMS), Bind as receiver (can receive SMS and delivery receipts), Bind as transceiver (can send and receive SMS), Send enquire_link to test connection Args: timeout: Response timeout Returns:… (+21 more)

### Community 7 - "PDU"
Cohesion: 0.06
Nodes (22): ABC, PDU, Abstract base class for all SMPP PDUs. This class provides the common…, Encode PDU body to bytes. Must be implemented by subclasses to encode the PDU-…, Decode PDU body from bytes. Must be implemented by subclasses to decode the…, Encode complete PDU to bytes. Returns: The complete encoded PDU including…, Decode PDU from bytes. Args: data: The byte data to decode Returns: The decoded…, Add optional parameter. If a parameter with the same tag already exists, it… (+14 more)

### Community 8 - "constants.py"
Cohesion: 0.09
Nodes (25): CommandStatus, EsmClass, get_request_command_id(), get_response_command_id(), InterfaceVersion, NpiType, OptionalTag, PriorityFlag (+17 more)

### Community 9 - "SMPPPDUException"
Cohesion: 0.04
Nodes (63): Exception raised for PDU-related errors., SMPPPDUException, calculate_pdu_length(), decode_cstring(), decode_integer(), decode_message_with_encoding(), encode_cstring(), encode_integer() (+55 more)

### Community 10 - "TestSMPPServerSubmitSmHandling"
Cohesion: 0.11
Nodes (10): Test submit_sm from receiver (wrong bind type)., Test submit_sm with custom message handler., Test submit_sm when message handler raises exception., Test submit_sm when send response fails., Test submit_sm when general exception occurs., Tests for submit_sm request handling., Test successful submit_sm from transmitter., Test successful submit_sm from transceiver. (+2 more)

### Community 11 - "TLVParameter"
Cohesion: 0.08
Nodes (17): Tag-Length-Value parameter for optional parameters. TLV parameters are used in…, Initialize TLV parameter. Args: tag: Parameter tag identifier value: Parameter…, Encode TLV parameter to bytes. Returns: The encoded TLV parameter as bytes, TLVParameter, Test TLV parameter string representation., Test TLV parameter equality., Test TLVParameter class., Test TLV parameter hashing. (+9 more)

### Community 12 - "TestSMPPClientPDUHandling"
Cohesion: 0.06
Nodes (17): Test handling deliver_sm when handler raises exception., Test sending deliver_sm_resp., Test sending deliver_sm_resp when exception occurs., Test sending enquire_link_resp., Test sending enquire_link_resp when exception occurs., Test handling unbind request., Test handling unbind request when exception occurs., Test handling unbind request when handler raises exception. (+9 more)

### Community 13 - "TestStandardMessagePDU"
Cohesion: 0.13
Nodes (14): Test decode with insufficient data for source address fields., Test delivery receipt request checking., Test StandardMessagePDU base class., Test setting delivery receipt request., Test Unicode message detection., Test StandardMessagePDU body encoding with basic data., Test encoding with message too long., TestStandardMessagePDU (+6 more)

### Community 15 - "SMSClient"
Cohesion: 0.09
Nodes (15): Exception, Check if this message is a server shutdown notification., Handle server shutdown notifications with appropriate responses., Thread-safe graceful shutdown process., Handle connection lost event with enhanced shutdown awareness., Handle unbind event with enhanced logging., Connect to SMSC and bind with enhanced shutdown awareness., Send a command to the server (for testing enhanced shutdown). Uses proper SMPP… (+7 more)

### Community 16 - "Set up Python with uv (composite action)"
Cohesion: 0.11
Nodes (28): CHANGELOG, CONTRIBUTING Guide, Conventional Commits, smppai Project Structure (client/server/protocol/transport/config), Semantic Release / Automated Versioning, Examples README, Set up Python with uv (composite action), Pull Request Template (+20 more)

### Community 17 - "test_server.py"
Cohesion: 0.07
Nodes (19): Unit tests for SMPP Server implementation This module contains tests for the…, Tests for generic_nack handling., Test successful generic_nack sending., Test generic_nack when exception occurs., Tests for server stop with client disconnect exceptions., Test server stop when client disconnect raises exception., Tests for custom authentication., Test custom authentication that succeeds. (+11 more)

### Community 18 - "test_factory.py"
Cohesion: 0.06
Nodes (21): Unit tests for SMPP PDU factory., Test creating PDU with invalid command ID., Test creating PDU with invalid parameters., Test create_typed_pdu function., Test creating typed PDU successfully., Test creating typed PDU with type mismatch., Test creating typed PDU with invalid command ID., Test decode_pdu function. (+13 more)

### Community 19 - "SMSCServer"
Cohesion: 0.10
Nodes (12): Set up all server event handlers., Authenticate client credentials with enhanced logging. Args: system_id: Client…, Handle new client connection with enhanced logging., Handle client disconnection with enhanced logging., Handle successful client bind with enhanced logging., Example SMSC server using SMPP with enhanced shutdown capabilities. Features: -…, Start the SMSC server., Stop the SMSC server with enhanced shutdown. (+4 more)

### Community 20 - "test_validation.py"
Cohesion: 0.14
Nodes (9): Unit tests for SMPP Protocol Validation functions. Tests all validation…, Tests for validate_data_coding function., Test validating valid data coding schemes., Test validating invalid data coding schemes., Tests for validate_command_id function., Test validating valid command IDs., Test validating invalid command IDs., TestCommandIdValidation (+1 more)

### Community 21 - "patch"
Cohesion: 0.10
Nodes (15): patch, Test that initialization creates SMPPConnection., Test PDU handling through _handle_client_pdu method., Test handling of BindTransmitter PDU through PDU handler., Test handling of BindReceiver PDU through PDU handler., Test handling of BindTransceiver PDU through PDU handler., Test handling of Unbind PDU through PDU handler., Test handling of SubmitSm PDU through PDU handler. (+7 more)

### Community 22 - "test_base.py"
Cohesion: 0.17
Nodes (5): Unit tests for SMPP PDU base classes., Test MessagePDU base class., Test MessagePDU default values., Test MessagePDU with custom values., TestMessagePDU

### Community 24 - "TestAddressValidation"
Cohesion: 0.08
Nodes (13): Tests for validate_address function., Test validating a valid international ISDN address., Test validating a valid national ISDN address., Test validating a valid alphanumeric address., Test validating an address that's too long., Test validating an address with invalid TON., Test validating an address with invalid NPI., Test validating international ISDN address with invalid format. (+5 more)

### Community 25 - "ClientSession"
Cohesion: 0.07
Nodes (23): ClientSession, Get list of all client sessions, Get list of bound client sessions, Represents a connected SMPP client session, Tests for ClientSession dataclass., Test ClientSession initialization with default values., Test ClientSession initialization with custom values., Tests for bind request handling. (+15 more)

### Community 26 - "MockPDU"
Cohesion: 0.14
Nodes (9): MockPDU, Test PDU sending functionality, Test sending PDU when not connected, Test sending PDU without waiting for response, Test sending PDU with response, Test PDU response timeout, Return mock encoded PDU, Test send data failure (+1 more)

### Community 27 - "exceptions.py"
Cohesion: 0.06
Nodes (38): SMPP Client (ESME) Implementation This module provides a comprehensive async…, Connect to SMSC server, Perform bind operation, Submit SMS message Args: source_addr: Source address (sender) destination_addr:…, async_handle_smpp_error(), handle_smpp_error(), wrapper(), Any (+30 more)

### Community 28 - "TestEnquireLink"
Cohesion: 0.14
Nodes (8): Test EnquireLink PDU., Test EnquireLink initialization., Test that custom command_id is preserved., Test EnquireLink body encoding (should be empty)., Test EnquireLink body decoding (should handle empty body)., Test that sequence number is auto-generated., Test custom sequence number., TestEnquireLink

### Community 29 - "TestOptionalParameterValidation"
Cohesion: 0.09
Nodes (12): Tests for validate_optional_parameter function., Test validating valid optional parameters., Test validating optional parameter with negative tag., Test validating optional parameter with tag too large., Test validating optional parameter with value too long., Test validating valid receipted message ID., Test validating receipted message ID with non-printable characters., Test validating receipted message ID with invalid ASCII. (+4 more)

### Community 30 - "TestPDU"
Cohesion: 0.10
Nodes (8): Initialize PDU after creation., Generate a unique sequence number. Returns: A unique sequence number between 1…, Test sequence number generation., Test sequence number is within valid bounds., Test that __post_init__ generates sequence number when 0., Test that __post_init__ preserves non-zero sequence number., Test PDU with custom values., TestPDU

### Community 31 - "Outbind"
Cohesion: 0.08
Nodes (13): Outbind, OUTBIND PDU - SMSC initiated bind request, Encode outbind body with system_id and password only, Decode outbind body with system_id and password only, Validate outbind fields Raises: SMPPPDUException: If validation fails, Test Outbind initialization., Test Outbind body encoding., Test Outbind body decoding. (+5 more)

### Community 32 - "TestShutdownIntegration"
Cohesion: 0.12
Nodes (14): asyncio, fixture, integration, performance, Integration tests for SMPP Server and Client shutdown interaction These tests…, Test that client can reconnect after server restart., Integration tests for server-client shutdown interaction, Performance tests for shutdown operations (+6 more)

### Community 33 - "TestSMPPClientProperties"
Cohesion: 0.10
Nodes (11): Tests for SMPPClient properties., Test is_connected property when connected., Test is_connected property when no connection., Test is_connected property when connection exists but not connected., Test is_bound property when bound and connected., Test is_bound property when not bound., Test is_bound property when bound but not connected., Test bind_type property. (+3 more)

### Community 34 - "QuerySm"
Cohesion: 0.14
Nodes (9): Base class for request PDUs. Request PDUs are sent by SMPP clients to servers…, RequestPDU, QuerySm, Validate alert_notification fields, Validate data_sm fields, Validate data_sm_resp fields, QUERY_SM PDU - Query status of a submitted message, Validate query_sm fields (+1 more)

### Community 35 - "utils.py"
Cohesion: 0.11
Nodes (19): calculate_message_length(), format_smpp_time(), generate_message_id(), is_valid_system_id(), mask_sensitive_data(), normalize_phone_number(), parse_smpp_time(), SMPP Utilities Module This module provides basic utility functions and helper… (+11 more)

### Community 36 - "TestSMPPClientUnbinding"
Cohesion: 0.14
Nodes (8): Tests for SMPPClient unbinding operations., Test successful unbind., Test unbind when not bound., Test unbind when connection is None but client state thinks it's bound., Test unbind with error response., Test unbind when exception occurs., Test unbind when handler raises exception., TestSMPPClientUnbinding

### Community 37 - "TestMessageDecoding"
Cohesion: 0.10
Nodes (11): Tests for decode_message_with_encoding function., Test decoding with default data coding., Test decoding with ASCII data coding., Test decoding with Latin-1 data coding., Test decoding with UCS2 data coding., Test decoding with octet unspecified data coding., Test decoding with unknown data coding (should fallback to UTF-8)., Test decoding Unicode with UTF-8 fallback. (+3 more)

### Community 38 - "asyncio"
Cohesion: 0.07
Nodes (21): asyncio, Test connection establishment and teardown, Test successful connection, Test connect when already connected, Test connection timeout, Test connection failure, Test disconnect when not connected, Test successful disconnection (+13 more)

### Community 39 - "test_message.py"
Cohesion: 0.22
Nodes (5): Unit tests for SMPP message PDUs., Test DeliverSm initialization., Test DeliverSm with custom values., Test delivery receipt detection., TestDeliverSm

### Community 40 - "._force_disconnect_remaining_clients"
Cohesion: 0.25
Nodes (4): Force disconnect all remaining clients., Send unbind requests to all bound clients., Force disconnect all clients., Send unbind request to a client

### Community 41 - "TestMessageEncoding"
Cohesion: 0.11
Nodes (10): Tests for encode_message_with_encoding function., Test encoding with default data coding., Test encoding with ASCII data coding., Test encoding with Latin-1 data coding., Test encoding with UCS2 data coding., Test encoding with octet unspecified data coding., Test encoding with unknown data coding (should fallback to UTF-8)., Test encoding Unicode with UTF-8 fallback. (+2 more)

### Community 42 - "TestEdgeCases"
Cohesion: 0.11
Nodes (10): Tests for edge cases and boundary conditions., Test system ID at exact boundary length., Test password at exact boundary length., Test address at exact boundary length., Test service type at exact boundary length., Test message at exact boundary length for GSM 7-bit., Test message at exact general boundary length., Test sequence number at boundary values. (+2 more)

### Community 43 - "test_session.py"
Cohesion: 0.18
Nodes (6): Unit tests for SMPP session PDUs., Test QuerySm initialization., Test QuerySm with custom values., Test QuerySm body encoding., Test QuerySm body decoding., TestQuerySm

### Community 44 - "TestGenericNack"
Cohesion: 0.17
Nodes (7): Test GenericNack body encoding (should be empty)., Test creating GenericNack for invalid PDU., Test creating GenericNack with error message., Test GenericNack PDU., Test GenericNack initialization., Test GenericNack with custom values., TestGenericNack

### Community 45 - ".parse_delivery_receipt"
Cohesion: 0.17
Nodes (6): Get message text as string using specified or auto-detected encoding Args:…, Set message text from string using specified or auto-detected encoding Args:…, Get appropriate encoding for the message based on data_coding Returns: str:…, Check if this is a delivery receipt Returns: bool: True if this is a delivery…, Check if this is a mobile originated message Returns: bool: True if this is a…, Parse delivery receipt message into structured data Returns: dict: Parsed…

### Community 46 - "TestSubmitSmResp"
Cohesion: 0.14
Nodes (8): Test SubmitSmResp PDU., Test SubmitSmResp initialization., Test SubmitSmResp with custom values., Test SubmitSmResp body encoding., Test SubmitSmResp body encoding with empty message_id., Test SubmitSmResp body decoding., Test SubmitSmResp body decoding with empty message_id., TestSubmitSmResp

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

### Community 57 - "DataSmResp"
Cohesion: 0.13
Nodes (9): DataSmResp, DATA_SM_RESP PDU - Response to data_sm, Encode data_sm_resp body, Decode data_sm_resp body, Test DataSmResp initialization., Test DataSmResp with custom values., Test DataSmResp body encoding., Test DataSmResp body decoding. (+1 more)

### Community 58 - "FieldValidator"
Cohesion: 0.16
Nodes (11): FieldValidator, get_validation_rule(), Any, Clear validation cache., Register a custom validation rule for a field. Args: field_name: Name of the…, Get validation rule for a field. Args: field_name: Name of the field Returns:…, Enhanced field validator with caching and custom rules., Validate field with result caching. Args: field_name: Name of the field value:… (+3 more)

### Community 59 - "TestSMPPClientConnection"
Cohesion: 0.14
Nodes (8): Tests for SMPPClient connection management., Test successful connection., Test connect when no connection object., Test connect when already connected., Test successful disconnection., Test disconnect when not connected., Test disconnect when unbind fails., TestSMPPClientConnection

### Community 60 - "TestAlertNotification"
Cohesion: 0.17
Nodes (7): Test AlertNotification PDU., Test AlertNotification initialization., Test AlertNotification with custom values., Test AlertNotification body encoding., Test AlertNotification body decoding., Test decode with insufficient data., TestAlertNotification

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

### Community 65 - "test_connection.py"
Cohesion: 0.12
Nodes (16): connected_connection(), connection(), mock_reader(), mock_writer(), MockEnquireLink, fixture, Unit tests for SMPP Connection module. Tests the async TCP connection handling,…, Mock asyncio StreamReader (+8 more)

### Community 66 - "TestBindParametersValidation"
Cohesion: 0.17
Nodes (7): Tests for validate_bind_parameters function., Test validating valid bind parameters., Test validating bind parameters with system type too long., Test validating bind parameters with invalid interface version., Test validating bind parameters with valid interface versions., Test validating bind parameters with invalid address range., TestBindParametersValidation

### Community 67 - "rules"
Cohesion: 0.15
Nodes (12): extends, rules, body-leading-blank, footer-leading-blank, header-max-length, scope-empty, scope-enum, subject-case (+4 more)

### Community 68 - ".process_message"
Cohesion: 0.12
Nodes (8): Handle SMS message from client with enhanced logging and commands., Process received message with enhanced command support., Send a response back to the client., Demonstrate the enhanced shutdown feature., Send delivery receipt to client., Broadcast message to all connected receiver clients., Send broadcast message to a specific client., Get comprehensive server statistics.

### Community 69 - "DataSm"
Cohesion: 0.13
Nodes (9): DataSm, DATA_SM PDU - Submit data using optional parameters, Get message payload from optional parameters, Set message payload as optional parameter, Get message text from payload, Set message text as payload, Test DataSm initialization., Test DataSm with custom values. (+1 more)

### Community 70 - ".decode"
Cohesion: 0.17
Nodes (6): Decode TLV parameter from bytes. Args: data: The byte data to decode from…, Test decoding with insufficient header data., Test decoding with insufficient value data., Test TLV parameter decoding., Test TLV parameter decoding with offset., Test decoding TLV with empty value.

### Community 71 - ".test_handle_connection_error_handler_exception"
Cohesion: 0.20
Nodes (5): Test state change handler exception handling, Test connection error handling, Test connection error handler exception, failing_handler(), TestErrorHandling

### Community 72 - "TestCreateRequestPDU"
Cohesion: 0.25
Nodes (5): Test create_request_pdu function., Test creating request PDU successfully., Test creating request PDU with response command ID., Test creating request PDU with invalid command ID., TestCreateRequestPDU

### Community 73 - "TestHelperFunctions"
Cohesion: 0.17
Nodes (7): Test helper factory functions., Test create_bind_pdu helper., Test create_bind_pdu with invalid type., Test create_submit_sm_pdu helper., Test create_enquire_link_pdu helper., Test create_generic_nack_pdu helper., TestHelperFunctions

### Community 74 - "TestRoundTripOperations"
Cohesion: 0.17
Nodes (7): Tests for round-trip encoding/decoding operations., Test encoding and decoding C-strings., Test encoding and decoding integers., Test encoding and decoding messages with UTF-8., Test encoding and decoding messages with UCS2., Test packing and unpacking TLV parameters., TestRoundTripOperations

### Community 75 - "TestSystemIdValidation"
Cohesion: 0.17
Nodes (7): Test validating a system ID that's too long., Test validating a system ID with invalid characters., Test that underscores are allowed in system ID., Tests for validate_system_id function., Test validating a valid system ID., Test validating an empty system ID., TestSystemIdValidation

### Community 76 - "TestRealWorldScenarios"
Cohesion: 0.17
Nodes (7): Tests for real-world usage scenarios., Test complete bind parameter validation flow., Test complete submit_sm parameter validation flow., Test alphanumeric addressing validation., Test Unicode message validation., Test that empty fields are allowed where appropriate., TestRealWorldScenarios

### Community 77 - "TestCreateErrorResponse"
Cohesion: 0.25
Nodes (5): Test create_error_response function., Test creating basic error response., Test creating error response with message., Test creating error response for response PDU., TestCreateErrorResponse

### Community 78 - "examples/client.py"
Cohesion: 0.18
Nodes (9): interactive_client_example(), main(), monitor_messages_example(), SMPP Client Example This example demonstrates how to use the SMPP client to…, Main example function demonstrating enhanced shutdown handling. Features…, Simple example of sending one SMS with enhanced shutdown awareness., Example of monitoring incoming messages with enhanced shutdown handling. This…, Interactive client that can send commands to test enhanced shutdown. (+1 more)

### Community 79 - "SMPPConnection"
Cohesion: 0.08
Nodes (17): Initialize SMPP Client Args: host: SMSC server hostname or IP port: SMSC server…, Exception, Check if connection is established, Check if connection is bound, Set connection state and trigger state change event, Get next sequence number, Establish TCP connection, Background task to receive and process PDUs (+9 more)

### Community 80 - "TestConnectionProperties"
Cohesion: 0.18
Nodes (6): Test connection properties and state management, Test state property getter, Test is_connected property, Test is_bound property, Test state change with handler, TestConnectionProperties

### Community 81 - "test_bind.py"
Cohesion: 0.33
Nodes (4): Unit tests for SMPP bind PDUs., Test BindReceiverResp PDU., Test BindReceiverResp initialization., TestBindReceiverResp

### Community 82 - "test_client.py"
Cohesion: 0.06
Nodes (20): Unit tests for SMPP Client implementation. Tests all functionality of the…, Tests for SMPPClient context manager., Test successful context manager usage., Test context manager when exception occurs., Tests for SMPPClient string representation., Test string representation., Test string representation when bound., Tests for SMPPClient event handlers. (+12 more)

### Community 83 - "BindType"
Cohesion: 0.14
Nodes (9): Handle successful bind with enhanced logging., BindType, Enum, Get current bind type, SMPP Client Module This module provides a comprehensive async SMPP client…, Tests for SMPPClient connection lost handling., Test handling connection lost., Test handling connection lost when handler raises exception. (+1 more)

### Community 84 - "TestBindRequestPDU"
Cohesion: 0.20
Nodes (4): Test BindRequestPDU base class., Test BindRequestPDU default values., Test BindRequestPDU with custom values., TestBindRequestPDU

### Community 85 - "TestCreateResponsePDU"
Cohesion: 0.20
Nodes (6): Test create_response_pdu function., Test creating response PDU successfully., Test creating response PDU with default status., Test creating response PDU from response command ID., Test creating response PDU for invalid command., TestCreateResponsePDU

### Community 86 - "test_codec.py"
Cohesion: 0.20
Nodes (6): Unit tests for SMPP Protocol Codec utilities. Tests all encoding/decoding…, Tests for edge cases and boundary conditions., Test handling of maximum values., Test handling of zero values., Test boundary length conditions., TestEdgeCases

### Community 87 - "TestPasswordValidation"
Cohesion: 0.20
Nodes (6): Tests for validate_password function., Test validating valid passwords., Test validating a password that's too long., Test validating a password with non-printable characters., Test that special printable characters are allowed., TestPasswordValidation

### Community 88 - "TestSequenceNumberValidation"
Cohesion: 0.20
Nodes (6): Tests for validate_sequence_number function., Test validating valid sequence numbers., Test validating sequence number zero., Test validating negative sequence number., Test validating sequence number that's too large., TestSequenceNumberValidation

### Community 89 - "TestSMPPServerProperties"
Cohesion: 0.20
Nodes (6): Tests for SMPPServer properties., Test that server is not running initially., Test that server reports running when started., Test client count when no clients connected., Test client count with connected clients., TestSMPPServerProperties

### Community 90 - "TestCommandUtilities"
Cohesion: 0.25
Nodes (5): Test command utility functions., Test is_command_supported function., Test get_pdu_name function., Test get_pdu_name for unknown command., TestCommandUtilities

### Community 91 - "TestContextManager"
Cohesion: 0.33
Nodes (4): Test async context manager functionality, Test successful context manager usage, Test context manager with exception, TestContextManager

### Community 92 - ".test_set_event_handlers"
Cohesion: 0.20
Nodes (4): Tests for server event handler initialization., Test that event handlers are initialized to None., Test setting custom event handlers., TestSMPPServerEventHandlers

### Community 93 - "TestSubmitSm"
Cohesion: 0.29
Nodes (4): Test SubmitSm initialization with defaults., Test SubmitSm with custom values., Test that custom command_id is preserved., TestSubmitSm

### Community 94 - "TestBindingStates"
Cohesion: 0.20
Nodes (6): Test connection binding state management, Test setting transmitter bound state, Test setting receiver bound state, Test setting transceiver bound state, Test setting invalid bound state, TestBindingStates

### Community 95 - "examples/server.py"
Cohesion: 0.18
Nodes (12): cleanup_background_tasks(), main(), SMPP Server Example This example demonstrates how to use the SMPP server with…, Main server function demonstrating enhanced shutdown capabilities. Features…, Monitor and log server statistics periodically., Send periodic broadcast messages to demonstrate server capabilities., Clean up background tasks gracefully., Simple server example showcasing async context manager with enhanced shutdown.… (+4 more)

### Community 96 - "TestDeliverSmResp"
Cohesion: 0.20
Nodes (6): Test DeliverSmResp PDU., Test DeliverSmResp initialization., Test DeliverSmResp with custom values., Test DeliverSmResp body encoding., Test DeliverSmResp body decoding., TestDeliverSmResp

### Community 97 - "._handle_client_pdu"
Cohesion: 0.09
Nodes (13): Exception, StreamReader, StreamWriter, Handle new client connection, Handle client disconnection, Handle PDU received from client, Handle bind request from client, Handle unbind request from client (+5 more)

### Community 98 - "TestUnbind"
Cohesion: 0.29
Nodes (4): Test Unbind initialization., Test Unbind body encoding (should be empty)., Test Unbind body decoding (should handle empty body)., TestUnbind

### Community 99 - "TestSMPPClientEdgeCases"
Cohesion: 0.20
Nodes (6): Tests for edge cases and boundary conditions., Test submit_sm with Unicode message., Test submit_sm with message at boundary length., Test connection state property during state transitions., Test binding sequence (bind, unbind, rebind)., TestSMPPClientEdgeCases

### Community 100 - ".__init__"
Cohesion: 0.50
Nodes (3): StreamReader, StreamWriter, Initialize SMPP connection Args: host: Remote host address port: Remote port…

### Community 101 - "TestBindTransmitterResp"
Cohesion: 0.20
Nodes (6): Test BindTransmitterResp PDU., Test BindTransmitterResp initialization., Test BindTransmitterResp with custom values., Test BindTransmitterResp body encoding., Test BindTransmitterResp body decoding., TestBindTransmitterResp

### Community 102 - "TestServiceTypeValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_service_type function., Test validating valid service types., Test validating a service type that's too long., Test validating a service type with non-printable characters., TestServiceTypeValidation

### Community 103 - "TestValidationRuleRegistry"
Cohesion: 0.25
Nodes (5): Tests for validation rule registry functions., Test registering a custom validation rule., Test getting a non-existent validation rule., Test overwriting an existing validation rule., TestValidationRuleRegistry

### Community 104 - "TestEsmClassValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_esm_class function., Test validating valid ESM class values., Test validating ESM class value below valid range., Test validating ESM class value above valid range., TestEsmClassValidation

### Community 105 - "TestPriorityFlagValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_priority_flag function., Test validating valid priority flag values., Test validating priority flag value below valid range., Test validating priority flag value above valid range., TestPriorityFlagValidation

### Community 106 - "TestRegisteredDeliveryValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_registered_delivery function., Test validating valid registered delivery values., Test validating registered delivery value below valid range., Test validating registered delivery value above valid range., TestRegisteredDeliveryValidation

### Community 107 - "TestFieldValidator"
Cohesion: 0.25
Nodes (5): Tests for FieldValidator class., Test FieldValidator initialization., Test validation with caching., Test clearing validation cache., TestFieldValidator

### Community 108 - "TestSMPPServerEdgeCases"
Cohesion: 0.20
Nodes (6): Tests for edge cases and error scenarios., Test client count after various operations., Test message ID counter behavior., Test getting bound clients with mixed session states., Test client connection when peer info is not available., TestSMPPServerEdgeCases

### Community 111 - ".get_optional_parameter"
Cohesion: 0.33
Nodes (3): Get optional parameter by tag. Args: tag: The parameter tag to search for…, Get optional parameter value by tag. Args: tag: The parameter tag to search for…, Check if optional parameter exists. Args: tag: The parameter tag to check for…

### Community 113 - "TestBindTransceiver"
Cohesion: 0.50
Nodes (3): Test BindTransceiver PDU., Test BindTransceiver initialization., TestBindTransceiver

### Community 114 - "TestBindTransceiverResp"
Cohesion: 0.50
Nodes (3): Test BindTransceiverResp PDU., Test BindTransceiverResp initialization., TestBindTransceiverResp

### Community 116 - "ConnectionState"
Cohesion: 0.14
Nodes (9): ConnectionState, Enum, SMPP Connection States, Get current connection state, SMPP Transport Layer This module provides the transport layer abstraction for…, Test initialization with custom values, Test SMPPConnection initialization, Test initialization with default values (+1 more)

### Community 117 - "TestSequenceNumber"
Cohesion: 0.33
Nodes (4): Test sequence number generation, Test sequence number generation, Test sequence number wraparound, TestSequenceNumber

### Community 118 - "TestSMPPServerInitialization"
Cohesion: 0.25
Nodes (5): Test default authentication method., Tests for SMPPServer initialization., Test server initialization with default values., Test server initialization with custom values., TestSMPPServerInitialization

### Community 119 - "SMPPException (base)"
Cohesion: 0.40
Nodes (5): SMPPBindException, SMPPConnectionException, SMPPException (base), SMPPMessageException, SMPPTimeoutException

### Community 120 - "TestSMPPServerMessageHandling"
Cohesion: 0.25
Nodes (5): Tests for server message handling., Test message ID generation., Test getting all client sessions., Test getting only bound client sessions., TestSMPPServerMessageHandling

### Community 124 - "TestBindReceiver"
Cohesion: 0.33
Nodes (4): Test BindReceiver PDU., Test BindReceiver initialization., Test that custom command_id is preserved., TestBindReceiver

### Community 126 - "TestSMPPServerEnquireLinkHandling"
Cohesion: 0.33
Nodes (4): Tests for enquire_link request handling., Test successful enquire_link request., Test enquire_link when exception occurs., TestSMPPServerEnquireLinkHandling

### Community 139 - "TestUnbindResp"
Cohesion: 0.40
Nodes (3): Test UnbindResp initialization., Test UnbindResp body encoding (should be empty)., TestUnbindResp

## Knowledge Gaps
- **28 isolated node(s):** `Packaging`, `Releasing`, `smppai`, `body-leading-blank`, `footer-leading-blank` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1093 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SMPPPDUException` connect `SMPPPDUException` to `SMPPValidationException`, `TestBindTransmitter`, `protocol/__init__.py`, `PDU`, `TLVParameter`, `TestStandardMessagePDU`, `.validate`, `test_factory.py`, `exceptions.py`, `Outbind`, `QuerySm`, `TestMessageDecoding`, `asyncio`, `TestMessageEncoding`, `.parse_delivery_receipt`, `TestQuerySmResp`, `TestCStringDecoding`, `TestIntegerEncoding`, `TestIntegerDecoding`, `TestCStringEncoding`, `TestFieldValidation`, `DataSmResp`, `TestAlertNotification`, `TestTLVPacking`, `TestTLVUnpacking`, `TestPDULengthCalculation`, `DataSm`, `.decode`, `TestCreateRequestPDU`, `TestHelperFunctions`, `TestCreateErrorResponse`, `SMPPConnection`, `TestCreateResponsePDU`, `TestCommandUtilities`?**
  _High betweenness centrality (0.233) - this node is a cross-community bridge._
- **Why does `SMPPServer` connect `SMPPServer` to `asyncio`, `protocol/__init__.py`, `constants.py`, `TestSMPPServerSubmitSmHandling`, `test_server.py`, `SMSCServer`, `patch`, `ClientSession`, `exceptions.py`, `._force_disconnect_remaining_clients`, `.process_message`, `TestSMPPServerProperties`, `.test_set_event_handlers`, `examples/server.py`, `._handle_client_pdu`, `TestSMPPServerEdgeCases`, `TestSMPPServerInitialization`, `TestSMPPServerMessageHandling`, `TestSMPPServerEnquireLinkHandling`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Why does `SMPPClient` connect `SMPPClient` to `TestSMPPClientProperties`, `asyncio`, `TestSMPPClientEdgeCases`, `protocol/__init__.py`, `TestSMPPClientUnbinding`, `TestSMPPClientConnection`, `TestSMPPClientPDUHandling`, `examples/client.py`, `SMSClient`, `SMPPConnection`, `test_client.py`, `BindType`, `ConnectionState`, `patch`, `exceptions.py`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `SMPPServer` (e.g. with `SMPPException` and `TestSMPPServerBindHandling`) actually correct?**
  _`SMPPServer` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `SMPPClient` (e.g. with `SMPPBindException` and `SMPPConnectionException`) actually correct?**
  _`SMPPClient` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `SMPPPDUException` (e.g. with `BindRequestPDU` and `BindResponsePDU`) actually correct?**
  _`SMPPPDUException` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ClientSession` (e.g. with `.test_shutdown_performance_with_many_clients()` and `TestClientSession`) actually correct?**
  _`ClientSession` has 13 INFERRED edges - model-reasoned connections that need verification._