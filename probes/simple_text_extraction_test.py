#!/usr/bin/env python3
"""
Simple probe to test text extraction - gets latest messages directly.

Usage:
    python probes/simple_text_extraction_test.py [account_name]
"""

import sys
from pathlib import Path

# Add src to path so we can import apple_mail_mcp
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector
from apple_mail_mcp.exceptions import MailError


def test_simple_extraction(account: str = "iCloud") -> None:
    """Test text extraction with a simplified approach."""
    print(f"🔍 Testing text extraction with account: {account}")
    print("=" * 80)

    mail = AppleMailConnector()

    # Step 1: Get messages directly using AppleScript
    print(f"\n📧 Step 1: Getting recent messages from {account}...")

    # Use AppleScript to get the first 10 messages
    script = f"""
    tell application "Mail"
        set theAccount to account "{account}"
        set theMessages to messages of inbox of theAccount
        set messageList to {{}}
        repeat with theMessage in items 1 thru (count of theMessages) of theMessages
            set messageId to id of theMessage as string
            set messageSubject to subject of theMessage
            set attachmentCount to count of mail attachments of theMessage
            if attachmentCount > 0 then
                set end of messageList to {{messageId:messageId, subject:messageSubject, attachments:attachmentCount}}
            end if
            if (count of messageList) ≥ 3 then exit repeat
        end repeat
        return messageList
    end tell
    """

    try:
        result = mail._run_applescript(script)
        print(f"   Raw result: {result}")

        if not result or result == "":
            print("   ℹ️  No messages with attachments found")
            print("\n💡 Tip: Send yourself an email with a .txt, .pdf, or .docx attachment")
            return

        # Parse the result (it will be a string representation)
        # For now, just check if we got something
        print(f"   ✅ Found messages with attachments")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n🔧 Let's try a more direct approach...")

        # Try even simpler: just get one message ID manually
        script2 = f"""
        tell application "Mail"
            set theAccount to account "{account}"
            set theMessages to messages of inbox of theAccount
            repeat with theMessage in theMessages
                set attachmentCount to count of mail attachments of theMessage
                if attachmentCount > 0 then
                    return {{id of theMessage as string, subject of theMessage, attachmentCount}}
                end if
            end repeat
            return "no messages"
        end tell
        """
        try:
            result2 = mail._run_applescript(script2)
            print(f"   Result: {result2}")

            if "no messages" in str(result2):
                print("\n   ℹ️  No messages with attachments found in inbox")
                return

            # Extract message ID (first element)
            parts = str(result2).split(",")
            message_id = parts[0].strip()
            print(f"\n   Message ID: {message_id}")

            # Step 2: Get attachments for this message
            print(f"\n📎 Step 2: Getting attachments...")
            attachments = mail.get_attachments(message_id)
            print(f"   Found {len(attachments)} attachment(s):")
            for i, att in enumerate(attachments):
                print(f"     {i}: {att['name']} ({att['size']:,} bytes)")

            # Step 3: Try to extract text from first attachment
            if attachments:
                print(f"\n📄 Step 3: Extracting text from '{attachments[0]['name']}'...")
                try:
                    text = mail.extract_attachment_text(message_id, 0)
                    print(f"   ✅ Success! Extracted {len(text)} characters")
                    print(f"\n   Preview (first 300 chars):")
                    print("   " + "-" * 76)
                    print(f"   {text[:300]}")
                    if len(text) > 300:
                        print(f"\n   ... ({len(text) - 300} more characters)")
                    print("   " + "-" * 76)
                except Exception as e:
                    print(f"   ❌ Error: {e}")

        except Exception as e2:
            print(f"   ❌ Error with direct approach: {e2}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    test_simple_extraction(account)
