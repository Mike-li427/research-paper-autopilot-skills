#!/usr/bin/env python3
"""Check a paper-reading workspace for common setup problems."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys


def check_workspace(root: str) -> tuple[list[str], list[str]]:
    ok: list[str] = []
    issues: list[str] = []
    for rel in ("papers", "slides", "analysis", "skills"):
        path = os.path.join(root, rel)
        (ok if os.path.exists(path) else issues).append(f"{rel}/ {'found' if os.path.exists(path) else 'missing'}")
    for rel in ("theme.tex", "beamerthemeSimple.sty"):
        path = os.path.join(root, rel)
        (ok if os.path.exists(path) else issues).append(f"{rel} {'found' if os.path.exists(path) else 'missing'}")
    for tool in ("xelatex",):
        path = shutil.which(tool)
        (ok if path else issues).append(f"{tool}: {path or 'not found'}")
    for tool in ("pdftoppm", "pdftocairo"):
        path = shutil.which(tool)
        if path:
            ok.append(f"{tool}: {path}")
    if not any(item.startswith("pdftoppm:") or item.startswith("pdftocairo:") for item in ok):
        issues.append("poppler renderer not found (`pdftoppm`/`pdftocairo`)")
    for module in ("fitz", "docling"):
        spec = importlib.util.find_spec(module)
        (ok if spec else issues).append(f"python module {module}: {'found' if spec else 'not found'}")
    return ok, issues


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Diagnose a paper-reading workspace setup.")
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args(argv[1:])
    root = os.path.abspath(args.workspace)
    ok, issues = check_workspace(root)
    print(f"Workspace: {root}\n")
    print("OK:")
    for item in ok:
        print(f"  - {item}")
    print("\nIssues:")
    if issues:
        for item in issues:
            print(f"  - {item}")
        return 1
    print("  - none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
