---
title: Tools
slug: tools
order: 2
description: The libre-mcp tool surface.
---

Create or open a document to get a `doc_id`, edit it, then export. Documents stay
open until closed.

| Tool | Arguments | Returns |
|------|-----------|---------|
| `create_document` | `kind` (writer\|calc\|impress\|draw) | `{doc_id, kind}` |
| `open_document` | `path` | `{doc_id, kind, path}` |
| `list_documents` | — | `{documents}` |
| `document_info` | `doc_id` | `{kind, url, modified}` |
| `save_document` | `doc_id`, `path?`, `format?` | `{path}` |
| `export_document` | `doc_id`, `path`, `format?` | `{path, filter}` |
| `close_document` | `doc_id` | `{closed}` |
| `get_text` | `doc_id` | `{text}` |
| `insert_text` | `doc_id`, `text`, `paragraph_break?` | `{ok}` |
| `find_and_replace` | `doc_id`, `search`, `replace`, `regex?` | `{count}` |
| `set_cells` | `doc_id`, `cells`, `sheet?` | `{written}` |
| `read_cells` | `doc_id`, `range`, `sheet?` | `{values}` |
| `add_slide` | `doc_id`, `layout?` | `{index, count}` |
| `set_slide_content` | `doc_id`, `index`, `title?`, `bullets?` | `{index}` |
| `list_slides` | `doc_id` | `{slides, count}` |
| `delete_slide` | `doc_id`, `index` | `{count}` |

Formats: `pdf`, `docx`, `odt`, `xlsx`, `ods`, `csv`, `html`, `txt`, `pptx`, `odp`
(inferred from the path extension). `cells` is a list of `{cell, value?|formula?}`
— a `formula` starts with `=` and is evaluated by Calc. Impress slides are
0-indexed (a new deck starts with one slide); `set_slide_content` fills the
title and bullet-body placeholders, `bullets` being one string per line.
