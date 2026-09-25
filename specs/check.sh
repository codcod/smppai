#!/usr/bin/env bash
# Model-check SmppSession.tla with TLC: the code as it is must pass, and
# switching off any one fix must bring back the bug it fixed.
#
#   specs/check.sh [path/to/tla2tools.jar]   (default: $TLA2TOOLS or specs/tla2tools.jar)
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
jar="${1:-${TLA2TOOLS:-$here/tla2tools.jar}}"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cp "$here/SmppSession.tla" "$work/"

# check NAME EXPECT DRAIN RELEASE REPORT_ONCE CLEAR FIFO
#   EXPECT: "ok", "deadlock", or the invariant/property TLC must report violated
check() {
    local name=$1 expect=$2
    cat > "$work/$name.cfg" <<EOF
CONSTANTS
    NSubmits = 2
    NUnbinds = 2
    Drain = "$3"
    ReleaseOnUnbind = $4
    ReportOnce = $5
    ClearOnUnbind = $6
    FifoStart = $7
SPECIFICATION Spec
INVARIANTS TypeOK NoLostAck NoGhostSession ReportedOnce StateAgreement
PROPERTIES Terminates Reported
EOF
    local out
    out="$(cd "$work" && java -XX:+UseParallelGC -cp "$jar" tlc2.TLC \
        -config "$name.cfg" -workers auto -cleanup SmppSession.tla 2>&1 || true)"

    local got
    if grep -q 'Model checking completed. No error has been found' <<<"$out"; then
        got=ok
    elif grep -q 'Deadlock reached' <<<"$out"; then
        got=deadlock
    else
        got="$(grep -oE '(Invariant|Temporal properties?) [A-Za-z]+ (is|was) violated' <<<"$out" \
            | head -1 | awk '{print $(NF-2)}')"
        [[ -n $got ]] || got="$(grep -oE 'Temporal properties were violated' <<<"$out" | head -1)"
    fi

    local states
    states="$(grep -oE '[0-9]+ distinct states found' <<<"$out" | tail -1 || true)"
    if [[ $got == "$expect" ]]; then
        printf 'ok    %-14s -> %s (%s)\n' "$name" "$expect" "${states:-n/a}"
    else
        printf 'FAIL  %-14s expected %s, got %s\n%s\n' "$name" "$expect" "${got:-?}" "$out"
        return 1
    fi
}

status=0
#     name            expect          drain     release report clear fifo
check Fixed           ok              earlier   TRUE    TRUE   TRUE  TRUE  || status=1
check LostAck         NoLostAck       none      TRUE    TRUE   TRUE  TRUE  || status=1
check DrainDeadlock   deadlock        others    TRUE    TRUE   TRUE  TRUE  || status=1
check GhostSession    NoGhostSession  earlier   FALSE   TRUE   TRUE  TRUE  || status=1
check DoubleReport    ReportedOnce    earlier   TRUE    FALSE  TRUE  TRUE  || status=1
check StaleState      StateAgreement  earlier   TRUE    TRUE   FALSE TRUE  || status=1
check NoFifoStart     NoLostAck       earlier   TRUE    TRUE   TRUE  FALSE || status=1
exit $status
