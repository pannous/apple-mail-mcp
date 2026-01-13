#!/usr/bin/env python3
"""
Probe to test text extraction from email attachments with a real email.

Usage:
    python probes/test_text_extraction.py [account_name]
"""

import sys
from pathlib import Path

# Add src to path so we can import apple_mail_mcp
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector
from apple_mail_mcp.exceptions import MailError


def test_text_extraction(account: str = "Gmail") -> None:
    """Test text extraction from a real email attachment."""
    print(f"🔍 Testing text extraction with account: {account}")
    print("=" * 80)

    mail = AppleMailConnector()

    # Step 1: Search for recent emails
    print("\n📧 Step 1: Searching for recent emails...")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
            limit=50,
        )
        print(f"   Found {len(messages)} messages")
    except MailError as e:
        print(f"   ❌ Error searching messages: {e}")
        return

    # Step 2: Find messages with attachments
    print("\n📎 Step 2: Finding messages with attachments...")
    messages_with_attachments = []
    for msg in messages:
        try:
            attachments = mail.get_attachments(msg["id"])
            if attachments:
                messages_with_attachments.append((msg, attachments))
                print(
                    f"   ✓ Message '{msg['subject'][:50]}...' has {len(attachments)} attachment(s)"
                )
        except MailError as e:
            print(f"   ⚠️  Error checking message {msg['id']}: {e}")
            continue

    if not messages_with_attachments:
        print("   ℹ️  No messages with attachments found in recent emails")
        print("\n💡 Tip: Send yourself an email with a .txt, .pdf, or .docx attachment")
        return

    # Step 3: Test text extraction on the first attachment
    print("\n📄 Step 3: Testing text extraction...")
    msg, attachments = messages_with_attachments[0]
    attachment = attachments[0]

    print(f"\n   Selected email:")
    print(f"     Subject: {msg['subject']}")
    print(f"     From: {msg.get('sender', 'Unknown')}")
    print(f"     Date: {msg.get('date_received', 'Unknown')}")
    print(f"\n   Selected attachment:")
    print(f"     Name: {attachment['name']}")
    print(f"     Size: {attachment['size']:,} bytes")
    print(f"     Type: {attachment.get('mime_type', 'unknown')}")

    # Try to extract text
    print(f"\n   Extracting text from '{attachment['name']}'...")
    try:
        text = mail.extract_attachment_text(
            message_id=msg["id"],
            attachment_index=0,
        )

        print(f"   ✅ Text extraction successful!")
        print(f"\n   Extracted text ({len(text)} characters):")
        print("   " + "-" * 76)
        # Show first 500 characters
        preview = text[:500]
        if len(text) > 500:
            preview += f"\n\n   ... (showing first 500 of {len(text)} total characters)"
        print(f"   {preview}")
        print("   " + "-" * 76)

    except MailError as e:
        print(f"   ❌ Error extracting text: {e}")
        print(f"   Note: This attachment type might not support text extraction")

    # Step 4: Try extracting from other attachments if available
    if len(attachments) > 1:
        print(f"\n📋 Step 4: Testing other attachments ({len(attachments) - 1} more)...")
        for idx in range(1, min(len(attachments), 4)):  # Test up to 3 more
            attachment = attachments[idx]
            print(f"\n   Attachment {idx + 1}: {attachment['name']}")
            try:
                text = mail.extract_attachment_text(
                    message_id=msg["id"],
                    attachment_index=idx,
                )
                print(
                    f"   ✅ Extracted {len(text)} characters from '{attachment['name']}'"
                )
            except MailError as e:
                print(f"   ⚠️  Could not extract from '{attachment['name']}': {e}")

    print("\n" + "=" * 80)
    print("✅ Text extraction probe completed!")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "Gmail"
    test_text_extraction(account)
