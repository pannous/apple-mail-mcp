#!/usr/bin/env python3
"""
Direct test of attachment text extraction using AppleScript.

Usage:
    python probes/direct_attachment_test.py [account_name]
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


def test_direct_extraction(account: str = "iCloud") -> None:
    """Test extraction directly."""
    print(f"🔍 Direct attachment text extraction test")
    print(f"   Account: {account}")
    print("=" * 80)

    # Step 1: Find a message with attachments
    print(f"\n📧 Step 1: Finding messages with attachments...")

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
                set msgSender to sender of theMessage
                set firstAttachmentName to name of first mail attachment of theMessage
                return msgId & "|" & msgSubject & "|" & msgSender & "|" & attachmentCount & "|" & firstAttachmentName
            end if
        end repeat
        return "NO_ATTACHMENTS_FOUND"
    end tell
    """

    try:
        result = run_applescript(script)

        if result == "NO_ATTACHMENTS_FOUND":
            print("   ℹ️  No messages with attachments found in INBOX")
            print("\n💡 Tip: Send yourself an email with a .txt, .pdf, or .docx attachment")
            return

        # Parse result
        parts = result.split("|")
        message_id = parts[0]
        subject = parts[1]
        sender = parts[2]
        att_count = parts[3]
        att_name = parts[4] if len(parts) > 4 else "unknown"

        print(f"   ✅ Found message with {att_count} attachment(s)")
        print(f"      Subject: {subject}")
        print(f"      From: {sender}")
        print(f"      First attachment: {att_name}")
        print(f"      Message ID: {message_id}")

        # Step 2: Get attachments info
        print(f"\n📎 Step 2: Getting attachment details...")
        mail = AppleMailConnector()
        try:
            attachments = mail.get_attachments(message_id)
            print(f"   Found {len(attachments)} attachment(s):")
            for i, att in enumerate(attachments):
                print(f"      [{i}] {att['name']} ({att['size']:,} bytes)")
        except Exception as e:
            print(f"   ⚠️  Could not get attachment details: {e}")
            attachments = [{"name": att_name}]

        # Step 3: Extract text
        print(f"\n📄 Step 3: Extracting text from attachment...")
        print(f"   Attempting to extract from: {attachments[0]['name']}")

        try:
            text = mail.extract_attachment_text(message_id, 0)
            print(f"   ✅ SUCCESS! Extracted {len(text)} characters")
            print(f"\n   📝 Text preview (first 400 chars):")
            print("   " + "=" * 76)
            preview = text[:400].replace("\n", "\n   ")
            print(f"   {preview}")
            if len(text) > 400:
                print(f"\n   ... (showing 400 of {len(text):,} total characters)")
            print("   " + "=" * 76)

            # Show some statistics
            print(f"\n   📊 Text statistics:")
            print(f"      Total characters: {len(text):,}")
            print(f"      Total lines: {text.count(chr(10)) + 1:,}")
            words = len(text.split())
            print(f"      Approximate words: {words:,}")

        except Exception as e:
            print(f"   ❌ Error extracting text: {e}")
            print(f"\n   Note: The file format '{att_name.split('.')[-1] if '.' in att_name else 'unknown'}' may not be supported")
            print(f"   Supported formats: .txt, .pdf, .docx, .py, .md, .json, .csv, etc.")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 80)
    print("✅ Test completed!")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    test_direct_extraction(account)
