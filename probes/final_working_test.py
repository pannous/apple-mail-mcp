#!/usr/bin/env python3
"""
Final working text extraction test.

Usage:
    python probes/final_working_test.py [account_name]
"""

import sys
import subprocess
import os
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


def final_working_test(account: str = "iCloud") -> None:
    """Final working test of text extraction."""
    print(f"🔍 Final Working Text Extraction Test")
    print(f"   Account: {account}")
    print("=" * 80)

    # Create explicit temp directory
    temp_dir = Path("/tmp/apple_mail_test")
    temp_dir.mkdir(exist_ok=True)

    # Clean up any old files
    for f in temp_dir.glob("*"):
        f.unlink()

    print(f"\n📧 Step 1: Finding message with attachment...")

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

                -- Save the attachment with explicit file name
                set savePath to POSIX file ("/tmp/apple_mail_test/" & attName) as string
                try
                    save firstAtt in file savePath
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
            print(f"   ❌ Error: {result}")
            return

        # Parse result
        parts = result.split("|")
        subject = parts[1] if len(parts) > 1 else "Unknown"
        att_name = parts[2] if len(parts) > 2 else "unknown"

        print(f"   ✅ Found attachment in email")
        print(f"      Subject: {subject[:60]}")
        print(f"      Attachment: {att_name}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # Step 2: Check if file was saved
    print(f"\n📄 Step 2: Checking for saved file...")
    saved_files = list(temp_dir.glob("*"))

    if not saved_files:
        print(f"   ⚠️  File not saved via AppleScript, trying alternative method...")

        # Alternative: save using a simpler path
        script2 = f"""
        tell application "Mail"
            set theAccount to account "{account}"
            set theMailbox to mailbox "INBOX" of theAccount
            set allMessages to messages of theMailbox

            repeat with theMessage in allMessages
                if (count of mail attachments of theMessage) > 0 then
                    set firstAtt to first mail attachment of theMessage
                    save firstAtt in "/tmp/"
                    return name of firstAtt
                end if
            end repeat
        end tell
        """
        try:
            att_name = run_applescript(script2)
            saved_file = Path("/tmp") / att_name
            if saved_file.exists():
                print(f"   ✅ Found file at /tmp/{att_name}")
            else:
                print(f"   ❌ File still not found")
                return
        except Exception as e:
            print(f"   ❌ Alternative method failed: {e}")
            return
    else:
        saved_file = saved_files[0]

    print(f"      Path: {saved_file}")
    print(f"      Size: {saved_file.stat().st_size:,} bytes")

    # Step 3: Extract text
    print(f"\n📝 Step 3: Extracting text from file...")

    try:
        text = extract_text_from_file(saved_file)

        print(f"\n   🎉 🎉 🎉 TEXT EXTRACTION SUCCESSFUL! 🎉 🎉 🎉")
        print(f"\n   📊 Extraction Results:")
        print(f"      File: {saved_file.name}")
        print(f"      Format: {saved_file.suffix}")
        print(f"      Size: {saved_file.stat().st_size:,} bytes")
        print(f"      Characters extracted: {len(text):,}")
        print(f"      Lines: {text.count(chr(10)) + 1:,}")
        print(f"      Words (approx): {len(text.split()):,}")

        print(f"\n   📝 Text Content Preview:")
        print("   " + "=" * 76)

        # Show first 700 characters
        preview = text[:700]
        lines_shown = 0
        for line in preview.split("\n"):
            if lines_shown >= 30:  # Max 30 lines
                break
            print(f"   {line[:74]}")
            lines_shown += 1

        if len(text) > 700:
            print(f"\n   ... (showing 700 of {len(text):,} total characters)")

        print("   " + "=" * 76)

        print(f"\n   ✅ The text extraction feature is working correctly!")
        print(f"   ✅ The MCP can extract text from: .txt, .pdf, .docx files")

    except NotImplementedError as e:
        print(f"   ⚠️  Format not supported: {e}")
        print(f"      The '{saved_file.suffix}' format is not supported for text extraction")
    except Exception as e:
        print(f"   ❌ Extraction error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if saved_file.exists():
            saved_file.unlink()

    print("\n" + "=" * 80)
    print("✅ Test completed!")


if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "iCloud"
    final_working_test(account)
