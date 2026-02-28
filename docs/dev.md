# Developer Guide

## Versioning

Versions are derived automatically from **git tags** using [`hatch-vcs`](https://github.com/ofek/hatch-vcs). There is no version string to maintain manually anywhere in the codebase.

- **Tagged commits** (e.g., `v0.2.0`) produce a clean version: `0.2.0`
- **Development builds** (commits after a tag) produce versions like: `0.2.1.dev3+gabcdef1`

## Publishing a New Version

Publishing is handled automatically by the [`publish-to-pypi.yml`](../.github/workflows/publish-to-pypi.yml) GitHub Actions workflow using [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) (no API tokens needed).

**Option A — Via GitHub UI (recommended):**

1. Go to **GitHub → Releases → Draft a new release**.
2. Create a new tag (e.g., `v0.2.0`) targeting `main`.
3. Add release notes and click **Publish release**.

**Option B — Via command line:**

```bash
git tag v0.2.0
git push origin v0.2.0
```

Either way, the workflow will automatically build the package and publish it to [PyPI](https://pypi.org/p/trino-mcp).

> **Note:** The PyPI trusted publisher must be configured at https://pypi.org/manage/account/publishing/ with environment name `pypi` and workflow `publish-to-pypi.yml`. See the workflow file for details.
