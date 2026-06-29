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

You need **LibreOffice installed** to develop (the live tests drive it). The
committed `.mcp.json` registers two servers: **`libre`** (the installed
`libre-mcp` binary, stable) and **`libre-dev`** (`./bin/run.sh --dev`, run from
source with hot-reload — use this while developing).

```bash
make sync          # install dev deps (uv)
make check         # black, ruff, ty, pytest (live integration runs if LibreOffice is present)
make install       # build + install the binary to ~/.local/bin
```

`make check` must pass before committing — it runs the MCP-stdio protocol test
and the session/worker integration tests. For interactive testing use the
registered `libre` MCP server or `make inspect`. See `DEVELOPMENT.md`.

## Dev hot-reload (tight feedback loop)

The **`libre-dev`** server runs `./bin/run.sh --dev` (debug mode), and in debug
mode the server watches the source and reloads so you can iterate without
reconnecting:

- **Edit an `op_*` method in `src/office/uno_worker.py`** (the document logic) →
  the UNO worker restarts; the change is live on the **next tool call**. Open
  `doc_id`s are dropped on reload — just recreate. This is the common loop, since
  tools are thin pass-throughs to these ops.
- **Edit a tool in `src/tools/*.py`** (add / rename / change a tool in an
  existing group file) → the tool surface is re-registered and the server pushes
  `notifications/tools/list_changed` so the client re-fetches. No reconnect.
- **A brand-new tool *group* file** (a new `src/tools/<x>.py`) still needs a
  server restart — it isn't imported until you add it to `_TOOL_MODULES` in
  `src/server.py`. Reconnect with `/mcp` → reconnect `libre`.

Hot-reload only runs in debug mode (`LIBRE_MCP_LOG_LEVEL=DEBUG`, set by
`--dev`); the shipped binary never reloads. Mechanism lives in `src/server.py`
(`_watch_and_reload`) + `OfficeSession.reload_worker`.

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

## Agent tooling (portability)

This repo uses the cross-agent standards so its guidance and skills work beyond
Claude Code:

- **Instructions** — `AGENTS.md` (this file) is canonical and read natively by
  most agents (OpenAI Codex, Cursor, GitHub Copilot, Gemini CLI, Zed, Windsurf,
  …). Claude Code reads `CLAUDE.md`, which just imports this file (`@AGENTS.md`),
  so both see the same content with no duplication.
- **Skills** — the `/docs` skill follows the open
  [agentskills.io](https://agentskills.io) `SKILL.md` spec (required frontmatter:
  `name` + `description`; keep the body short). It lives in `.claude/skills/`
  (read by Claude Code, and auto-discovered by GitHub Copilot and Cursor) and is
  exposed at `.agents/skills/` (a symlink) for OpenAI Codex.

To fan these out to directory-of-rules tools (`.cursor/rules/`,
`.github/instructions/`, `.windsurf/rules/`) or add `GEMINI.md`/Aider bridges, a
sync tool like [ruler](https://github.com/intellectronica/ruler) or
[rulesync](https://github.com/dyoshikawa/rulesync) can generate them from this
single source.

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
