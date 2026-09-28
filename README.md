![GitHub release (latest by date)](https://img.shields.io/github/v/release/N6REJ/joomla-packager)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

# Joomla Extension Packager

A reusable GitHub composite action for packaging and releasing Joomla extensions. This action automates the entire process of versioning, packaging, and releasing Joomla modules, plugins, and components.<br>
there is a workflows version documented here: <a href="https://www.hallhome.us/joomla-packager/packager-documentation">Packager Documentation</a>

## 🚀 Features

- **Automatic Versioning**: Date-based versioning (YYYY.MM.DD format) with support for multiple releases per day
- **Manual Version Override**: Specify custom versions (e.g., 1.0.0, 2.0.0-beta) for semantic versioning
- **File Updates**: Automatically updates version and copyright information across all files (can be disabled)
- **Changelog Generation**: Creates changelogs from commit messages following Keep a Changelog format
- **Package Creation**: Builds properly structured ZIP files for Joomla installation
- **GitHub Releases**: Creates releases with artifacts and release notes
- **Joomla Updates**: Updates the Joomla update server XML
- **Multi-Extension Support**: Works with modules, plugins, and components
- **Extensible**: Easy to extend and customize for specific needs

## 📋 Quick Start

1. **Reference the action in your workflow** using the `uses:` field, pointing to the public repository and release/tag (replace `N6REJ/joomla-packager@v1` with the correct owner/repo and version/tag):

```yaml
name: Package Extension
on:
  pull_request:
    types: [closed]
    branches: [main]
  workflow_dispatch:

jobs:
  package:
    if: github.event_name == 'workflow_dispatch' || (github.event_name == 'pull_request' && github.event.pull_request.merged == true)
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GH_PAT }}
      
      - uses: N6REJ/joomla-packager@v2025.6.24
        with:
          extension-name: 'mod_example'
          extension-xml: 'mod_example.xml'
          extension-type: 'module'
          author: 'Your Name'
          copyright-holder: 'Your Company'
          copyright-start-year: '2024'
          github-token: ${{ secrets.GH_PAT }}
```

2. **Set up your GitHub PAT** in repository secrets as `GH_PAT` or whatever you use for `github-token:`


## 🔧 Configuration

### Required Inputs

| Input | Description |
|-------|-------------|
| `extension-name` | Extension folder and file prefix (e.g., `mod_example`) |
| `extension-xml` | Main XML manifest file (e.g., `mod_example.xml`) |
| `extension-type` | Type: `module`, `plugin`, or `component` |
| `author` | Your name or handle |
| `copyright-holder` | Copyright holder name |
| `copyright-start-year` | Year copyright started |
| `github-token` | GitHub PAT with repo permissions |

### Optional Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `manual-version` | `''` | Explicit version, overrides every scheme |
| `version-scheme` | `date` | `date` → `2025.10.02.3`, or `semver` → bumps the patch of the manifest `<version>` when that version was already released |
| `timezone` | `America/Chicago` | IANA zone used for the date-based version, the manifest `<creationDate>` and the changelog date. GitHub runners are UTC, which stamps an evening US build with tomorrow's date |
| `create-release` | `true` | Create the GitHub release and upload the package |
| `update-joomla-server` | `true` | Publish `updates.xml` **after** the release asset is verified (requires `create-release`) |
| `commit-changes` | `false` | Commit and push the manifest, `updates.xml` and changelog back to the branch |
| `updates-xml-file` | `updates.xml` | Update feed file name |
| `changelog-file` | `CHANGELOG.md` | Generated changelog file name |
| `license-file` | `License.txt` | License file name |
| `file-updates` | `true` | Rewrite version/date/copyright in manifest, PHP, INI and CSS files |
| `generate-changelog` | `true` | Generate a changelog from the commits since the previous tag |
| `upload-artifact` | `true` | Also upload the unpacked package as a workflow artifact |
| `readme` | `false` | Include `README.md` in the package ZIP |
| `php-version` | `8.1` | PHP version used for the packaging steps |
| `dir-tree-file` | `directory-structure.txt` | Directory listing attached to the release, empty to skip. Not included in the installable package |

> **Note:** `helper-file`, `favicon-file`, `package-dir`, `css-dir`, `js-dir`, `tmpl-dir` and `language-dir` are accepted for backwards compatibility but are not currently used by the action.

### Releases and the update feed

The action is careful about *when* a version becomes public:

- **The feed is published last.** `updates.xml` is only rewritten after the release has been created, and only once the release asset has been confirmed to exist. A failed release therefore never leaves installed sites being offered a download that 404s.
- **Re-runs do not mint empty versions.** Before choosing a version, the action fingerprints the files that actually ship and compares that against the most recent release. If nothing has changed, that version is reused and the release steps are skipped — a re-run, a manual dispatch or a retried job cannot push an identical package onto every installed site as an "update available". The fingerprint mirrors the packaging step's exclusions, so it covers exactly what a user installs: it ignores what the action itself regenerates (`CHANGELOG.md`, `updates.xml`), the manifest's own `<version>`, `<creationDate>` and `<copyright>`, `@version`/`@copyright` headers in PHP, CSS and language files, and everything the package excludes such as `.github/`, `.gitignore`, `build/` and `README.md`. Editing a CI workflow or re-pinning this action therefore does not bump your users' version, while a real source change — including a new field in the manifest — still does.
- **Nothing is left behind.** The action updates files in the workspace only. Set `commit-changes: 'true'` to have it commit and push the version bump, the feed and the changelog back to your branch — otherwise your workflow must do that itself, and a diff check that ignores untracked files will silently drop the feed update. When a version is reused, the changelog is not regenerated and nothing is committed, so the branch stays untouched.
- **Only release metadata is generated.** `dir-tree-file` is written next to the build directory and attached to the release, not inside the installable package, so it never ends up on the end user's server.
- **Dates follow your day, not the runner's.** The version, the manifest `<creationDate>` and the changelog date are all computed in `timezone` (default `America/Chicago`). Set it to `UTC` or your own zone as needed. An unrecognised zone fails the run rather than silently falling back to UTC.

## 🔑 Token Permissions

The `github-token` input (or the default `GITHUB_TOKEN`) is used for creating GitHub Releases, uploading artifacts, updating files, and optionally interacting with pull requests, issues, and GitHub Packages. For the action to perform all its features, the token must have the following permissions:

| Permission           | Why Needed                                                                 |
|----------------------|----------------------------------------------------------------------------|
| contents: write      | Create releases, upload release assets, update files in the repository     |
| pull-requests: write | Update or comment on pull requests (e.g., for changelog or status)         |
| actions: write       | Trigger or manage other workflows, upload artifacts                        |
| packages: write      | Publish to GitHub Packages (optional)                                      |
| issues: write        | Create or comment on issues (optional, e.g., for release notes)            |

- **Minimum required:** `contents: write` (for releases, assets, and file updates)
- **Recommended for full functionality:** Add `pull-requests: write`, `actions: write`, `packages: write`, and `issues: write` as needed for your workflow.
- The default `GITHUB_TOKEN` provided by GitHub Actions usually has `contents: write` and `pull-requests: write` by default, but you may need to explicitly set these in your workflow’s `permissions` block for full access.
- If using a Personal Access Token (PAT), it must have the `repo` scope for private repositories (includes all the above), or at least `public_repo` for public repositories. Add `workflow` and `write:packages` if you need to trigger workflows or publish packages.

**Example permissions block for your workflow:**

```yaml
permissions:
  contents: write
  pull-requests: write
  actions: write
  packages: write
  issues: write
```

If you encounter permission errors, check your workflow's `permissions` block and your token's scopes.

## 📝 Commit Message Format

The action categorizes commits based on their prefix:

- **Added**: `Add`, `Create`, `Implement`, `Feature`
- **Changed**: `Update`, `Improve`, `Enhance`, `Refactor`, `Change`
- **Fixed**: `Fix`, `Bug`, `Correct`, `Resolve`
- **Removed**: `Remove`, `Delete`, `Deprecate`
- **Security**: `Security`

## 🎯 Use Cases

### Basic Module Packaging

```yaml
- uses: N6REJ/joomla-packager@v1
  with:
    extension-name: 'mod_hello_world'
    extension-xml: 'mod_hello_world.xml'
    extension-type: 'module'
    author: 'John Doe'
    copyright-holder: 'Acme Corp'
    copyright-start-year: '2024'
    github-token: ${{ secrets.GH_PAT }}
```

### Plugin with Custom Directories

```yaml
- uses: N6REJ/joomla-packager@v1
  with:
    extension-name: 'plg_system_cache'
    extension-xml: 'plg_system_cache.xml'
    extension-type: 'plugin'
    author: 'Jane Smith'
    copyright-holder: 'Tech Solutions'
    copyright-start-year: '2023'
    github-token: ${{ secrets.GH_PAT }}
    css-dir: 'assets/css'
    js-dir: 'assets/js'
    package-dir: 'dist'
```

### Component with All Features

```yaml
- uses: N6REJ/joomla-packager@v1
  with:
    extension-name: 'com_myapp'
    extension-xml: 'com_myapp.xml'
    extension-type: 'component'
    author: 'Dev Team'
    copyright-holder: 'My Company'
    copyright-start-year: '2022'
    github-token: ${{ secrets.GH_PAT }}
    php-version: '8.2'
    generate-changelog: 'true'
    create-release: 'true'
    update-joomla-server: 'true'
```

### Package with Multiple Extensions

This example shows how to package a complete Joomla package containing a component, module, and multiple plugins (based on [N6REJ/bears_aichatbot](https://github.com/N6REJ/bears_aichatbot)):

```yaml
- uses: N6REJ/joomla-packager@v1
  with:
    extension-name: 'pkg_bears_aichatbot'
    extension-xml: 'pkg_bears_aichatbot.xml'
    extension-type: 'package'
    author: 'N6REJ'
    copyright-holder: 'N6REJ'
    copyright-start-year: '2024'
    github-token: ${{ secrets.GH_PAT }}
    file-updates: 'true'  # Updates version in all included extensions
```

When packaging multiple extensions, the action will:
- Update the package XML manifest
- Update all referenced component, module, and plugin XML files
- Update version and copyright in all PHP, CSS, and language files
- Maintain consistent versioning across all included extensions

### Using Manual Version

```yaml
- uses: N6REJ/joomla-packager@v1
  with:
    extension-name: 'mod_example'
    extension-xml: 'mod_example.xml'
    extension-type: 'module'
    author: 'Your Name'
    copyright-holder: 'Your Company'
    copyright-start-year: '2024'
    github-token: ${{ secrets.GH_PAT }}
    manual-version: '2.0.0'  # Specify your own version
```

### Using Semantic Versioning

```yaml
- uses: N6REJ/joomla-packager@main
  with:
    extension-name: 'mod_example'
    extension-xml: 'mod_example.xml'
    extension-type: 'module'
    author: 'Your Name'
    copyright-holder: 'Your Company'
    copyright-start-year: '2024'
    github-token: ${{ secrets.GH_PAT }}
    version-scheme: 'semver'   # uses the manifest <version>, bumping the patch if already released
    commit-changes: 'true'     # push the version bump and update feed back to main
```

## 🔄 Extending the Action

You can extend this action in several ways:

1. **Fork and Modify**: Customize the action for your specific needs
2. **Wrapper Workflows**: Add pre/post processing steps
3. **Use Outputs**: Access version, package path, and release URL in subsequent steps
4. **Custom Deployment**: Add deployment steps after packaging

Example with custom deployment:

```yaml
- name: Package Extension
  id: package
  uses: N6REJ/joomla-packager@v1
  with:
    # ... your inputs ...

- name: Deploy to Production
  run: |
    echo "Deploying version ${{ steps.packager.outputs.version }}"
    # Your deployment script here
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Share your use cases

## 📄 License

This project is open source and available under the GPL3+ License.

## 🙏 Credits

Based on the workflow from [N6REJ/mod_bears_pricing_tables](https://github.com/N6REJ/mod_bears_pricing_tables).

Example package implementation: [N6REJ/bears_aichatbot](https://github.com/N6REJ/bears_aichatbot) - A complete Joomla package with component, module, and multiple plugins.

---

Made with ❤️ for the Joomla community

## Additional Documentation

For more detailed documentation and usage examples, visit:
https://www.hallhome.us/joomla-packager
