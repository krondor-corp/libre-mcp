---
title: File support
slug: formats
order: 3
description: Which document areas and file formats libre-mcp can read, create, and edit.
---

What libre-mcp can do with each file format, by area. Legend: **✓** supported ·
**~** partial · **—** not yet.

- **Read** — open the file and pull content back through a tool
  (`get_text` for Writer, `read_cells` for Calc, `list_slides` for Impress).
- **Create** — make a new document and `export_document` it to this format.
- **Edit** — open an existing file and change it with the area's tools, then save.

> **Headless & live apply to everything.** Every operation runs **headless** by
> default; with the dev `--live` flag the same document opens in a **visible**
> LibreOffice window. They're properties of the engine, not the format, so they're
> not repeated per row.

## Word processing — Writer

| Format | MIME type | Read | Create | Edit |
|--------|-----------|:----:|:------:|:----:|
| ODT (.odt) | `application/vnd.oasis.opendocument.text` | ✓ | ✓ | ✓ |
| Word (.docx) | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | ✓ | ✓ | ✓ |
| Word 97 (.doc) | `application/msword` | ✓ | ✓ | ✓ |
| RTF (.rtf) | `application/rtf` | ✓ | ✓ | ✓ |
| Text (.txt) | `text/plain` | ✓ | ✓ | ✓ |
| HTML (.html) | `text/html` | ✓ | ✓ | ✓ |

Read returns the full document text; editing uses the Writer tools
(`add_paragraph`, `add_list`, `insert_table`, `insert_image`, `add_page_box`, …).

## Spreadsheets — Calc

| Format | MIME type | Read | Create | Edit |
|--------|-----------|:----:|:------:|:----:|
| ODS (.ods) | `application/vnd.oasis.opendocument.spreadsheet` | ✓ | ✓ | ✓ |
| Excel (.xlsx) | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | ✓ | ✓ | ✓ |
| Excel 97 (.xls) | `application/vnd.ms-excel` | ✓ | ✓ | ✓ |
| CSV (.csv) | `text/csv` | ✓ | ✓ | ✓ |
| HTML (.html) | `text/html` | ✓ | ✓ | ✓ |

Read returns cell values via `read_cells`; editing writes cells and formulas via
`set_cells`.

## Presentations / slides — Impress

| Format | MIME type | Read | Create | Edit |
|--------|-----------|:----:|:------:|:----:|
| ODP (.odp) | `application/vnd.oasis.opendocument.presentation` | ~ | ✓ | ✓ |
| PowerPoint (.pptx) | `application/vnd.openxmlformats-officedocument.presentationml.presentation` | ~ | ✓ | ✓ |

Read is **partial** — `list_slides` returns slide titles and count, not full slide
content. Editing covers slides, text, shapes, gradients, and images.

## Drawings — Draw

| Format | MIME type | Read | Create | Edit |
|--------|-----------|:----:|:------:|:----:|
| ODG (.odg) | `application/vnd.oasis.opendocument.graphics` | — | ~ | — |

Draw documents can be created and exported, but there are no dedicated Draw
editing or reading tools yet (build visuals as Impress slides instead).

## PDF — output / interchange

| Format | MIME type | Read | Create | Edit |
|--------|-----------|:----:|:------:|:----:|
| PDF (.pdf) | `application/pdf` | — | ✓ (export) | — |

PDF is an **output** format: any Writer, Calc, or Impress document exports to it.
libre-mcp does not extract text from or edit existing PDFs (opening one imports it
into Draw, lossily).

## Beyond these

`open_document` uses LibreOffice's importers, so it can *open* more legacy and
niche formats than the table lists (e.g. `.ppt`, `.pptx` variants, `.fodt`) — but
the formats above are the ones libre-mcp explicitly reads, creates, and exports.
The export filters live in the `_FILTERS` map in `src/office/uno_worker.py`.
