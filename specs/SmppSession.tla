---------------------------- MODULE SmppSession ----------------------------
(***************************************************************************)
(* One bound ESME session against SMPPServer, from bound to closed:        *)
(* pipelined submit_sm, the client's unbind (possibly twice), and both     *)
(* ends closing the socket.                                                *)
(*                                                                         *)
(* Code: src/smpp/server/server.py (_handle_client_pdu, _handle_submit_sm, *)
(* _handle_unbind_request, _handle_client_disconnected) and the unbind     *)
(* paths of src/smpp/client/client.py.                                     *)
(*                                                                         *)
(* asyncio runs a task without interruption between two awaits, so each   *)
(* action below is the code between two awaits of one task. The server's  *)
(* handler tasks for this session are `tasks`, in arrival order, like      *)
(* ClientSession._tasks. Timeouts are not modelled: a wait that only a     *)
(* timeout ends is a stall (30 s by default), so it shows up as a deadlock.*)
(*                                                                         *)
(* Each fix is a constant, so a config can switch one off and check that   *)
(* TLC finds the bug again; see README.md.                                 *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS
    NSubmits,        \* submit_sm the client may send
    NUnbinds,        \* unbind the client may send; 2 = unbind() called twice
    Drain,           \* what an unbind waits for before unbind_resp:
                     \*   "earlier" requests (fixed), all "others", or "none" (0.9.0)
    ReleaseOnUnbind, \* unbind drops the session from _clients and reports it
    ReportOnce,      \* on_client_disconnected fires at most once per session
    ClearOnUnbind,   \* the client's unbind returns SMPPConnection.state to OPEN
    FifoStart        \* asyncio starts tasks in the order they were created

ASSUME /\ NSubmits \in Nat /\ NUnbinds \in Nat \ {0}
       /\ Drain \in {"earlier", "others", "none"}
       /\ {ReleaseOnUnbind, ReportOnce, ClearOnUnbind, FifoStart} \subseteq BOOLEAN

SubmitIds == 1..NSubmits
UnbindIds == NSubmits + 1 .. NSubmits + NUnbinds

VARIABLES
    c2s, s2c,      \* the socket's two directions, as FIFO queues of PDUs
    srvOpen,       \* server end open: its receive loop still reads
    cliOpen,       \* client end open
    cli,           \* client: "bound", "unbinding" (unbind sent), "done" (unbind returned)
    cliBound,      \* SMPPClient._bound
    cliConnState,  \* the client's SMPPConnection.state: "BOUND", "OPEN" or "CLOSED"
    sent,          \* request ids the client has sent
    waiting,       \* requests the client awaits a response to (_pending_pdus)
    answered,      \* submit ids the client got ESME_ROK for
    failed,        \* submit ids the client saw fail with no response
    bound,         \* ClientSession.bound
    tracked,       \* the session is in SMPPServer._clients
    reports,       \* calls of on_client_disconnected for the session
    reported,      \* ClientSession._disconnect_reported
    tasks,         \* the session's in-flight handler tasks, in arrival order
    lost,          \* a spawned _handle_client_disconnected (connection lost) is pending
    accepted       \* submit ids on_submit accepted, e.g. stored in a database

vars == <<c2s, s2c, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
          waiting, answered, failed, bound, tracked, reports, reported, tasks,
          lost, accepted>>

Task == [id: SubmitIds \cup UnbindIds, kind: {"submit", "unbind"},
         pc: {"new", "handler", "drain", "close", "release"},
         waitFor: SUBSET (SubmitIds \cup UnbindIds)]

TypeOK ==
    /\ srvOpen \in BOOLEAN /\ cliOpen \in BOOLEAN /\ cliBound \in BOOLEAN
    /\ cli \in {"bound", "unbinding", "done"}
    /\ cliConnState \in {"BOUND", "OPEN", "CLOSED"}
    /\ sent \subseteq SubmitIds \cup UnbindIds /\ waiting \subseteq sent
    /\ answered \subseteq SubmitIds /\ failed \subseteq SubmitIds
    /\ bound \in BOOLEAN /\ tracked \in BOOLEAN /\ reported \in BOOLEAN
    /\ reports \in Nat /\ lost \in BOOLEAN /\ accepted \subseteq SubmitIds
    /\ \A k \in DOMAIN tasks : tasks[k] \in Task

Init ==
    /\ c2s = <<>> /\ s2c = <<>>
    /\ srvOpen = TRUE /\ cliOpen = TRUE
    /\ cli = "bound" /\ cliBound = TRUE /\ cliConnState = "BOUND"
    /\ sent = {} /\ waiting = {} /\ answered = {} /\ failed = {}
    /\ bound = TRUE /\ tracked = TRUE /\ reports = 0 /\ reported = FALSE
    /\ tasks = <<>> /\ lost = FALSE /\ accepted = {}

(* A server write reaches the client only while both ends are open *)
Send(m) == s2c' = IF srvOpen /\ cliOpen THEN Append(s2c, m) ELSE s2c

Remove(k) == [j \in 1..Len(tasks) - 1 |-> IF j < k THEN tasks[j] ELSE tasks[j + 1]]

SetPc(k, pc) == tasks' = [tasks EXCEPT ![k].pc = pc]

(* _handle_client_disconnected: stop tracking, then report *)
Report ==
    /\ tracked' = FALSE
    /\ IF ReportOnce /\ reported
         THEN UNCHANGED <<reports, reported>>
         ELSE reports' = reports + 1 /\ reported' = TRUE

---------------------------------------------------------------------------
(* Client. submit_sm and unbind() only check _bound, which stays TRUE     *)
(* until an unbind returns, so both may be sent while an unbind is out.   *)

CliSubmit(i) ==
    /\ cliOpen /\ cliBound /\ i \notin sent
    /\ c2s' = Append(c2s, [type |-> "submit", id |-> i])
    /\ sent' = sent \cup {i} /\ waiting' = waiting \cup {i}
    /\ UNCHANGED <<s2c, srvOpen, cliOpen, cli, cliBound, cliConnState, answered,
                   failed, bound, tracked, reports, reported, tasks, lost, accepted>>

CliUnbind(u) ==
    /\ cliOpen /\ cliBound /\ u \notin sent
    /\ c2s' = Append(c2s, [type |-> "unbind", id |-> u])
    /\ sent' = sent \cup {u} /\ waiting' = waiting \cup {u}
    /\ cli' = "unbinding"
    /\ UNCHANGED <<s2c, srvOpen, cliOpen, cliBound, cliConnState, answered,
                   failed, bound, tracked, reports, reported, tasks, lost, accepted>>

(* The receive loop takes a response; an unbind_resp ends unbind(), whose  *)
(* finally clears the bind, and the application goes on to disconnect.    *)
CliRecv ==
    /\ cliOpen /\ s2c # <<>>
    /\ LET m == Head(s2c) IN
         /\ s2c' = Tail(s2c)
         /\ waiting' = waiting \ {m.id}
         /\ IF m.type = "submit_resp"
              THEN /\ answered' = IF m.ok THEN answered \cup {m.id} ELSE answered
                   /\ UNCHANGED <<cli, cliBound, cliConnState>>
              ELSE /\ cli' = "done" /\ cliBound' = FALSE
                   /\ cliConnState' = IF ClearOnUnbind THEN "OPEN" ELSE cliConnState
                   /\ UNCHANGED answered
    /\ UNCHANGED <<c2s, srvOpen, cliOpen, sent, failed, bound, tracked,
                   reports, reported, tasks, lost, accepted>>

(* disconnect(), or the receive loop seeing EOF: whatever is still awaited fails *)
CliClose ==
    /\ cliOpen
    /\ \/ cli = "done"
       \/ ~srvOpen /\ s2c = <<>>
    /\ cliOpen' = FALSE /\ cliConnState' = "CLOSED" /\ cliBound' = FALSE
    /\ failed' = failed \cup (waiting \cap SubmitIds) /\ waiting' = {}
    /\ s2c' = <<>>
    /\ UNCHANGED <<c2s, srvOpen, cli, sent, answered, bound, tracked, reports,
                   reported, tasks, lost, accepted>>

---------------------------------------------------------------------------
(* Server receive loop: each request becomes a handler task (_spawn)      *)

SrvRecv ==
    /\ srvOpen /\ c2s # <<>>
    /\ tasks' = Append(tasks, [id |-> Head(c2s).id, kind |-> Head(c2s).type,
                               pc |-> "new", waitFor |-> {}])
    /\ c2s' = Tail(c2s)
    /\ UNCHANGED <<s2c, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
                   waiting, answered, failed, bound, tracked, reports, reported,
                   lost, accepted>>

(* EOF after the client closed: on_connection_lost spawns                 *)
(* _handle_client_disconnected, which runs later                          *)
SrvEof ==
    /\ srvOpen /\ ~cliOpen /\ c2s = <<>>
    /\ srvOpen' = FALSE /\ lost' = TRUE
    /\ UNCHANGED <<c2s, s2c, cliOpen, cli, cliBound, cliConnState, sent, waiting,
                   answered, failed, bound, tracked, reports, reported, tasks,
                   accepted>>

SrvLost ==
    /\ lost /\ lost' = FALSE
    /\ Report
    /\ UNCHANGED <<c2s, s2c, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
                   waiting, answered, failed, bound, tasks, accepted>>

(* create_task schedules with call_soon, so a task's first step comes     *)
(* after the first steps of the tasks created before it                   *)
Started(k) == FifoStart => \A j \in 1..k - 1 : tasks[j].pc # "new"

(* _handle_submit_sm, up to awaiting on_submit                            *)
SubmitStart(k) ==
    /\ tasks[k].kind = "submit" /\ tasks[k].pc = "new" /\ Started(k)
    /\ IF bound
         THEN SetPc(k, "handler") /\ UNCHANGED s2c
         ELSE /\ Send([type |-> "submit_resp", id |-> tasks[k].id, ok |-> FALSE])
              /\ tasks' = Remove(k)
    /\ UNCHANGED <<c2s, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
                   waiting, answered, failed, bound, tracked, reports, reported,
                   lost, accepted>>

(* on_submit returns: the message is taken, and submit_sm_resp is written *)
SubmitDone(k) ==
    /\ tasks[k].kind = "submit" /\ tasks[k].pc = "handler"
    /\ accepted' = accepted \cup {tasks[k].id}
    /\ Send([type |-> "submit_resp", id |-> tasks[k].id, ok |-> TRUE])
    /\ tasks' = Remove(k)
    /\ UNCHANGED <<c2s, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
                   waiting, answered, failed, bound, tracked, reports, reported,
                   lost>>

(* _handle_unbind_request: refuse new requests, pick what to wait for     *)
UnbindStart(k) ==
    /\ tasks[k].kind = "unbind" /\ tasks[k].pc = "new" /\ Started(k)
    /\ bound' = FALSE
    /\ tasks' = [tasks EXCEPT
                   ![k].pc = "drain",
                   ![k].waitFor =
                     CASE Drain = "earlier" -> {tasks[j].id : j \in 1..k - 1}
                       [] Drain = "others"  -> {tasks[j].id : j \in DOMAIN tasks \ {k}}
                       [] Drain = "none"    -> {}]
    /\ UNCHANGED <<c2s, s2c, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
                   waiting, answered, failed, tracked, reports, reported, lost,
                   accepted>>

(* Those tasks are done: write unbind_resp *)
UnbindReply(k) ==
    /\ tasks[k].kind = "unbind" /\ tasks[k].pc = "drain"
    /\ \A j \in DOMAIN tasks : tasks[j].id \notin tasks[k].waitFor
    /\ Send([type |-> "unbind_resp", id |-> tasks[k].id])
    /\ SetPc(k, "close")
    /\ UNCHANGED <<c2s, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
                   waiting, answered, failed, bound, tracked, reports, reported,
                   lost, accepted>>

(* connection.disconnect(): the receive loop is cancelled, unread requests *)
(* are dropped, and no connection loss is reported                         *)
UnbindClose(k) ==
    /\ tasks[k].kind = "unbind" /\ tasks[k].pc = "close"
    /\ srvOpen' = FALSE /\ c2s' = <<>>
    /\ tasks' = IF ReleaseOnUnbind THEN [tasks EXCEPT ![k].pc = "release"]
                                   ELSE Remove(k)
    /\ UNCHANGED <<s2c, cliOpen, cli, cliBound, cliConnState, sent, waiting,
                   answered, failed, bound, tracked, reports, reported, lost,
                   accepted>>

UnbindRelease(k) ==
    /\ tasks[k].kind = "unbind" /\ tasks[k].pc = "release"
    /\ Report
    /\ tasks' = Remove(k)
    /\ UNCHANGED <<c2s, s2c, srvOpen, cliOpen, cli, cliBound, cliConnState, sent,
                   waiting, answered, failed, bound, lost, accepted>>

---------------------------------------------------------------------------

Quiescent == ~srvOpen /\ ~cliOpen /\ tasks = <<>> /\ ~lost

(* Everything finished: stutter, so that TLC's deadlock check only flags *)
(* states where something is stuck                                       *)
Finished == Quiescent /\ UNCHANGED vars

Next ==
    \/ \E i \in SubmitIds : CliSubmit(i)
    \/ \E u \in UnbindIds : CliUnbind(u)
    \/ CliRecv \/ CliClose
    \/ SrvRecv \/ SrvEof \/ SrvLost
    \/ \E k \in DOMAIN tasks :
         \/ SubmitStart(k) \/ SubmitDone(k)
         \/ UnbindStart(k) \/ UnbindReply(k) \/ UnbindClose(k) \/ UnbindRelease(k)
    \/ Finished

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

---------------------------------------------------------------------------
(* Invariants                                                             *)

(* A message the server took is never reported to the client as failed:   *)
(* no socket fails in this model, so a client retry would be a duplicate  *)
NoLostAck == accepted \cap failed = {}

(* Once the socket is closed and every handler has run, the server no     *)
(* longer counts the session against max_connections                     *)
NoGhostSession == Quiescent => ~tracked

ReportedOnce == reports <= 1

(* SMPPClient.is_bound agrees with its connection's state *)
StateAgreement == cliOpen => (cliBound <=> cliConnState = "BOUND")

(* Properties                                                             *)

(* The session always winds down: both ends close, every handler finishes *)
Terminates == <>Quiescent

(* ...and on_client_disconnected fires for it *)
Reported == <>(reports >= 1)
=============================================================================
