# Joomla Extension Packager GitHub Action

This GitHub Action packages and releases Joomla extensions (modules, plugins & components) with built-in validation for extension structure. All logic and validation is handled within the action—your workflow only needs to call this action.

## Features
- Packages Joomla modules, plugins, and components
- Validates extension folder structure (admin/administrator, language(s), etc.)
- Updates version, copyright, and changelog
- Creates GitHub releases and uploads artifacts
- Generates directory tree and changelog files

# Usage
## Inputs
Below is a detailed explanation of all inputs supported by this action:

### Extension Identification
- **extension-name** (string, optional):
  - Description: Extension folder and file prefix (e.g. `mod_example`, `plg_system_example`). If not specified, derived from repository name.
  - Default: `''`
- **extension-xml** (string, optional):
  - Description: Main XML file (e.g. `mod_example.xml`). If not specified, derived from extension name.
  - Default: `''`
- **extension-type** (string, optional):
  - Description: Type of extension (`module`, `plugin`, `component`). If not specified, derived from repository name prefix.
  - Default: `''`

### Author and Copyright
- **author** (string, optional):
  - Description: Author name or handle. If not specified, uses the repository owner.
  - Default: `''`
- **copyright-holder** (string, optional):
  - Description: Copyright string (e.g. `Your Name (YourHandle)`). If omitted, copyright update steps will be skipped.
  - Default: `''`
- **copyright-start-year** (string, optional):
  - Description: Copyright start year (e.g. `2024`). If omitted, copyright update steps will be skipped.
  - Default: `''`

### Version Control
- **github-token** (string, required):
  - Description: GitHub token for authentication.
- **manual-version** (string, optional):
  - Description: Manual version override (e.g. `1.2.3`). If not specified, uses automatic date-based versioning.
  - Default: `''`

### PHP Configuration
- **php-version** (string, optional):
  - Description: PHP version to use.
  - Default: `'8.1'`

### File Configurations
- **changelog-file** (string, optional):
  - Description: Changelog filename.
  - Default: `'CHANGELOG.md'`
- **helper-file** (string, optional):
  - Description: Helper PHP file.
  - Default: `'helper.php'`
- **license-file** (string, optional):
  - Description: License file.
  - Default: `'License.txt'`
- **favicon-file** (string, optional):
  - Description: Favicon file (leave empty to skip).
  - Default: `'favicon.ico'`
- **updates-xml-file** (string, optional):
  - Description: Updates XML file.
  - Default: `'updates.xml'`

### Directory Configurations
- **css-dir** (string, optional):
  - Description: CSS directory.
  - Default: `'css'`
- **js-dir** (string, optional):
  - Description: JS directory.
  - Default: `'js'`
- **tmpl-dir** (string, optional):
  - Description: Template directory.
  - Default: `'tmpl'`
- **language-dir** (string, optional):
  - Description: Language directory.
  - Default: `'language'`
- **package-dir** (string, optional):
  - Description: Package output directory.
  - Default: `'package'`

### Additional Features
- **dir-tree-file** (string, optional):
  - Description: Directory tree output file (leave empty to skip).
  - Default: `'directory-structure.txt'`
- **file-updates** (string, optional):
  - Description: Whether to update version and copyright in files (`true` or `false`).
  - Default: `'true'`
- **generate-changelog** (string, optional):
  - Description: Whether to generate changelog from commits (`true` or `false`).
  - Default: `'true'`
- **create-release** (string, optional):
  - Description: Whether to create a GitHub release (`true` or `false`).
  - Default: `'true'`
- **upload-artifact** (string, optional):
  - Description: Whether to upload as GitHub artifact (`true` or `false`).
  - Default: `'true'`
- **update-joomla-server** (string, optional):
  - Description: Whether to update Joomla update server XML (`true` or `false`).
  - Default: `'true'`

For most projects, you only need to set the required inputs. All other options have sensible defaults and can be overridden as needed.

## Component Structure Validation
If `extension-type` is `component`, the action will:
- **Require** either an `admin` or `administrator` directory at the root.
- **Require** either a `language` or `languages` directory inside the `admin`/`administrator` directory.
- **Warn** if the following are missing:
  - `src` or `tmpl` inside `admin`/`administrator`
  - `site` at root (and its `src`, `tmpl`, `language(s)`)
  - `media`, `services`, `forms`, `lib`/`libraries`, `helpers`/`helper` at root

If any of these optional folders exist (including `media`), they will be included in the package automatically. The `media` directory is always included for any extension type (module, plugin, or component) if it exists. If the required folders are missing, the action will fail and print an error. Warnings are printed for recommended folders.

## Excluding Unnecessary Files

The action automatically excludes the following from your package:
- `.git/`, `.github/`, `.DS_Store`, `Thumbs.db`, `node_modules/`, and `.packagerignore` itself
- Any files or directories listed in a `.packagerignore` file at the root of your repository (if present)

The `.packagerignore` file works like a `.gitignore`—add one pattern per line to exclude files or folders from the package. Lines starting with `#` are treated as comments.

## Outputs
- `version`: The generated version number
- `creation-date`: The creation date
- `package-path`: Path to the created package
- `release-url`: URL of the created release

## Example
See the usage example above. All you need to do is call this action in your workflow; all packaging, validation, and release logic is handled internally.


Add the following to your workflow (e.g. `.github/workflows/release.yml`):

```yaml
name: Joomla Extension Packager
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

      - uses: N6REJ/joomla-packager@2025.6.24
        with:
          extension-name: 'mod_example'
          extension-xml: 'mod_example.xml'
          extension-type: 'module'
          author: 'Your Name'
          copyright-holder: 'Your Company'
          copyright-start-year: '2024'
          github-token: ${{ secrets.GH_PAT }}
```

> **Note:**
> Replace `latest` with a specific version tag (e.g. `v1.0.0`) for production workflows to ensure stability.
> 
> **Authentication:**
> You must create a Personal Access Token (PAT) with appropriate permissions (e.g. `repo`, `workflow`) and add it to your repository secrets as `GH_PAT`. The default `GITHUB_TOKEN` does not have sufficient permissions for some release and artifact operations.
