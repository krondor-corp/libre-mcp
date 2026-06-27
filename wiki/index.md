---
title: libre-mcp
description: A stdio MCP server for controlling LibreOffice (Writer & Calc) over UNO.
---

libre-mcp lets an MCP client — Claude Code, Claude Desktop, or anything that
speaks the protocol — create and edit LibreOffice **Writer** and **Calc**
documents, run spreadsheet formulas, and export to PDF/DOCX/XLSX and more.

It runs LibreOffice headless and drives it over UNO, with each instance isolated
on its own named pipe and profile so parallel sessions never collide.

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
claude mcp add libre -- libre-mcp
```

- **[Install](/docs/install/)** — get it onto your machine
- **[Quickstart](/docs/quickstart/)** — your first document
- **[Tools](/docs/tools/)** — the full tool surface
- **[Architecture](/docs/architecture/)** — how it works under the hood
