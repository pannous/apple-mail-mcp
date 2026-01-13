#!/usr/bin/env python3
"""
Test text extraction using the actual connector methods.

Usage:
    python probes/test_with_connector.py [account_name] [mailbox]
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector
from apple_mail_mcp.exceptions import MailError


def test_with_connector(account: str = "iCloud", mailbox: str = "INBOX") -> None:
    """Test extraction using connector's search methods."""
    print(f"🔍 Testing text extraction")
    print(f"   Account: {account}")
    print(f"   Mailbox: {mailbox}")
    print("=" * 80)

    mail = AppleMailConnector()

    # Step 1: Search for recent messages (without date filters that might cause issues)
    print(f"\n📧 Step 1: Searching for recent messages...")

    try:
        # Search without filters to avoid AppleScript comparison issues
        messages = mail.search_messages(
            account=account,
            mailbox=mailbox,
            limit=20,  # Get more messages to find one with attachments
        )
        print(f"   ✅ Found {len(messages)} messages")

    except Exception as e:
        print(f"   ❌ Error searching: {e}")
        print(f"\n   Let's try a different mailbox...")
        # Try a different mailbox
        for alt_mailbox in ["Sent Messages", "Sent Items", "Archive"]:
            try:
                print(f"   Trying {alt_mailbox}...")
                messages = mail.search_messages(
                    account=account,
                    mailbox=alt_mailbox,
                    limit=10,
                )
                print(f"   ✅ Found {len(messages)} messages in {alt_mailbox}")
                mailbox = alt_mailbox
                break
            except Exception as e2:
                print(f"   ⚠️  {alt_mailbox} failed: {e2}")
                continue
        else:
            print(f"\n   ❌ Could not access any mailboxes")
            return

    # Step 2: Find messages with attachments
    print(f"\n📎 Step 2: Finding messages with attachments...")
    msg_with_att = None
    for msg in messages:
        try:
            attachments = mail.get_attachments(msg["id"])
            if attachments:
                msg_with_att = (msg, attachments)
                print(f"   ✅ Found message with {len(attachments)} attachment(s)")
                print(f"      Subject: {msg.get('subject', 'No subject')[:60]}")
                print(f"      Message ID: {msg['id']}")
                break
        except Exception as e:
            # Skip messages with errors
            continue

    if not msg_with_att:
        print("   ℹ️  No messages with attachments found")
        print(f"\n💡 Tip: Send yourself an email to {account}/{mailbox} with a .txt, .pdf, or .docx attachment")
        return

    msg, attachments = msg_with_att

    # Show attachment details
    print(f"\n   Attachments in this message:")
    for i, att in enumerate(attachments):
        print(f"      [{i}] {att['name']} ({att['size']:,} bytes, {att.get('mime_type', 'unknown')})")

    # Step 3: Extract text from the first attachment
    print(f"\n📄 Step 3: Extracting text from attachment...")
    att = attachments[0]
    print(f"   Target: {att['name']}")

    try:
        text = mail.extract_attachment_text(msg["id"], 0)

        print(f"\n   ✅ SUCCESS! Text extraction completed")
        print(f"\n   📊 Extraction results:")
        print(f"      Attachment: {att['name']}")
        print(f"      Characters: {len(text):,}")
        print(f"      Lines: {text.count(chr(10)) + 1:,}")
        print(f"      Words (approx): {len(text.split()):,}")

        print(f"\n   📝 Text preview (first 500 chars):")
        print("   " + "=" * 76)
        preview = text[:500]
        # Indent each line
        for line in preview.split("\n"):
            print(f"   {line}")
        if len(text) > 500:
            print(f"\n   ... (showing 500 of {len(text):,} total characters)")
        print("   " + "=" * 76)

        # Step 4: Try other attachments if available
        if len(attachments) > 1:
            print(f"\n🔄 Step 4: Testing other attachments...")
            for i in range(1, min(len(attachments), 4)):
                att = attachments[i]
                print(f"\n   Attachment {i + 1}: {att['name']}")
                try:
                    text = mail.extract_attachment_text(msg["id"], i)
                    print(f"   ✅ Extracted {len(text):,} characters")
                except Exception as e:
                    print(f"   ⚠️  Could not extract: {e}")

    except NotImplementedError as e:
        print(f"   ⚠️  Unsupported format: {e}")
        print(f"   The format '{att['name'].split('.')[-1] if '.' in att['name'] else 'unknown'}' is not supported")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 80)
    print("✅ Test completed!")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    mailbox = sys.argv[2] if len(sys.argv) > 2 else "INBOX"
    test_with_connector(account, mailbox)
