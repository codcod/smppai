# Graph Report - smppai  (2026-09-23)

## Corpus Check
- 55 files · ~53,223 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 7, .lock 1)

## Summary
- 2290 nodes · 4047 edges · 157 communities (120 shown, 35 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 434 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef701578`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SMPPValidationException
- .__init__
- SMPPServer
- asyncio
- TestCreatePDU
- SMPPPDUException
- SMPPClient
- PDU
- ClientSession
- TestSystemIdValidation
- .validate
- TLVParameter
- TestSMPPServerStartStop
- TestStandardMessagePDU
- .decode
- SMSClient
- Set up Python with uv (composite action)
- test_server.py
- gsm/__init__.py
- SMSCServer
- test_validation.py
- ._force_disconnect_remaining_clients
- TestMessagePDU
- TestSMPPClientEdgeCases
- TestAddressValidation
- ._handle_client_pdu
- TestCreateResponsePDU
- TestSMPPClientUnbinding
- TestEnquireLink
- TestOptionalParameterValidation
- test_base.py
- Outbind
- TestShutdownIntegration
- SubmitSm
- protocol/__init__.py
- utils.py
- exceptions.py
- TestMessageDecoding
- MockPDU
- TestDeliverSmResp
- TestRealWorldScenarios
- TestMessageEncoding
- TestEdgeCases
- TestQuerySm
- TestGenericNack
- TestAlertNotification
- .process_message
- TestQuerySmResp
- conftest.py
- test_bind.py
- TestCStringDecoding
- TestIntegerEncoding
- TestIntegerDecoding
- TestCStringEncoding
- TestFieldValidation
- TestMessageLengthValidation
- TestPDUStructureValidation
- .set_message_payload
- EnquireLinkResp
- .test_create_error_response_unknown_request
- .test_set_event_handlers
- TestTLVPacking
- TestTLVUnpacking
- TestPDULengthCalculation
- TestSubmitSmParametersValidation
- TestHelperFunctions
- TestBindParametersValidation
- rules
- test_gsm_features.py
- TestBindingStates
- .decode
- examples/client.py
- UDH
- TestSMPPServerClientConnection
- TestRoundTripOperations
- ._handle_pdu_received
- TestPDUClasses
- Unbind
- patch
- SMPPConnection
- TestConnectionProperties
- TestSubmitSmResp
- test_client.py
- TestRegisteredDeliveryValidation
- .test_custom_values
- test_message.py
- test_codec.py
- TestPasswordValidation
- TestSequenceNumberValidation
- TestSMPPServerEdgeCases
- test_session.py
- TestBindTransmitterResp
- TestSMPPServerMessageHandling
- TestSMPPClientPDUHandling
- BindTransmitter
- examples/server.py
- .get_optional_parameter
- TestGetPDUClass
- TestSequenceNumber
- TestBindReceiver
- decode_gsm7
- .validate
- TestUnbindResp
- .encode_body
- .__init__
- TestPriorityFlagValidation
- .test_post_init_preserves_sequence
- .test_set_event_handlers
- .test_handle_connection_error_handler_exception
- PACKAGING.md
- .test_decode_body_insufficient_data_source
- RELEASING.md
- .test_decode_body_insufficient_data_message
- DataSmResp
- TestSMPPClientWaitMethods
- .test_set_delivery_receipt_requested
- .test_is_unicode_message
- .test_default_values
- SMPPException (base)
- test_connection.py
- ConcatenatedSMSHeader
- gsm_features_demo.py
- make_parts
- TestCreateRequestPDU
- .__init__
- .test_get_message_encoding
- .test_send_pdu_with_response
- TestPDUReceiving
- MessagePart
- DeliverSm
- unit/__init__.py
- unit/protocol/pdu/__init__.py
- Dependabot Configuration
- Bug Report Issue Template
- Documentation Issue Template
- Feature Request Issue Template
- smppai
- TestServiceTypeValidation
- TestEsmClassValidation
- .decode_body
- TestBindTransceiver
- .decode_body
- asyncio
- .create_for_invalid_pdu
- .encode_body
- Enum
- protocol/constants.py
- .decode_body
- Exception
- Any
- asyncio
- IntEnum
- .get_message_payload
- TestMemoryManagement
- test_factory.py

## God Nodes (most connected - your core abstractions)
1. `SMPPServer` - 149 edges
2. `SMPPClient` - 145 edges
3. `SMPPPDUException` - 101 edges
4. `ClientSession` - 89 edges
5. `CommandId` - 66 edges
6. `PDU` - 51 edges
7. `SMPPConnection` - 43 edges
8. `SMPPValidationException` - 42 edges
9. `SubmitSm` - 42 edges
10. `BindTransmitter` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Pre-commit Hooks Configuration` --semantically_similar_to--> `Lint & Format Check Job`  [INFERRED] [semantically similar]
  .pre-commit-config.yaml → .github/workflows/ci.yml
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPClient (ESME)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md
- `CONTRIBUTING Guide` --semantically_similar_to--> `CI Workflow`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → .github/workflows/ci.yml
- `smppai Project Structure (client/server/protocol/transport/config)` --semantically_similar_to--> `SMPPServer (SMSC)`  [INFERRED] [semantically similar]
  CONTRIBUTING.md → README.md
- `demo_submit_sm_with_udh()` --calls--> `SubmitSm`  [INFERRED]
  examples/gsm_features_demo.py → src/smpp/protocol/pdu/message.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI Workflow Pipeline Stages** — github_workflows_ci_lint, github_workflows_ci_type_check, github_workflows_ci_security, github_workflows_ci_unit_tests, github_workflows_ci_integration_test, github_workflows_ci_build, github_workflows_ci_coverage_report, github_workflows_ci_all_checks [EXTRACTED 1.00]
- **Shared Quality-Check Toolchain (ruff/mypy/pytest/bandit)** — pre_commit_config, github_workflows_ci_lint, contributing, github_pull_request_template [INFERRED 0.85]
- **SMPP Exception Hierarchy** — readme_smppexception, readme_smppconnectionexception, readme_smppbindexception, readme_smpptimeoutexception, readme_smppmessageexception [INFERRED 0.85]

## Communities (157 total, 35 thin omitted)

### Community 0 - "SMPPValidationException"
Cohesion: 0.11
Nodes (33): Exception raised for validation errors., SMPPValidationException, SMPP Protocol Validation This module provides validation functions for SMPP…, Validate SMPP service type field. Args: service_type: Service type to validate…, Validate message length based on data coding. Args: message: Message bytes to…, Validate data coding scheme. Args: data_coding: Data coding value to validate…, Validate ESM class field. Args: esm_class: ESM class value to validate Raises:…, Validate priority flag field. Args: priority_flag: Priority flag value to… (+25 more)

### Community 1 - ".__init__"
Cohesion: 0.21
Nodes (5): Any, IntEnum, Exception, SMPP-specific error codes for better error categorization., SMPPErrorCode

### Community 2 - "SMPPServer"
Cohesion: 0.04
Nodes (38): Event, create_simple_server(), Create a simple SMPP server with minimal configuration. Args: host: Server bind…, Set the grace period for shutdown notifications, Set the delay after grace period before final shutdown, Initialize SMPP Server Args: host: Server bind address port: Server bind port…, Get current shutdown configuration, Configure all shutdown parameters with comprehensive validation. Args:… (+30 more)

### Community 3 - "asyncio"
Cohesion: 0.04
Nodes (33): asyncio, Test successful connection., Test connect when no connection object., Test connect when already connected., Test successful disconnection., Test disconnect when not connected., Test disconnect when unbind fails., Test successful bind as transmitter. (+25 more)

### Community 4 - "TestCreatePDU"
Cohesion: 0.17
Nodes (7): Test creating PDU with invalid command ID., Test creating PDU with invalid parameters., Test create_pdu function., Test creating BindTransmitter PDU., Test creating SubmitSm PDU., Test creating EnquireLink PDU., TestCreatePDU

### Community 5 - "SMPPPDUException"
Cohesion: 0.04
Nodes (62): Exception raised for PDU-related errors., SMPPPDUException, calculate_pdu_length(), decode_cstring(), decode_integer(), decode_message_with_encoding(), encode_cstring(), encode_integer() (+54 more)

### Community 6 - "SMPPClient"
Cohesion: 0.03
Nodes (40): ConnectionState, Handle successful bind with enhanced logging., Exception, Check if client is connected to SMSC, Check if client is bound to SMSC, Get current bind type, Disconnect from SMSC server, Bind as transmitter (can send SMS) (+32 more)

### Community 7 - "PDU"
Cohesion: 0.06
Nodes (24): ABC, CommandStatus, SMPP Command Status codes as defined in SMPP v3.4 specification, MessagePDU, PDU, SMPP PDU Base Classes and Utilities This module contains the base PDU class and…, Abstract base class for all SMPP PDUs. This class provides the common…, Initialize PDU after creation. (+16 more)

### Community 8 - "ClientSession"
Cohesion: 0.06
Nodes (36): ClientSession, Get list of bound client sessions, Represents a connected SMPP client session, Get list of all client sessions, asyncio, Tests for enquire_link request handling., Test successful enquire_link request., Test enquire_link when exception occurs. (+28 more)

### Community 9 - "TestSystemIdValidation"
Cohesion: 0.17
Nodes (7): Tests for validate_system_id function., Test validating a valid system ID., Test validating an empty system ID., Test validating a system ID that's too long., Test validating a system ID with invalid characters., Test that underscores are allowed in system ID., TestSystemIdValidation

### Community 10 - ".validate"
Cohesion: 0.40
Nodes (3): Validate bind response fields. Raises: SMPPPDUException: If validation fails, Validate message PDU fields. Raises: SMPPPDUException: If validation fails, Validate empty body PDU. Only validates base PDU fields since there's no body…

### Community 11 - "TLVParameter"
Cohesion: 0.08
Nodes (17): Tag-Length-Value parameter for optional parameters. TLV parameters are used in…, Initialize TLV parameter. Args: tag: Parameter tag identifier value: Parameter…, Encode TLV parameter to bytes. Returns: The encoded TLV parameter as bytes, TLVParameter, Test TLV parameter string representation., Test TLVParameter class., Test TLV parameter equality., Test TLV parameter hashing. (+9 more)

### Community 12 - "TestSMPPServerStartStop"
Cohesion: 0.20
Nodes (6): Tests for server start/stop functionality., Test successful server start., Test starting server when already running raises exception., Test successful server stop., Test stopping server when not running., TestSMPPServerStartStop

### Community 13 - "TestStandardMessagePDU"
Cohesion: 0.15
Nodes (12): Test decode with insufficient data for destination address fields., Test delivery receipt request checking., Test StandardMessagePDU base class., Test StandardMessagePDU body encoding with basic data., Test encoding with message too long., Test StandardMessagePDU body decoding., TestStandardMessagePDU, __init__() (+4 more)

### Community 14 - ".decode"
Cohesion: 0.13
Nodes (8): Decode UDH element from bytes., Decode UDH from bytes. Args: data: Bytes to decode from offset: Starting offset…, Check if this message has User Data Header. Returns: True if UDH indicator is…, Extract UDH from short message if present. Returns: UDH object if present, None…, Get message content without UDH. Returns: Message content bytes (short_message…, Set UDH for this message. Args: udh: UDH object to set, Check if this is part of a concatenated SMS. Returns: True if this message has…, Get concatenated SMS information if present. Returns: ConcatenatedSMSHeader if…

### Community 15 - "SMSClient"
Cohesion: 0.09
Nodes (15): Exception, Check if this message is a server shutdown notification., Handle server shutdown notifications with appropriate responses., Thread-safe graceful shutdown process., Handle connection lost event with enhanced shutdown awareness., Handle unbind event with enhanced logging., Connect to SMSC and bind with enhanced shutdown awareness., Send a command to the server (for testing enhanced shutdown). Uses proper SMPP… (+7 more)

### Community 16 - "Set up Python with uv (composite action)"
Cohesion: 0.11
Nodes (28): CHANGELOG, CONTRIBUTING Guide, Conventional Commits, smppai Project Structure (client/server/protocol/transport/config), Semantic Release / Automated Versioning, Examples README, Set up Python with uv (composite action), Pull Request Template (+20 more)

### Community 17 - "test_server.py"
Cohesion: 0.07
Nodes (19): Unit tests for SMPP Server implementation This module contains tests for the…, Tests for server stop with client disconnect exceptions., Test server stop when client disconnect raises exception., Tests for custom authentication., Test custom authentication that succeeds., Test when authentication is disabled., Tests for server async context manager., Test successful context manager usage. (+11 more)

### Community 18 - "gsm/__init__.py"
Cohesion: 0.24
Nodes (5): GSM constants for compatibility with python-smpplib. Provides constants for…, GSM 7-bit encoding implementation for SMS messages. Provides encoding and…, GSM-specific functionality for SMPP implementation. This module provides GSM…, Message segmentation for SMS messages. Provides automatic message splitting for…, User Data Header (UDH) implementation for SMS messages. Provides UDH parsing…

### Community 19 - "SMSCServer"
Cohesion: 0.10
Nodes (12): Set up all server event handlers., Authenticate client credentials with enhanced logging. Args: system_id: Client…, Handle new client connection with enhanced logging., Handle client disconnection with enhanced logging., Handle successful client bind with enhanced logging., Example SMSC server using SMPP with enhanced shutdown capabilities. Features: -…, Start the SMSC server., Stop the SMSC server with enhanced shutdown. (+4 more)

### Community 20 - "test_validation.py"
Cohesion: 0.14
Nodes (9): Unit tests for SMPP Protocol Validation functions. Tests all validation…, Tests for validate_data_coding function., Test validating valid data coding schemes., Test validating invalid data coding schemes., Tests for validate_command_id function., Test validating valid command IDs., Test validating invalid command IDs., TestCommandIdValidation (+1 more)

### Community 21 - "._force_disconnect_remaining_clients"
Cohesion: 0.11
Nodes (9): Send shutdown notification to a client session with comprehensive error…, Send shutdown notification to all bound clients, Enhanced graceful shutdown with broadcast notifications and grace periods., Send notifications and wait for clients to disconnect gracefully., Wait for grace period and check if clients disconnect. Returns: True if all…, Force disconnect all remaining clients., Send unbind requests to all bound clients., Force disconnect all clients. (+1 more)

### Community 22 - "TestMessagePDU"
Cohesion: 0.20
Nodes (4): Test MessagePDU base class., Test MessagePDU default values., Test MessagePDU with custom values., TestMessagePDU

### Community 23 - "TestSMPPClientEdgeCases"
Cohesion: 0.20
Nodes (6): Tests for edge cases and boundary conditions., Test submit_sm with Unicode message., Test submit_sm with message at boundary length., Test connection state property during state transitions., Test binding sequence (bind, unbind, rebind)., TestSMPPClientEdgeCases

### Community 24 - "TestAddressValidation"
Cohesion: 0.08
Nodes (13): Test validating a valid national ISDN address., Test validating a valid alphanumeric address., Test validating an address that's too long., Test validating an address with invalid TON., Test validating an address with invalid NPI., Test validating international ISDN address with invalid format., Test validating national ISDN address with invalid format., Test validating alphanumeric address with invalid format. (+5 more)

### Community 25 - "._handle_client_pdu"
Cohesion: 0.08
Nodes (14): Exception, StreamReader, StreamWriter, Handle new client connection, Handle client disconnection, Handle PDU received from client, Handle bind request from client, Handle unbind request from client (+6 more)

### Community 26 - "TestCreateResponsePDU"
Cohesion: 0.20
Nodes (6): Test create_response_pdu function., Test creating response PDU successfully., Test creating response PDU with default status., Test creating response PDU from response command ID., Test creating response PDU for invalid command., TestCreateResponsePDU

### Community 27 - "TestSMPPClientUnbinding"
Cohesion: 0.14
Nodes (8): Tests for SMPPClient unbinding operations., Test successful unbind., Test unbind when not bound., Test unbind when connection is None but client state thinks it's bound., Test unbind with error response., Test unbind when exception occurs., Test unbind when handler raises exception., TestSMPPClientUnbinding

### Community 28 - "TestEnquireLink"
Cohesion: 0.14
Nodes (8): Test EnquireLink PDU., Test EnquireLink initialization., Test that custom command_id is preserved., Test EnquireLink body encoding (should be empty)., Test EnquireLink body decoding (should handle empty body)., Test that sequence number stays 0 until send_pdu assigns it., Test custom sequence number., TestEnquireLink

### Community 29 - "TestOptionalParameterValidation"
Cohesion: 0.09
Nodes (12): Tests for validate_optional_parameter function., Test validating valid optional parameters., Test validating optional parameter with negative tag., Test validating optional parameter with tag too large., Test validating optional parameter with value too long., Test validating valid receipted message ID., Test validating receipted message ID with non-printable characters., Test validating receipted message ID with invalid ASCII. (+4 more)

### Community 30 - "test_base.py"
Cohesion: 0.15
Nodes (6): Unit tests for SMPP PDU base classes., Test PDU with custom values., Test BindRequestPDU base class., Test BindRequestPDU default values., TestBindRequestPDU, TestPDU

### Community 31 - "Outbind"
Cohesion: 0.08
Nodes (13): Outbind, OUTBIND PDU - SMSC initiated bind request, Encode outbind body with system_id and password only, Decode outbind body with system_id and password only, Validate outbind fields Raises: SMPPPDUException: If validation fails, Test Outbind initialization., Test Outbind body encoding., Test Outbind body decoding. (+5 more)

### Community 32 - "TestShutdownIntegration"
Cohesion: 0.12
Nodes (14): integration, performance, asyncio, fixture, Integration tests for SMPP Server and Client shutdown interaction These tests…, Test that client can reconnect after server restart., Integration tests for server-client shutdown interaction, Performance tests for shutdown operations (+6 more)

### Community 33 - "SubmitSm"
Cohesion: 0.08
Nodes (17): SUBMIT_SM PDU - Request to submit a short message, SubmitSm, Test creating error response with message., Test SubmitSm initialization with defaults., Test SubmitSm with custom values., Test that custom command_id is preserved., TestSubmitSm, Test submit_sm from receiver (wrong bind type). (+9 more)

### Community 34 - "protocol/__init__.py"
Cohesion: 0.08
Nodes (66): SMPP AI - Async SMPP Protocol v3.4 Implementation A comprehensive, async…, CommandId, NpiType, Numbering Plan Indicator (NPI) values, SMPP Command IDs as defined in SMPP v3.4 specification, Type of Number (TON) values, TonType, SMPP Protocol Module This module contains the core SMPP protocol implementation… (+58 more)

### Community 35 - "utils.py"
Cohesion: 0.11
Nodes (19): calculate_message_length(), format_smpp_time(), generate_message_id(), is_valid_system_id(), mask_sensitive_data(), normalize_phone_number(), parse_smpp_time(), SMPP Utilities Module This module provides basic utility functions and helper… (+11 more)

### Community 36 - "exceptions.py"
Cohesion: 0.07
Nodes (38): Enum, BindType, SMPP Client (ESME) Implementation This module provides a comprehensive async…, Connect to SMSC server, Perform bind operation, Submit SMS message Args: source_addr: Source address (sender) destination_addr:…, SMPP Client Module This module provides a comprehensive async SMPP client…, SMPP Exception Classes This module defines all SMPP-specific exception classes… (+30 more)

### Community 37 - "TestMessageDecoding"
Cohesion: 0.10
Nodes (11): Tests for decode_message_with_encoding function., Test decoding with default data coding., Test decoding with ASCII data coding., Test decoding with Latin-1 data coding., Test decoding with UCS2 data coding., Test decoding with octet unspecified data coding., Test decoding with unknown data coding (should fallback to UTF-8)., Test decoding Unicode with UTF-8 fallback. (+3 more)

### Community 38 - "MockPDU"
Cohesion: 0.14
Nodes (7): MockEnquireLink, MockPDU, Test sending PDU when not connected, Test sending PDU without waiting for response, Test PDU response timeout, Return mock encoded PDU, Test send data failure

### Community 39 - "TestDeliverSmResp"
Cohesion: 0.20
Nodes (6): Test DeliverSmResp PDU., Test DeliverSmResp initialization., Test DeliverSmResp with custom values., Test DeliverSmResp body encoding., Test DeliverSmResp body decoding., TestDeliverSmResp

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
Cohesion: 0.12
Nodes (8): Handle SMS message from client with enhanced logging and commands., Process received message with enhanced command support., Send a response back to the client., Demonstrate the enhanced shutdown feature., Send delivery receipt to client., Broadcast message to all connected receiver clients., Send broadcast message to a specific client., Get comprehensive server statistics.

### Community 47 - "TestQuerySmResp"
Cohesion: 0.17
Nodes (7): Test QuerySmResp PDU., Test QuerySmResp initialization., Test QuerySmResp with custom values., Test QuerySmResp body encoding., Test QuerySmResp body decoding., Test decode with insufficient data., TestQuerySmResp

### Community 48 - "conftest.py"
Cohesion: 0.17
Nodes (14): event_loop(), mock_asyncio_sleep(), mock_logger(), mock_time(), fixture, Shared test fixtures and configuration for SMPP unit tests., Create an event loop for async tests., Mock asyncio.sleep to speed up tests. (+6 more)

### Community 49 - "test_bind.py"
Cohesion: 0.20
Nodes (7): Unit tests for SMPP bind PDUs., Test BindReceiverResp PDU., Test BindReceiverResp initialization., Test BindTransceiverResp PDU., Test BindTransceiverResp initialization., TestBindReceiverResp, TestBindTransceiverResp

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

### Community 58 - "EnquireLinkResp"
Cohesion: 0.23
Nodes (8): EnquireLinkResp, ENQUIRE_LINK_RESP PDU - Response to enquire_link, Test EnquireLinkResp PDU., Test EnquireLinkResp initialization., Test EnquireLinkResp with custom values., Test EnquireLinkResp body encoding (should be empty)., Test EnquireLinkResp body decoding., TestEnquireLinkResp

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

### Community 65 - "TestHelperFunctions"
Cohesion: 0.17
Nodes (7): Test helper factory functions., Test create_bind_pdu helper., Test create_bind_pdu with invalid type., Test create_submit_sm_pdu helper., Test create_enquire_link_pdu helper., Test create_generic_nack_pdu helper., TestHelperFunctions

### Community 66 - "TestBindParametersValidation"
Cohesion: 0.17
Nodes (7): Tests for validate_bind_parameters function., Test validating valid bind parameters., Test validating bind parameters with system type too long., Test validating bind parameters with invalid interface version., Test validating bind parameters with valid interface versions., Test validating bind parameters with invalid address range., TestBindParametersValidation

### Community 67 - "rules"
Cohesion: 0.15
Nodes (12): extends, rules, body-leading-blank, footer-leading-blank, header-max-length, scope-empty, scope-enum, subject-case (+4 more)

### Community 68 - "test_gsm_features.py"
Cohesion: 0.25
Nodes (5): Unit tests for GSM functionality., Test integration with MessagePDU., Test SubmitSm PDU with UDH., Test SubmitSm PDU without UDH., TestMessagePDUIntegration

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

### Community 73 - "TestSMPPServerClientConnection"
Cohesion: 0.17
Nodes (7): Tests for client connection handling., Test successful client connection handling., Test client connection with event handler., Test client connection when handler raises exception., Test client disconnection handling., Test client disconnection when handler raises exception., TestSMPPServerClientConnection

### Community 74 - "TestRoundTripOperations"
Cohesion: 0.17
Nodes (7): Tests for round-trip encoding/decoding operations., Test encoding and decoding C-strings., Test encoding and decoding integers., Test encoding and decoding messages with UTF-8., Test encoding and decoding messages with UCS2., Test packing and unpacking TLV parameters., TestRoundTripOperations

### Community 75 - "._handle_pdu_received"
Cohesion: 0.18
Nodes (6): DeliverSm, PDU, Handle received PDU from connection, Handle deliver_sm PDU, Send enquire_link_resp, Handle unbind request from SMSC

### Community 76 - "TestPDUClasses"
Cohesion: 0.20
Nodes (6): Test PDU_CLASSES mapping., Test bind command mappings., Test message command mappings., Test session command mappings., Test that all mapped commands have valid classes., TestPDUClasses

### Community 77 - "Unbind"
Cohesion: 0.17
Nodes (10): UNBIND PDU - Request to unbind from SMSC, Unbind, Test Unbind initialization., Test Unbind body encoding (should be empty)., Test Unbind body decoding (should handle empty body)., TestUnbind, Tests for unbind request handling., Test successful unbind request. (+2 more)

### Community 78 - "patch"
Cohesion: 0.09
Nodes (16): patch, Test that initialization creates SMPPConnection., Test PDU handling through _handle_client_pdu method., Test handling of BindTransmitter PDU through PDU handler., Test handling of BindReceiver PDU through PDU handler., Test handling of BindTransceiver PDU through PDU handler., Test handling of Unbind PDU through PDU handler., Test handling of SubmitSm PDU through PDU handler. (+8 more)

### Community 79 - "SMPPConnection"
Cohesion: 0.05
Nodes (28): Initialize SMPP Client Args: host: SMSC server hostname or IP port: SMSC server…, Exception, Check if connection is established, Check if connection is bound, Set connection state and trigger state change event, Get next sequence number, Mark the connection open and start its background tasks., Activate a connection whose reader/writer were provided by an accepted socket. (+20 more)

### Community 80 - "TestConnectionProperties"
Cohesion: 0.18
Nodes (6): Test connection properties and state management, Test state property getter, Test is_connected property, Test is_bound property, Test state change with handler, TestConnectionProperties

### Community 81 - "TestSubmitSmResp"
Cohesion: 0.14
Nodes (8): Test SubmitSmResp PDU., Test SubmitSmResp initialization., Test SubmitSmResp with custom values., Test SubmitSmResp body encoding., Test SubmitSmResp body encoding with empty message_id., Test SubmitSmResp body decoding., Test SubmitSmResp body decoding with empty message_id., TestSubmitSmResp

### Community 82 - "test_client.py"
Cohesion: 0.06
Nodes (23): Unit tests for SMPP Client implementation. Tests all functionality of the…, Tests for SMPPClient connection lost handling., Test handling connection lost., Test handling connection lost when handler raises exception., Tests for SMPPClient context manager., Test successful context manager usage., Test context manager when exception occurs., Tests for SMPPClient string representation. (+15 more)

### Community 83 - "TestRegisteredDeliveryValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_registered_delivery function., Test validating valid registered delivery values., Test validating registered delivery value below valid range., Test validating registered delivery value above valid range., TestRegisteredDeliveryValidation

### Community 85 - "test_message.py"
Cohesion: 0.22
Nodes (5): Unit tests for SMPP message PDUs., Test DeliverSm initialization., Test DeliverSm with custom values., Test delivery receipt detection., TestDeliverSm

### Community 86 - "test_codec.py"
Cohesion: 0.20
Nodes (6): Unit tests for SMPP Protocol Codec utilities. Tests all encoding/decoding…, Tests for edge cases and boundary conditions., Test handling of maximum values., Test handling of zero values., Test boundary length conditions., TestEdgeCases

### Community 87 - "TestPasswordValidation"
Cohesion: 0.20
Nodes (6): Tests for validate_password function., Test validating valid passwords., Test validating a password that's too long., Test validating a password with non-printable characters., Test that special printable characters are allowed., TestPasswordValidation

### Community 88 - "TestSequenceNumberValidation"
Cohesion: 0.20
Nodes (6): Tests for validate_sequence_number function., Test validating valid sequence numbers., Test validating sequence number zero., Test validating negative sequence number., Test validating sequence number that's too large., TestSequenceNumberValidation

### Community 89 - "TestSMPPServerEdgeCases"
Cohesion: 0.20
Nodes (6): Tests for edge cases and error scenarios., Test client count after various operations., Test message ID counter behavior., Test getting bound clients with mixed session states., Test client connection when peer info is not available., TestSMPPServerEdgeCases

### Community 90 - "test_session.py"
Cohesion: 0.29
Nodes (4): Unit tests for SMPP session PDUs., Test DataSm initialization., Test DataSm with custom values., TestDataSm

### Community 91 - "TestBindTransmitterResp"
Cohesion: 0.20
Nodes (6): Test BindTransmitterResp PDU., Test BindTransmitterResp initialization., Test BindTransmitterResp with custom values., Test BindTransmitterResp body encoding., Test BindTransmitterResp body decoding., TestBindTransmitterResp

### Community 92 - "TestSMPPServerMessageHandling"
Cohesion: 0.25
Nodes (5): Tests for server message handling., Test message ID generation., Test getting all client sessions., Test getting only bound client sessions., TestSMPPServerMessageHandling

### Community 93 - "TestSMPPClientPDUHandling"
Cohesion: 0.06
Nodes (17): Test handling unhandled PDU., Test handling PDU when exception occurs., Test handling deliver_sm., Test handling deliver_sm when handler raises exception., Test sending deliver_sm_resp., Test sending deliver_sm_resp when exception occurs., Test sending enquire_link_resp., Test sending enquire_link_resp when exception occurs. (+9 more)

### Community 94 - "BindTransmitter"
Cohesion: 0.13
Nodes (13): BindTransmitter, BIND_TRANSMITTER PDU - Request to bind as transmitter, Test decode with insufficient data., Test BindTransmitter PDU., Test BindTransmitter initialization with defaults., Test BindTransmitter with custom values., Test BindTransmitter body encoding., Test BindTransmitter body decoding. (+5 more)

### Community 95 - "examples/server.py"
Cohesion: 0.18
Nodes (12): cleanup_background_tasks(), main(), SMPP Server Example This example demonstrates how to use the SMPP server with…, Main server function demonstrating enhanced shutdown capabilities. Features…, Monitor and log server statistics periodically., Send periodic broadcast messages to demonstrate server capabilities., Clean up background tasks gracefully., Simple server example showcasing async context manager with enhanced shutdown.… (+4 more)

### Community 96 - ".get_optional_parameter"
Cohesion: 0.33
Nodes (3): Get optional parameter by tag. Args: tag: The parameter tag to search for…, Get optional parameter value by tag. Args: tag: The parameter tag to search for…, Check if optional parameter exists. Args: tag: The parameter tag to check for…

### Community 97 - "TestGetPDUClass"
Cohesion: 0.25
Nodes (5): Test get_pdu_class function., Test getting PDU class for valid command ID., Test getting PDU class for invalid command ID., Test getting PDU class for zero command ID., TestGetPDUClass

### Community 98 - "TestSequenceNumber"
Cohesion: 0.33
Nodes (4): Test sequence number generation, Test sequence number generation, Test sequence number wraparound, TestSequenceNumber

### Community 99 - "TestBindReceiver"
Cohesion: 0.33
Nodes (4): Test BindReceiver PDU., Test BindReceiver initialization., Test that custom command_id is preserved., TestBindReceiver

### Community 100 - "decode_gsm7"
Cohesion: 0.16
Nodes (13): decode_gsm7(), encode_gsm7(), Encode text to GSM 7-bit format. Args: text: Unicode text to encode Returns:…, Decode GSM 7-bit encoded data to text. Args: data: GSM 7-bit encoded bytes…, Reassemble message parts into original message. Args: parts: List of…, reassemble_parts(), Test GSM 7-bit encoding and decoding., Test basic GSM 7-bit encoding. (+5 more)

### Community 102 - "TestUnbindResp"
Cohesion: 0.40
Nodes (3): Test UnbindResp initialization., Test UnbindResp body encoding (should be empty)., TestUnbindResp

### Community 104 - ".__init__"
Cohesion: 0.50
Nodes (3): StreamReader, StreamWriter, Initialize SMPP connection Args: host: Remote host address port: Remote port…

### Community 105 - "TestPriorityFlagValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_priority_flag function., Test validating valid priority flag values., Test validating priority flag value below valid range., Test validating priority flag value above valid range., TestPriorityFlagValidation

### Community 107 - ".test_set_event_handlers"
Cohesion: 0.20
Nodes (4): Tests for server event handler initialization., Test that event handlers are initialized to None., Test setting custom event handlers., TestSMPPServerEventHandlers

### Community 109 - ".test_handle_connection_error_handler_exception"
Cohesion: 0.20
Nodes (5): Test state change handler exception handling, Test connection error handling, Test connection error handler exception, failing_handler(), TestErrorHandling

### Community 114 - "DataSmResp"
Cohesion: 0.17
Nodes (9): DataSmResp, DATA_SM_RESP PDU - Response to data_sm, Encode data_sm_resp body, Decode data_sm_resp body, Test DataSmResp initialization., Test DataSmResp with custom values., Test DataSmResp body encoding., Test DataSmResp body decoding. (+1 more)

### Community 115 - "TestSMPPClientWaitMethods"
Cohesion: 0.12
Nodes (8): Tests for SMPPClient wait methods., Test wait_for_connection when connection succeeds., Test wait_for_connection timeout., Test wait_for_connection when already connected., Test wait_for_bind when bind succeeds., Test wait_for_bind timeout., Test wait_for_bind when already bound., TestSMPPClientWaitMethods

### Community 119 - "SMPPException (base)"
Cohesion: 0.40
Nodes (5): SMPPBindException, SMPPConnectionException, SMPPException (base), SMPPMessageException, SMPPTimeoutException

### Community 120 - "test_connection.py"
Cohesion: 0.10
Nodes (20): ConnectionState, Enum, SMPP Connection Handling This module provides async TCP connection handling for…, SMPP Connection States, Get current connection state, SMPP Transport Layer This module provides the transport layer abstraction for…, connected_connection(), connection() (+12 more)

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

### Community 128 - "TestPDUReceiving"
Cohesion: 0.12
Nodes (9): Test PDU receiving functionality, Test successful PDU reception, Test PDU reception with no reader, Test PDU reception timeout, Test incomplete PDU read, Test PDU with invalid length, Test handling received PDU as response, Test handling received PDU as incoming (+1 more)

### Community 129 - "MessagePart"
Cohesion: 0.33
Nodes (4): MessagePart, A single part of a segmented SMS message. Attributes: content: Message content…, Get the complete short message including UDH. Returns: Complete message bytes…, Get ESM class with UDH indicator if needed. Args: base_esm_class: Base ESM…

### Community 130 - "DeliverSm"
Cohesion: 0.14
Nodes (9): DeliverSm, Get message text as string using specified or auto-detected encoding Args:…, Set message text from string using specified or auto-detected encoding Args:…, Get appropriate encoding for the message based on data_coding Returns: str:…, DELIVER_SM PDU - Deliver a short message or delivery receipt, Check if this is a delivery receipt Returns: bool: True if this is a delivery…, Check if this is a mobile originated message Returns: bool: True if this is a…, Parse delivery receipt message into structured data Returns: dict: Parsed… (+1 more)

### Community 139 - "TestServiceTypeValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_service_type function., Test validating valid service types., Test validating a service type that's too long., Test validating a service type with non-printable characters., TestServiceTypeValidation

### Community 140 - "TestEsmClassValidation"
Cohesion: 0.25
Nodes (5): Tests for validate_esm_class function., Test validating valid ESM class values., Test validating ESM class value below valid range., Test validating ESM class value above valid range., TestEsmClassValidation

### Community 142 - "TestBindTransceiver"
Cohesion: 0.50
Nodes (3): Test BindTransceiver PDU., Test BindTransceiver initialization., TestBindTransceiver

### Community 144 - "asyncio"
Cohesion: 0.13
Nodes (9): asyncio, Test successful connection, Test connect when already connected, Test connection timeout, Test disconnect when not connected, Test successful disconnection, Test background task functionality, Test enquire link loop (+1 more)

### Community 148 - "protocol/constants.py"
Cohesion: 0.11
Nodes (22): EsmClass, get_request_command_id(), get_response_command_id(), InterfaceVersion, is_response_command(), MessageState, OptionalTag, PriorityFlag (+14 more)

### Community 162 - "TestMemoryManagement"
Cohesion: 0.50
Nodes (3): Test memory management and limits, Test memory limit enforcement, TestMemoryManagement

### Community 168 - "test_factory.py"
Cohesion: 0.07
Nodes (19): Decode PDU from bytes. Args: data: The byte data to decode Returns: The decoded…, decode_pdu(), Decode PDU from bytes using the factory. Args: data: Raw PDU bytes Returns:…, Receive and decode a single PDU, Unit tests for SMPP PDU factory., Test create_typed_pdu function., Test creating typed PDU successfully., Test creating typed PDU with type mismatch. (+11 more)

## Knowledge Gaps
- **28 isolated node(s):** `Packaging`, `Releasing`, `smppai`, `body-leading-blank`, `footer-leading-blank` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1137 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SMPPPDUException` connect `SMPPPDUException` to `TestPDUReceiving`, `.__init__`, `DeliverSm`, `TestCreatePDU`, `PDU`, `.validate`, `TLVParameter`, `TestStandardMessagePDU`, `TestCreateResponsePDU`, `Outbind`, `protocol/__init__.py`, `exceptions.py`, `TestMessageDecoding`, `test_factory.py`, `TestMessageEncoding`, `TestAlertNotification`, `TestQuerySmResp`, `TestCStringDecoding`, `TestIntegerEncoding`, `TestIntegerDecoding`, `TestCStringEncoding`, `TestFieldValidation`, `TestTLVPacking`, `TestTLVUnpacking`, `TestPDULengthCalculation`, `TestHelperFunctions`, `.decode`, `SMPPConnection`, `BindTransmitter`, `TestGetPDUClass`, `.validate`, `DataSmResp`, `test_connection.py`, `TestCreateRequestPDU`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **Why does `SMPPClient` connect `SMPPClient` to `protocol/__init__.py`, `asyncio`, `exceptions.py`, `examples/client.py`, `._handle_pdu_received`, `patch`, `SMSClient`, `SMPPConnection`, `test_client.py`, `TestSMPPClientWaitMethods`, `TestSMPPClientEdgeCases`, `TestSMPPClientUnbinding`, `.test_set_event_handlers`, `TestSMPPClientPDUHandling`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `SMPPServer` connect `SMPPServer` to `TestSMPPServerEdgeCases`, `SubmitSm`, `protocol/__init__.py`, `exceptions.py`, `PDU`, `ClientSession`, `TestSMPPServerClientConnection`, `.test_set_event_handlers`, `TestSMPPServerStartStop`, `Unbind`, `.process_message`, `patch`, `test_server.py`, `SMSCServer`, `._force_disconnect_remaining_clients`, `._handle_client_pdu`, `TestSMPPServerMessageHandling`, `examples/server.py`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `SMPPServer` (e.g. with `SMPPException` and `TestSMPPServerBindHandling`) actually correct?**
  _`SMPPServer` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `SMPPClient` (e.g. with `SMPPBindException` and `SMPPConnectionException`) actually correct?**
  _`SMPPClient` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `SMPPPDUException` (e.g. with `BindRequestPDU` and `BindResponsePDU`) actually correct?**
  _`SMPPPDUException` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ClientSession` (e.g. with `TestShutdownPerformance` and `.test_shutdown_performance_with_many_clients()`) actually correct?**
  _`ClientSession` has 14 INFERRED edges - model-reasoned connections that need verification._