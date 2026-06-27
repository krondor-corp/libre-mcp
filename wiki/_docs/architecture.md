---
title: Architecture
slug: architecture
order: 4
description: How libre-mcp drives LibreOffice.
---

Two processes, both Python:

```text
MCP client ──stdio JSON-RPC──▶  libre-mcp server   (uv, Python >=3.12, mcp SDK)
                                    │ spawns + supervises
                                    ├─▶ headless soffice   (isolated profile + named pipe)
                                    └─▶ uno_worker.py       (LibreOffice's Python, stdlib-only)
                                          └─ newline-JSON RPC over stdio
```

## The server

Runs on a normal uv-managed Python ≥3.12 with the `mcp` SDK. It owns the MCP
stdio channel, defines the tools, and supervises the other two processes. It
never imports `uno`.

## The UNO worker

`uno_worker.py` runs under **LibreOffice's own Python interpreter** — the only
one that can reliably `import uno` (pyuno is a native module built against that
interpreter). It is intentionally **stdlib-only**, so there is nothing to
install alongside LibreOffice. It holds the connection to soffice and executes
document operations, keeping open documents keyed by `doc_id`.

## Headless LibreOffice

Launched with `--headless` and a **unique named pipe** plus an isolated
`UserInstallation` profile. Using a named pipe (not a TCP port) means concurrent
instances never race over a shared port — important for parallel git worktrees.

## Resilience

Instances are disposable. If the URP bridge is disposed (soffice died), the
worker reports a fatal error, the session is rebuilt, and the failed call is
retried once. When the MCP client disconnects, the server reaps both soffice and
the worker so nothing is leaked.

## Why Python (not Rust)

The only complete LibreOffice automation binding is PyUNO. A Rust server would
have to shell out to a Python UNO bridge anyway, so the interesting half would be
Python regardless — matching the language to the binding removes a process
boundary.
