#!/usr/bin/env python3
"""Fail-on-warning gate for XeLaTeX/LaTeX `.log` files.

Scans a LaTeX log and exits non-zero if it finds any of the problems that make a
Beamer deck unacceptable for presentation:

  * LaTeX errors            (lines beginning with "! ", or "LaTeX Error:")
  * package errors          ("Package <name> Error:")
  * missing files           ("File `...' not found", "! ... No such file ...",
                             "LaTeX Warning: File `...' not found")
  * overfull \\hbox          ("Overfull \\hbox ...")
  * overfull \\vbox          ("Overfull \\vbox ...")
  * undefined references    ("Reference `...' ... undefined",
                             "There were undefined references")
  * undefined citations      ("Citation `...' ... undefined")

Usage:
    python3 check_latex_log.py [main.log ...]

If no path is given, defaults to "main.log" in the current directory.

Exit codes:
    0  log is clean (no matched problems)
    1  one or more problems found
    2  usage / file-not-found error

This script is pure standard library and has no third-party dependencies.

Note: a clean log is necessary but NOT sufficient. Many visual problems (clipped
TikZ, unreadable fonts, awkward spacing) produce no warning at all. Also inspect
the PDF visually as required by your chosen build mode -- at minimum a final
full-deck pass is mandatory in every mode. See render_pdf_pages.py and SKILL.md
("Visual QA mode" + section 10).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field

# Each category maps to a list of compiled regexes. A log line matching any regex
# in a category is recorded under that category. Order here controls report order.
CATEGORIES: "list[tuple[str, list[re.Pattern[str]]]]" = [
    (
        "LaTeX errors",
        [
            re.compile(r"^! "),
            re.compile(r"LaTeX Error:"),
            re.compile(r"^! LaTeX Error:"),
        ],
    ),
    (
        "Package errors",
        [
            re.compile(r"Package\s+\S+\s+Error:"),
        ],
    ),
    (
        "Missing files",
        [
            re.compile(r"File\s+[`'\"].*?[`'\"]\s+not found"),
            re.compile(r"No such file or directory"),
            re.compile(r"!\s+I can't find file"),
            re.compile(r"!\s+LaTeX Error: File\s+[`'\"].*?[`'\"]\s+not found"),
        ],
    ),
    (
        "Overfull hbox",
        [
            re.compile(r"Overfull\s+\\hbox"),
        ],
    ),
    (
        "Overfull vbox",
        [
            re.compile(r"Overfull\s+\\vbox"),
        ],
    ),
    (
        "Undefined references",
        [
            re.compile(r"Reference\s+[`'\"].*?[`'\"]\s+on page .* undefined"),
            re.compile(r"Reference\s+[`'\"].*?[`'\"]\s+undefined"),
            re.compile(r"There were undefined references"),
            re.compile(r"LaTeX Warning:.*undefined references"),
        ],
    ),
    (
        "Undefined citations",
        [
            re.compile(r"Citation\s+[`'\"].*?[`'\"]\s+.*undefined"),
        ],
    ),
]


@dataclass
class Hit:
    line_no: int
    text: str


@dataclass
class Report:
    path: str
    hits: "dict[str, list[Hit]]" = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(len(v) for v in self.hits.values())


def scan_log(path: str) -> Report:
    report = Report(path=path)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        raise
    except OSError as exc:  # pragma: no cover - defensive
        raise OSError(f"could not read {path}: {exc}") from exc

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        for category, patterns in CATEGORIES:
            if any(p.search(line) for p in patterns):
                report.hits.setdefault(category, []).append(Hit(idx, line.strip()))
                # one category per line is enough; stop at the first match
                break
    return report


def print_report(report: Report) -> None:
    if report.total == 0:
        print(f"OK: {report.path} is clean (no LaTeX errors or layout warnings).")
        return

    print(f"FAIL: {report.path} -- {report.total} problem(s) found.\n")
    for category, _patterns in CATEGORIES:
        hits = report.hits.get(category)
        if not hits:
            continue
        print(f"== {category} ({len(hits)}) ==")
        for hit in hits:
            print(f"  line {hit.line_no}: {hit.text}")
        print()


def main(argv: "list[str]") -> int:
    paths = argv[1:] or ["main.log"]
    any_problem = False
    exit_usage_error = False

    for path in paths:
        try:
            report = scan_log(path)
        except FileNotFoundError:
            print(f"ERROR: log file not found: {path}", file=sys.stderr)
            exit_usage_error = True
            continue
        except OSError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            exit_usage_error = True
            continue
        print_report(report)
        if report.total > 0:
            any_problem = True

    if exit_usage_error:
        return 2
    if any_problem:
        print(
            "Fix these before accepting the deck. Prefer splitting/redesigning "
            "slides over shrinking fonts. A clean log is necessary but not "
            "sufficient -- also inspect the PDF visually.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
