# Development

**Clone and open the repo in Claude Code — you have a live dev server with
hot-reload.** The committed `.mcp.json` registers two servers:

- **`libre`** — the installed `libre-mcp` binary (stable; needs `make install`
  or `install.sh` first).
- **`libre-dev`** — `./bin/run.sh --dev --live`, run from your working tree
  (`uv run libre-mcp`) over stdio. **Use this while developing**: `--dev` adds
  debug logging + hot-reload (below) and `--live` opens a **visible LibreOffice
  window** so you can watch documents being built. The two flags are independent.

```bash
git clone https://github.com/krondor-corp/libre-mcp
cd libre-mcp && claude        # approve the `libre` server when prompted
```

Requires [uv](https://docs.astral.sh/uv/) and LibreOffice; `bin/run.sh` handles
deps and per-branch profile isolation, so multiple worktrees run independently.

## Hot-reload

In dev mode (`bin/run.sh --dev`, i.e. `LIBRE_MCP_LOG_LEVEL=DEBUG`) the server
watches the source and reloads, so you iterate without reconnecting:

- **`src/office/uno_worker.py`** (the `op_*` document logic — where the real work
  is) → the UNO worker restarts; live on the **next tool call**. Open `doc_id`s
  are dropped on reload, so recreate them. Tools are thin pass-throughs to these
  ops, so this is the common loop.
- **`src/tools/*.py`** (add / rename / change a tool in an existing group) → the
  tool surface is re-registered and the server pushes
  `notifications/tools/list_changed`, so the client re-fetches. No reconnect.

A **brand-new tool group file** (a new `src/tools/<x>.py`) still needs a restart
— add it to `_TOOL_MODULES` in `src/server.py`, then `/mcp` → reconnect `libre`.

`make dev` runs `./bin/run.sh --dev` standalone (add `--live` for a window).

## Live mode

`--live` (env `LIBRE_MCP_LIVE=1`) launches soffice **non-headless** and pops each
open document into a real LibreOffice window, so you watch the agent build it in
real time instead of export → read-PDF. It needs a display, so it's a local-dev
aid only — the shipped binary and CI always run headless. `--live` is independent
of `--dev`; the committed `.mcp.json` turns both on for `libre-dev`.

## Commands

```bash
make check         # lint, type-check, test (live integration if LibreOffice is present)
make binary        # build dist/libre-mcp
make install       # build + install to ~/.local/bin (override INSTALL_DIR)
```

## Testing

`make check` runs the suite, including:

- `tests/test_mcp_stdio.py` — drives the server over the real MCP stdio protocol
  (initialize → tools/list → call_tool), covering the FastMCP wiring;
- `tests/test_integration.py` — exercises the session/worker/soffice path
  directly.

Live integration tests run only when LibreOffice is found, otherwise they skip
(the tool-listing test always runs). For interactive poking, use the registered
`libre` MCP server in Claude Code, or `make inspect` (the MCP Inspector).

## Configuration

| Env var | Default | Meaning |
|---------|---------|---------|
| `LIBRE_MCP_SOFFICE_PATH` | auto | soffice binary override |
| `LIBRE_MCP_PYTHON_PATH` | auto | LibreOffice python override |
| `LIBRE_MCP_LOG_LEVEL` | `INFO` | stderr log level (`DEBUG` enables hot-reload) |
| `LIBRE_MCP_LIVE` | `false` | run a visible LibreOffice window (needs a display) |

See [RELEASES.md](RELEASES.md) for the release process.
