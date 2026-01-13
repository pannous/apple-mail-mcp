# ✅ Setup Complete!

Your Apple Mail MCP server is now installed and configured for Claude Desktop.

## What Was Done

1. ✅ **Installed package** in editable mode (`pip install -e ".[dev]"`)
   - Package: `apple-mail-mcp` v0.3.0
   - Location: `/Users/me/ai/mcp/apple-mail-mcp`
   - Mode: Editable (changes take effect on Claude restart)

2. ✅ **Configured Claude Desktop**
   - Config: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Backup: `~/Library/Application Support/Claude/claude_desktop_config.json.backup`
   - Added: `apple-mail` MCP server

3. ✅ **Created helper scripts**
   - `install.sh` - Reinstall/update the package
   - `configure_claude.sh` - Reconfigure Claude Desktop
   - `INSTALL.md` - Detailed installation guide

## Next Step: Restart Claude

**⚠️ IMPORTANT: You MUST restart Claude Desktop for the MCP to be available.**

To restart:
1. Quit Claude Desktop completely (Cmd+Q)
2. Reopen Claude Desktop
3. Start a new conversation

## Testing

After restarting Claude Desktop, test the MCP by asking:

```
List my mailboxes
```

or

```
Search for unread emails in my inbox
```

## Current Configuration

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

## Development Workflow

Now that it's installed in editable mode:

1. **Make changes** to files in `src/apple_mail_mcp/`
2. **Run tests**: `pytest`
3. **Restart Claude Desktop** (no reinstall needed!)
4. **Test** your changes

## Troubleshooting

### MCP Not Showing Up

Check Claude Desktop logs:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

### Test Server Manually

Run the server directly to test:
```bash
apple-mail-mcp
```

or

```bash
python3 -m apple_mail_mcp.server
```

### Permissions

On first use, macOS will prompt for:
- **Automation**: Allow controlling Apple Mail
- Grant this when prompted

### Reinstall

If you need to reinstall:
```bash
cd /Users/me/ai/mcp/apple-mail-mcp
./install.sh
```

## Available Tools

Once loaded, Claude will have access to these Apple Mail tools:

- `search_messages` - Search emails with filters
- `get_message` - Read full message content
- `send_email` - Send emails (with confirmation)
- `list_mailboxes` - List mail folders
- `mark_as_read` - Mark messages as read/unread
- `get_attachments` - List email attachments
- `save_attachment` - Save attachments to disk
- `move_message` - Move messages between mailboxes
- `set_flag` - Flag/unflag messages
- `get_thread` - Get email conversation threads
- `reply_to_message` - Reply to emails
- `forward_message` - Forward emails

See [TOOLS.md](TOOLS.md) for detailed documentation.

## Next Steps

1. **Restart Claude Desktop** ← DO THIS NOW
2. Test the MCP
3. Read [TOOLS.md](TOOLS.md) for available commands
4. Check [CLAUDE.md](.claude/CLAUDE.md) for development guidelines

---

**Remember:** This MCP session needs to be restarted for the changes to take effect!
