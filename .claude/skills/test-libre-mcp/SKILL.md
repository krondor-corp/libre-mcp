---
name: test-libre-mcp
description: Smoke-test and validate the libre-mcp server end to end — run the quality gate and drive live LibreOffice document round-trips (Writer + Calc + export) through the real MCP stdio protocol. Use after editing tools/worker/session/server code, when verifying the server works in this environment, or before cutting a release. Requires LibreOffice installed.
---

# Testing the libre-mcp server

libre-mcp is a stdio MCP server that controls LibreOffice over UNO. This skill
verifies it works, end to end, in an environment that has LibreOffice installed.

## Key facts that shape testing

- **Stateless across runs.** Open documents live only for the lifetime of one
  server process. Each `dev/client.py run` invocation spawns a *fresh* server +
  LibreOffice, so `doc_id`s (doc-1, doc-2, …) only persist **within a single
  `run`**. To test a multi-step flow, put every command in one `run`.
- **Self-isolating.** Each instance uses a unique named pipe + a per-branch
  profile dir, so tests never collide with a running server or another worktree.
- **Use `scratch/` for outputs.** It's git-kept but its contents are gitignored.
  Write exported files there (or `/tmp`), never into the tree.
- **Needs LibreOffice.** The integration tests auto-skip without it; this skill
  assumes it's present (macOS: `/Applications/LibreOffice.app`; Linux: distro/TDF
  package). Override discovery with `LIBRE_MCP_SOFFICE_PATH` / `LIBRE_MCP_PYTHON_PATH`.

## Procedure

### 1. Preflight
```bash
make sync             # uv sync (dev deps)
```
Confirm LibreOffice is discoverable (this prints the soffice + bundled-python paths or errors):
```bash
uv run python -c "from src.office import discovery as d; s=d.find_soffice(None); print(s); print(d.find_bundled_python(None, s))"
```

### 2. Quality gate
```bash
make check            # black --check, ruff, ty, pytest (incl. integration if LO present)
```
All four must pass. The integration tests already cover a Writer round-trip +
PDF export and a Calc formula; if they ran (didn't skip), the core path is good.

### 3. Live smoke test over real MCP stdio
Drive the server exactly as an MCP host would, in one persistent session, writing
outputs to `scratch/`:
```bash
uv run python dev/client.py run <<'EOF'
create_document {"kind": "writer"}
insert_text {"doc_id": "doc-1", "text": "libre-mcp skill smoke test"}
get_text {"doc_id": "doc-1"}
export_document {"doc_id": "doc-1", "path": "PWD/scratch/skill_test.pdf"}
create_document {"kind": "calc"}
set_cells {"doc_id": "doc-2", "cells": [{"cell": "A1", "value": 6}, {"cell": "A2", "value": 7}, {"cell": "A3", "formula": "=A1*A2"}]}
read_cells {"doc_id": "doc-2", "range": "A3:A3"}
EOF
```
Replace `PWD` with the absolute repo path (export paths must be absolute). Expect:
`get_text` echoes the inserted line, `read_cells` returns `42.0`, and
`export_document` reports the written path.

`make dev-list` (list tools) and `make dev-demo` (canned Writer→PDF) are quick
sanity checks too.

### 4. Verify artifacts
```bash
test "$(head -c5 scratch/skill_test.pdf)" = "%PDF-" && echo "pdf ok"
```

### 5. Concurrency check (optional, for worktree/parallel changes)
Run two `run` sessions at once and confirm both return correct, independent
results — this is what catches instance-isolation regressions.

## Interpreting failures

- `unknown doc_id: doc-N` across separate `run`s → expected (stateless); combine
  into one `run`.
- `could not locate the soffice binary` → LibreOffice not installed / not found;
  set `LIBRE_MCP_SOFFICE_PATH`.
- Worker/`DisposedException` → the session auto-restarts once; persistent failure
  means soffice is crashing (check the per-branch `.lo_profiles/<branch>/instance-*/soffice.log`).
