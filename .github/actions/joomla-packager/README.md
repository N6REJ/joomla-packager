# Joomla Extension Packager Action

A reusable GitHub composite action for packaging and releasing Joomla extensions (modules, plugins, and components).

## Features

- 🔄 Automatic version generation based on date (YYYY.MM.DD format)
- 🎯 Manual version override support (e.g., 1.2.3, 2.0.0-beta)
- 🤖 Automatic extension name detection from repository name
- 📝 Updates version and copyright information across all files
- 📋 Generates changelog from commit messages
- 📦 Creates ZIP packages for Joomla installation
- 🚀 Creates GitHub releases with artifacts
- 🔧 Updates Joomla update server XML
- 🌳 Generates directory structure documentation
- 🎨 Supports modules, plugins, and components

## Usage

### Basic Example

```yaml
name: Package and Release
on:
  pull_request:
    types: [closed]
    branches:
      - main
  workflow_dispatch:

jobs:
  package:
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

      - name: Package Extension
        uses: ./.github/actions/joomla-packager
        with:
          extension-name: 'mod_example'
          extension-xml: 'mod_example.xml'
          extension-type: 'module'
          author: 'YourName'
          copyright-holder: 'Your Company (YourHandle)'
          copyright-start-year: '2024'
          github-token: ${{ secrets.GH_PAT }}
```

### Advanced Example with All Options

```yaml
- name: Package Extension
  uses: ./.github/actions/joomla-packager
  with:
    # Required inputs
    extension-name: 'plg_system_example'
    extension-xml: 'plg_system_example.xml'
    extension-type: 'plugin'
    author: 'John Doe'
    copyright-holder: 'Acme Corp (johndoe)'
    copyright-start-year: '2023'
    github-token: ${{ secrets.GH_PAT }}
    
    # Optional inputs
    php-version: '8.2'
    changelog-file: 'CHANGELOG.md'
    helper-file: 'helper.php'
    license-file: 'LICENSE'
    favicon-file: 'icon.png'
    updates-xml-file: 'updates.xml'
    css-dir: 'assets/css'
    js-dir: 'assets/js'
    tmpl-dir: 'tmpl'
    language-dir: 'language'
    package-dir: 'dist'
    dir-tree-file: 'structure.txt'
    generate-changelog: 'true'
    create-release: 'true'
    upload-artifact: 'true'
    update-joomla-server: 'true'
```

## Inputs

### Required Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `extension-type` | Type of extension | `module`, `plugin`, `component` |
| `author` | Author name or handle | `John Doe` |
| `copyright-holder` | Copyright string | `Acme Corp (johndoe)` |
| `copyright-start-year` | Copyright start year | `2023` |
| `github-token` | GitHub token for authentication | `${{ secrets.GH_PAT }}` |

### Optional Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `extension-name` | Extension folder and file prefix (e.g. mod_example) | Derived from repository name |
| `extension-xml` | Main XML manifest file (e.g. mod_example.xml) | Derived from extension name |
| `manual-version` | Manual version override (e.g. 1.2.3, 2.0.0-beta) | `` (uses automatic versioning) |
| `php-version` | PHP version to use | `8.1` |
| `file-updates` | Whether to update version and copyright in files | `true` |
| `changelog-file` | Changelog filename | `CHANGELOG.md` |
| `helper-file` | Helper PHP file | `helper.php` |
| `license-file` | License file | `License.txt` |
| `favicon-file` | Favicon/icon file | `favicon.ico` |
| `updates-xml-file` | Joomla updates XML | `updates.xml` |
| `css-dir` | CSS directory | `css` |
| `js-dir` | JavaScript directory | `js` |
| `tmpl-dir` | Template directory | `tmpl` |
| `language-dir` | Language directory | `language` |
| `package-dir` | Package output directory | `package` |
| `dir-tree-file` | Directory tree output | `directory-structure.txt` |
| `generate-changelog` | Generate changelog from commits | `true` |
| `create-release` | Create GitHub release | `true` |
| `upload-artifact` | Upload as GitHub artifact | `true` |
| `update-joomla-server` | Update Joomla update server | `true` |

## Outputs

| Output | Description |
|--------|-------------|
| `version` | The generated version number |
| `creation-date` | The creation date |
| `package-path` | Path to the created package |
| `release-url` | URL of the created release |

## Version Format

The action supports two versioning modes:

### Automatic Versioning (Default)
- Format: `YYYY.MM.DD[.N]`
- Example: `2024.01.15` or `2024.01.15.2` (if multiple releases on same day)
- Automatically increments if multiple releases occur on the same day

### Manual Versioning
- Use the `manual-version` input to specify any version format
- Examples: `1.0.0`, `2.1.3`, `3.0.0-beta.1`, `1.2.3-rc.2`
- Useful for semantic versioning or specific release milestones

Example with manual version:
```yaml
- uses: ./.github/actions/joomla-packager
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

## Changelog Generation

Commits are automatically categorized based on their prefix:
- **Added**: `Add`, `Create`, `Implement`, `Feature`
- **Changed**: `Update`, `Improve`, `Enhance`, `Refactor`, `Change`
- **Fixed**: `Fix`, `Bug`, `Correct`, `Resolve`
- **Removed**: `Remove`, `Delete`, `Deprecate`
- **Security**: `Security`

## File Updates

The action automatically updates version and copyright information across all files by default. This includes:
- Version in XML manifest files
- Creation date in XML files
- Copyright years in all supported files
- `@version` tags in PHP files
- Version headers in CSS files
- Copyright notices in language files

### Disabling File Updates

If you want to manage file versions manually or have files that shouldn't be modified, you can disable automatic file updates:

```yaml
- uses: ./.github/actions/joomla-packager
  with:
    extension-name: 'mod_example'
    extension-xml: 'mod_example.xml'
    extension-type: 'module'
    author: 'Your Name'
    copyright-holder: 'Your Company'
    copyright-start-year: '2024'
    github-token: ${{ secrets.GH_PAT }}
    file-updates: 'false'  # Disable automatic file updates
```

When `file-updates` is set to `false`, the action will:
- Still generate the version number (automatic or manual)
- Create the package with existing file contents
- Create releases and artifacts
- But NOT modify any files in your repository

## Extension Type Support

### Modules
Standard Joomla module structure with:
- Main PHP file
- XML manifest
- Helper file
- Templates, CSS, JS, and language files

### Plugins
Plugin structure with support for:
- Plugin PHP file
- XML manifest
- Forms and fields directories
- Language files

### Components
Component structure with:
- Admin and site directories
- Media directory
- XML manifest
- Language files

## Requirements

- GitHub repository with proper permissions
- Personal Access Token (PAT) with repo permissions
- Extension files in standard Joomla structure

## Example Workflow

Create `.github/workflows/package.yml`:

```yaml
name: Package Extension
on:
  push:
    branches: [main]
  pull_request:
    types: [closed]
    branches: [main]
  workflow_dispatch:

jobs:
  package:
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch' || (github.event_name == 'pull_request' && github.event.pull_request.merged == true)
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GH_PAT }}
      
      - uses: ./.github/actions/joomla-packager
        with:
          extension-name: 'mod_mymodule'
          extension-xml: 'mod_mymodule.xml'
          extension-type: 'module'
          author: 'My Name'
          copyright-holder: 'My Company'
          copyright-start-year: '2024'
          github-token: ${{ secrets.GH_PAT }}
```

## Extending the Action

This composite action can be extended by:

1. **Forking and modifying** the action.yml file
2. **Creating a wrapper workflow** that adds additional steps
3. **Using outputs** in subsequent workflow steps
4. **Customizing file patterns** for your specific needs

### Example Extension

```yaml
- name: Package Extension
  id: package
  uses: ./.github/actions/joomla-packager
  with:
    extension-name: 'com_example'
    extension-xml: 'com_example.xml'
    extension-type: 'component'
    author: 'Your Name'
    copyright-holder: 'Your Company'
    copyright-start-year: '2024'
    github-token: ${{ secrets.GH_PAT }}

- name: Additional Processing
  run: |
    echo "Version created: ${{ steps.package.outputs.version }}"
    echo "Package location: ${{ steps.package.outputs.package-path }}"
    # Add your custom processing here

- name: Deploy to Server
  run: |
    # Custom deployment logic
    echo "Deploying version ${{ steps.package.outputs.version }}"
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure your PAT has appropriate permissions
2. **Files Not Found**: Check your extension structure matches Joomla standards
3. **Version Conflicts**: The action handles multiple releases per day automatically
4. **Missing Dependencies**: Ensure all required files exist in your repository

### Debug Mode

Add debug logging to your workflow:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This action is provided as-is for use in Joomla extension development.
