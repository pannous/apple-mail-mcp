#!/bin/bash
set -e

CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
BACKUP_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json.backup"

echo "🔧 Configuring Claude Desktop for Apple Mail MCP"
echo "================================================"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Claude Desktop config not found at:"
    echo "   $CONFIG_FILE"
    echo ""
    echo "💡 Please install Claude Desktop first"
    exit 1
fi

echo "✓ Found Claude Desktop config"

# Backup existing config
echo "📋 Creating backup..."
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "✓ Backup saved to: $BACKUP_FILE"

# Check if apple-mail already configured
if grep -q '"apple-mail"' "$CONFIG_FILE"; then
    echo ""
    echo "⚠️  apple-mail MCP is already configured"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Use Python to update JSON properly
python3 - "$CONFIG_FILE" << 'EOF'
import json
import sys

config_file = sys.argv[1]

# Read existing config
with open(config_file, 'r') as f:
    config = json.load(f)

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add or update apple-mail server
config['mcpServers']['apple-mail'] = {
    'command': 'python3',
    'args': ['-m', 'apple_mail_mcp.server']
}

# Write back
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuration updated successfully!")
EOF

echo ""
echo "📝 Current configuration:"
cat "$CONFIG_FILE"

echo ""
echo ""
echo "✅ Done! Next steps:"
echo ""
echo "1. Restart Claude Desktop"
echo "2. Test by asking Claude: 'List my mailboxes'"
echo ""
echo "💡 To restore previous config:"
echo "   cp \"$BACKUP_FILE\" \"$CONFIG_FILE\""
