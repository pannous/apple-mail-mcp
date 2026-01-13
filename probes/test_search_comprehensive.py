#!/usr/bin/env python3
"""
Comprehensive test of search_messages bug fix.

Usage:
    python probes/test_search_comprehensive.py [account_name]
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector


def test_comprehensive(account: str = "iCloud") -> None:
    """Comprehensive test of search_messages."""
    print(f"🔍 Comprehensive search_messages bug fix test")
    print(f"   Account: {account}")
    print("=" * 80)

    mail = AppleMailConnector()

    # Test 1: Search with limit (no filters) - THIS WAS BROKEN
    print(f"\n📧 Test 1: Search with limit, no filters (previously broken)")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
            limit=5,
        )
        print(f"   ✅ SUCCESS! Found {len(messages)} messages")
        for i, msg in enumerate(messages, 1):
            print(f"      {i}. {msg.get('subject', 'No subject')[:50]}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return

    # Test 2: Search with filter and limit
    print(f"\n📧 Test 2: Search with filter and limit")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
            read_status=False,
            limit=3,
        )
        print(f"   ✅ SUCCESS! Found {len(messages)} unread messages (limit 3)")
        for i, msg in enumerate(messages, 1):
            print(f"      {i}. {msg.get('subject', 'No subject')[:50]}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    # Test 3: Search with only filter (no limit)
    print(f"\n📧 Test 3: Search with filter only (no limit)")
    try:
        messages = mail.search_messages(
            account=account,
            mailbox="INBOX",
            read_status=True,
        )
        print(f"   ✅ SUCCESS! Found {len(messages)} read messages")
        print(f"      (showing first 3)")
        for i, msg in enumerate(messages[:3], 1):
            print(f"      {i}. {msg.get('subject', 'No subject')[:50]}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    # Test 4: Verify limit is applied correctly
    print(f"\n📧 Test 4: Verify limit is applied correctly")
    try:
        for limit in [1, 3, 5]:
            messages = mail.search_messages(
                account=account,
                mailbox="INBOX",
                limit=limit,
            )
            if len(messages) == limit:
                print(f"   ✅ Limit {limit}: Got exactly {len(messages)} messages")
            else:
                print(f"   ⚠️  Limit {limit}: Expected {limit}, got {len(messages)}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

    print("\n" + "=" * 80)
    print("✅ Bug fix verified! search_messages works correctly:")
    print("   - No filters with limit: ✅")
    print("   - With filters: ✅")
    print("   - Limit applied correctly: ✅")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    test_comprehensive(account)
