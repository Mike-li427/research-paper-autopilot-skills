#!/usr/bin/env python3
"""Check that a built deck has rendered pages for visual QA."""

from __future__ import annotations

import argparse
import os
import re
import sys


def expected_pdf_pages(log_path: str) -> int | None:
    if not os.path.exists(log_path):
        return None
    with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    match = re.search(r"Output written on .*?\((\d+) pages?\)", text)
    return int(match.group(1)) if match else None


def check_visual_qa(deck_dir: str, preview_dir: str | None = None) -> list[str]:
    preview = preview_dir or os.path.join(deck_dir, "_preview")
    issues: list[str] = []
    if not os.path.exists(os.path.join(deck_dir, "main.pdf")):
        issues.append("main.pdf is missing")
    if not os.path.isdir(preview):
        issues.append(f"preview directory is missing: {preview}")
        return issues
    rendered = [name for name in os.listdir(preview) if name.lower().endswith(".png")]
    if not rendered:
        issues.append("preview directory contains no PNG pages")
    expected = expected_pdf_pages(os.path.join(deck_dir, "main.log"))
    if expected is not None and len(rendered) < expected:
        issues.append(f"only {len(rendered)} rendered page(s), but log reports {expected}")
    return issues


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check rendered-page visual QA coverage.")
    parser.add_argument("deck_dir")
    parser.add_argument("--preview-dir", default=None)
    args = parser.parse_args(argv[1:])
    if not os.path.isdir(args.deck_dir):
        print(f"ERROR: deck directory not found: {args.deck_dir}", file=sys.stderr)
        return 2
    issues = check_visual_qa(args.deck_dir, args.preview_dir)
    if issues:
        print("Visual QA checks failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("Visual QA checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
