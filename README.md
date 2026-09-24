# SMPP AI - SMPP Protocol v3.4 Async Implementation

An async implementation (hence "ai" in the name) of the SMPP (Short Message
Peer-to-Peer) protocol v3.4 in Python.

It provides an `SMPPClient` (ESME) and `SMPPServer` (SMSC), full PDU
encoding/decoding with TLV optional parameters, GSM 7-bit encoding and
message segmentation for concatenated SMS.

## Installation

Start with `uv sync`.

Run examples with:

```bash
uv run examples/server_basic.py
uv run examples/client_basic.py  # in a separate command line
```

Requires Python 3.10+. The only runtime dependency is `typing-extensions`.

## Documentation

The [user manual](docs/user-manual.adoc) covers everything: quick start,
the client and server APIs, event handlers, PDU/TLV support, data coding
schemes, GSM segmentation and UDH, error handling, logging and testing.
Build it to PDF/EPUB with [snowball](https://github.com/codcod/snowball)
(`snowball.yaml` is already configured), or read the AsciiDoc source
directly.

`examples/` has complete, runnable client, server, and GSM-features
programs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, local quality-check
commands, and the commit/PR process.

## References

- [SMPP v3.4 Specification](https://smpp.org/SMPP_v3_4_Issue1_2.pdf)
- [SMPP Protocol Overview](https://smpp.org/)
- [SMS Forum](https://www.smsforum.net/)
