# TLA+ models

`SmppSession.tla` models one bound ESME session against `SMPPServer`:
pipelined `submit_sm`, the client's `unbind` (possibly sent twice), and both
ends closing the socket. It covers the server's handler tasks
(`src/smpp/server/server.py`) and the unbind paths of the client
(`src/smpp/client/client.py`).

asyncio runs a task without interruption between two `await`s, so each
action in the spec is the code between two awaits of one task. TLC then
tries every order in which those steps can run.

## Running

Needs Java 11+.

```bash
curl -fsSL -o specs/tla2tools.jar \
  https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar
specs/check.sh
```

This takes about 15 seconds. CI runs it in the `model-check` job.

## What is checked

| Name | Kind | Meaning |
|---|---|---|
| `NoLostAck` | invariant | A message `on_submit` accepted is never reported to the client as failed. The model has no network faults, so a client retry would be a duplicate. |
| `NoGhostSession` | invariant | Once the socket is closed and every handler has run, the session is gone from `_clients`, so it no longer counts against `max_connections`. |
| `ReportedOnce` | invariant | `on_client_disconnected` fires at most once per session. |
| `StateAgreement` | invariant | `SMPPClient.is_bound` agrees with its `SMPPConnection.state`. |
| `Terminates` | liveness | Both ends close and every handler finishes. |
| `Reported` | liveness | `on_client_disconnected` fires for the session. |
| no deadlock | TLC built-in | No reachable state where nothing can move but work is left. |

## Each fix is a switch

Every fix is a constant in the spec. `check.sh` checks the code as it is,
then switches each fix off in turn. TLC must find the bug again, which
shows that the model can see it:

| Config | Switched off | TLC reports |
|---|---|---|
| `Fixed` | nothing | no error |
| `LostAck` | unbind waits for in-flight requests (`Drain = "none"`, as in 0.9.0) | `NoLostAck` violated: unbind answers and closes while `on_submit` is still running |
| `DrainDeadlock` | unbind waits only for *earlier* requests (`Drain = "others"`) | deadlock: two unbinds wait for each other; in the code, a 30 s stall until `shutdown_timeout` |
| `GhostSession` | unbind removes the session (`ReleaseOnUnbind`) | `NoGhostSession` violated: `disconnect()` never reports a lost connection |
| `DoubleReport` | once-only reporting (`ReportOnce`) | `ReportedOnce` violated: unbind and the client's EOF both report |
| `StaleState` | client unbind resets the connection state (`ClearOnUnbind`) | `StateAgreement` violated |
| `NoFifoStart` | asyncio starting tasks in creation order (`FifoStart`) | `NoLostAck` violated |

The last row is an assumption the code relies on, not a fix. A `submit_sm`
that arrives after an `unbind` is refused only because the unbind task
starts, and clears `bound`, before the submit task does. asyncio guarantees
this, because `create_task` schedules tasks with `call_soon`, which runs
them in order.

## Not modelled yet

The model leaves out:

- bind, including async `authenticate`;
- `enquire_link`;
- the server's `stop()` and its shutdown notifications;
- network failures;
- server-initiated `deliver_sm`.

Adding `stop()` next would cover the one known remaining corner. If
`stop()` is awaited from inside an `on_submit` while the same client
unbinds, the unbind waits for that handler, and `stop()` waits for the
unbind. Timeouts end this, but only after `shutdown_timeout`.
