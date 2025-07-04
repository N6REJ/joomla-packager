# Migration Guide

This guide helps you migrate from the original workflow to use the composite action.

## Original Workflow vs Composite Action

### Before (Original Workflow)

The original workflow had all logic embedded in a single YAML file with environment variables:

```yaml
env:
  AUTHOR: "N6REJ"
  REPO: "N6REJ/mod_bears_aichatbot"
  MODULE_NAME: "mod_bears_aichatbot"
  MODULE_XML: "mod_bears_aichatbot.xml"
  COPYRIGHT_HOLDER: "N6REJ (N6REJ)"
  COPYRIGHT_START_YEAR: "2025"
  # ... more environment variables

jobs:
  update-version-and-release:
    runs-on: ubuntu-latest
    steps:
      # ... 20+ steps with complex logic
```

### After (Using Composite Action)

With the composite action, your workflow becomes much simpler:

```yaml
jobs:
  package:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GH_PAT }}

      - name: Joomla Extension Packager
        uses: N6REJ/joomla-packager@2025.6.23
        id: packager
        with:
          author: 'N6REJ'
          copyright-holder: 'N6REJ (N6REJ)'
          copyright-start-year: '2025'
          github-token: ${{ secrets.GH_PAT }}
```

## Step-by-Step Migration

### 1. Update Your Workflow

Replace your existing workflow with a simplified version:

```yaml
name: Package and Release Module

on:
  pull_request:
    types: [closed]
    branches:
      - main
  workflow_dispatch:

jobs:
  package:
    if: github.event_name == 'workflow_dispatch' || (github.event_name == 'pull_request' && github.event.pull_request.merged == true)
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GH_PAT }}

      - name: Joomla Extension Packager
        uses: N6REJ/joomla-packager@2025.6.23
        id: packager
        with:
          author: 'N6REJ'
          copyright-holder: 'N6REJ (N6REJ)'
          copyright-start-year: '2025'
          github-token: ${{ secrets.GH_PAT }}
      
      - name: Commit changes
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          
          if git diff --exit-code; then
            echo "No changes to commit"
          else
            git add .
            git commit -m "Update version to ${{ steps.packager.outputs.version }} [skip ci]"
            git push origin main
          fi
```

### 3. Map Environment Variables to Inputs

| Original Env Variable | Composite Action Input | Notes |
|----------------------|------------------------|-------|
| `AUTHOR` | `author` | |
| `MODULE_NAME` | `extension-name` | |
| `MODULE_XML` | `extension-xml` | |
| `COPYRIGHT_HOLDER` | `copyright-holder` | |
| `COPYRIGHT_START_YEAR` | `copyright-start-year` | |
| `PHP_VERSION` | `php-version` | |
| `MODULE_TOKEN` | `github-token` | |
| `CHANGELOG_FILE` | `changelog-file` | |
| `HELPER_FILE` | `helper-file` | |
| `LICENSE_FILE` | `license-file` | |
| `FAVICON_FILE` | `favicon-file` | |
| `UPDATES_XML_FILE` | `updates-xml-file` | |
| `CSS_DIR` | `css-dir` | |
| `JS_DIR` | `js-dir` | |
| `TMPL_DIR` | `tmpl-dir` | |
| `LANGUAGE_DIR` | `language-dir` | |
| `PACKAGE_DIR` | `package-dir` | |
| `DIR_TREE_FILE` | `dir-tree-file` | |
| (none) | `extension-type` | Optional, e.g. module, plugin, component |
| (none) | `manual-version` | Optional, for manual version override |
| (none) | `file-updates` | Optional, default 'true' |
| (none) | `generate-changelog` | Optional, default 'true' |
| (none) | `create-release` | Optional, default 'true' |
| (none) | `upload-artifact` | Optional, default 'true' |
| (none) | `update-joomla-server` | Optional, default 'true' |

> **Note:** The inputs listed as `(none)` are new options available in the composite action and do not have direct equivalents in the original workflow. They provide additional flexibility and control over the packaging and release process.

## Benefits of Migration

### 1. **Reusability**
- Use the same action across multiple repositories
- Share with the community
- Maintain consistency across projects

### 2. **Maintainability**
- Update logic in one place
- Easier to debug and test
- Clear separation of concerns

### 3. **Flexibility**
- Easy to extend with additional steps
- Can be used for modules, plugins, and components
- Customizable through inputs
- Support for both automatic and manual versioning

### 4. **Simplicity**
- Cleaner workflow files
- Less duplication
- Easier to understand

### 5. **Enhanced Features**
- Manual version override support
- Better error handling
- More configuration options

## Advanced Usage After Migration

### Adding Custom Steps

You can add custom steps before or after the packaging:

```yaml
- name: Run custom validation
  run: |
    # Your custom validation logic
    
- name: Package Module
  uses: N6REJ/joomla-packager@2025.6.23
  id: packager
  with:
    # ... your inputs
    
- name: Deploy to server
  run: |
    # Your deployment logic
    echo "Deploying version ${{ steps.packager.outputs.version }}"
```

### Using Outputs

The composite action provides outputs you can use:

```yaml
- name: Package Module
  uses: N6REJ/joomla-packager@2025.6.23
  id: packager
  with:
    # ... your inputs

- name: Use outputs
  run: |
    echo "Version: ${{ steps.packager.outputs.version }}"
    echo "Package: ${{ steps.packager.outputs.package-path }}"
    echo "Release: ${{ steps.packager.outputs.release-url }}"
```

### Conditional Features

You can control features through inputs:

```yaml
- uses: N6REJ/joomla-packager@2025.6.23
  with:
    extension-name: 'mod_example'
    extension-xml: 'mod_example.xml'
    extension-type: 'module'
    author: 'Your Name'
    copyright-holder: 'Your Company'
    copyright-start-year: '2024'
    github-token: ${{ secrets.GH_PAT }}
    # Control features
    generate-changelog: 'true'
    create-release: ${{ github.ref == 'refs/heads/main' }}
    upload-artifact: 'true'
    update-joomla-server: 'false'
```

## Troubleshooting

### Common Issues

1. **Missing secrets**: Ensure `GH_PAT` is set in repository secrets
2. **Permission errors**: Check workflow permissions are set correctly
3. **File not found**: Verify paths are relative to repository root
4. **Version conflicts**: The action handles this automatically

### Testing Your Migration

1. Create a test branch
2. Make a small change
3. Create a pull request
4. Merge to trigger the workflow
5. Verify the package is created correctly

## Need Help?

- Check the [composite action README](README.md)
- Review the [example module workflow](example-module.yml)
- Review the [example plugin workflow](example-plugin.yml)
- Review the [example component workflow](example-component.yml)
- Review the [example package workflow](example-pkg.yml)
- Open an issue if you encounter problems
