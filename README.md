# libre-mcp

A stdio [MCP](https://modelcontextprotocol.io) server for controlling
**LibreOffice** (Writer and Calc) from Claude Code and other MCP clients, over
the UNO automation API. macOS and Linux.

## Architecture

Two processes, both Python:

Full docs: **[libre-mcp.krondor.org](https://libre-mcp.krondor.org)**.

```
Claude Code ──stdio JSON-RPC──▶  libre-mcp server   (uv, Python >=3.12, mcp SDK)
                                      │ spawns + supervises
                                      ├─▶ headless soffice   (isolated profile + named pipe)
                                      └─▶ uno_worker.py       (LibreOffice's Python, stdlib-only)
                                            └─ newline-JSON RPC over stdio
```

- The **server** owns the MCP stdio channel, defines the tools, and supervises
  the other two processes. It runs on a normal uv-managed Python ≥3.12 with the
  `mcp` SDK.
- A headless **soffice** is launched with an isolated `UserInstallation` profile
  and a **unique named pipe** (not a TCP port), so concurrent instances never
  race over a shared port — important for parallel git worktrees.
- The **UNO worker** (`src/office/uno_worker.py`) runs under LibreOffice's
  Python — the only interpreter that can reliably `import uno`. It is
  intentionally **stdlib-only**, so there is nothing to install alongside
  LibreOffice. (On Debian/Ubuntu it falls back to the system `python3` provided
  by `python3-uno`.)

Instances are disposable: if the URP bridge is disposed (soffice died), the
worker reports a fatal error and the session is rebuilt, retrying the call once.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
claude mcp add libre -- libre-mcp
```

Downloads a prebuilt, self-contained binary (no Python needed on the host).
Update in place with `libre-mcp update`.

## Requirements

- LibreOffice installed:
  - macOS: `/Applications/LibreOffice.app`
  - Debian/Ubuntu: `apt install libreoffice-writer libreoffice-calc python3-uno`
  - TDF/opt Linux builds bundle their own Python and need nothing extra.

Paths are auto-discovered; override with `LIBRE_MCP_SOFFICE_PATH` /
`LIBRE_MCP_PYTHON_PATH` if needed. (`uv` is only needed for development.)

## Develop

```bash
make sync        # uv sync (dev deps)
make check       # fmt-check + lint + types + test
make inspect     # run the MCP Inspector against the server
```

`make test` runs unit tests always; the end-to-end tests run only when
LibreOffice is found, otherwise they skip.

## Run it locally (dev client)

`dev/client.py` spawns the server exactly as an MCP host would, does the
initialize handshake, and drives tools — no registration needed.

```bash
make dev-list          # list the tools
make dev-demo          # scripted writer -> PDF round-trip
```

For ad-hoc multi-step sessions, pipe `TOOL {json-args}` lines into `run`. A
single `run` keeps one server (and one LibreOffice) alive for the whole batch,
so `doc_id`s persist across calls (first created doc is `doc-1`, next `doc-2`, …):

```bash
uv run python dev/client.py run <<'EOF'
create_document {"kind": "calc"}
set_cells {"doc_id": "doc-1", "cells": [{"cell": "A1", "value": 21}, {"cell": "A2", "formula": "=A1*2"}]}
read_cells {"doc_id": "doc-1", "range": "A1:A2"}
EOF
```

## Register with Claude Code

A project-scoped `.mcp.json` is committed with a **relative** command
(`./bin/run.sh`), so a fresh checkout / worktree self-registers and runs its own
copy. Or register explicitly:

```bash
claude mcp add --transport stdio libre -- $(pwd)/bin/run.sh
```

## Parallel worktrees

The design is worktree-safe by construction:

- **Unique named pipe per instance** — no shared TCP port to race over, so two
  worktrees (or two sessions) starting at the same moment never collide.
- **cwd-relative profiles** — `.lo_profiles/instance-<pipe>` lives under each
  worktree's own directory, fully isolated and gitignored.
- **Clean reaping** — the server tears down its soffice + worker when the client
  disconnects (lifespan hook), so worktrees don't leak LibreOffice processes.
- **Relative `.mcp.json`** — each worktree registers/runs its own `bin/run.sh`.

## Tools

| Tool | Purpose |
|------|---------|
| `create_document(kind)` | New writer/calc/impress/draw doc → `doc_id` |
| `open_document(path)` | Open a file → `doc_id` |
| `list_documents()` / `document_info(doc_id)` | Inspect open docs |
| `save_document(doc_id, path?, format?)` | Save in place or to a path |
| `export_document(doc_id, path, format?)` | Export (pdf, docx, xlsx, csv, …) |
| `close_document(doc_id)` | Close a doc |
| `get_text(doc_id)` | Read a Writer doc's text |
| `insert_text(doc_id, text, paragraph_break?)` | Append text |
| `find_and_replace(doc_id, search, replace, regex?)` | Replace text |
| `set_cells(doc_id, cells, sheet?)` | Write Calc cells/formulas |
| `read_cells(doc_id, range, sheet?)` | Read a Calc range |

## Configuration

| Env var | Default | Meaning |
|---------|---------|---------|
| `LIBRE_MCP_SOFFICE_PATH` | auto | soffice binary override |
| `LIBRE_MCP_PYTHON_PATH` | auto | bundled python override |
| `LIBRE_MCP_PROFILE_DIR` | `./.lo_profiles` | per-instance profile root |
| `LIBRE_MCP_KEEP_PROFILE` | `false` | keep profiles for debugging |
| `LIBRE_MCP_STARTUP_TIMEOUT` | `30` | seconds to wait for soffice |
| `LIBRE_MCP_LOG_LEVEL` | `INFO` | stderr log level |

UNO transport uses a **unique named pipe** per instance (not a TCP port), so
nothing needs configuring and concurrent instances never collide.
