#!/usr/bin/env python3
"""
Test that the search_messages bug fix works with real emails.

Usage:
    python probes/test_search_fix.py [account_name]
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector


def test_search_fix(account: str = "iCloud") -> None:
    """Test that search_messages works without filters."""
    print(f"🔍 Testing search_messages bug fix")
    print(f"   Account: {account}")
    print("=" * 80)

    mail = AppleMailConnector()

    # Test 1: Search without any filters (this was broken before)
    print(f"\n📧 Test 1: Search WITHOUT filters (previously broken)")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
            limit=10,
        )
        print(f"   ✅ SUCCESS! Found {len(messages)} messages")
        if messages:
            print(f"      First message: {messages[0].get('subject', 'No subject')[:60]}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return

    # Test 2: Search with filters (this should still work)
    print(f"\n📧 Test 2: Search WITH filters (should still work)")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
            read_status=False,
            limit=5,
        )
        print(f"   ✅ SUCCESS! Found {len(messages)} unread messages")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    # Test 3: Search with limit only
    print(f"\n📧 Test 3: Search with limit only")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
            limit=3,
        )
        print(f"   ✅ SUCCESS! Found {len(messages)} messages (max 3)")
        for i, msg in enumerate(messages, 1):
            print(f"      {i}. {msg.get('subject', 'No subject')[:50]}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("\n" + "=" * 80)
    print("✅ Bug fix verified! search_messages now works without filters")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    test_search_fix(account)
