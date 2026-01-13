#!/usr/bin/env python3
"""Test search without limit first."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector


def test_no_limit(account: str = "iCloud") -> None:
    """Test search without limit."""
    print(f"🔍 Testing search WITHOUT limit")
    print("=" * 80)

    mail = AppleMailConnector()

    print(f"\n📧 Test: Search without any filters or limit")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
        )
        print(f"   ✅ SUCCESS! Found {len(messages)} messages")
        if messages:
            for i, msg in enumerate(messages[:5], 1):
                print(f"      {i}. {msg.get('subject', 'No subject')[:50]}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    test_no_limit(account)
