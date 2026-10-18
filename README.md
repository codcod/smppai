# SMPP AI - SMPP Protocol v3.4 Async Implementation

An async implementation (hence "ai" in the name) of the SMPP (Short Message
Peer-to-Peer) protocol v3.4 in Python.

It provides an `SMPPClient` (ESME) and `SMPPServer` (SMSC), full PDU
encoding/decoding with TLV optional parameters, GSM 7-bit encoding and
message segmentation for concatenated SMS. Both sides can run over TCP or TLS.

## Installation

Start with `uv sync`.

Send an SMS:

```python
import smpp

async with smpp.connect("localhost", 2775, "my_client", "my_pass") as client:
    await client.send("+306900000000", "Hello!", sender="ACME")
```

Run examples with:

```bash
uv run examples/server_basic.py
uv run examples/client_basic.py  # in a separate command line
```

Requires Python 3.10+. No runtime dependencies. Optional: `uv add 'smppai[fast]'` for uvloop.

To test an ESME without a carrier, run the simulator SMSC. It answers
`submit_sm` with delivery receipts and injects MO from an HTTP `POST /mo`
(see the user manual's simulator chapter):

```bash
uv run python -m smpp.sim --stat DELIVRD:9 --stat UNDELIV:1
```

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
