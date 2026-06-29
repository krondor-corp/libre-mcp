# Development

**Clone and open the repo in Claude Code — you have a live dev server with
hot-reload.** The committed `.mcp.json` runs `./bin/run.sh --dev`, which launches
the server from your working tree (`uv run libre-mcp`) over stdio in debug mode.

```bash
git clone https://github.com/krondor-corp/libre-mcp
cd libre-mcp && claude        # approve the `libre` server when prompted
```

Requires [uv](https://docs.astral.sh/uv/) and LibreOffice; `bin/run.sh` handles
deps and per-branch profile isolation, so multiple worktrees run independently.

## Hot-reload

In dev mode (`bin/run.sh --dev`, i.e. `LIBRE_MCP_LOG_LEVEL=DEBUG`) the server
watches `src/office/uno_worker.py` and restarts the worker on change, so edits to
the **document logic** (the `op_*` methods — where the real work is) take effect
on the **next tool call, with no MCP reconnect**. Tools are thin pass-throughs to
those ops, so this covers the common iteration loop.

Changes to the **tool surface** (adding/renaming a tool, its args) still need a
reconnect — the tool list is sent to the client once at `initialize` and cached
client-side, which no stdio server can swap live. Reconnect with `/mcp` →
reconnect `libre`, or restart the session.

`make dev` runs the same `./bin/run.sh --dev` standalone.

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
| `LIBRE_MCP_LOG_LEVEL` | `INFO` | stderr log level |

See [RELEASES.md](RELEASES.md) for the release process.
