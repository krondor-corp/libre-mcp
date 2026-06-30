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
| `delete_slide` | `doc_id`, `index` | `{count}` |
| `set_presentation_size` | `doc_id`, `preset` | `{width, height}` |
| `set_slide_background` | `doc_id`, `slide`, `color`, `color2?`, `angle?` | `{ok}` |
| `add_textbox` | `doc_id`, `slide`, `text`, `x`, `y`, `w`, `h`, `size?`, `color?`, `bold?`, `align?`, `valign?`, `font?` | `{ok}` |
| `add_shape` | `doc_id`, `slide`, `x`, `y`, `w`, `h`, `shape?`, `fill?`, `fill2?`, `line?`, `corner?`, `text?` | `{ok}` |
| `add_image` | `doc_id`, `slide`, `path`, `x`, `y`, `w`, `h` | `{ok}` |

Formats: `pdf`, `docx`, `odt`, `xlsx`, `ods`, `csv`, `html`, `txt`, `pptx`, `odp`
(inferred from the path extension). `cells` is a list of `{cell, value?|formula?}`
— a `formula` starts with `=` and is evaluated by Calc.

## Slide graphics

Slides are 0-indexed (a new deck starts with one slide). `set_slide_content`
fills the title/bullet placeholders; for **engaging, themed decks** use the
graphics tools. Their `x`/`y`/`w`/`h` are **percent (0-100)** of the slide and
colors are **hex** (`#c2410c`). `shape` is `rect`|`round`|`ellipse`|`line`. Build
each slide **background-first** (it stacks to the back), then layer text and
shapes on top. See the [agent guide](/llms.txt) for copy-pasteable deck recipes.

## Writer documents

Beyond plain `insert_text`, build **branded documents** (letterheads, reports,
one-pagers): `add_paragraph` is the workhorse (large bold = a heading),
`add_list` makes bullets, `insert_table` draws a table with an accent header row,
and `insert_image` embeds an image inline. `add_page_box` places a **page-anchored
band or callout** — `x`/`y`/`w`/`h` are percent (0-100) of the *page* — for header
and footer bands. Sizes are in points, spacing/margins in cm, colors in hex.

## Live editing & concurrency

The server drives **one** LibreOffice in an isolated profile — a separate process
from your everyday LibreOffice. So:

- **To watch edits live, edit the window the server opens** (live mode,
  `show: true`). It shares the server's document model, so you and the agent see
  each other's changes instantly. Opening the *same file* in your own LibreOffice
  is a **separate in-memory copy** — the two processes can't see each other's
  unsaved edits (local LibreOffice has no real-time co-editing; that's a
  cloud/Collabora feature). The only bridge between two instances is the file on
  disk: save in one, reopen in the other.
- **The agent won't clobber your in-flight edits.** Every document carries a
  revision counter (`rev`) bumped on *any* change — agent or human. A tool that
  would edit a document changed since the agent last looked at it (`rev` >
  `seen`) is **refused with a `{conflict: true}` warning**; the agent re-reads
  (e.g. `get_text`) to pick up your change, then retries. `close_document`
  likewise refuses to discard unsaved changes unless you pass `force`. This holds
  for **every document kind** (Writer, Calc, Impress, Draw).
