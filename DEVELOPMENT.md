# Development

**Clone and open the repo in Claude Code — you have a live dev server.** The
committed `.mcp.json` registers `libre` to run `./bin/run.sh`, which launches the
server from your working tree (`uv run libre-mcp`) over stdio, so it always runs
your current source — no build or reinstall. Approve it when prompted and test
your changes directly.

```bash
git clone https://github.com/krondor-corp/libre-mcp
cd libre-mcp && claude        # approve the `libre` server when prompted
```

Requires [uv](https://docs.astral.sh/uv/) and LibreOffice; `bin/run.sh` handles
deps and per-branch profile isolation, so multiple worktrees run independently.

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
