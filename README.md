# libre-mcp

A stdio [MCP](https://modelcontextprotocol.io) server for controlling
**LibreOffice** (Writer & Calc) from Claude Code and other MCP clients — create
and edit documents, run spreadsheet formulas, and export to PDF/DOCX/XLSX and
more. macOS and Linux.

Full docs: **[libre-mcp.krondor.org](https://libre-mcp.krondor.org)**

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
claude mcp add libre -- libre-mcp
```

Installs a prebuilt, self-contained binary to `~/.local/bin` (no Python needed on
the host). Update in place with `libre-mcp update`.

## Requirements

LibreOffice must be installed:

- **macOS:** `/Applications/LibreOffice.app`
- **Debian/Ubuntu:** `apt install libreoffice-writer libreoffice-calc python3-uno`
- **Other Linux (TDF/opt builds):** bundle their own Python — nothing extra.

Paths are auto-discovered; override with `LIBRE_MCP_SOFFICE_PATH` /
`LIBRE_MCP_PYTHON_PATH` if LibreOffice lives somewhere unusual.

## Usage

Ask your MCP client to work with documents. The typical flow is **create/open →
edit → export**; documents stay open (referenced by `doc_id`) until closed.

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

Full arguments and examples: the
[tool reference](https://libre-mcp.krondor.org/docs/tools/).

## Links

- [Documentation & quickstart](https://libre-mcp.krondor.org)
- [How it works](https://libre-mcp.krondor.org/docs/architecture/)
- [Development](https://libre-mcp.krondor.org/docs/development/)
- [Releases](RELEASES.md)
