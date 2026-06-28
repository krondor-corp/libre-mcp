# libre-mcp

A stdio MCP server that controls headless LibreOffice (Writer, Calc, Impress)
over UNO. Two processes: a Python `mcp` server (`src/`) supervises a headless
`soffice` and a stdlib-only UNO worker (`src/office/uno_worker.py`) that runs
under LibreOffice's own Python.

- Develop: `DEVELOPMENT.md` · Release: `RELEASES.md`
- Test the server end to end: invoke the **`/test-libre-mcp`** skill.

## When you implement a feature

After adding or changing a tool, export format, or document type, **invoke the
`/docs` skill** and follow it. It is the checklist for keeping documentation in
sync so the new capability is reflected for both humans and agents:

- the tool tables (`README.md` + `wiki/_docs/tools.md`),
- the agent guide (`wiki/llms.txt`) — add a recipe if it's a new deliverable,
- and the headline copy when it's a new document type or output format.

`wiki/llms.txt` is the canonical, minimal usage guide for agents driving the
server (served at libre-mcp.krondor.org/llms.txt). Keep it current.

## Conventions

- `make check` (black, ruff, ty, pytest) must pass; tools live one-group-per-file
  under `src/tools/`, backed by ops in `src/office/uno_worker.py`.
- The UNO worker is **stdlib-only** (it runs under LibreOffice's reduced Python).
