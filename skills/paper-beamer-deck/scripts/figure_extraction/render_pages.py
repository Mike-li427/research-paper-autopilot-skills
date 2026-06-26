#!/usr/bin/env python3
"""Render source-paper PDF pages to PNG images with PyMuPDF.

The figure extraction pipeline keeps page rendering separate from figure
detection so fallback/manual-review mode is still useful when layout extraction
tools are unavailable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RenderedPage:
    page: int
    image_path: str
    width_px: int
    height_px: int
    width_pt: float
    height_pt: float


def import_fitz():
    try:
        import fitz  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "PyMuPDF is required for page rendering. Install it with "
            "`python3 -m pip install pymupdf`."
        ) from exc
    return fitz


def page_selection(page_count: int, pages: Iterable[int] | None = None) -> list[int]:
    if pages is None:
        return list(range(1, page_count + 1))
    selected = sorted(set(pages))
    invalid = [page for page in selected if page < 1 or page > page_count]
    if invalid:
        raise ValueError(
            f"page(s) outside PDF range 1-{page_count}: "
            + ", ".join(str(page) for page in invalid)
        )
    return selected


def render_pages(
    pdf_path: str,
    out_dir: str,
    dpi: int = 300,
    pages: Iterable[int] | None = None,
) -> list[RenderedPage]:
    """Render PDF pages to ``page_001.png`` style files.

    Page numbers are 1-based. Dimensions in the returned records include both
    rendered-pixel size and PDF point size; bboxes in ``figures.json`` are PDF
    points in the page coordinate system used by PyMuPDF.
    """

    fitz = import_fitz()
    os.makedirs(out_dir, exist_ok=True)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    rendered: list[RenderedPage] = []

    with fitz.open(pdf_path) as doc:
        for page_number in page_selection(doc.page_count, pages):
            page = doc.load_page(page_number - 1)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            rel_name = f"page_{page_number:03d}.png"
            out_path = os.path.join(out_dir, rel_name)
            pix.save(out_path)
            rect = page.rect
            rendered.append(
                RenderedPage(
                    page=page_number,
                    image_path=rel_name,
                    width_px=pix.width,
                    height_px=pix.height,
                    width_pt=float(rect.width),
                    height_pt=float(rect.height),
                )
            )
    return rendered
