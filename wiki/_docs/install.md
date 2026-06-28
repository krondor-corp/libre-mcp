---
title: Install
slug: install
order: 1
description: Install libre-mcp and connect it to your client.
---

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
```

Installs a prebuilt binary to `~/.local/bin` (override with `INSTALL_DIR`). Update
with `libre-mcp update`.

## Requirements

LibreOffice must be installed:

- **macOS:** `/Applications/LibreOffice.app`
- **Debian/Ubuntu:** `apt install libreoffice-writer libreoffice-calc python3-uno`
- **Other Linux (TDF/opt builds):** nothing extra.

## Connect

`libre-mcp` is a stdio MCP server. Point your client at the `libre-mcp` command:

```bash
claude mcp add libre -- libre-mcp        # Claude Code
```

For Cursor, Claude Desktop, and Windsurf, add to their MCP config:

```json
{ "mcpServers": { "libre": { "command": "libre-mcp" } } }
```

VS Code (`.vscode/mcp.json`) uses `servers` instead:

```json
{ "servers": { "libre": { "type": "stdio", "command": "libre-mcp" } } }
```
