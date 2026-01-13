# Installation Guide for Apple Mail MCP (Local Development)

## Quick Start

```bash
# 1. Install the package
./install.sh

# 2. Configure Claude Desktop
./configure_claude.sh

# 3. Restart Claude Desktop
```

## Manual Installation

If you prefer to install manually:

### Step 1: Install Package

```bash
cd /Users/me/ai/mcp/apple-mail-mcp
pip install -e ".[dev]"
```

The `-e` flag installs in "editable" mode, meaning:
- Changes to the code take effect immediately
- No need to reinstall after making changes
- Just restart Claude Desktop to pick up changes

### Step 2: Configure Claude Desktop

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add to the `mcpServers` section:

```json
{
  "mcpServers": {
    "apple-mail": {
      "command": "python3",
      "args": ["-m", "apple_mail_mcp.server"]
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

## Testing

After installation, test by asking Claude:

```
List my mailboxes
```

or

```
Search for unread emails in my inbox
```

## Development Workflow

1. Make changes to the code in `src/apple_mail_mcp/`
2. Run tests: `pytest`
3. Restart Claude Desktop (no reinstall needed!)
4. Test your changes through Claude

## Troubleshooting

### MCP Server Not Showing Up

Check Claude Desktop logs:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

### Permission Issues

Grant permissions when prompted:
- **Automation**: Allow controlling Apple Mail
- **Full Disk Access**: Only needed for Phase 4 features

### Python Version Issues

Ensure you're using Python 3.10+:
```bash
python3 --version
```

### Module Not Found

If you get "No module named 'apple_mail_mcp'":
```bash
# Reinstall in editable mode
cd /Users/me/ai/mcp/apple-mail-mcp
pip install -e .
```

## Uninstalling

To remove:
```bash
# Uninstall package
pip uninstall apple-mail-mcp

# Remove from Claude Desktop config
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
# Remove the "apple-mail" entry from mcpServers
```

## Alternative: Run Without Installing

You can also run the server directly without installing:

```json
{
  "mcpServers": {
    "apple-mail": {
      "command": "python3",
      "args": [
        "/Users/me/ai/mcp/apple-mail-mcp/src/apple_mail_mcp/server.py"
      ]
    }
  }
}
```

However, this won't include the entry point and may have import issues.

## Next Steps

- Read [TOOLS.md](TOOLS.md) for available commands
- Check [README.md](README.md) for usage examples
- See [CLAUDE.md](.claude/CLAUDE.md) for development guidelines
