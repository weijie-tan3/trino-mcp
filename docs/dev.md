# Developer Guide

## Publishing a New Version

Publishing is handled automatically by the [`publish-to-pypi.yml`](../.github/workflows/publish-to-pypi.yml) GitHub Actions workflow using [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) (no API tokens needed).

**Steps:**

1. Update the `version` in [`pyproject.toml`](../pyproject.toml) (e.g., `0.1.3` → `0.1.4`).
2. Commit and merge to `main`.
3. Go to **GitHub → Releases → Draft a new release**.
4. Create a new tag matching the version (e.g., `v0.1.4`).
5. Click **Publish release**.

The workflow will automatically build the package and publish it to [PyPI](https://pypi.org/p/trino-mcp).

> **Note:** The PyPI trusted publisher must be configured at https://pypi.org/manage/account/publishing/ with environment name `pypi` and workflow `publish-to-pypi.yml`. See the workflow file for details.
