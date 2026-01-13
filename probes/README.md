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

## Search Messages Probes

### ✅ `test_search_comprehensive.py` (RECOMMENDED)

**Status**: ✅ Working
**Purpose**: Comprehensive test of search_messages bug fix.

```bash
python probes/test_search_comprehensive.py [account_name]
```

This probe verifies:
- Search with limit but no filters (previously broken)
- Search with filters and limit
- Search with filters only
- Correct limit application

**Test Results**: All tests pass ✅

---

### Other Search Probes

- `test_search_fix.py` - Basic search fix verification
- `test_search_no_limit.py` - Tests search without limit
- `debug_search.py` - Displays generated AppleScript for debugging

## Known Issues

### ✅ FIXED: search_messages() bug

**Status**: ✅ Fixed in commit a1002c9

The function previously generated invalid AppleScript ("whose true") when no filters were provided and had issues with the "items 1 thru N" syntax. This has been fixed by:
1. Omitting the "whose" clause when no conditions exist
2. Applying limits in Python instead of AppleScript

### ⚠️ OPEN: Message ID format mismatch

**Status**: ⚠️ Open issue

Direct AppleScript message IDs don't match the format expected by `get_attachments()`. This doesn't affect normal usage through the MCP server but causes issues when testing with direct AppleScript message ID retrieval.

**Workaround**: Use the search_messages() function to get properly formatted message IDs.
