# Releases

libre-mcp is pure Python, so a release is a single wheel that works on macOS and
Linux — no per-platform build matrix.

## Cutting a release

1. Bump `version` in `pyproject.toml` (and `src/__init__.py:__version__`).
2. Commit, then tag and push:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
3. The **Release** workflow (`.github/workflows/release.yml`) fires on the `v*`
   tag: it runs `uv build` (wheel + sdist) and publishes a GitHub Release with
   auto-generated notes and both artifacts attached. A tag containing a hyphen
   (e.g. `v0.1.0-rc1`) is marked as a prerelease.

You can also trigger it manually via **workflow_dispatch** with an explicit tag.

## Versioning

- Source of truth: the `version` field in `pyproject.toml`.
- Tags are `v<version>` (the `v` prefix is required — the workflow triggers on
  `tags: ['v*']`).
- Semantic versioning.

## Install path

End users install with the bootstrap script, which installs `uv` if needed,
downloads the latest release wheel, and installs it as an isolated uv tool:

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
```

Then register the global command with Claude Code:

```bash
claude mcp add libre -- libre-mcp
```

LibreOffice must be installed on the host (Debian/Ubuntu also need
`python3-uno`).

## CI

`.github/workflows/test.yml` runs on every push to `main` and every PR: it
installs LibreOffice + `python3-uno` and runs `make check` (black, ruff, ty, and
pytest including the live integration tests).
