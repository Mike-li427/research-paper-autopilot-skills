#!/usr/bin/env python3
"""Generate a Markdown quality report for a Beamer deck directory."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

try:
    from check_latex_log import scan_log
except ImportError:  # pragma: no cover
    scan_log = None  # type: ignore


def status(value: bool) -> str:
    return "ok" if value else "missing"


def load_json(path: str) -> dict[str, Any] | None:
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else None


def build_report(deck_dir: str, figures_json: str | None = None) -> str:
    main_tex = os.path.join(deck_dir, "main.tex")
    notes_md = os.path.join(deck_dir, "notes.md")
    makefile = os.path.join(deck_dir, "Makefile")
    main_pdf = os.path.join(deck_dir, "main.pdf")
    main_log = os.path.join(deck_dir, "main.log")
    preview_dir = os.path.join(deck_dir, "_preview")

    lines = [
        "# Quality Report",
        "",
        f"- Deck directory: `{deck_dir}`",
        f"- `main.tex`: {status(os.path.exists(main_tex))}",
        f"- `notes.md`: {status(os.path.exists(notes_md))}",
        f"- `Makefile`: {status(os.path.exists(makefile))}",
        f"- `main.pdf`: {status(os.path.exists(main_pdf))}",
        "",
        "## Compilation",
        "",
    ]

    if os.path.exists(main_log) and scan_log is not None:
        report = scan_log(main_log)
        lines.append(f"- Log gate: {'ok' if report.total == 0 else 'failed'}")
        lines.append(f"- Problems found: {report.total}")
        for category, hits in report.hits.items():
            lines.append(f"  - {category}: {len(hits)}")
    else:
        lines.append("- Log gate: not checked (`main.log` missing)")

    lines.extend(["", "## Visual QA", ""])
    if os.path.isdir(preview_dir):
        rendered = [name for name in os.listdir(preview_dir) if name.lower().endswith(".png")]
        lines.append(f"- Rendered preview pages: {len(rendered)}")
    else:
        lines.append("- Rendered preview pages: missing")
    lines.append("- Final visual inspection: record manually in `notes.md` / `slides/README.md`")

    lines.extend(["", "## Figure Extraction", ""])
    manifest = load_json(figures_json) if figures_json else None
    if manifest:
        figures = manifest.get("figures", [])
        ok = sum(1 for item in figures if isinstance(item, dict) and item.get("status") == "ok")
        review = sum(1 for item in figures if isinstance(item, dict) and item.get("status") == "needs_manual_review")
        lines.append(f"- Manifest: `{figures_json}`")
        lines.append(f"- Extractor: {manifest.get('extractor', {}).get('primary', 'unknown')}")
        lines.append(f"- Figures ok: {ok}")
        lines.append(f"- Needs manual review: {review}")
        filtered = manifest.get("filtered", [])
        lines.append(f"- Filtered detections: {len(filtered) if isinstance(filtered, list) else 0}")
    else:
        lines.append("- Manifest: not provided")

    lines.extend(["", "## Open Risks", ""])
    risks = []
    if not os.path.exists(main_pdf):
        risks.append("Deck PDF has not been built.")
    if not os.path.isdir(preview_dir):
        risks.append("Rendered visual QA pages are missing.")
    if manifest:
        review = [item for item in manifest.get("figures", []) if isinstance(item, dict) and item.get("status") == "needs_manual_review"]
        if review:
            risks.append(f"{len(review)} extracted figure record(s) still need manual review.")
    if risks:
        lines.extend(f"- {risk}" for risk in risks)
    else:
        lines.append("- No obvious script-detected risks.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a deck quality report.")
    parser.add_argument("deck_dir", help="deck directory, e.g. slides/foo")
    parser.add_argument("--figures-json", default=None, help="optional figure extraction manifest")
    parser.add_argument("--out", default=None, help="output path (default: <deck_dir>/quality_report.md)")
    args = parser.parse_args(argv[1:])

    if not os.path.isdir(args.deck_dir):
        print(f"ERROR: deck directory not found: {args.deck_dir}", file=sys.stderr)
        return 2
    out = args.out or os.path.join(args.deck_dir, "quality_report.md")
    report = build_report(args.deck_dir, args.figures_json)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
