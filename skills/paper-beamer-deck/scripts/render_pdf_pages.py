#!/usr/bin/env python3
"""Render selected PDF pages to PNG images for visual inspection.

PDF visual inspection is a mandatory quality gate for generated Beamer decks
(see SKILL.md section 10). This script turns chosen pages of a compiled PDF into
images you can actually look at.

It is **best-effort**: it auto-detects whichever PDF rasterizer is available and
uses it. In rough order of preference:

  1. pdftoppm        (poppler-utils)   -- recommended, fast, high quality
  2. pdftocairo      (poppler-utils)   -- also poppler, PNG output
  3. magick / convert (ImageMagick)    -- needs a working Ghostscript delegate
                                          for PDF; quality/DPI via -density

If none is found, it prints the exact packages to install and exits non-zero.
It never silently "succeeds" with no output.

Usage:
    python3 render_pdf_pages.py main.pdf
    python3 render_pdf_pages.py main.pdf --pages 1-5,8,12 --dpi 150 --out _preview
    python3 render_pdf_pages.py --help

Dependencies (install one):
    poppler-utils      Debian/Ubuntu: apt-get install poppler-utils
                       macOS:        brew install poppler
    ImageMagick        Debian/Ubuntu: apt-get install imagemagick ghostscript
                       macOS:        brew install imagemagick ghostscript

Pure standard library (argparse + subprocess + shutil); no Python packages needed.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys


def parse_pages(spec: "str | None") -> "list[int] | None":
    """Parse a page spec like "1-5,8,12" into a sorted list of 1-based ints.

    Returns None to mean "all pages".
    """
    if spec is None or spec.strip() == "" or spec.strip().lower() == "all":
        return None
    pages: "set[int]" = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            lo_s, hi_s = chunk.split("-", 1)
            try:
                lo, hi = int(lo_s), int(hi_s)
            except ValueError:
                raise ValueError(f"invalid page range: {chunk!r}")
            if lo < 1 or hi < lo:
                raise ValueError(f"invalid page range: {chunk!r}")
            pages.update(range(lo, hi + 1))
        else:
            try:
                n = int(chunk)
            except ValueError:
                raise ValueError(f"invalid page number: {chunk!r}")
            if n < 1:
                raise ValueError(f"page numbers are 1-based: {chunk!r}")
            pages.add(n)
    return sorted(pages)


def which(*names: str) -> "str | None":
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def run(cmd: "list[str]") -> int:
    print("  $ " + " ".join(cmd))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:
        print(f"  ! failed to run {cmd[0]}: {exc}", file=sys.stderr)
        return 127
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    return proc.returncode


def render_with_pdftoppm(tool: str, pdf: str, pages: "list[int] | None",
                         dpi: int, out_dir: str, stem: str) -> int:
    """pdftoppm renders one contiguous range per call; loop over pages."""
    ranges = contiguous_ranges(pages)
    rc_all = 0
    if ranges is None:
        prefix = os.path.join(out_dir, f"{stem}-page")
        rc_all |= run([tool, "-png", "-r", str(dpi), pdf, prefix])
    else:
        for lo, hi in ranges:
            prefix = os.path.join(out_dir, f"{stem}-page")
            rc_all |= run([tool, "-png", "-r", str(dpi),
                           "-f", str(lo), "-l", str(hi), pdf, prefix])
    return rc_all


def render_with_pdftocairo(tool: str, pdf: str, pages: "list[int] | None",
                           dpi: int, out_dir: str, stem: str) -> int:
    ranges = contiguous_ranges(pages)
    rc_all = 0
    prefix = os.path.join(out_dir, f"{stem}-page")
    if ranges is None:
        rc_all |= run([tool, "-png", "-r", str(dpi), pdf, prefix])
    else:
        for lo, hi in ranges:
            rc_all |= run([tool, "-png", "-r", str(dpi),
                           "-f", str(lo), "-l", str(hi), pdf, prefix])
    return rc_all


def render_with_imagemagick(tool: str, pdf: str, pages: "list[int] | None",
                            dpi: int, out_dir: str, stem: str) -> int:
    """ImageMagick uses 0-based page indices in pdf[...]. Render page by page so
    output filenames are predictable and a single bad page does not abort all."""
    rc_all = 0
    if pages is None:
        out = os.path.join(out_dir, f"{stem}-page.png")
        rc_all |= run([tool, "-density", str(dpi), pdf, out])
    else:
        for p in pages:
            out = os.path.join(out_dir, f"{stem}-page-{p:03d}.png")
            rc_all |= run([tool, "-density", str(dpi), f"{pdf}[{p - 1}]", out])
    return rc_all


def contiguous_ranges(pages: "list[int] | None") -> "list[tuple[int, int]] | None":
    if pages is None:
        return None
    ranges: "list[tuple[int, int]]" = []
    start = prev = pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
            continue
        ranges.append((start, prev))
        start = prev = p
    ranges.append((start, prev))
    return ranges


DEP_MESSAGE = """\
No PDF rasterizer found. Install ONE of the following and re-run:

  poppler-utils (recommended -- provides pdftoppm / pdftocairo)
      Debian/Ubuntu:  sudo apt-get install poppler-utils
      Fedora:         sudo dnf install poppler-utils
      macOS:          brew install poppler

  ImageMagick (+ Ghostscript for PDF support)
      Debian/Ubuntu:  sudo apt-get install imagemagick ghostscript
      Fedora:         sudo dnf install ImageMagick ghostscript
      macOS:          brew install imagemagick ghostscript

If you cannot install any of these, fall back to a manual workflow: open the PDF
in any viewer and inspect the pages directly, or take screenshots. See
extract_pdf_figures.md for related manual workflows.
"""


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(
        description="Render selected PDF pages to PNG images for visual inspection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=DEP_MESSAGE,
    )
    parser.add_argument("pdf", help="path to the PDF (e.g. main.pdf)")
    parser.add_argument("--pages", default=None,
                        help='pages to render, e.g. "1-5,8,12" (default: all)')
    parser.add_argument("--dpi", type=int, default=150,
                        help="render resolution in DPI (default: 150)")
    parser.add_argument("--out", default="_preview",
                        help="output directory (default: _preview)")
    args = parser.parse_args(argv[1:])

    if not os.path.isfile(args.pdf):
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    try:
        pages = parse_pages(args.pages)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    stem = os.path.splitext(os.path.basename(args.pdf))[0]
    os.makedirs(args.out, exist_ok=True)

    pdftoppm = which("pdftoppm")
    pdftocairo = which("pdftocairo")
    imagemagick = which("magick", "convert")

    if pdftoppm:
        print(f"Using pdftoppm ({pdftoppm}) at {args.dpi} DPI -> {args.out}/")
        rc = render_with_pdftoppm(pdftoppm, args.pdf, pages, args.dpi, args.out, stem)
    elif pdftocairo:
        print(f"Using pdftocairo ({pdftocairo}) at {args.dpi} DPI -> {args.out}/")
        rc = render_with_pdftocairo(pdftocairo, args.pdf, pages, args.dpi, args.out, stem)
    elif imagemagick:
        print(f"Using ImageMagick ({imagemagick}) at {args.dpi} DPI -> {args.out}/")
        print("  (note: ImageMagick needs a working Ghostscript PDF delegate)")
        rc = render_with_imagemagick(imagemagick, args.pdf, pages, args.dpi, args.out, stem)
    else:
        print(DEP_MESSAGE, file=sys.stderr)
        return 3

    produced = sorted(
        f for f in os.listdir(args.out)
        if f.startswith(stem) and f.lower().endswith(".png")
    )
    if not produced:
        print("ERROR: no images were produced. The rasterizer may have failed "
              "(see messages above).", file=sys.stderr)
        return 1

    print(f"\nRendered {len(produced)} image(s) into {args.out}/:")
    for name in produced:
        print(f"  {os.path.join(args.out, name)}")
    if rc != 0:
        print("\nWARNING: the rasterizer reported a non-zero status on at least one "
              "page; some pages may be missing.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
