#!/usr/bin/env python3
"""
Session Start Hook for Claude Code.
Dynamically injects current date information at session startup.
"""
import sys
from datetime import datetime


def main():
    """Session start hook - runs once per session."""
    try:
        # Get current date information
        now = datetime.now()
        full_date = now.strftime('%B %d, %Y')        # "July 30, 2025"
        day_of_week = now.strftime('%A')             # "Wednesday"
        
        # Output as system reminder that gets injected into context
        print("<system-reminder>", file=sys.stderr)
        print(f"Today's date is {full_date} ({day_of_week}). ", file=sys.stderr, end="")
        print("Use this current date for any date-related operations or timestamps.", file=sys.stderr)
        print("</system-reminder>", file=sys.stderr)
        
        # Don't block any operations
        sys.exit(0)
        
    except Exception as e:
        # Never block on hook errors, just log and continue
        print(f"Session start hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()