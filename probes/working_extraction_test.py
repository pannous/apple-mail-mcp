#!/usr/bin/env python3
"""
Working text extraction test - gets message reference directly.

Usage:
    python probes/working_extraction_test.py [account_name]
"""

import sys
import subprocess
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apple_mail_mcp.mail_connector import extract_text_from_file


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


def working_test(account: str = "iCloud") -> None:
    """Working test that saves attachment and extracts text."""
    print(f"🔍 Working Text Extraction Test")
    print(f"   Account: {account}")
    print("=" * 80)

    # Step 1: Find message and save attachment directly
    print(f"\n📧 Step 1: Finding message with attachment and saving it...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        script = f"""
        tell application "Mail"
            set theAccount to account "{account}"
            set theMailbox to mailbox "INBOX" of theAccount
            set allMessages to messages of theMailbox

            repeat with theMessage in allMessages
                set attachmentCount to count of mail attachments of theMessage
                if attachmentCount > 0 then
                    set msgSubject to subject of theMessage
                    set firstAtt to first mail attachment of theMessage
                    set attName to name of firstAtt

                    -- Save the attachment
                    try
                        save firstAtt in POSIX file "{temp_path}"
                        return "SUCCESS|" & msgSubject & "|" & attName
                    on error errMsg
                        return "ERROR|" & errMsg
                    end try
                end if
            end repeat
            return "NONE"
        end tell
        """

        try:
            result = run_applescript(script)

            if result == "NONE":
                print("   ℹ️  No messages with attachments found")
                print(f"\n💡 Send an email to {account} with a .txt, .pdf, or .docx file")
                return

            if result.startswith("ERROR"):
                print(f"   ❌ Error saving attachment: {result}")
                return

            # Parse result
            parts = result.split("|")
            status = parts[0]
            subject = parts[1] if len(parts) > 1 else "Unknown"
            att_name = parts[2] if len(parts) > 2 else "unknown"

            print(f"   ✅ Found and saved attachment")
            print(f"      Email: {subject[:60]}")
            print(f"      Attachment: {att_name}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return

        # Step 2: Find the saved file
        print(f"\n📄 Step 2: Locating saved file...")
        saved_files = list(temp_path.glob("*"))

        if not saved_files:
            print(f"   ❌ No files found in {temp_path}")
            return

        saved_file = saved_files[0]
        print(f"   ✅ Found file: {saved_file.name}")
        print(f"      Size: {saved_file.stat().st_size:,} bytes")

        # Step 3: Extract text
        print(f"\n📝 Step 3: Extracting text from file...")

        try:
            text = extract_text_from_file(saved_file)

            print(f"\n   ✅ ✅ ✅ TEXT EXTRACTION SUCCESSFUL! ✅ ✅ ✅")
            print(f"\n   📊 Extraction Results:")
            print(f"      File: {saved_file.name}")
            print(f"      Format: {saved_file.suffix}")
            print(f"      Size: {saved_file.stat().st_size:,} bytes")
            print(f"      Characters extracted: {len(text):,}")
            print(f"      Lines: {text.count(chr(10)) + 1:,}")
            print(f"      Words (approx): {len(text.split()):,}")

            print(f"\n   📝 Text Content Preview:")
            print("   " + "=" * 76)

            # Show first 600 characters
            preview = text[:600]
            for line in preview.split("\n")[:25]:  # Max 25 lines
                print(f"   {line[:74]}")

            if len(text) > 600:
                print(f"\n   ... (showing 600 of {len(text):,} total characters)")

            print("   " + "=" * 76)

        except NotImplementedError as e:
            print(f"   ⚠️  Format not supported: {e}")
            print(f"      File format '{saved_file.suffix}' cannot be extracted")
        except Exception as e:
            print(f"   ❌ Extraction error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Test completed!")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    working_test(account)
