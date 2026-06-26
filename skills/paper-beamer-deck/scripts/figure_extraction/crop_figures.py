#!/usr/bin/env python3
"""Crop detected figure regions from rendered PDF pages.

Bounding boxes are represented in PDF points as ``[x0, y0, x1, y1]`` in the
page coordinate system used by PyMuPDF. Crops are rendered directly from the
page with a clip rectangle, which is equivalent to high-resolution page
rendering followed by an exact crop and avoids embedded-image-only extraction.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

try:  # Allow both package-style and direct script imports.
    from .render_pages import import_fitz
except ImportError:  # pragma: no cover - exercised by direct CLI use
    from render_pages import import_fitz  # type: ignore


@dataclass(frozen=True)
class CroppedFigure:
    image_path: str
    width_px: int
    height_px: int


def slugify(text: str, fallback: str = "figure") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return (slug or fallback)[:60].strip("-") or fallback


def validate_bbox(bbox: list[float], page_width: float, page_height: float) -> None:
    if len(bbox) != 4:
        raise ValueError("bbox must contain exactly four numbers")
    x0, y0, x1, y1 = [float(v) for v in bbox]
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"bbox has non-positive area: {bbox}")
    if x0 < 0 or y0 < 0 or x1 > page_width or y1 > page_height:
        raise ValueError(
            f"bbox {bbox} is outside page bounds [0, 0, {page_width}, {page_height}]"
        )


def crop_pdf_region(
    pdf_path: str,
    page_number: int,
    bbox: list[float],
    out_path: str,
    dpi: int = 300,
) -> CroppedFigure:
    fitz = import_fitz()
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with fitz.open(pdf_path) as doc:
        if page_number < 1 or page_number > doc.page_count:
            raise ValueError(f"page {page_number} outside PDF range 1-{doc.page_count}")
        page = doc.load_page(page_number - 1)
        validate_bbox(bbox, float(page.rect.width), float(page.rect.height))
        clip = fitz.Rect(*[float(v) for v in bbox])
        pix = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
        pix.save(out_path)
        return CroppedFigure(
            image_path=out_path,
            width_px=pix.width,
            height_px=pix.height,
        )
