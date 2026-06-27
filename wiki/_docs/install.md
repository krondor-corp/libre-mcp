---
title: Install
slug: install
order: 1
description: Install libre-mcp and register it with your MCP client.
---

## Prerequisites

- **LibreOffice** installed (the server drives it):
  - macOS: `/Applications/LibreOffice.app`
  - Linux (Debian/Ubuntu): `sudo apt-get install libreoffice-writer libreoffice-calc python3-uno`
  - Linux (TDF/opt builds) ship their own bundled Python and need nothing extra.
- That's it — [uv](https://docs.astral.sh/uv/) is installed for you by the script.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
```

This installs `uv` if needed, downloads the latest release wheel, and installs
the `libre-mcp` command as an isolated uv tool. Pin a version with
`LIBRE_MCP_VERSION=v0.1.0`.

## Register with Claude Code

```bash
claude mcp add libre -- libre-mcp
```

## From source

```bash
git clone https://github.com/krondor-corp/libre-mcp
cd libre-mcp
make install        # uv sync
claude mcp add libre -- $(pwd)/bin/run.sh
```

A project-scoped `.mcp.json` (relative `./bin/run.sh`) is also committed, so a
fresh checkout or git worktree self-registers with no setup.
