---
title: Tools
slug: tools
order: 2
description: The libre-mcp tool surface.
---

Create or open a document to get a `doc_id`, edit it, then export. Documents stay
open until closed.

> **Building with an agent?** [llms.txt](/llms.txt) is a complete,
> copy-pasteable guide to driving the server, with recipes for Writer, Calc, and
> Impress deliverables.

| Tool | Arguments | Returns |
|------|-----------|---------|
| `create_document` | `kind` (writer\|calc\|impress\|draw) | `{doc_id, kind}` |
| `open_document` | `path` | `{doc_id, kind, path}` |
| `list_documents` | — | `{documents}` |
| `document_info` | `doc_id` | `{kind, url, modified, rev, seen}` |
| `save_document` | `doc_id`, `path?`, `format?` | `{path}` |
| `export_document` | `doc_id`, `path`, `format?` | `{path, filter}` |
| `close_document` | `doc_id`, `force?` | `{closed}` (refuses on unsaved changes unless `force`) |
| `get_text` | `doc_id` | `{text}` |
| `insert_text` | `doc_id`, `text`, `paragraph_break?` | `{ok}` |
| `find_and_replace` | `doc_id`, `search`, `replace`, `regex?` | `{count}` |
| `page_setup` | `doc_id`, `margin?`, `top?`, `color?` | `{ok}` |
| `add_paragraph` | `doc_id`, `text`, `size?`, `color?`, `bold?`, `italic?`, `align?`, `font?`, `space_before?`, `space_after?`, `style?` | `{ok}` |
| `add_list` | `doc_id`, `items`, `ordered?`, `size?`, `color?` | `{ok}` |
| `insert_table` | `doc_id`, `rows`, `header?`, `accent?`, `color?`, `size?` | `{ok}` |
| `insert_image` | `doc_id`, `path`, `width_cm?` | `{ok}` |
| `add_page_box` | `doc_id`, `x`, `y`, `w`, `h`, `text?`, `fill?`, `color?`, `size?`, `bold?`, `align?`, `font?`, `pad?` | `{ok}` |
| `set_cells` | `doc_id`, `cells`, `sheet?` | `{written}` |
| `read_cells` | `doc_id`, `range`, `sheet?` | `{values}` |
| `add_slide` | `doc_id`, `layout?` | `{index, count}` |
| `set_slide_content` | `doc_id`, `index`, `title?`, `bullets?` | `{index}` |
| `list_slides` | `doc_id` | `{slides, count}` |
| `read_slide` | `doc_id`, `index` | `{index, title, bullets, text}` |
| `delete_slide` | `doc_id`, `index` | `{count}` |
| `set_presentation_size` | `doc_id`, `preset` | `{width, height}` |
| `set_slide_background` | `doc_id`, `slide`, `color`, `color2?`, `angle?` | `{ok}` |
| `add_textbox` | `doc_id`, `slide`, `text`, `x`, `y`, `w`, `h`, `size?`, `color?`, `bold?`, `align?`, `valign?`, `font?` | `{ok}` |
| `add_shape` | `doc_id`, `slide`, `x`, `y`, `w`, `h`, `shape?`, `fill?`, `fill2?`, `line?`, `corner?`, `text?` | `{ok}` |
| `add_image` | `doc_id`, `slide`, `path`, `x`, `y`, `w`, `h` | `{ok}` |

Formats: `pdf`, `docx`, `odt`, `xlsx`, `ods`, `csv`, `html`, `txt`, `pptx`, `odp`
(inferred from the path extension). `cells` is a list of `{cell, value?|formula?}`
— a `formula` starts with `=` and is evaluated by Calc.
