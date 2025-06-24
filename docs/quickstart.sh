#!/bin/bash

# Joomla Extension Packager - Quick Start Script
# This script helps you set up the composite action for your extension

echo "🚀 Joomla Extension Packager - Quick Start"
echo "=========================================="
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: This script must be run from the root of a git repository"
    exit 1
fi

# Get extension details
echo "Please provide your extension details:"
echo ""

read -p "Extension type (module/plugin/component): " EXT_TYPE
read -p "Extension name (e.g., mod_example): " EXT_NAME
read -p "Extension XML file (e.g., mod_example.xml): " EXT_XML
read -p "Author name: " AUTHOR
read -p "Copyright holder: " COPYRIGHT_HOLDER
read -p "Copyright start year: " COPYRIGHT_YEAR

# Create workflow directory if it doesn't exist
mkdir -p .github/workflows

# Generate workflow file
WORKFLOW_FILE=".github/workflows/package-release.yml"

cat > "$WORKFLOW_FILE" << EOF
name: Package and Release

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
          token: \${{ secrets.GH_PAT }}
      
      - name: Joomla Extension Packager
        uses: N6REJ/joomla-packager@2025.6.23
        id: packager
        with:
          extension-name: '$EXT_NAME'
          extension-xml: '$EXT_XML'
          extension-type: '$EXT_TYPE'
          author: '$AUTHOR'
          copyright-holder: '$COPYRIGHT_HOLDER'
          copyright-start-year: '$COPYRIGHT_YEAR'
          github-token: \${{ secrets.GH_PAT }}
      
      - name: Commit changes
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          
          if git diff --exit-code; then
            echo "No changes to commit"
          else
            git add .
            git commit -m "Update version to \${{ steps.packager.outputs.version }} [skip ci]"
            git push origin main
          fi
EOF

echo ""
echo "✅ Workflow created at: $WORKFLOW_FILE"
echo ""
echo "Next steps:"
echo "1. Add the composite action to your repository:"
echo "   - Copy the .github/actions/joomla-packager directory"
echo ""
echo "2. Set up your GitHub Personal Access Token:"
echo "   - Go to Settings > Secrets and variables > Actions"
echo "   - Create a new secret named 'GH_PAT'"
echo "   - Use a token with 'repo' permissions"
echo ""
echo "3. Commit and push your changes:"
echo "   git add ."
echo "   git commit -m 'Add Joomla packager action'"
echo "   git push"
echo ""
echo "4. Test the workflow:"
echo "   - Go to Actions tab in your repository"
echo "   - Select 'Package and Release' workflow"
echo "   - Click 'Run workflow'"
echo ""
echo "📚 For more information, see README.md"
