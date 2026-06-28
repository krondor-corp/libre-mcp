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

## Testing without Claude

`dev/client.py` drives the server over MCP stdio (`doc_id`s persist across the
commands in one `run`):

```bash
uv run python dev/client.py run <<'EOF'
create_document {"kind": "calc"}
set_cells {"doc_id": "doc-1", "cells": [{"cell": "A1", "value": 21}, {"cell": "A2", "formula": "=A1*2"}]}
read_cells {"doc_id": "doc-1", "range": "A1:A2"}
EOF
```

## Configuration

| Env var | Default | Meaning |
|---------|---------|---------|
| `LIBRE_MCP_SOFFICE_PATH` | auto | soffice binary override |
| `LIBRE_MCP_PYTHON_PATH` | auto | LibreOffice python override |
| `LIBRE_MCP_LOG_LEVEL` | `INFO` | stderr log level |

See [RELEASES.md](RELEASES.md) for the release process.
