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
| `list_documents()` / `document_info(doc_id)` | Inspect open docs (`modified`, `rev`) |
| `save_document(doc_id, path?, format?)` | Save in place or to a path |
| `export_document(doc_id, path, format?)` | Export (pdf, docx, xlsx, csv, …) |
| `close_document(doc_id, force?)` | Close a doc (refuses on unsaved changes; `force` discards) |
| `get_text(doc_id)` | Read a Writer doc's text |
| `insert_text(doc_id, text, paragraph_break?)` | Append text |
| `find_and_replace(doc_id, search, replace, regex?)` | Replace text |
| `page_setup(doc_id, margin?, top?, color?)` | Page margins / background |
| `add_paragraph(doc_id, text, size?, color?, bold?, align?, …)` | Styled paragraph / heading |
| `add_list(doc_id, items, ordered?)` | Bulleted / numbered list |
| `insert_table(doc_id, rows, header?, accent?)` | Table (accent header row) |
| `insert_image(doc_id, path, width_cm?)` | Inline image |
| `add_page_box(doc_id, x, y, w, h, text?, fill?, …)` | Page-anchored band / callout |
| `set_cells(doc_id, cells, sheet?)` | Write Calc cells/formulas |
| `read_cells(doc_id, range, sheet?)` | Read a Calc range |
| `add_slide(doc_id, layout?)` | Append an Impress slide |
| `set_slide_content(doc_id, index, title?, bullets?)` | Set a slide's title/bullets |
| `list_slides(doc_id)` / `delete_slide(doc_id, index)` | Inspect / remove slides |
| `set_presentation_size(doc_id, preset)` | Slide aspect (16:9 / 4:3) |
| `set_slide_background(doc_id, slide, color, color2?)` | Solid or gradient background |
| `add_textbox(doc_id, slide, text, x, y, w, h, …)` | Positioned, styled text |
| `add_shape(doc_id, slide, x, y, w, h, shape, fill, …)` | Rect/round/ellipse/line (+ text) |
| `add_image(doc_id, slide, path, x, y, w, h)` | Place an image on a slide |

Slide graphics (and Writer page boxes) position by **percent (0-100)** and take
**hex colors** — enough to build themed, graphic-rich decks *and* branded
documents (letterheads, reports, one-pagers). Full arguments: the
[tool reference](https://libre-mcp.krondor.org/docs/tools/).

### Live editing & concurrency

The server drives **one** headless/visible LibreOffice in an isolated profile —
its own process, separate from your everyday LibreOffice. That has two
consequences worth knowing:

- **To watch edits live, edit the window the server opens** (live mode,
  `show: true`) — it shares the server's document model, so you and the agent see
  each other's changes instantly. Opening the *same file* in your own LibreOffice
  gives you a **separate** in-memory copy; the two processes can't see each
  other's unsaved edits (local LibreOffice has no real-time co-editing — that's a
  cloud/Collabora feature). The only bridge between two instances is the file on
  disk: save in one, reopen in the other.
- **The agent won't clobber your in-flight edits.** Every document carries a
  revision counter bumped on *any* change (agent or human); a tool that would
  edit a document you changed since the agent last looked is **refused with a
  conflict warning** until the agent re-reads it. Likewise `close_document`
  refuses to discard unsaved changes unless you pass `force`.

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
