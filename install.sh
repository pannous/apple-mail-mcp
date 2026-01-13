#!/bin/bash
set -e

echo "🍎 Installing Apple Mail MCP Server (local development)"
echo "======================================================"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Install in editable mode
echo ""
echo "📦 Installing package in editable mode..."
pip install -e ".[dev]"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Configure Claude Desktop by editing:"
echo "   ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "2. Add this configuration:"
echo ""
cat << 'EOF'
{
  "mcpServers": {
    "apple-mail": {
      "command": "python3",
      "args": ["-m", "apple_mail_mcp.server"]
    }
  }
}
EOF
echo ""
echo "3. Restart Claude Desktop"
echo ""
echo "💡 To test the server directly, run:"
echo "   apple-mail-mcp"
echo ""
echo "🔧 After making code changes, just restart Claude Desktop"
echo "   (no need to reinstall thanks to editable mode)"
