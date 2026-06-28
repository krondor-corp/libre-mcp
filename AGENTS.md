# AGENTS.md

Guidance for AI agents working in this repository. Human contributors: see
`README.md`, `DEVELOPMENT.md`, and `RELEASES.md`.

## Project

libre-mcp is a stdio MCP server that controls a headless LibreOffice (Writer,
Calc, Impress) over UNO. Three processes:

- the MCP server (`src/`, Python ≥3.12 + the `mcp` SDK) — owns the stdio channel,
  defines tools, and supervises the others;
- a headless `soffice` (unique named pipe + isolated profile);
- a stdlib-only UNO worker (`src/office/uno_worker.py`) that runs under
  LibreOffice's own Python and does the actual document work.

Tools live one group per file under `src/tools/` (document, writer, calc,
impress), each backed by an `op_*` method in `uno_worker.py`.

## Setup, build, test

```bash
make sync          # install dev deps (uv)
make check         # black, ruff, ty, pytest (live integration runs if LibreOffice is present)
make binary        # build the standalone binary -> dist/libre-mcp
```

`make check` must pass before committing. Drive the running server end to end
with `dev/client.py` (see `DEVELOPMENT.md`), or follow the `test-libre-mcp` skill
(`.claude/skills/test-libre-mcp/SKILL.md`).

## When you implement a feature

After adding or changing a tool, export format, or document type, **update the
docs** following the checklist in `.claude/skills/docs/SKILL.md` (Claude Code:
run the `/docs` skill). Keep these in sync:

- the tool tables — `README.md` (`## Usage`) and `wiki/_docs/tools.md`;
- the agent guide — `wiki/llms.txt` (add a recipe if it's a new deliverable);
- the headline copy — only when it's a new document type or output format
  (`README.md` intro, `wiki/_config.yml`, `wiki/_layouts/home.html`, `wiki/llms.txt`).

`wiki/llms.txt` is the canonical, minimal usage guide for agents that *drive* the
server (served at libre-mcp.krondor.org/llms.txt). Keep it current.

## Conventions

- The UNO worker (`src/office/uno_worker.py`) is **stdlib-only** — it runs under
  LibreOffice's reduced Python; never import third-party packages there.
- Add a tool as a thin `src/tools/*.py` entry that calls a worker op; match the
  surrounding style.
- Commits use conventional-commit prefixes (`feat:`, `fix:`, `docs:`, …); they
  drive the automated release-PR version bump.

## References

Implementing a worker op means calling the LibreOffice UNO API:

- UNO IDL reference: <https://api.libreoffice.org/docs/idl/ref/index.html>
  - Writer — `com.sun.star.text`:
    <https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1text.html>
  - Calc — `com.sun.star.sheet`:
    <https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1sheet.html>
  - Impress — `com.sun.star.presentation`:
    <https://api.libreoffice.org/docs/idl/ref/namespacecom_1_1sun_1_1star_1_1presentation.html>
- Developer's Guide: <https://wiki.documentfoundation.org/Documentation/DevGuide>
- Python / PyUNO scripting: <https://wiki.documentfoundation.org/Macros/Python_Guide>
- Export filter names (for the `_FILTERS` map):
  <https://help.libreoffice.org/latest/en-US/text/shared/guide/convertfilters.html>
- MCP: <https://modelcontextprotocol.io> · Python SDK:
  <https://github.com/modelcontextprotocol/python-sdk>
