#!/usr/bin/env python3
"""Debug script to see the AppleScript being generated."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import AppleMailConnector
from unittest.mock import patch


def debug_search() -> None:
    """Show the AppleScript that gets generated."""

    mail = AppleMailConnector()

    # Capture the AppleScript
    original_run = mail._run_applescript

    def capture_script(script: str) -> str:
        print("Generated AppleScript:")
        print("=" * 80)
        print(script)
        print("=" * 80)
        raise Exception("Captured script, stopping execution")

    mail._run_applescript = capture_script

    print("Test 1: No filters, with limit")
    try:
        mail.search_messages("iCloud", "INBOX", limit=10)
    except:
        pass

    print("\n\nTest 2: No filters, no limit")
    try:
        mail.search_messages("iCloud", "INBOX")
    except:
        pass

    print("\n\nTest 3: With filter, with limit")
    try:
        mail.search_messages("iCloud", "INBOX", read_status=False, limit=10)
    except:
        pass


if __name__ == "__main__":
    debug_search()
