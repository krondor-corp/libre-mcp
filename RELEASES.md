# Releases

Mirrors the confit release flow: conventional-commit → release PR → tag → build.
End users get a prebuilt, self-contained binary (PyInstaller) per platform.

## The automated flow

1. **Push to `main`** → `release-pr.yml` reads conventional commits since the
   last `v*` tag, computes a semver bump, bumps `pyproject.toml` +
   `src/__init__.py`, regenerates `CHANGELOG.md` (git-cliff), and opens/updates a
   single `release-automation` PR.
2. **Merge that PR** → `release-tag.yml` reads the version from `pyproject.toml`
   and pushes a `v<version>` tag. It uses the **`RELEASE_PAT`** secret, because
   the default `GITHUB_TOKEN` cannot trigger another workflow.
3. **Tag `v*`** → `release.yml` builds the binary on a native runner per target
   (linux x86_64/aarch64, darwin x86_64/aarch64), packages
   `libre-mcp-<tag>-<arch>-<os>.tar.gz`, and publishes a GitHub Release.

You can also build a release manually via `release.yml`'s **workflow_dispatch**
with an explicit tag.

## One-time GitHub setup

- **Actions permissions**: Settings → Actions → General → Workflow permissions →
  "Read and write permissions" (so `release-pr.yml` can open PRs).
- **`RELEASE_PAT`** secret: a fine-grained PAT with Contents: read/write, so the
  tag push from `release-tag.yml` triggers `release.yml`.

## Versioning

- Source of truth: `version` in `pyproject.toml` (mirrored in `src/__init__.py`).
- Tags are `v<version>`; a tag containing `-` (e.g. `v0.2.0-rc1`) is a prerelease.

## Manual release

If you'd rather skip the PR bot: bump the version, commit, then
`git tag v0.2.0 && git push origin v0.2.0`.

## Install / update

```bash
curl -fsSL https://raw.githubusercontent.com/krondor-corp/libre-mcp/main/install.sh | bash
libre-mcp update   # in-place self-update to the latest release
```

## Local build

```bash
make binary        # -> dist/libre-mcp
```

## CI

`test.yml` runs on every push to `main` and PR: installs LibreOffice +
`python3-uno` and runs `make check` (black, ruff, ty, pytest incl. live
integration).
