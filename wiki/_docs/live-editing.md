---
title: Live editing & concurrency
slug: live-editing
order: 4
description: How live editing works, and how the server avoids clobbering human edits.
---

The server drives **one** LibreOffice instance in an isolated profile — its own
process, separate from your everyday LibreOffice. That single fact shapes both
how you watch edits happen live and how the server keeps an agent from
overwriting your changes. Everything below holds for **every document kind**
(Writer, Calc, Impress, Draw).

## One shared window for live editing

In live mode (`show: true`) the server opens a **visible** window backed by the
*same* document model it edits through tools. Edit in that window and the agent
sees your changes instantly; the agent edits and you watch them land in real
time. It's one model, two editors.

Opening the *same file* in your **own** LibreOffice is different: that's a
separate process with its own in-memory copy. The two instances can't see each
other's unsaved edits — local LibreOffice has no real-time co-editing (that's a
cloud / Collabora feature). The only bridge between two instances is the file on
disk: save in one, reopen in the other. Only one instance can hold a file
read-write at a time (the `.~lock` file); a second open is read-only or a copy.

> **So:** to follow along live, edit the window the server opens — not a copy you
> open yourself.

## The conflict guard

Every open document carries a **revision counter** (`rev`) that is bumped on
*any* change — an agent tool call **or** a human typing in the live window. The
server also records the revision it last acted on (`seen`).

- A tool that would **mutate** a document whose `rev` has advanced past `seen`
  (you changed it since the agent last looked) is **refused** — it returns
  `{conflict: true, warning, rev, seen}` instead of editing.
- The agent recovers by **re-reading** the document (`get_text`, `read_cells`,
  `read_slide`). A read resyncs `seen` to the current `rev` and surfaces your
  change, so the agent merges instead of clobbering — then retries the edit.
- `force: true` overrides the guard without re-reading. It's rarely the right
  move; prefer re-reading.

`document_info` reports `modified`, `rev`, and `seen` at any time, so the state
is always inspectable.

## Closing is guarded too

`close_document` **refuses to discard unsaved changes** unless you pass
`force: true`. Save first with `save_document` so in-flight work — yours or the
agent's — is never silently thrown away.
