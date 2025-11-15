# GitHub Pages Setup Instructions

This document explains how to enable GitHub Pages for the Trino MCP Server documentation.

## Prerequisites

This PR has added all the necessary files for documentation:
- Documentation content in `docs/` directory
- MkDocs configuration in `mkdocs.yml`
- GitHub Actions workflow in `.github/workflows/docs.yml`

## Enabling GitHub Pages

Once this PR is merged to the `main` branch, follow these steps to enable GitHub Pages:

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/weijie-tan3/trino-mcp
2. Click on **Settings** (in the repository menu)
3. Scroll down and click on **Pages** (in the left sidebar)
4. Under **Source**, select **GitHub Actions** from the dropdown
5. Save the changes

### Step 2: Merge this PR

1. Review and approve this PR
2. Merge it to the `main` branch

### Step 3: Wait for Deployment

1. After merging, the GitHub Actions workflow will automatically run
2. Go to the **Actions** tab to monitor the deployment progress
3. Wait for the "Deploy Documentation" workflow to complete (usually takes 1-2 minutes)

### Step 4: Access Your Documentation

Once the deployment is complete, your documentation will be available at:

**https://weijie-tan3.github.io/trino-mcp/**

## Automatic Updates

After the initial setup, the documentation will automatically rebuild and redeploy whenever:
- Changes are pushed to the `main` branch
- A PR is merged to the `main` branch

## Manual Deployment (Optional)

If you need to manually trigger a deployment:

1. Go to the **Actions** tab
2. Select the "Deploy Documentation" workflow
3. Click "Run workflow"
4. Select the `main` branch
5. Click "Run workflow"

## Local Development

To build and preview the documentation locally:

```bash
# Install dependencies
pip install mkdocs mkdocs-material

# Serve locally (with live reload)
mkdocs serve

# Build static site
mkdocs build
```

Visit http://127.0.0.1:8000/trino-mcp/ to view the local documentation.

## Troubleshooting

### Documentation Not Deploying

1. Check the Actions tab for error messages
2. Ensure GitHub Pages is enabled and set to "GitHub Actions"
3. Verify the workflow file is in `.github/workflows/docs.yml`
4. Check that the repository has the necessary permissions:
   - Go to Settings → Actions → General
   - Under "Workflow permissions", ensure "Read and write permissions" is selected

### 404 Error When Accessing Docs

1. Wait a few minutes after the workflow completes
2. Clear your browser cache
3. Check that the deployment completed successfully in the Actions tab

### Build Errors

1. Check the workflow logs in the Actions tab
2. Ensure all documentation files are valid Markdown
3. Test the build locally with `mkdocs build --strict`

## Custom Domain (Optional)

To use a custom domain for your documentation:

1. Add a `CNAME` file to the `docs/` directory with your domain name
2. Configure DNS settings for your domain to point to GitHub Pages
3. Update `site_url` in `mkdocs.yml` to your custom domain

See [GitHub Pages documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site) for detailed instructions.

## Support

If you encounter any issues:
- Check the [MkDocs documentation](https://www.mkdocs.org/)
- Check the [GitHub Pages documentation](https://docs.github.com/en/pages)
- Open an issue in this repository
