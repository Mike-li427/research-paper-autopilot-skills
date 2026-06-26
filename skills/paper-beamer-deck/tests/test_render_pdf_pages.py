"""Regression tests for ``scripts/render_pdf_pages.py``.

Hermetic — exercises the page-spec parsing, range coalescing, and CLI exit codes
without invoking any PDF rasterizer (no poppler / ImageMagick / Ghostscript
needed). The actual subprocess rendering is intentionally out of scope here, as
it requires external binaries. Runs under both ``unittest`` and ``pytest``.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from _import import load_script

rpp = load_script("render_pdf_pages")


class ParsePagesTests(unittest.TestCase):
    def test_none_and_all_mean_all_pages(self) -> None:
        self.assertIsNone(rpp.parse_pages(None))
        self.assertIsNone(rpp.parse_pages(""))
        self.assertIsNone(rpp.parse_pages("  "))
        self.assertIsNone(rpp.parse_pages("all"))
        self.assertIsNone(rpp.parse_pages("ALL"))

    def test_mixed_spec_is_sorted_and_deduped(self) -> None:
        self.assertEqual(rpp.parse_pages("1-5,8,12"), [1, 2, 3, 4, 5, 8, 12])
        self.assertEqual(rpp.parse_pages("12,3,3,1-2"), [1, 2, 3, 12])

    def test_invalid_specs_raise(self) -> None:
        for bad in ("3-1", "0", "abc", "1-", "-5", "2-x"):
            with self.subTest(spec=bad):
                with self.assertRaises(ValueError):
                    rpp.parse_pages(bad)


class ContiguousRangesTests(unittest.TestCase):
    def test_none_passthrough(self) -> None:
        self.assertIsNone(rpp.contiguous_ranges(None))

    def test_coalesces_runs(self) -> None:
        self.assertEqual(
            rpp.contiguous_ranges([1, 2, 3, 5, 8, 9]),
            [(1, 3), (5, 5), (8, 9)],
        )

    def test_single_page(self) -> None:
        self.assertEqual(rpp.contiguous_ranges([7]), [(7, 7)])


class MainExitCodeTests(unittest.TestCase):
    def test_missing_pdf_exits_two(self) -> None:
        self.assertEqual(
            rpp.main(["render_pdf_pages.py", "/no/such/file.pdf"]), 2
        )

    def test_bad_pages_spec_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "main.pdf")
            with open(pdf, "wb") as fh:
                fh.write(b"%PDF-1.4\n")  # contents irrelevant; only existence is checked
            rc = rpp.main(["render_pdf_pages.py", pdf, "--pages", "3-1"])
        self.assertEqual(rc, 2)

    def test_no_rasterizer_exits_three(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "main.pdf")
            with open(pdf, "wb") as fh:
                fh.write(b"%PDF-1.4\n")
            out = os.path.join(d, "_preview")
            # Simulate a machine with no pdftoppm / pdftocairo / magick / convert.
            with mock.patch.object(rpp.shutil, "which", return_value=None):
                rc = rpp.main(["render_pdf_pages.py", pdf, "--out", out])
        # Never silently "succeeds": a missing rasterizer is a hard exit 3.
        self.assertEqual(rc, 3)


if __name__ == "__main__":
    unittest.main()
