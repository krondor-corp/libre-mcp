# Changelog

All notable changes to this project are documented here.

## [0.2.0] - 2026-06-29

### Bug Fixes

- Graceful errors in `libre-mcp update`
- Rust accent in the manual dark-theme block too
- Match dark-mode accent to the light rust (16 85% 42%)

### Documentation

- Document RELEASE_PAT setup steps in RELEASES.md
- Focus README on install + usage, move dev details to wiki
- Add "connect it to your coding tool" section to README
- Add acknowledgements section to README
- Rework wiki (confit layout, light/dark, logo) and slim docs
- Reshape wiki logo into an "L" (pixel grid, amber)
- Rust accent theme + tonal rust L logo
- Surface presentation / PowerPoint (.pptx) support
- Make llms.txt the agent usage guide; add /docs maintenance skill
- Adopt the AGENTS.md standard
- Drop CLAUDE.md symlink; AGENTS.md is read natively
- Add LibreOffice/UNO + MCP reference links
- Drop the Reference section from the Tools page
- Encode cross-agent portability (AGENTS.md + SKILL.md standards)

### Features

- Standalone binary packaging, self-update, confit-style releases
- Impress tools — build and edit presentations
- Hot-reload the UNO worker in debug mode; collapse run/dev scripts
- Hot-reload the tool surface in debug mode (tools/list_changed)

### Refactor

- Adopt the env.sh server-script pattern (krondor convention)

### Testing

- Cover the MCP stdio path in pytest; remove dev/client.py

### Build

- Make install builds+installs the binary; make sync for deps

