---
title: Quickstart
slug: quickstart
order: 2
description: Create, edit, and export your first document.
---

Once registered, ask your MCP client to work with documents directly. The
typical flow is **create/open → edit → export**.

## A Writer document

1. `create_document` with `kind: "writer"` → returns a `doc_id`.
2. `insert_text` to append text (set `paragraph_break: true` to start a new paragraph).
3. `find_and_replace` to edit, `get_text` to read it back.
4. `export_document` to write a PDF/DOCX.

## A Calc spreadsheet

```text
create_document  {"kind": "calc"}                  -> {"doc_id": "doc-1"}
set_cells        {"doc_id": "doc-1", "cells": [
                    {"cell": "A1", "value": 21},
                    {"cell": "A2", "value": 2},
                    {"cell": "A3", "formula": "=A1*A2"}]}
read_cells       {"doc_id": "doc-1", "range": "A1:A3"}  -> [[21.0],[2.0],[42.0]]
export_document  {"doc_id": "doc-1", "path": "/tmp/out.xlsx"}
```

## Notes

- Documents persist between tool calls until you `close_document`.
- LibreOffice starts on the first tool call.
- Export `path` must be absolute; the format is inferred from the extension
  (`pdf`, `docx`, `odt`, `xlsx`, `ods`, `csv`, `html`, `txt`) or set explicitly.
