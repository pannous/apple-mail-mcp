# Tools Documentation

Complete reference for all MCP tools provided by the Apple Mail MCP server.

## Current Tools (Phase 1 - v0.1.0)

### search_messages

Search for messages matching specified criteria.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `account` | string | Yes | - | Account name (e.g., "Gmail", "iCloud") |
| `mailbox` | string | No | "INBOX" | Mailbox/folder name |
| `sender_contains` | string | No | None | Filter by sender email or domain |
| `subject_contains` | string | No | None | Filter by subject keywords |
| `read_status` | boolean | No | None | Filter by read status (true=read, false=unread) |
| `limit` | integer | No | 50 | Maximum number of results to return |

**Returns:**

```json
{
  "success": true,
  "account": "Gmail",
  "mailbox": "INBOX",
  "messages": [
    {
      "id": "12345",
      "subject": "Meeting Tomorrow",
      "sender": "john@example.com",
      "date_received": "Mon Jan 15 2024 10:30:00",
      "read_status": false
    }
  ],
  "count": 1
}
```

**Examples:**

```python
# Find all unread messages
search_messages(account="Gmail", read_status=False)

# Find messages from specific sender
search_messages(account="Gmail", sender_contains="john@example.com")

# Find messages with keyword in subject
search_messages(account="Gmail", subject_contains="invoice", limit=10)

# Complex search
search_messages(
    account="Gmail",
    mailbox="Work",
    sender_contains="@company.com",
    subject_contains="urgent",
    read_status=False,
    limit=20
)
```

**Error Codes:**

- `account_not_found`: Specified account doesn't exist
- `not_found`: Mailbox not found
- `unknown`: Unexpected error occurred

---

### get_message

Retrieve full details of a specific message.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message_id` | string | Yes | - | Message ID from search results |
| `include_content` | boolean | No | true | Include message body content |

**Returns:**

```json
{
  "success": true,
  "message": {
    "id": "12345",
    "subject": "Meeting Tomorrow",
    "sender": "john@example.com",
    "date_received": "Mon Jan 15 2024 10:30:00",
    "read_status": false,
    "flagged": true,
    "content": "Let's meet tomorrow at 2pm to discuss the project..."
  }
}
```

**Examples:**

```python
# Get message with content
get_message(message_id="12345")

# Get message without content (faster)
get_message(message_id="12345", include_content=False)
```

**Error Codes:**

- `message_not_found`: Message doesn't exist or was deleted
- `unknown`: Unexpected error occurred

---

### send_email

Send an email via Apple Mail.

**⚠️ Security Note:** This operation requires user confirmation before sending.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `subject` | string | Yes | - | Email subject line |
| `body` | string | Yes | - | Email body (plain text) |
| `to` | array[string] | Yes | - | List of recipient email addresses |
| `cc` | array[string] | No | [] | List of CC recipients |
| `bcc` | array[string] | No | [] | List of BCC recipients |

**Returns:**

```json
{
  "success": true,
  "message": "Email sent successfully",
  "details": {
    "subject": "Meeting Tomorrow",
    "recipients": 3
  }
}
```

**Examples:**

```python
# Simple email
send_email(
    subject="Hello",
    body="Just wanted to say hi!",
    to=["friend@example.com"]
)

# Email with CC and BCC
send_email(
    subject="Project Update",
    body="Here's the latest status...",
    to=["team@company.com"],
    cc=["manager@company.com"],
    bcc=["archive@company.com"]
)

# Email to multiple recipients
send_email(
    subject="Team Meeting",
    body="Meeting at 2pm today.",
    to=["alice@company.com", "bob@company.com", "charlie@company.com"]
)
```

**Validation Rules:**

- At least one `to` recipient required
- Maximum 100 total recipients (to + cc + bcc)
- All email addresses must be valid format
- User confirmation required before sending

**Error Codes:**

- `validation_error`: Invalid recipients or parameters
- `cancelled`: User cancelled the send operation
- `send_error`: Mail.app failed to send the email
- `unknown`: Unexpected error occurred

---

### list_mailboxes

List all mailboxes (folders) for a specific account.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `account` | string | Yes | - | Account name (e.g., "Gmail", "iCloud") |

**Returns:**

```json
{
  "success": true,
  "account": "Gmail",
  "mailboxes": [
    {
      "name": "INBOX",
      "unread_count": 5
    },
    {
      "name": "Sent",
      "unread_count": 0
    },
    {
      "name": "Archive",
      "unread_count": 2
    }
  ]
}
```

**Examples:**

```python
# List mailboxes
list_mailboxes(account="Gmail")

# List mailboxes for different account
list_mailboxes(account="iCloud")
```

**Error Codes:**

- `account_not_found`: Account doesn't exist
- `unknown`: Unexpected error occurred

---

### mark_as_read

Mark one or more messages as read or unread.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message_ids` | array[string] | Yes | - | List of message IDs to update |
| `read` | boolean | No | true | true to mark as read, false for unread |

**Returns:**

```json
{
  "success": true,
  "updated": 3,
  "requested": 3
}
```

**Examples:**

```python
# Mark messages as read
mark_as_read(message_ids=["12345", "12346", "12347"])

# Mark messages as unread
mark_as_read(message_ids=["12345"], read=False)
```

**Validation Rules:**

- Maximum 100 message IDs per request
- At least one message ID required

**Error Codes:**

- `validation_error`: Too many message IDs or invalid input
- `unknown`: Unexpected error occurred

---

## Coming Soon (Phase 2 - v0.2.0)

### send_email_with_attachments

Send email with file attachments.

**Parameters:**
- `subject`, `body`, `to`, `cc`, `bcc` (same as send_email)
- `attachments`: array[string] - File paths to attach

### get_attachments

List or save attachments from a message.

**Parameters:**
- `message_id`: string - Message ID
- `save_directory`: string (optional) - Directory to save attachments

### move_messages

Move messages to a different mailbox.

**Parameters:**
- `message_ids`: array[string] - Messages to move
- `destination_mailbox`: string - Target mailbox name
- `account`: string - Account name

### flag_message

Set color flag on messages.

**Parameters:**
- `message_id`: string - Message to flag
- `color`: string - Flag color (none, orange, red, yellow, blue, green, purple, gray)

### create_mailbox

Create a new mailbox/folder.

**Parameters:**
- `account`: string - Account name
- `name`: string - Mailbox name
- `parent_mailbox`: string (optional) - Parent for nested mailboxes

### get_thread

Get all messages in a conversation thread.

**Parameters:**
- `message_id`: string - Any message in the thread

### delete_messages

Delete messages (move to trash).

**Parameters:**
- `message_ids`: array[string] - Messages to delete
- `confirm`: boolean - Require confirmation

---

## Error Handling

All tools return a consistent error format:

```json
{
  "success": false,
  "error": "Detailed error message",
  "error_type": "error_category"
}
```

**Common Error Types:**

- `account_not_found`: Account doesn't exist
- `mailbox_not_found`: Mailbox doesn't exist
- `message_not_found`: Message doesn't exist or was deleted
- `validation_error`: Invalid parameters
- `permission_error`: Insufficient permissions
- `cancelled`: User cancelled the operation
- `unknown`: Unexpected error

---

## Best Practices

### Search Performance

```python
# Good: Use specific filters
search_messages(
    account="Gmail",
    sender_contains="@company.com",
    read_status=False,
    limit=20
)

# Bad: Retrieve everything then filter
all_messages = search_messages(account="Gmail", limit=10000)
# ... filter in Python
```

### Error Handling

```python
# Always check success field
result = search_messages(account="Gmail")

if result["success"]:
    messages = result["messages"]
    print(f"Found {result['count']} messages")
else:
    print(f"Error: {result['error']}")
    print(f"Type: {result['error_type']}")
```

### Batch Operations

```python
# Good: Process in batches
message_ids = [...]  # Large list
for i in range(0, len(message_ids), 100):
    batch = message_ids[i:i+100]
    mark_as_read(message_ids=batch)

# Bad: Single request with too many IDs
mark_as_read(message_ids=message_ids)  # May fail if > 100
```

### Account Names

```python
# Use exact account name from Mail.app
# Check in Mail → Settings → Accounts

# Good
list_mailboxes(account="Gmail")

# Bad (won't work)
list_mailboxes(account="gmail")
list_mailboxes(account="my gmail account")
```

---

## Security Considerations

### Sending Emails

- All send operations require user confirmation
- Validate recipients before sending
- Limit recipient count to prevent spam
- Operations are logged for audit trail

### Input Validation

- All inputs are sanitized and validated
- Email addresses must match valid format
- Message IDs are sanitized
- File paths are validated (Phase 2+)

### Rate Limiting

- Bulk operations limited to 100 items
- Consider implementing additional rate limits for production use

---

## Tool Combinations

### Example Workflows

**Inbox Zero Workflow:**

```python
# 1. Find all unread messages
unread = search_messages(account="Gmail", read_status=False)

# 2. For each message, get full details
for msg in unread["messages"]:
    full_msg = get_message(message_id=msg["id"])
    # Process message...

# 3. Mark processed messages as read
processed_ids = [msg["id"] for msg in unread["messages"]]
mark_as_read(message_ids=processed_ids)
```

**Email Response Workflow:**

```python
# 1. Search for specific email
results = search_messages(
    account="Gmail",
    sender_contains="client@company.com",
    subject_contains="proposal",
    limit=1
)

# 2. Get full message
original = get_message(message_id=results["messages"][0]["id"])

# 3. Send reply
send_email(
    subject=f"Re: {original['message']['subject']}",
    body="Thank you for your proposal...",
    to=[original["message"]["sender"]]
)
```

---

## API Stability

- **Phase 1 (v0.1.x)**: Current tools are stable
- **Phase 2 (v0.2.x)**: New tools will be added, existing tools unchanged
- **Phase 3+ (v0.3.x+)**: Advanced features, backward compatible

Breaking changes will only occur in major versions (1.0.0, 2.0.0, etc.).
