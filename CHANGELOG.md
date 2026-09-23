# CHANGELOG


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
