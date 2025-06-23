# Joomla Extension Packager Workflows Documentation

This page provides a comprehensive guide to the automated packaging workflows for Joomla modules, plugins, components, and multi-extension packages using GitHub Actions. Each workflow is tailored for its extension type, and the package workflow can bundle any combination of modules, plugins, and components.

## Table of Contents

- [Available Workflows & Quick Links](#workflows)
- [How to Use](#how-to-use)
- [Examples](#examples)
- [Tips and Best Practices](#tips-and-best-practices)
- [FAQ](#faq)

## Available Workflows & Quick Links

- **Module Packaging:** [module-packager.yml](https://github.com/N6REJ/n6rej.github.io/blob/master/.github/workflows/module-packager.yml)
- **Plugin Packaging:** [plugin-packager.yml](https://github.com/N6REJ/n6rej.github.io/blob/master/.github/workflows/plugin-packager.yml)
- **Component Packaging:** [component-packager.yml](https://github.com/N6REJ/n6rej.github.io/blob/master/.github/workflows/component-packager.yml)
- **Package (Multi-Extension):** [package-packager.yml](https://github.com/N6REJ/n6rej.github.io/blob/master/.github/workflows/package-packager.yml)

## How to Use

1. Copy the desired `.yml` workflow file from above into your repository's `.github/workflows/` directory.
2. Edit the `env:` section at the top of the workflow file to match your extension's details.
3. Push your changes or trigger the workflow manually from the GitHub Actions tab.
4. Check the [Releases, for example](https://github.com/N6REJ/mod_bears_pricing_tables/releases) section for your packaged extension ZIP and changelog.

## Examples

### Sample Workflow YAML

```yaml
name: Package and Release Bears AI Chatbot Module

on:
  pull_request:
    types: [closed]
    branches:
      - main
  workflow_dispatch:

# =============================
# Universal Joomla Module Packaging Workflow
# To use for your own module, change the variables below:
# AUTHOR: Your name or handle
# REPO: Your repo path (org/repo)
# MODULE_NAME: Module folder and file prefix (e.g. mod_example)
# MODULE_XML: Main XML file (e.g. mod_example.xml)
# COPYRIGHT_HOLDER: Copyright string (e.g. YourName (YourHandle))
# COPYRIGHT_START_YEAR: Copyright start year (e.g. 2025)
# PHP_VERSION: PHP version to use (e.g. 8.1)
# MODULE_TOKEN: Your token secret name (default: GH_PAT)
# CHANGELOG_FILE: Changelog filename (default: CHANGELOG.md)
# HELPER_FILE: Helper PHP file (default: helper.php)
# LICENSE_FILE: License file (default: License.txt)
# FAVICON_FILE: Favicon file (default: favicon.ico, can be blank to skip)
# UPDATES_XML_FILE: Updates XML file (default: updates.xml)
# CSS_DIR: CSS directory (default: css)
# JS_DIR: JS directory (default: js)
# TMPL_DIR: Template directory (default: tmpl)
# LANGUAGE_DIR: Language directory (default: language)
# PACKAGE_DIR: Package output directory (default: package)
# DIR_TREE_FILE: Directory tree output file, used as an additional file in release listing. (default: directory-structure.txt, can be blank to skip)
# =============================

env:
  AUTHOR: "N6REJ"
  REPO: "N6REJ/mod_bears_aichatbot"
  MODULE_NAME: "mod_bears_aichatbot"
  MODULE_XML: "mod_bears_aichatbot.xml"
  COPYRIGHT_HOLDER: "BearLeeAble (N6REJ)"
  COPYRIGHT_START_YEAR: "2025"
  PHP_VERSION: "8.1"
  MODULE_TOKEN: "GH_PAT" # Set your token secret name here (default: GH_PAT)
  CHANGELOG_FILE: "CHANGELOG.md"
  HELPER_FILE: "helper.php"
  LICENSE_FILE: "License.txt"
  FAVICON_FILE: "favicon.ico"
  UPDATES_XML_FILE: "updates.xml"
  CSS_DIR: "css"
  JS_DIR: "js"
  TMPL_DIR: "tmpl"
  LANGUAGE_DIR: "language"
  PACKAGE_DIR: "package"
  DIR_TREE_FILE: "directory-structure.txt"
```

### Example Directory Structure

```
my-joomla-module/
├── .github/
│   └── workflows/
│       └── module-packager.yml
├── mod_example.php
├── mod_example.xml
├── helper.php
├── tmpl/
│   └── default.php
├── language/
│   └── en-GB.mod_example.ini
└── ...
```

### Sample Release Result

- ZIP file:
  ```
  mod_example-2025.06.13.1.zip
  ```
- Changelog:
  ```
  CHANGELOG.md
  ```
- Release notes auto-generated from commit messages

## Tips and Best Practices

- Use clear, conventional commit messages for changelog generation.
- Keep your file and directory names consistent with the variables in your workflow.
- Review the workflow logs for troubleshooting if a build fails.
- Use the **package** workflow to bundle multiple extension types into a single ZIP and release.

## FAQ

- **Q: Can I use more than one packager workflow?**  
  **A:** Yes! Each workflow (module, plugin, component, package) can be used independently or together. The **package** workflow is for multi-extension releases.


- **Q: Where do I find my packaged ZIP?**  
  **A:** In the [Releases, for example](https://github.com/N6REJ/mod_bears_pricing_tables/releases) section of your repository after the workflow completes.

---

For more details, see the [project README](https://github.com/N6REJ/n6rej.github.io/blob/master/README.md) or [view on GitHub](https://github.com/N6REJ/n6rej.github.io).
