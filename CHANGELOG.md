# CHANGELOG


## v0.8.2 (2026-09-25)

### Bug Fixes

- **client**: Reassemble split data_sm, refuse with RX_R_APPN (SMP-022)
  ([`19e4fb1`](https://github.com/codcod/smppai/commit/19e4fb1674a35038e567215409e618677a47705b))


## v0.8.1 (2026-09-25)

### Bug Fixes

- Refuse unhandled data_sm and harden data_sm payloads (SMP-021)
  ([`4878f5f`](https://github.com/codcod/smppai/commit/4878f5ff9a0d9dd03117f269302805a9d510f8c4))


## v0.8.0 (2026-09-25)

### Features

- Send and handle data_sm in client and server (SMP-007)
  ([`2fd5444`](https://github.com/codcod/smppai/commit/2fd54442417dfe76a797782af1f7847463b08424))

### Testing

- Give oversized data_sm cases short ids (SMP-007)
  ([`7cc54a6`](https://github.com/codcod/smppai/commit/7cc54a634deb39ded24f84a4dbe40021a990aaac))


## v0.7.1 (2026-09-25)

### Bug Fixes

- Pack stateful-codec text by run when splitting (SMP-010)
  ([`c866859`](https://github.com/codcod/smppai/commit/c866859a12c7dc5f2888b10d7d36a67fc5707308))


## v0.7.0 (2026-09-25)

### Bug Fixes

- **server**: Validate interface_version, TLV only as v3.4 (SMP-008)
  ([`174415c`](https://github.com/codcod/smppai/commit/174415c93dc0bf1c6e54fe1c38ed68820f7fe089))

### Chores

- **deps**: Sync uv.lock with v0.6.2
  ([`73a9fe7`](https://github.com/codcod/smppai/commit/73a9fe7f56b82c249f81bc3b9566db608fd4604b))

### Continuous Integration

- Re-lock uv.lock in the semantic-release commit
  ([`9beb21f`](https://github.com/codcod/smppai/commit/9beb21f500b2cf0da0e0cde90248328cfc6d9f1c))

### Features

- Report sc_interface_version on bind, record peer version (SMP-008)
  ([`d12708d`](https://github.com/codcod/smppai/commit/d12708db924046249a9d604b183689edc412c060))


## v0.6.2 (2026-09-25)

### Bug Fixes

- **client**: Bound inbound queue, expire stale parts (SMP-018)
  ([`fd62c06`](https://github.com/codcod/smppai/commit/fd62c063223990b1f9c50c180685044bfc2a7a92))


## v0.6.1 (2026-09-25)

### Bug Fixes

- **protocol**: Decode bodyless error responses with TLVs (SMP-016)
  ([`9d62a3d`](https://github.com/codcod/smppai/commit/9d62a3d731f8b2e388a9061a26ffc5aaa879209e))

- **protocol**: Only accept known TLV tags as a bodyless tail (SMP-019)
  ([`d1cf908`](https://github.com/codcod/smppai/commit/d1cf908397cff63f7adf4592bde9277b08ef640b))

### Chores

- **deps**: Sync uv.lock with released version 0.6.0
  ([`b0d5e07`](https://github.com/codcod/smppai/commit/b0d5e0790cada575996161650477a9003c7698c8))


## v0.6.0 (2026-09-24)

### Chores

- Upgrade uv.lock and remove stub justfile
  ([`1308d46`](https://github.com/codcod/smppai/commit/1308d461e0e195d7032754a76295d3ed807af288))

### Features

- **client**: Add high-level connect/send/messages API (SMP-011)
  ([`5a5ba44`](https://github.com/codcod/smppai/commit/5a5ba44906ed33d9ab5e8474950e22d729df732a))


## v0.5.0 (2026-09-24)

### Bug Fixes

- **protocol**: Tighten typed TLV accessor edge cases (SMP-017)
  ([`24ad98a`](https://github.com/codcod/smppai/commit/24ad98ae9db4d62dacc01e6015a79622cf891271))

### Features

- **protocol**: Add typed get_tlv/set_tlv TLV accessors (SMP-009)
  ([`59ad11f`](https://github.com/codcod/smppai/commit/59ad11f61c3647ff08dd64bb5491116516a20d95))


## v0.4.1 (2026-09-24)

### Bug Fixes

- **protocol**: Decode header-only error resps and NUL TLVs (SMP-014)
  ([`f5e8a2d`](https://github.com/codcod/smppai/commit/f5e8a2dddef1625f57d34d464fab555671b3e167))


## v0.4.0 (2026-09-24)

### Features

- Add query_sm, cancel_sm and replace_sm (SMP-006)
  ([`5e1da8a`](https://github.com/codcod/smppai/commit/5e1da8a71a94839600ea1186945040f696c84505))

### Testing

- **client**: Cover replace_sm/_send_management errors (SMP-006)
  ([`ec0a7bd`](https://github.com/codcod/smppai/commit/ec0a7bda94047cd9b381b176641e8c1449cdae6d))


## v0.3.3 (2026-09-24)

### Chores

- **examples**: Use opensmpp sim credentials and sync uv.lock
  ([`6cc0944`](https://github.com/codcod/smppai/commit/6cc0944f17f92e2a5ec4f500652259e04fa0ce83))

### Performance Improvements

- **transport**: Cut per-PDU receive and validation overhead (SMP-012)
  ([`0b49fce`](https://github.com/codcod/smppai/commit/0b49fceeb9c2448e407e4cef1a8d439d93dc6c90))


## v0.3.2 (2026-09-24)

### Bug Fixes

- **protocol**: Order submit_sm/deliver_sm fields per SMPP 3.4 (SMP-013)
  ([`462437e`](https://github.com/codcod/smppai/commit/462437e761782486ff4fcd7361b7d7badce2078e))

### Testing

- **tests**: Make opensmpp sim test skip and wait robustly (SMP-013)
  ([`f692046`](https://github.com/codcod/smppai/commit/f692046cedd830ea77837e0d46ce7313124fb060))


## v0.3.1 (2026-09-24)

### Bug Fixes

- **client**: Satisfy mypy on sent_message_ids assignment (SMP-004)
  ([`7198b32`](https://github.com/codcod/smppai/commit/7198b32d645c137db04fa53b821f56f12b09a052))

- **client**: Send long text as codec-encoded concatenated SMS (SMP-004)
  ([`2975a9c`](https://github.com/codcod/smppai/commit/2975a9c0844f5ee62e2b167ce3ac3da60c06e0ba))

### Continuous Integration

- Mirror the GitHub Actions checks in make ci (SMP-004)
  ([`64959d6`](https://github.com/codcod/smppai/commit/64959d6da2c39f40cb36cb22441b67b75d1587a8))

### Refactoring

- **client**: Drop unreachable UnicodeEncodeError branch (SMP-004)
  ([`109ca75`](https://github.com/codcod/smppai/commit/109ca7538a3e014fe4c18dcc739a5f5477096c35))

### Testing

- **tests**: Cover submit_multipart and reassemble_parts (SMP-004)
  ([`f23bd0c`](https://github.com/codcod/smppai/commit/f23bd0c031a076d67233d8ee16d1c92343931f2b))


## v0.3.0 (2026-09-23)

### Bug Fixes

- **protocol**: Use SMPP v3.4 status codes; raise throttling (SMP-005)
  ([`4aaa0a9`](https://github.com/codcod/smppai/commit/4aaa0a9d667401548b6f3457395caed2806021a4))

### Chores

- Ignore generated graphify output
  ([`c04ecd2`](https://github.com/codcod/smppai/commit/c04ecd22f52b44db13a54b619235bae1c1abe5b2))

- Set major_on_zero = false; undo the 1.0.0 release
  ([`a286894`](https://github.com/codcod/smppai/commit/a28689425031a76e50957a978978c90e07418432))

### Documentation

- Split examples into basic/advanced, add AsciiDoc user manual
  ([`b0801e9`](https://github.com/codcod/smppai/commit/b0801e980a778e69c9fef59474794f1693b1cda7))

### Testing

- **tests**: Pin all of Table 5-2; show throttle catch order (SMP-005)
  ([`af22f0a`](https://github.com/codcod/smppai/commit/af22f0a44823d4361a50f91d1ef1af903b5ee264))

### Breaking Changes

- **tests**: CommandStatus numeric values now follow SMPP v3.4 Table 5-2 (0x06 upward were
  renumbered, e.g. ESME_RINVPASWD 0x06 -> 0x0E), and ESME_RINVSRCADR/ESME_RINVDESTADR now mean
  invalid address rather than invalid TON (use ESME_RINVSRCTON/ESME_RINVDSTTON).
  SMPPThrottlingException now subclasses SMPPMessageException.


## v0.2.8 (2026-09-23)

### Bug Fixes

- **protocol**: Stop mapping reserved data_coding 0xF8-0xFF to a codec (SMP-003)
  ([`ce4855c`](https://github.com/codcod/smppai/commit/ce4855cb4a957fff8d117b317924d1ef0b6e87cb))

### Chores

- **deps**: Sync uv.lock with project version 0.2.7 (SMP-003)
  ([`db46317`](https://github.com/codcod/smppai/commit/db46317d8a68c82ace1b7d2be5316b01aacc5bd7))


## v0.2.7 (2026-09-23)

### Bug Fixes

- **protocol**: Align short_message validation with the encoder (SMP-003)
  ([`4ffd52c`](https://github.com/codcod/smppai/commit/4ffd52cab26cb971d46b2d3b9e1df41bcd2610c6))

- **protocol**: Reject reserved data_coding 0xF8-0xFF (SMP-003)
  ([`87ca8f8`](https://github.com/codcod/smppai/commit/87ca8f859011cbbcef6104a73ff1036c9cd60d13))


## v0.2.6 (2026-09-23)

### Bug Fixes

- **protocol**: Encode default data_coding as GSM 03.38 (SMP-002)
  ([`de52efe`](https://github.com/codcod/smppai/commit/de52efe041ec1b2346019bb76613d943d2816aee))


## v0.2.5 (2026-09-23)

### Bug Fixes

- Bound requires-python below 3.14, pin version (SMP-001)
  ([`658a181`](https://github.com/codcod/smppai/commit/658a1810db5e3c6f590d0af3469d86d100357c93))

- **client**: Honor data_coding when encoding submit_sm text (SMP-001)
  ([`e7ead49`](https://github.com/codcod/smppai/commit/e7ead49093637a55a0e6ba260ef0a92948d013bf))

- **client**: Reject text not encodable in data_coding (SMP-001)
  ([`5d11352`](https://github.com/codcod/smppai/commit/5d1135222396c8704b5b0c3623702a917050592f))

- **protocol**: Stop auto-generating PDU sequence numbers (SMP-001)
  ([`0eed97a`](https://github.com/codcod/smppai/commit/0eed97aef4bf40b737dd3d092882bfc82a612b4b))

- **server**: Honor data_coding when encoding deliver_sm text (SMP-001)
  ([`862515d`](https://github.com/codcod/smppai/commit/862515d05e5d807aaab4961247c2a9c935276f84))

- **server**: Skip shutdown grace sleep with no clients (SMP-001)
  ([`63e3591`](https://github.com/codcod/smppai/commit/63e3591afdc461c51421640aa784ccdbf44ba1a4))

- **server**: Use connection.accept() for inbound clients (SMP-001)
  ([`0ac13f1`](https://github.com/codcod/smppai/commit/0ac13f14d26639ebf2af95f57779a594f461f851))

- **transport**: Add accept() for inbound connection setup (SMP-001)
  ([`a3d71fd`](https://github.com/codcod/smppai/commit/a3d71fd2bf84063c9c4c39ea2b661fca62d0e870))

- **transport**: Only responses complete pending requests (SMP-001)
  ([`936b4df`](https://github.com/codcod/smppai/commit/936b4dfae594615b093caabb77d667bd5ac600b9))

### Chores

- Format
  ([`ef70157`](https://github.com/codcod/smppai/commit/ef7015788c2769d405dd69e49558d03b56566293))

- Graphify reactor
  ([`5f7f851`](https://github.com/codcod/smppai/commit/5f7f851c6279773db922521248c69bfde4bcf269))

- Graphify reactor
  ([`b1f4553`](https://github.com/codcod/smppai/commit/b1f4553dcbb4d7f50d94a9eed0e45b1bfe6e39f9))

- Graphify reactor
  ([`a1ee1cb`](https://github.com/codcod/smppai/commit/a1ee1cb91dbc4895cb76e91e51e722063f5bba10))

- Remove deprecated entry
  ([`389aeaf`](https://github.com/codcod/smppai/commit/389aeafb07bad109554a3bc578f1fdf9d4a26ec7))

- Uv update
  ([`641e611`](https://github.com/codcod/smppai/commit/641e611c3481b01a0a2d61391fb9c87a438fd8fb))

### Continuous Integration

- **deps**: Bump actions/cache from 5 to 6
  ([`ac2c757`](https://github.com/codcod/smppai/commit/ac2c757dd11412b9e09acc81e7e80b2229f8f004))

- **deps**: Bump actions/checkout from 6 to 7
  ([`15bdfea`](https://github.com/codcod/smppai/commit/15bdfea837d266d891e56f85510546bb9f80a9b0))

- **deps**: Bump actions/download-artifact from 7 to 8
  ([`585715d`](https://github.com/codcod/smppai/commit/585715dfb8c25b576385576ca5cad8cc6f05ab8b))

- **deps**: Bump actions/upload-artifact from 6 to 7
  ([`c311b55`](https://github.com/codcod/smppai/commit/c311b556245d6f8d6ebc34d8581800e6facff8d9))

- **deps**: Bump codecov/codecov-action from 5 to 7
  ([`dd2868b`](https://github.com/codcod/smppai/commit/dd2868b572f2ae951f897e51eb42a51ff1db9e9a))

### Refactoring

- Delete unused SMPP error-handling helpers (SMP-001)
  ([`faf73c3`](https://github.com/codcod/smppai/commit/faf73c3b1d28d858fc223b01267a32f484eefaf8))

- **protocol**: Delete unused validation-rule registry (SMP-001)
  ([`ae058a3`](https://github.com/codcod/smppai/commit/ae058a3c6190b102c940c2bada8a8b0c0bdbb16a))

### Testing

- **protocol**: Cover PDU.validate sequence-number bounds (SMP-001)
  ([`378a1fd`](https://github.com/codcod/smppai/commit/378a1fdf1c8d2d51c6cd91601076a66e8c766051))


## v0.2.4 (2026-09-22)

### Bug Fixes

- **tests**: Make test_check_memory_limits async so asyncio.Future() has a running loop
  ([`c95ac5e`](https://github.com/codcod/smppai/commit/c95ac5e7357213d5987c573946aa6c21d254457e))

- **tests**: Register cleanup_after_test as an async fixture and exclude its own task from
  cancellation
  ([`6615d8a`](https://github.com/codcod/smppai/commit/6615d8a34f4445b063a84e92af6bcedfc8f7a7b9))


## v0.2.3 (2026-09-22)

### Continuous Integration

- **deps**: Bump actions/cache from 4 to 5
  ([`9ea2cd1`](https://github.com/codcod/smppai/commit/9ea2cd1effa6c146d679107f839456fcded64fd2))

- **deps**: Bump actions/checkout from 5 to 6
  ([`8016151`](https://github.com/codcod/smppai/commit/8016151a7aa693dd78d9ae5eb4448cfb3b38e070))

- **deps**: Bump actions/download-artifact from 6 to 7
  ([`aa09793`](https://github.com/codcod/smppai/commit/aa097931e508b4ef49e874a2fb18f9858499f772))

- **deps**: Bump actions/upload-artifact from 5 to 6
  ([`91c9382`](https://github.com/codcod/smppai/commit/91c938296bade63f4bee73b2335e648349e1a863))


## v0.2.2 (2026-09-22)

### Bug Fixes

- **ci**: Pin astral-sh/setup-uv to v6, v7's cache prune breaks the save step
  ([`f26a437`](https://github.com/codcod/smppai/commit/f26a437753252aab773dd7af1cae8e336d8f320b))

- **ci**: Pin setup-uv composite action to v6, v7 breaks cache save when nested in a composite
  action
  ([`fa759b3`](https://github.com/codcod/smppai/commit/fa759b3db101c3904d87266d6dbb6be82f4121e8))

- **gsm**: Replace star import with explicit names, drop unused test imports
  ([`c04d8dd`](https://github.com/codcod/smppai/commit/c04d8dde567ee1f5a0a14bb779bb04101433ff75))

### Chores

- Align repo tooling, remove dead config module, packaging docs
  ([`42d9121`](https://github.com/codcod/smppai/commit/42d91210659c98a03294d8b30bd3d3b4367d0a27))

- Sync graphify-out after tooling/config commit
  ([`2f8a9d0`](https://github.com/codcod/smppai/commit/2f8a9d068295ce12c5275f2fbc31fd22b6dc796e))

### Continuous Integration

- **deps**: Bump actions/checkout from 4 to 5
  ([`af3e409`](https://github.com/codcod/smppai/commit/af3e409c66d16009df5c3ae31958e1276664c8a0))

- **deps**: Bump actions/download-artifact from 4 to 5
  ([`2cf33c9`](https://github.com/codcod/smppai/commit/2cf33c9107afc2ca334a4899ec957d900fc40bc8))

- **deps**: Bump actions/download-artifact from 5 to 6
  ([`04361ef`](https://github.com/codcod/smppai/commit/04361ef9cb8ec408ec7556bedc72af8534e96800))

- **deps**: Bump actions/upload-artifact from 4 to 5
  ([`6013fda`](https://github.com/codcod/smppai/commit/6013fda679e1bdc0cafb48486705a3578eb857fa))

- **deps**: Bump astral-sh/setup-uv from 6 to 7
  ([`d89e46a`](https://github.com/codcod/smppai/commit/d89e46a00fdb9173a4584e2099877a8e75a938bf))


## v0.2.1 (2025-06-24)

### Bug Fixes

- Pylance complaints
  ([`1e58465`](https://github.com/codcod/smppai/commit/1e58465920e86cb56abf83e89641271bd97b610d))

### Chores

- Adjust pytest settings
  ([`113cdc9`](https://github.com/codcod/smppai/commit/113cdc92d70e16915f44d5840244fd99d5e48229))

- Remove unused code
  ([`e2ec545`](https://github.com/codcod/smppai/commit/e2ec545683f324687a65cc42d2b7d135b88f5c4f))


## v0.2.0 (2025-06-23)

### Bug Fixes

- Allow for 3.12 and 3.13 only
  ([`4c86956`](https://github.com/codcod/smppai/commit/4c869562b6efdf753742fc4ee8f0ffe04e6f0ca7))

- Allow for lower python version
  ([`7d6ac86`](https://github.com/codcod/smppai/commit/7d6ac86aea41255f9436be9719ad0faaf1c46b59))

- Dont fail on errors
  ([`b5ab24e`](https://github.com/codcod/smppai/commit/b5ab24e6ccc4679ee2de8cf72b4215dc0107de11))

- Improve graceful shutdown implementation
  ([`95ea3ea`](https://github.com/codcod/smppai/commit/95ea3eabcdd7d0ffa93f322b8c74371f0e1d1302))

- Remove env context from job name in GitHub Actions
  ([`8ae2875`](https://github.com/codcod/smppai/commit/8ae287592edd2927f7d1a7dada659f1190b1ae61))

- Resolve GitHub Actions matrix/env error
  ([`20b01ed`](https://github.com/codcod/smppai/commit/20b01ed116241d49dd0a5b703c0528e6541add11))

- Simplify coverage reporting in CI workflow
  ([`e7a4a2c`](https://github.com/codcod/smppai/commit/e7a4a2c0cf1bab9b9623b8acb6a41546bba52a4a))

- Specify bash shell for Windows compatibility in unit-tests
  ([`d08c201`](https://github.com/codcod/smppai/commit/d08c2016442e1126123d5834eacf64c89cf53fdc))

### Chores

- Add black as code formatter
  ([`fc1a697`](https://github.com/codcod/smppai/commit/fc1a69740df0eede20a029a49318540197797a5f))

- Black formatting
  ([`9321ffa`](https://github.com/codcod/smppai/commit/9321ffa6ab40ce885a5d1097a41863f23ec74001))

- Change port plus minor adjustments
  ([`98ef766`](https://github.com/codcod/smppai/commit/98ef766bd18ca20577feec97d56a54700067109d))

### Continuous Integration

- Allow for 3.10+
  ([`5103f31`](https://github.com/codcod/smppai/commit/5103f31f61ddccda6cac95bdfa2e59b6f230635c))

- Make templates less noisy
  ([`89fd7cc`](https://github.com/codcod/smppai/commit/89fd7ccba1aee7259b9f2129d1160c182d2803be))

- Optimize
  ([`e4c4636`](https://github.com/codcod/smppai/commit/e4c46364a6bd3eb29a0650b48ce16ce6e31b2591))

### Documentation

- Add graceful server shutdown example
  ([`9c15d24`](https://github.com/codcod/smppai/commit/9c15d244d259499a04a40b216eaeabb6e0c2598c))

### Features

- Add graceful shutdown to SMPP server
  ([`f258f4e`](https://github.com/codcod/smppai/commit/f258f4e12adf5014fd5a0ac671c864cb6a820fde))

- Shutdown with grace period
  ([`42a565a`](https://github.com/codcod/smppai/commit/42a565a5bd5f742608f2c637e696aa69c436a99a))

### Refactoring

- Optimize and standardize caching strategy in CI workflow
  ([`16c9994`](https://github.com/codcod/smppai/commit/16c999413caf004f1665dce50b73e426bfc5eabe))


## v0.1.0 (2025-06-21)

### Continuous Integration

- Add ruff dependency back
  ([`e9ee25e`](https://github.com/codcod/smppai/commit/e9ee25ef4e83ea0e694ede25b12ad8fca380171f))

- Add twine and build dependency back
  ([`f8a51fa`](https://github.com/codcod/smppai/commit/f8a51fa9a1a5f543dbc0e8129c571d080a0a5fe0))

- Fixes
  ([`88e0cef`](https://github.com/codcod/smppai/commit/88e0cef3cdaed2e87320aa4b7679241985f59f39))

### Features

- Bump version
  ([`11f3edb`](https://github.com/codcod/smppai/commit/11f3edbdf0a2c3e8236c279d1fce9b31c61aece5))


## v0.0.0 (2025-06-21)
