#!/usr/bin/env python3
"""
Final text extraction test - bypasses search_messages bug.

Usage:
    python probes/final_extraction_test.py [account_name]
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector


def run_applescript(script: str) -> str:
    """Run an AppleScript and return the result."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise Exception(f"AppleScript error: {result.stderr}")
    return result.stdout.strip()


def final_test(account: str = "iCloud") -> None:
    """Final test of text extraction."""
    print(f"🔍 Final Text Extraction Test")
    print(f"   Account: {account}")
    print("=" * 80)

    # Step 1: Find a message with attachments using direct AppleScript
    print(f"\n📧 Step 1: Finding a message with attachments...")

    script = f"""
    tell application "Mail"
        set theAccount to account "{account}"
        set theMailbox to mailbox "INBOX" of theAccount
        set allMessages to messages of theMailbox

        repeat with theMessage in allMessages
            set attachmentCount to count of mail attachments of theMessage
            if attachmentCount > 0 then
                set msgId to id of theMessage as string
                set msgSubject to subject of theMessage
                set attList to ""
                repeat with att in mail attachments of theMessage
                    set attList to attList & name of att & ";"
                end repeat
                return msgId & "|" & msgSubject & "|" & attachmentCount & "|" & attList
            end if
        end repeat
        return "NONE"
    end tell
    """

    try:
        result = run_applescript(script)

        if result == "NONE":
            print("   ℹ️  No messages with attachments found")
            print(f"\n💡 Send an email to {account} with a .txt, .pdf, or .docx file attached")
            return

        # Parse result
        parts = result.split("|")
        message_id = parts[0]
        subject = parts[1] if len(parts) > 1 else "Unknown"
        att_count = parts[2] if len(parts) > 2 else "?"
        att_names = parts[3].split(";") if len(parts) > 3 else []

        print(f"   ✅ Found message with {att_count} attachment(s)")
        print(f"      Subject: {subject[:60]}")
        print(f"      Message ID: {message_id}")
        print(f"      Attachments: {', '.join([n for n in att_names if n])}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Step 2: Use the connector to extract text
    print(f"\n📄 Step 2: Extracting text using AppleMailConnector...")

    mail = AppleMailConnector()

    try:
        # First, get attachment details
        print(f"   Getting attachment details...")
        attachments = mail.get_attachments(message_id)
        print(f"   ✅ Found {len(attachments)} attachment(s):")
        for i, att in enumerate(attachments):
            print(f"      [{i}] {att['name']} ({att['size']:,} bytes)")

        # Extract text from first attachment
        print(f"\n   Extracting text from: {attachments[0]['name']}...")
        text = mail.extract_attachment_text(message_id, 0)

        print(f"\n   ✅ ✅ ✅ TEXT EXTRACTION SUCCESSFUL! ✅ ✅ ✅")
        print(f"\n   📊 Results:")
        print(f"      File: {attachments[0]['name']}")
        print(f"      Characters: {len(text):,}")
        print(f"      Lines: {text.count(chr(10)) + 1:,}")
        print(f"      Words (approx): {len(text.split()):,}")

        print(f"\n   📝 Text Content Preview:")
        print("   " + "=" * 76)

        # Show first 600 characters with proper indentation
        preview_lines = text[:600].split("\n")
        for line in preview_lines[:20]:  # Max 20 lines
            print(f"   {line[:74]}")  # Wrap long lines

        if len(text) > 600:
            print(f"\n   ... (showing first 600 of {len(text):,} total characters)")

        print("   " + "=" * 76)

        # Test other attachments if available
        if len(attachments) > 1:
            print(f"\n   Testing additional attachments...")
            for i in range(1, min(len(attachments), 3)):
                att = attachments[i]
                try:
                    text2 = mail.extract_attachment_text(message_id, i)
                    print(f"   ✅ [{i}] {att['name']}: {len(text2):,} characters extracted")
                except Exception as e:
                    print(f"   ⚠️  [{i}] {att['name']}: {str(e)[:60]}")

    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        import traceback
        print(f"\n   Traceback:")
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Test completed!")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    final_test(account)
