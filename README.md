# Python implementation of SMPP v3.4 protocol

![workflow](https://github.com/codcod/smppai/actions/workflows/starter.yaml/badge.svg)

[SMPP](https://smpp.org) protocol (v3.4) implementation. At some point in time
also ESME (client) and SMSC (server).

Start OpenSMPP Simulator:

    $ docker compose up -d

Connect to `127.0.0.1` on port 2775 with `smppclient1` as login name and
`password` as password.

    $ make venv
    $ make run

Uses [smpplib](https://github.com/python-smpplib/python-smpplib).

## Useful shell commands

List TCP4 sockets and their state: 

    $ netstat -an -f inet -p tcp |grep -v 192.168

List sockets associated with port 2775 (SMSC Simulator default port):

    $ lsof -nP -i4TCP:2775

Find out the process name related with the socket:

    $ ps -Ao pid,command | grep -v grep | grep <pid>
