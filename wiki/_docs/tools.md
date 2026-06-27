---
title: Tools
slug: tools
order: 3
description: The full libre-mcp tool surface.
---

All tools take and return JSON. Document-scoped tools take a `doc_id` returned by
`create_document` / `open_document`.

## Documents

| Tool | Arguments | Returns |
|------|-----------|---------|
| `create_document` | `kind` (writer\|calc\|impress\|draw) | `{doc_id, kind}` |
| `open_document` | `path` | `{doc_id, kind, path}` |
| `list_documents` | — | `{documents: [{doc_id, kind, url}]}` |
| `document_info` | `doc_id` | `{kind, url, modified}` |
| `save_document` | `doc_id`, `path?`, `format?` | `{path}` |
| `export_document` | `doc_id`, `path`, `format?` | `{path, filter}` |
| `close_document` | `doc_id` | `{closed}` |

`save_document` with no `path` saves in place; with a `path` it saves a copy.
Formats: `pdf`, `docx`, `odt`, `xlsx`, `ods`, `csv`, `html`, `txt`.

## Writer

| Tool | Arguments | Returns |
|------|-----------|---------|
| `get_text` | `doc_id` | `{text}` |
| `insert_text` | `doc_id`, `text`, `paragraph_break?` | `{ok}` |
| `find_and_replace` | `doc_id`, `search`, `replace`, `regex?` | `{count}` |

## Calc

| Tool | Arguments | Returns |
|------|-----------|---------|
| `set_cells` | `doc_id`, `cells`, `sheet?` | `{written}` |
| `read_cells` | `doc_id`, `range`, `sheet?` | `{values}` |

`cells` is a list of `{cell, value?\|formula?}` entries — a numeric `value` is
written as a number, a `formula` (starting with `=`) is evaluated by Calc.
`sheet` selects a sheet by name or 0-based index (defaults to the first).
