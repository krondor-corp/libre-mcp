---
name: docs
description: Update libre-mcp's documentation after adding or changing a capability (a tool, an export format, a document type). Invoke this whenever you implement a feature so the tool tables, the llms.txt agent guide, and the human-facing headline copy stay in sync and reflect the new capability for both humans and agents.
---

# Keeping libre-mcp docs in sync

Run this after any change to the tool surface, supported formats, or document
types. The goal: a human reading the README/wiki **and** an agent reading
`wiki/llms.txt` can both discover and use the new capability.

## 1. Tool tables (must match the actual tools)

Update both — they list the same tools and must agree:

- `README.md` → the `## Usage` table
- `wiki/_docs/tools.md` → the tools table

Add/rename the row(s): tool name, arguments, and return shape. Mirror the
docstrings in `src/tools/*.py`.

## 2. Agent guide — `wiki/llms.txt`

This is the canonical, copy-pasteable usage guide for agents. Update it:

- Add the tool under the right heading (Documents / Writer / Calc / Impress / …).
- If the feature enables a new **deliverable**, add a short **Recipe**
  (create → edit → export), matching the existing recipe style.
- If it's a new document type or export format, update the top-of-file summary.

## 3. Headline copy (only for a new document type or output format)

When the capability is genuinely new-surface (e.g. presentations, a new export
target), update everywhere capabilities are listed:

- `README.md` — intro paragraph + the Usage lead-in
- `wiki/_config.yml` — `description`
- `wiki/_layouts/home.html` — hero tagline + feature cards
- `wiki/llms.txt` — summary line

## 4. Export formats

If you added an export format, add it in **both**:

- the formats note in `wiki/_docs/tools.md` (and `wiki/llms.txt`)
- the `_FILTERS` map in `src/office/uno_worker.py`

## Verify

- `cd wiki && bundle exec jekyll build` succeeds.
- Catch stale copy: grep the old phrasing, e.g.
  `grep -rn "Writer & Calc" README.md wiki/`
- Sanity: the new tool appears in the README table, the wiki tools table, and
  `llms.txt` (with a recipe if it's a deliverable).
