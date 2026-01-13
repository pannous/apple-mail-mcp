# Test Probes for Apple Mail MCP

This directory contains test probes for validating MCP functionality with real Apple Mail data.

## Text Extraction Probes

### ✅ `final_working_test.py` (RECOMMENDED)

**Status**: ✅ Working
**Purpose**: Test text extraction from email attachments using the `extract_text_from_file` function.

```bash
python probes/final_working_test.py [account_name]
```

This probe:
- Finds a message with attachments in Apple Mail
- Saves the first attachment to `/tmp/apple_mail_test/`
- Extracts text using the `extract_text_from_file()` function
- Displays extracted text statistics and preview

**Tested successfully with**: PDF files from iCloud account

---

### Other Probes (For Reference)

These probes were created during development to work around bugs in `search_messages()` and message ID handling:

- `test_text_extraction.py` - Original attempt using MailConnector.search_messages (fails due to bug)
- `simple_text_extraction_test.py` - Simplified version with direct AppleScript
- `direct_attachment_test.py` - Tests message ID retrieval (exposes ID format issue)
- `test_with_connector.py` - Uses connector's search methods (fails due to search bug)
- `final_extraction_test.py` - Bypasses search, but still hits message ID issue
- `working_extraction_test.py` - Saves attachment directly, hits temp directory issue

## Usage

The probes require:
1. Apple Mail configured with at least one account
2. At least one email with an attachment in the INBOX
3. Text extraction dependencies installed: `pip install -e ".[text-extraction]"`

## Test Results (2026-01-13)

✅ **Text extraction is working correctly**

- Tested with: PDF attachment (5,518 bytes)
- Extracted: 590 characters, 29 lines
- Format: German tax document (Umsatzsteuer-Voranmeldung)
- All 7 unit tests passing

## Known Issues

1. **search_messages() bug**: The function generates invalid AppleScript ("whose true") when no filters are provided
2. **Message ID format**: Direct AppleScript message IDs don't match the format expected by `get_attachments()`

These issues don't affect the core text extraction functionality, which works correctly when attachments are accessed properly.
