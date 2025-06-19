# Joomla Extension Packager

A reusable GitHub composite action for packaging and releasing Joomla extensions. This action automates the entire process of versioning, packaging, and releasing Joomla modules, plugins, and components.

## 🚀 Features

- **Automatic Versioning**: Date-based versioning (YYYY.MM.DD format) with support for multiple releases per day
- **File Updates**: Automatically updates version and copyright information across all files
- **Changelog Generation**: Creates changelogs from commit messages following Keep a Changelog format
- **Package Creation**: Builds properly structured ZIP files for Joomla installation
- **GitHub Releases**: Creates releases with artifacts and release notes
- **Joomla Updates**: Updates the Joomla update server XML
- **Multi-Extension Support**: Works with modules, plugins, and components
- **Extensible**: Easy to extend and customize for specific needs

## 📋 Quick Start

1. **Add the action to your repository** by copying the `.github/actions/joomla-packager` directory

2. **Create a workflow** in `.github/workflows/package.yml`:

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
      
      - uses: ./.github/actions/joomla-packager
        with:
          extension-name: 'mod_example'
          extension-xml: 'mod_example.xml'
          extension-type: 'module'
          author: 'Your Name'
          copyright-holder: 'Your Company'
          copyright-start-year: '2024'
          github-token: ${{ secrets.GH_PAT }}
```

3. **Set up your GitHub PAT** in repository secrets as `GH_PAT`

## 📁 Repository Structure

```
joomla-packager/
├── .github/
│   ├── actions/
│   │   └── joomla-packager/
│   │       ├── action.yml          # The composite action
│   │       └── README.md           # Action documentation
│   └── workflows/
│       └── example-usage.yml       # Example workflow
└── README.md                       # This file
```

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

See the [action README](.github/actions/joomla-packager/README.md) for all available options.

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
- uses: ./.github/actions/joomla-packager
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
- uses: ./.github/actions/joomla-packager
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
- uses: ./.github/actions/joomla-packager
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
  uses: ./.github/actions/joomla-packager
  with:
    # ... your inputs ...

- name: Deploy to Production
  run: |
    echo "Deploying version ${{ steps.package.outputs.version }}"
    # Your deployment script here
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Share your use cases

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Credits

Based on the workflow from [N6REJ/mod_bears_pricing_tables](https://github.com/N6REJ/mod_bears_pricing_tables).

---

Made with ❤️ for the Joomla community
