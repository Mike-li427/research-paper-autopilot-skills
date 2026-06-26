#!/usr/bin/env python3
"""Check lightweight source-traceability and figure-attribution expectations."""

from __future__ import annotations

import argparse
import os
import re
import sys


PLACEHOLDER_RE = re.compile(r"<[^>]+>|\|\s*\|\s*\|\s*\|")


def check_deck(deck_dir: str) -> list[str]:
    notes = os.path.join(deck_dir, "notes.md")
    main = os.path.join(deck_dir, "main.tex")
    issues: list[str] = []
    if not os.path.exists(notes):
        return ["notes.md is missing"]
    with open(notes, "r", encoding="utf-8", errors="replace") as fh:
        notes_text = fh.read()
    if "## Source Traceability" not in notes_text:
        issues.append("notes.md is missing `## Source Traceability`")
    else:
        section = notes_text.split("## Source Traceability", 1)[1]
        section = section.split("\n## ", 1)[0]
        filled_rows = [
            line for line in section.splitlines()
            if line.startswith("|") and "---" not in line and not PLACEHOLDER_RE.search(line)
        ]
        if not filled_rows:
            issues.append("Source Traceability table appears empty or placeholder-only")
    if os.path.exists(main):
        with open(main, "r", encoding="utf-8", errors="replace") as fh:
            main_text = fh.read()
        include_count = len(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{", main_text))
        if include_count and ("From the paper" not in main_text and "Adapted from the paper" not in main_text and "From the paper" not in notes_text and "Adapted from the paper" not in notes_text):
            issues.append("deck uses includegraphics but no paper-figure attribution phrase was found")
    return issues


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check deck source traceability and figure attribution.")
    parser.add_argument("deck_dir")
    args = parser.parse_args(argv[1:])
    if not os.path.isdir(args.deck_dir):
        print(f"ERROR: deck directory not found: {args.deck_dir}", file=sys.stderr)
        return 2
    issues = check_deck(args.deck_dir)
    if issues:
        print("Deck source checks failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("Deck source checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
