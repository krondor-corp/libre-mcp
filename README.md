# libre-mcp

A stdio [MCP](https://modelcontextprotocol.io) server for controlling
**LibreOffice** (Writer, Calc & Impress) from Claude Code and other MCP clients —
create and edit documents, spreadsheets, and presentations; run formulas; and
export to PDF, DOCX, XLSX, **PPTX**, and more. macOS and Linux.

Full docs: **[libre-mcp.krondor.org](https://libre-mcp.krondor.org)**

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
```

Installs a prebuilt, self-contained binary to `~/.local/bin` (no Python needed on
the host). Update in place with `libre-mcp update`.

From a source checkout instead (needs [uv](https://docs.astral.sh/uv/)):

```bash
make install      # build + install the binary to ~/.local/bin
```

## Connect it to your coding tool

`libre-mcp` is a stdio MCP server, so any MCP-capable client can run it. Make
sure `libre-mcp` is on your `PATH` (or use its absolute path).

**Claude Code**
```bash
claude mcp add libre -- libre-mcp
```

**Cursor** — `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project):
```json
{
  "mcpServers": {
    "libre": { "command": "libre-mcp" }
  }
}
```

**Claude Desktop** — Settings → Developer → Edit Config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "libre": { "command": "libre-mcp" }
  }
}
```

**VS Code** (GitHub Copilot) — `.vscode/mcp.json`, or `code --add-mcp '{"name":"libre","command":"libre-mcp"}'`:
```json
{
  "servers": {
    "libre": { "type": "stdio", "command": "libre-mcp" }
  }
}
```

**Windsurf** — `~/.codeium/windsurf/mcp_config.json`: same `mcpServers` shape as Cursor.

Restart the client (or reload its MCP config) and `libre`'s tools appear.

## Requirements

LibreOffice must be installed:

- **macOS:** `/Applications/LibreOffice.app`
- **Debian/Ubuntu:** `apt install libreoffice-writer libreoffice-calc python3-uno`
- **Other Linux (TDF/opt builds):** bundle their own Python — nothing extra.

Paths are auto-discovered; override with `LIBRE_MCP_SOFFICE_PATH` /
`LIBRE_MCP_PYTHON_PATH` if LibreOffice lives somewhere unusual.

## Usage

Ask your MCP client to work with documents, spreadsheets, or presentations. The
typical flow is **create/open → edit → export** (e.g. build a deck and save it as
`.pptx`); documents stay open (referenced by `doc_id`) until closed.

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
| `add_slide(doc_id, layout?)` | Append an Impress slide |
| `set_slide_content(doc_id, index, title?, bullets?)` | Set a slide's title/bullets |
| `list_slides(doc_id)` / `delete_slide(doc_id, index)` | Inspect / remove slides |

Full arguments and examples: the
[tool reference](https://libre-mcp.krondor.org/docs/tools/).

## Links

- [Documentation](https://libre-mcp.krondor.org)
- [Development](DEVELOPMENT.md)
- [Releases](RELEASES.md)

## Acknowledgements

Built on the work of others:

- [LibreOffice](https://www.libreoffice.org/) and The Document Foundation — the
  office suite and its [UNO](https://www.openoffice.org/udk/) / PyUNO automation
  API that does all the real work.
- [Model Context Protocol](https://modelcontextprotocol.io) and the
  [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk).
- [PyInstaller](https://pyinstaller.org/), [uv](https://docs.astral.sh/uv/), and
  [git-cliff](https://git-cliff.org/) for packaging and releases.
- [confit](https://confit.krondor.org) — the model for this project's release and
  docs setup.
