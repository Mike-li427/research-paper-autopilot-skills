"""Regression tests for ``scripts/check_latex_log.py``.

Hermetic — no LaTeX toolchain required; the tests feed crafted ``.log`` text and
assert on the matched categories and process exit codes. Runs under both
``python3 -m unittest`` and ``python3 -m pytest``.
"""

from __future__ import annotations

import os
import tempfile
import unittest

from _import import load_script

clog = load_script("check_latex_log")


def _write_log(tmpdir: str, name: str, text: str) -> str:
    path = os.path.join(tmpdir, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


# One line per problem category, deliberately non-overlapping so each line lands
# in exactly one category. Two of them are "LaTeX errors", so 8 lines -> 7
# categories, 8 total hits.
DIRTY_LOG = "\n".join(
    [
        "This is a normal line that should never match.",
        "! Undefined control sequence.",
        "./main.tex:10: LaTeX Error: Something is badly wrong.",
        "Package hyperref Error: Option clash for package hyperref.",
        "File `missing-figure.png' not found.",
        "Overfull \\hbox (12.0pt too wide) in paragraph at lines 1--2.",
        "Overfull \\vbox (5.0pt too high) has occurred while \\output is active.",
        "LaTeX Warning: Reference `fig:x' on page 2 undefined on input line 5.",
        "LaTeX Warning: Citation `smith2020' on page 1 undefined on input line 3.",
        "",
    ]
)

CLEAN_LOG = "\n".join(
    [
        "This is XeTeX, Version 3.14159265",
        "(./main.tex (./main.aux))",
        "Output written on main.pdf (33 pages).",
        "Transcript written on main.log.",
        "",
    ]
)


class ScanLogTests(unittest.TestCase):
    def test_clean_log_has_no_hits(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = _write_log(d, "main.log", CLEAN_LOG)
            report = clog.scan_log(path)
        self.assertEqual(report.total, 0)
        self.assertEqual(report.hits, {})

    def test_dirty_log_detects_every_category(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = _write_log(d, "main.log", DIRTY_LOG)
            report = clog.scan_log(path)

        expected = {
            "LaTeX errors",
            "Package errors",
            "Missing files",
            "Overfull hbox",
            "Overfull vbox",
            "Undefined references",
            "Undefined citations",
        }
        self.assertEqual(set(report.hits), expected)
        # 8 problem lines (two of them are LaTeX errors), the rest are clean.
        self.assertEqual(report.total, 8)
        self.assertEqual(len(report.hits["LaTeX errors"]), 2)

    def test_one_category_per_line(self) -> None:
        # This single line matches both "LaTeX errors" (^! and "LaTeX Error:")
        # and "Missing files" ("File `...' not found"). The `break` must record
        # it under the FIRST category only.
        line = "! LaTeX Error: File `foo.sty' not found."
        with tempfile.TemporaryDirectory() as d:
            path = _write_log(d, "main.log", line + "\n")
            report = clog.scan_log(path)
        self.assertEqual(report.total, 1)
        self.assertIn("LaTeX errors", report.hits)
        self.assertNotIn("Missing files", report.hits)


class MainExitCodeTests(unittest.TestCase):
    def test_clean_log_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = _write_log(d, "main.log", CLEAN_LOG)
            self.assertEqual(clog.main(["check_latex_log.py", path]), 0)

    def test_dirty_log_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = _write_log(d, "main.log", DIRTY_LOG)
            self.assertEqual(clog.main(["check_latex_log.py", path]), 1)

    def test_missing_file_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "does-not-exist.log")
            self.assertEqual(clog.main(["check_latex_log.py", missing]), 2)

    def test_mixed_clean_and_dirty_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            clean = _write_log(d, "clean.log", CLEAN_LOG)
            dirty = _write_log(d, "dirty.log", DIRTY_LOG)
            self.assertEqual(clog.main(["check_latex_log.py", clean, dirty]), 1)


if __name__ == "__main__":
    unittest.main()
