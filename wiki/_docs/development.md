---
title: Development
slug: development
order: 5
description: Local development, testing, and building from source.
---

## Setup

Requires [uv](https://docs.astral.sh/uv/) and LibreOffice.

```bash
git clone https://github.com/krondor-corp/libre-mcp
cd libre-mcp
make sync          # install dev deps
make check         # black, ruff, ty, pytest (live integration runs if LibreOffice is present)
```

## Driving the server while you work

`dev/client.py` spawns the server over real MCP stdio and runs tools — no
registration needed. A single `run` keeps one server (and one LibreOffice) alive
for the whole batch, so `doc_id`s persist across the commands in it:

```bash
make dev-list      # list tools
make dev-demo      # scripted writer -> PDF round-trip

uv run python dev/client.py run <<'EOF'
create_document {"kind": "calc"}
set_cells {"doc_id": "doc-1", "cells": [{"cell": "A1", "value": 21}, {"cell": "A2", "formula": "=A1*2"}]}
read_cells {"doc_id": "doc-1", "range": "A1:A2"}
EOF
```

Point it at a built binary instead of source with
`LIBRE_MCP_SERVER_CMD=./dist/libre-mcp`.

## Building the binary

```bash
make binary        # -> dist/libre-mcp
make install       # build + install to ~/.local/bin (override INSTALL_DIR)
```

## Configuration

| Env var | Default | Meaning |
|---------|---------|---------|
| `LIBRE_MCP_SOFFICE_PATH` | auto | soffice binary override |
| `LIBRE_MCP_PYTHON_PATH` | auto | LibreOffice python override |
| `LIBRE_MCP_PROFILE_DIR` | `./.lo_profiles` | per-instance profile root |
| `LIBRE_MCP_KEEP_PROFILE` | `false` | keep profiles for debugging |
| `LIBRE_MCP_STARTUP_TIMEOUT` | `30` | seconds to wait for soffice |
| `LIBRE_MCP_LOG_LEVEL` | `INFO` | stderr log level |

## Releasing

See [RELEASES.md](https://github.com/krondor-corp/libre-mcp/blob/main/RELEASES.md).
