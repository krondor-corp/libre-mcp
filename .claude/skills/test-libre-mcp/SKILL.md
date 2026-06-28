---
name: test-libre-mcp
description: Smoke-test and validate the libre-mcp server end to end — run the quality gate (which drives the real MCP stdio protocol and live LibreOffice round-trips for Writer, Calc, and Impress) and optionally exercise the registered server by hand. Use after editing tools/worker/session/server code, when verifying the server works in this environment, or before cutting a release. Requires LibreOffice installed.
---

# Testing the libre-mcp server

libre-mcp is a stdio MCP server that controls LibreOffice over UNO. This skill
verifies it works end to end in an environment with LibreOffice installed.

## Key facts

- **Documents are per-process.** They live only for the lifetime of one running
  server process and are referenced by `doc_id`; a fresh server starts numbering
  at `doc-1`.
- **Self-isolating.** Each instance uses a unique named pipe + a per-branch
  profile dir, so tests never collide with a running server or another worktree.
- **Use `scratch/` for outputs** — git-kept, contents gitignored. Never write
  exports into the tree.
- **Needs LibreOffice** (macOS: `/Applications/LibreOffice.app`; Linux:
  distro/TDF package). Override discovery with `LIBRE_MCP_SOFFICE_PATH` /
  `LIBRE_MCP_PYTHON_PATH`.

## Procedure

### 1. Preflight
```bash
make sync     # uv sync (dev deps)
uv run python -c "from src.office import discovery as d; s=d.find_soffice(None); print(s); print(d.find_bundled_python(None, s))"
```
The second line prints the soffice + interpreter paths, or a DiscoveryError.

### 2. Quality gate (the core validation)
```bash
make check    # black --check, ruff, ty, pytest
```
The suite includes `tests/test_mcp_stdio.py` (drives the server over the real MCP
stdio protocol: initialize → tools/list → call_tool) and
`tests/test_integration.py` (Writer round-trip + PDF export, Calc formula). With
LibreOffice present these run live; if they ran (didn't skip), the core path is
good.

### 3. Manual exploration (optional)
Drive the registered `libre` MCP server directly — create a document, edit it,
and export to `scratch/` — then verify the artifact:
```bash
test "$(head -c5 scratch/out.pdf)" = "%PDF-" && echo "pdf ok"
```
`make inspect` launches the MCP Inspector against the server as an alternative.

## Interpreting failures

- `could not locate the soffice binary` / a python that can `import uno` →
  LibreOffice not installed/found; set `LIBRE_MCP_SOFFICE_PATH` /
  `LIBRE_MCP_PYTHON_PATH` (Debian/Ubuntu also need `python3-uno`).
- Worker / `DisposedException` → the session auto-restarts once; a persistent
  failure means soffice is crashing — check
  `.lo_profiles/<branch>/instance-*/soffice.log`.
