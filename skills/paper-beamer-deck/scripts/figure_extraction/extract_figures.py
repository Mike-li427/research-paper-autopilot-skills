#!/usr/bin/env python3
"""Extract academic-paper figures into a manifest-driven workspace.

The CLI is intentionally conservative: automatic success requires a reliable
layout-tool bbox or an explicit manual override. If no layout extractor is
available, it renders pages and creates review records instead of guessing
figure boundaries visually.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # Allow both package-style and direct script execution.
    from .crop_figures import crop_pdf_region, slugify
    from .render_pages import RenderedPage, import_fitz, render_pages
except ImportError:  # pragma: no cover - direct CLI use
    from crop_figures import crop_pdf_region, slugify  # type: ignore
    from render_pages import RenderedPage, import_fitz, render_pages  # type: ignore


SCHEMA_VERSION = "1.0"
CAPTION_RE = re.compile(
    r"\b((?:Fig(?:ure)?\.?|Table|圖|表)\s*"
    r"(?:S?\d+[A-Za-z]?(?:\([a-z]\))?|[IVXLCDM]+))"
    r"\s*[:：.\-–]\s*(.+)",
    re.IGNORECASE,
)


@dataclass
class FigureCandidate:
    index: int
    label: str | None = None
    page: int | None = None
    bbox: list[float] | None = None
    caption: str = ""
    kind: str | None = None
    method: str = "none"
    status: str = "needs_manual_review"
    reason: str | None = None
    image_path: str | None = None
    data_paths: dict[str, str] = field(default_factory=dict)
    confidence: float | None = None
    source: dict[str, Any] = field(default_factory=dict)
    sidecar_data: dict[str, str] = field(default_factory=dict, repr=False)

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "index": self.index,
            "label": self.label,
            "page": self.page,
            "bbox": self.bbox,
            "caption": self.caption,
            "image_path": self.image_path,
            "method": self.method,
            "status": self.status,
        }
        if self.kind:
            data["type"] = self.kind
        if self.data_paths:
            data["data_paths"] = self.data_paths
        if self.confidence is not None:
            data["confidence"] = self.confidence
        if self.reason:
            data["reason"] = self.reason
        if self.source:
            data["source"] = self.source
        return data


def parse_pages(spec: str | None) -> list[int] | None:
    if spec is None or spec.strip() == "" or spec.strip().lower() == "all":
        return None
    pages: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            lo_s, hi_s = chunk.split("-", 1)
            lo, hi = int(lo_s), int(hi_s)
            if lo < 1 or hi < lo:
                raise ValueError(f"invalid page range: {chunk!r}")
            pages.update(range(lo, hi + 1))
        else:
            n = int(chunk)
            if n < 1:
                raise ValueError(f"page numbers are 1-based: {chunk!r}")
            pages.add(n)
    return sorted(pages)


def relpath(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def normalize_bbox(value: Any) -> list[float] | None:
    """Normalize common bbox shapes to ``[x0, y0, x1, y1]`` floats."""
    if value is None:
        return None
    if isinstance(value, dict):
        keys = [("x0", "y0", "x1", "y1"), ("x1", "y1", "x2", "y2")]
        for names in keys:
            if all(name in value for name in names):
                return [float(value[name]) for name in names]
        if all(name in value for name in ("left", "top", "width", "height")):
            x0 = float(value["left"])
            y0 = float(value["top"])
            return [x0, y0, x0 + float(value["width"]), y0 + float(value["height"])]
    if isinstance(value, (list, tuple)) and len(value) == 4:
        return [float(v) for v in value]
    return None


def label_key(label: str | None) -> str:
    return re.sub(r"\s+", " ", (label or "").strip().lower())


def normalize_label(text: str) -> str:
    label = re.sub(r"\s+", " ", text.strip())
    if re.match(r"(?i)^fig\.?\s+", label):
        return re.sub(r"(?i)^fig\.?", "Figure", label, count=1)
    if label.startswith("圖"):
        return "Figure " + label[1:].strip()
    if label.startswith("表"):
        return "Table " + label[1:].strip()
    return label


def normalize_type(text: str | None) -> str:
    value = (text or "").strip().lower()
    aliases = {
        "fig": "picture",
        "figure": "picture",
        "image": "picture",
        "table": "table",
        "chart": "chart",
        "picture": "picture",
    }
    return aliases.get(value, value)


def parse_type_filter(spec: str | None) -> set[str] | None:
    if spec is None or not spec.strip() or spec.strip().lower() == "all":
        return None
    return {normalize_type(part) for part in spec.split(",") if part.strip()}


def load_overrides(path: str | None) -> list[FigureCandidate]:
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, list):
        raise ValueError("figure_overrides.json must contain a JSON array")
    overrides: list[FigureCandidate] = []
    for idx, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError("each figure override must be an object")
        bbox = normalize_bbox(item.get("bbox"))
        if bbox is None:
            raise ValueError(f"override #{idx} is missing a valid bbox")
        page = item.get("page")
        if page is None:
            raise ValueError(f"override #{idx} is missing a page")
        overrides.append(
            FigureCandidate(
                index=idx,
                label=item.get("label") or f"Manual Figure {idx}",
                page=int(page),
                bbox=bbox,
                caption=str(item.get("caption", "")),
                kind=item.get("type"),
                method="manual_override",
                status="pending_crop",
                confidence=1.0,
                source={"override": os.path.basename(path)},
            )
        )
    return overrides


def choose_default_override(out_dir: str, explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for candidate in ("figure_overrides.json", os.path.join(out_dir, "figure_overrides.json")):
        if os.path.exists(candidate):
            return candidate
    return None


def run_docling(
    pdf_path: str,
    use_ocr: bool = False,
) -> tuple[list[FigureCandidate], str | None]:
    if importlib.util.find_spec("docling") is None:
        return [], "docling not installed"
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as exc:
        return [], f"docling import failed: {exc}"

    try:
        options = PdfPipelineOptions(
            do_ocr=use_ocr,
            do_picture_classification=False,
            do_picture_description=False,
            generate_picture_images=False,
        )
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=options)
            }
        )
        result = converter.convert(pdf_path)
    except Exception as exc:
        return [], f"docling conversion failed: {exc}"

    document = getattr(result, "document", None)
    if document is None:
        return [], "docling conversion produced no document"
    candidates = parse_docling_document(document)
    if not candidates:
        return [], "docling produced no picture/table records with bounding boxes"
    return candidates, None


def parse_docling_document(document: Any) -> list[FigureCandidate]:
    candidates: list[FigureCandidate] = []
    items = list(getattr(document, "pictures", []) or [])
    items.extend(getattr(document, "tables", []) or [])

    for item in items:
        prov = first_provenance(item)
        if prov is None:
            continue
        page = getattr(prov, "page_no", None)
        bbox = docling_bbox_to_top_left(prov, document)
        if page is None or bbox is None:
            continue

        caption = docling_caption_text(item, document)
        label = label_from_caption(caption)
        kind_value = getattr(item, "label", None)
        kind = normalize_type(str(getattr(kind_value, "value", kind_value or "picture")))
        sidecar_data = table_sidecar_data(item) if kind == "table" else {}
        candidates.append(
            FigureCandidate(
                index=len(candidates) + 1,
                label=label,
                page=int(page),
                bbox=bbox,
                caption=caption,
                kind=kind,
                method="docling",
                status="pending_crop",
                source={"self_ref": str(getattr(item, "self_ref", ""))},
                sidecar_data=sidecar_data,
            )
        )
    return candidates


def table_sidecar_data(item: Any) -> dict[str, str]:
    data: dict[str, str] = {}
    if hasattr(item, "export_to_markdown"):
        try:
            value = item.export_to_markdown()
            if value:
                data["markdown"] = str(value)
        except Exception:
            pass
    if hasattr(item, "export_to_html"):
        try:
            value = item.export_to_html()
            if value:
                data["html"] = str(value)
        except Exception:
            pass
    if hasattr(item, "export_to_dataframe"):
        try:
            dataframe = item.export_to_dataframe()
            if hasattr(dataframe, "to_csv"):
                data["csv"] = dataframe.to_csv(index=False)
        except Exception:
            pass
    return data


def first_provenance(item: Any) -> Any | None:
    prov = getattr(item, "prov", None) or []
    return prov[0] if prov else None


def docling_bbox_to_top_left(prov: Any, document: Any) -> list[float] | None:
    bbox = getattr(prov, "bbox", None)
    page_no = getattr(prov, "page_no", None)
    if bbox is None or page_no is None:
        return None

    page_height = docling_page_height(document, int(page_no))
    if page_height is not None and hasattr(bbox, "to_top_left_origin"):
        bbox = bbox.to_top_left_origin(page_height=page_height)
    if hasattr(bbox, "as_tuple"):
        values = bbox.as_tuple()
    else:
        values = (
            getattr(bbox, "l", None),
            getattr(bbox, "t", None),
            getattr(bbox, "r", None),
            getattr(bbox, "b", None),
        )
    if any(value is None for value in values):
        return None
    x0, y0, x1, y1 = [float(value) for value in values]
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def docling_page_height(document: Any, page_no: int) -> float | None:
    pages = getattr(document, "pages", {}) or {}
    page = pages.get(page_no) if hasattr(pages, "get") else None
    size = getattr(page, "size", None)
    height = getattr(size, "height", None)
    return float(height) if height is not None else None


def docling_caption_text(item: Any, document: Any) -> str:
    parts: list[str] = []
    for ref in getattr(item, "captions", []) or []:
        resolved = None
        if hasattr(ref, "resolve"):
            try:
                resolved = ref.resolve(document)
            except Exception:
                resolved = None
        if resolved is None:
            continue
        text = getattr(resolved, "text", None) or getattr(resolved, "orig", None)
        if text:
            parts.append(str(text).strip())
    return " ".join(part for part in parts if part).strip()


def label_from_caption(caption: str) -> str | None:
    match = CAPTION_RE.search(caption)
    if not match:
        return None
    return normalize_label(match.group(1))


def run_pdffigures2(pdf_path: str, page_base: str = "auto") -> tuple[list[FigureCandidate], str | None]:
    tool = shutil.which("pdffigures2")
    if not tool:
        return [], "pdffigures2 not found on PATH"
    with tempfile.TemporaryDirectory(prefix="pdffigures2-") as tmp:
        metadata_dir = os.path.join(tmp, "metadata")
        raw_dir = os.path.join(tmp, "raw")
        os.makedirs(metadata_dir, exist_ok=True)
        os.makedirs(raw_dir, exist_ok=True)
        cmd = [tool, "-m", metadata_dir, "-d", raw_dir, pdf_path]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except OSError as exc:
            return [], f"pdffigures2 failed to start: {exc}"
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout or "").strip()
            return [], "pdffigures2 exited non-zero" + (f": {msg}" if msg else "")

        json_files = sorted(Path(metadata_dir).glob("*.json"))
        if not json_files:
            return [], "pdffigures2 produced no metadata JSON"
        candidates: list[FigureCandidate] = []
        for path in json_files:
            candidates.extend(parse_pdffigures2_json(path, page_base=page_base))
        if not candidates:
            return [], "pdffigures2 metadata contained no figures with bbox records"
        return candidates, None


def parse_pdffigures2_json(path: Path, page_base: str = "auto") -> list[FigureCandidate]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    records = raw.get("figures", raw) if isinstance(raw, dict) else raw
    if not isinstance(records, list):
        return []
    candidates: list[FigureCandidate] = []
    for idx, item in enumerate(records, start=1):
        if not isinstance(item, dict):
            continue
        bbox = normalize_bbox(
            item.get("regionBoundary")
            or item.get("renderDpiBoundary")
            or item.get("bbox")
            or item.get("boundary")
        )
        label = item.get("name") or item.get("label") or item.get("figureLabel")
        page_raw = item.get("page")
        page = int(page_raw) if page_raw is not None else None
        if page is not None and (page_base == "zero" or (page_base == "auto" and page == 0)):
            page += 1
        caption = item.get("caption") or item.get("captionText") or ""
        kind = item.get("figType") or item.get("type")
        status = "pending_crop" if bbox is not None and page is not None else "needs_manual_review"
        reason = None if status == "pending_crop" else "No reliable bounding box found"
        candidates.append(
            FigureCandidate(
                index=idx,
                label=str(label) if label else None,
                page=page,
                bbox=bbox,
                caption=str(caption),
                kind=str(kind) if kind else None,
                method="pdffigures2",
                status=status,
                reason=reason,
                source={"metadata": str(path.name)},
            )
        )
    return candidates


def discover_caption_records(pdf_path: str) -> list[FigureCandidate]:
    """Find text captions for fallback review records without inferring bboxes."""
    fitz = import_fitz()
    candidates: list[FigureCandidate] = []
    seen: set[tuple[int, str]] = set()
    with fitz.open(pdf_path) as doc:
        for page_index, page in enumerate(doc, start=1):
            lines = [" ".join(line.split()) for line in page.get_text("text").splitlines()]
            for i, line in enumerate(lines):
                match = CAPTION_RE.search(line)
                if not match:
                    continue
                label = normalize_label(match.group(1))
                key = (page_index, label_key(label))
                if key in seen:
                    continue
                seen.add(key)
                caption_tail = collect_caption_tail(match.group(2).strip(), lines[i + 1:])
                candidates.append(
                    FigureCandidate(
                        index=len(candidates) + 1,
                        label=label,
                        page=page_index,
                        bbox=None,
                        caption=caption_tail,
                        kind="table" if label.lower().startswith("table") else "picture",
                        method="caption_text_fallback",
                        status="needs_manual_review",
                        reason="Layout extractor unavailable or failed; provide bbox in figure_overrides.json",
                    )
                )
    return candidates


def collect_caption_tail(first: str, following_lines: list[str], limit: int = 500) -> str:
    parts = [first]
    for line in following_lines[:3]:
        if not line or CAPTION_RE.search(line):
            break
        if len(" ".join(parts + [line])) > limit:
            break
        parts.append(line)
    return " ".join(parts).strip()


def apply_overrides(
    detected: list[FigureCandidate],
    overrides: list[FigureCandidate],
) -> list[FigureCandidate]:
    if not overrides:
        return detected
    by_label = {label_key(candidate.label): candidate for candidate in detected if candidate.label}
    result = list(detected)
    for override in overrides:
        key = label_key(override.label)
        if key and key in by_label:
            target = by_label[key]
            target.page = override.page
            target.bbox = override.bbox
            target.caption = override.caption or target.caption
            target.kind = override.kind or target.kind
            target.method = "manual_override"
            target.status = "pending_crop"
            target.reason = None
            target.confidence = 1.0
            target.source = override.source
        else:
            result.append(override)
    for idx, candidate in enumerate(result, start=1):
        candidate.index = idx
    return result


def filter_candidates(
    candidates: list[FigureCandidate],
    pages: list[RenderedPage],
    allowed_types: set[str] | None,
    min_area_ratio: float,
) -> tuple[list[FigureCandidate], list[dict[str, Any]]]:
    page_areas = {page.page: page.width_pt * page.height_pt for page in pages}
    kept: list[FigureCandidate] = []
    filtered: list[dict[str, Any]] = []
    for candidate in candidates:
        is_manual = candidate.method.startswith("manual_override")
        reason = filter_reason(candidate, page_areas, allowed_types, min_area_ratio)
        if reason and not is_manual:
            filtered.append({**candidate.to_json(), "filter_reason": reason})
            continue
        kept.append(candidate)
    for idx, candidate in enumerate(kept, start=1):
        candidate.index = idx
    return kept, filtered


def filter_reason(
    candidate: FigureCandidate,
    page_areas: dict[int, float],
    allowed_types: set[str] | None,
    min_area_ratio: float,
) -> str | None:
    kind = normalize_type(candidate.kind)
    if allowed_types is not None and kind and kind not in allowed_types:
        return f"type {kind!r} not in requested type filter"
    if min_area_ratio <= 0 or candidate.bbox is None or candidate.page is None:
        return None
    page_area = page_areas.get(candidate.page)
    if not page_area:
        return None
    x0, y0, x1, y1 = candidate.bbox
    area_ratio = max(0.0, (x1 - x0) * (y1 - y0)) / page_area
    if area_ratio < min_area_ratio:
        return f"area ratio {area_ratio:.4f} below min_area_ratio {min_area_ratio:.4f}"
    return None


def crop_candidates(
    pdf_path: str,
    out_dir: str,
    candidates: list[FigureCandidate],
    dpi: int,
) -> None:
    figures_dir = os.path.join(out_dir, "figures")
    for candidate in candidates:
        if candidate.status != "pending_crop":
            continue
        if candidate.page is None or candidate.bbox is None:
            candidate.status = "needs_manual_review"
            candidate.reason = "No reliable bounding box found"
            candidate.method = "none" if candidate.method == "pending_crop" else candidate.method
            continue
        label = candidate.label or f"Figure {candidate.index}"
        slug_source = candidate.caption or label
        name = (
            f"fig_{candidate.index:03d}_page_{candidate.page:03d}_"
            f"{slugify(slug_source, fallback=slugify(label))}.png"
        )
        out_path = os.path.join(figures_dir, name)
        try:
            crop_pdf_region(pdf_path, candidate.page, candidate.bbox, out_path, dpi=dpi)
        except Exception as exc:  # keep manifest explicit, do not hide failed crops
            candidate.status = "needs_manual_review"
            candidate.reason = f"Could not crop bbox: {exc}"
            candidate.image_path = None
            continue
        method = candidate.method
        if method == "docling":
            method = "docling+render_crop"
        elif method == "pdffigures2":
            method = "pdffigures2+render_crop"
        elif method == "manual_override":
            method = "manual_override+render_crop"
        else:
            method = f"{method}+render_crop"
        candidate.method = method
        candidate.status = "ok"
        candidate.reason = None
        candidate.image_path = relpath(out_path, out_dir)
        if normalize_type(candidate.kind) == "table":
            candidate.data_paths = write_table_sidecars(out_dir, candidate)


def write_table_sidecars(out_dir: str, candidate: FigureCandidate) -> dict[str, str]:
    if not candidate.sidecar_data:
        return {}
    paths: dict[str, str] = {}
    table_dir = os.path.join(out_dir, "tables")
    os.makedirs(table_dir, exist_ok=True)
    label = candidate.label or f"table {candidate.index}"
    stem = f"table_{candidate.index:03d}_page_{candidate.page or 0:03d}_{slugify(label, fallback='table')}"
    extensions = {"markdown": "md", "html": "html", "csv": "csv"}
    for key, value in candidate.sidecar_data.items():
        extension = extensions.get(key)
        if not extension or not value:
            continue
        path = os.path.join(table_dir, f"{stem}.{extension}")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(value)
            if not value.endswith("\n"):
                fh.write("\n")
        paths[key] = relpath(path, out_dir)
    return paths


def write_preview(
    out_dir: str,
    figures: list[FigureCandidate],
    pages: list[RenderedPage],
) -> str:
    previews_dir = os.path.join(out_dir, "previews")
    os.makedirs(previews_dir, exist_ok=True)
    page_map = {page.page: page for page in pages}
    rows = []
    for fig in figures:
        image_html = "<span class='missing'>No crop</span>"
        if fig.image_path:
            image_html = (
                f"<a href='../{html.escape(fig.image_path)}'>"
                f"<img src='../{html.escape(fig.image_path)}' alt='{html.escape(fig.label or str(fig.index))}' />"
                "</a>"
            )
        overlay_html = render_overlay_html(fig, page_map)
        rows.append(
            "<section class='figure'>"
            f"<div class='image'>{image_html}</div>"
            "<div>"
            "<dl>"
            f"<dt>Label</dt><dd>{html.escape(fig.label or '')}</dd>"
            f"<dt>Page</dt><dd>{html.escape(str(fig.page or ''))}</dd>"
            f"<dt>Type</dt><dd>{html.escape(fig.kind or '')}</dd>"
            f"<dt>Status</dt><dd class='{html.escape(fig.status)}'>{html.escape(fig.status)}</dd>"
            f"<dt>Method</dt><dd>{html.escape(fig.method)}</dd>"
            f"<dt>BBox</dt><dd>{html.escape(json.dumps(fig.bbox))}</dd>"
            f"<dt>Caption</dt><dd>{html.escape(fig.caption)}</dd>"
            f"<dt>Reason</dt><dd>{html.escape(fig.reason or '')}</dd>"
            "</dl>"
            f"{overlay_html}"
            "</div>"
            "</section>"
        )
    body = "\n".join(rows) or "<p>No figure records found. Inspect rendered pages and add figure_overrides.json.</p>"
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Figure Extraction Preview</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #222; }}
    h1 {{ font-size: 1.6rem; }}
    .figure {{ display: grid; grid-template-columns: minmax(220px, 38%) 1fr; gap: 1rem; padding: 1rem 0; border-top: 1px solid #ddd; }}
    img {{ max-width: 100%; border: 1px solid #bbb; background: white; }}
    dl {{ display: grid; grid-template-columns: 7rem 1fr; gap: .35rem .8rem; margin: 0; }}
    dt {{ font-weight: 700; color: #444; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .ok {{ color: #126c39; font-weight: 700; }}
    .needs_manual_review {{ color: #9a4b00; font-weight: 700; }}
    .missing {{ display: inline-block; padding: 2rem; border: 1px dashed #aaa; color: #666; }}
    .overlay-wrap {{ max-width: 520px; margin-top: 1rem; }}
    .overlay-title {{ font-weight: 700; margin: 0 0 .4rem; color: #444; }}
    .page-overlay {{ position: relative; display: inline-block; line-height: 0; }}
    .page-overlay img {{ width: 100%; max-width: 520px; }}
    .bbox {{ position: absolute; border: 3px solid #d22; box-sizing: border-box; background: rgba(210, 34, 34, .08); }}
    .hint {{ color: #666; font-size: .9rem; line-height: 1.35; }}
  </style>
</head>
<body>
  <h1>Figure Extraction Preview</h1>
  {body}
</body>
</html>
"""
    path = os.path.join(previews_dir, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return path


def render_overlay_html(fig: FigureCandidate, page_map: dict[int, RenderedPage]) -> str:
    if fig.page is None or fig.bbox is None:
        return (
            "<p class='hint'>No bbox yet. Use the rendered page dimensions shown "
            "in figure_overrides.example.json to provide one.</p>"
        )
    page = page_map.get(fig.page)
    if not page:
        return "<p class='hint'>Page render unavailable for bbox overlay.</p>"
    x0, y0, x1, y1 = fig.bbox
    left = 100.0 * x0 / page.width_pt
    top = 100.0 * y0 / page.height_pt
    width = 100.0 * (x1 - x0) / page.width_pt
    height = 100.0 * (y1 - y0) / page.height_pt
    style = (
        f"left:{left:.4f}%;top:{top:.4f}%;"
        f"width:{width:.4f}%;height:{height:.4f}%;"
    )
    return (
        "<div class='overlay-wrap'>"
        "<p class='overlay-title'>BBox on rendered page</p>"
        "<div class='page-overlay'>"
        f"<img src='../pages/{html.escape(page.image_path)}' alt='page {page.page}' />"
        f"<span class='bbox' style='{html.escape(style)}'></span>"
        "</div>"
        f"<p class='hint'>Page {page.page}: {page.width_pt:.1f} x {page.height_pt:.1f} PDF points.</p>"
        "</div>"
    )


def write_override_example(
    out_dir: str,
    figures: list[FigureCandidate],
    pages: list[RenderedPage],
) -> str:
    page_map = {page.page: page for page in pages}
    examples: list[dict[str, Any]] = []
    review_figures = [fig for fig in figures if fig.status == "needs_manual_review"]
    if not review_figures:
        review_figures = [FigureCandidate(index=1, label="Figure 1", page=pages[0].page if pages else 1)]

    for fig in review_figures:
        page = page_map.get(fig.page or 0)
        width = page.width_pt if page else 612.0
        height = page.height_pt if page else 792.0
        examples.append(
            {
                "label": fig.label or f"Figure {fig.index}",
                "page": fig.page or 1,
                "bbox": [
                    round(width * 0.12, 2),
                    round(height * 0.18, 2),
                    round(width * 0.88, 2),
                    round(height * 0.55, 2),
                ],
                "caption": fig.caption or "Replace with the figure caption.",
                "_note": "Replace bbox with [x0, y0, x1, y1] in PDF points, origin top-left.",
                "_page_size_pt": [round(width, 2), round(height, 2)],
            }
        )

    path = os.path.join(out_dir, "figure_overrides.example.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(examples, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path


def build_manifest(
    pdf_path: str,
    out_dir: str,
    dpi: int,
    pages: list[RenderedPage],
    figures: list[FigureCandidate],
    extractor_status: str,
    extractor_reason: str | None,
    backend: str,
    attempts: list[dict[str, str]],
    filters: dict[str, Any],
    filtered: list[dict[str, Any]],
    override_path: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_pdf": pdf_path,
        "dpi": dpi,
        "bbox_units": "pdf_points",
        "bbox_origin": "top-left page coordinate system as used by PyMuPDF",
        "extractor": {
            "primary": backend,
            "status": extractor_status,
            "reason": extractor_reason,
            "attempts": attempts,
            "filters": filters,
            "override_path": override_path,
        },
        "pages": [
            {
                "page": p.page,
                "image_path": f"pages/{p.image_path}",
                "width_px": p.width_px,
                "height_px": p.height_px,
                "width_pt": p.width_pt,
                "height_pt": p.height_pt,
            }
            for p in pages
        ],
        "figures": [candidate.to_json() for candidate in figures],
        "filtered": filtered,
        "manual_review": {
            "instructions": (
                "Inspect previews/index.html and pages/page_*.png. For any "
                "needs_manual_review record, add figure_overrides.json with "
                "label, page, bbox, and optional caption, then rerun this CLI."
            )
        },
    }


def run_layout_backend(
    pdf_path: str,
    backend: str,
    use_docling_ocr: bool,
    pdffigures2_page_base: str,
) -> tuple[list[FigureCandidate], str, str | None, str, list[dict[str, str]]]:
    attempts: list[dict[str, str]] = []
    if backend in ("auto", "docling"):
        candidates, reason = run_docling(pdf_path, use_ocr=use_docling_ocr)
        attempts.append({"backend": "docling", "status": "ok" if candidates else "failed", "reason": reason or ""})
        if candidates:
            return candidates, "ok", None, "docling", attempts
        if backend == "docling":
            return [], "fallback", reason, "docling", attempts

    if backend in ("auto", "pdffigures2"):
        candidates, reason = run_pdffigures2(pdf_path, page_base=pdffigures2_page_base)
        attempts.append({"backend": "pdffigures2", "status": "ok" if candidates else "failed", "reason": reason or ""})
        if candidates:
            return candidates, "ok", None, "pdffigures2", attempts
        if backend == "pdffigures2":
            return [], "fallback", reason, "pdffigures2", attempts

    if backend == "none":
        reason = "automatic layout extraction disabled"
        attempts.append({"backend": "none", "status": "skipped", "reason": reason})
        return [], "fallback", reason, "none", attempts

    reason = "; ".join(
        f"{attempt['backend']}: {attempt['reason']}" for attempt in attempts if attempt["reason"]
    ) or "no layout backend produced figure records"
    primary = "docling" if backend == "auto" else backend
    return [], "fallback", reason, primary, attempts


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Extract academic-paper figures using layout metadata plus rendered-page crops."
    )
    parser.add_argument("pdf", help="source paper PDF")
    parser.add_argument("--out", required=True, help="output directory, e.g. build/figures")
    parser.add_argument("--dpi", type=int, default=300, help="render/crop DPI (default: 300)")
    parser.add_argument("--pages", default=None, help='page subset to render, e.g. "1-3,8" (default: all)')
    parser.add_argument("--overrides", default=None, help="path to figure_overrides.json")
    parser.add_argument(
        "--type",
        dest="types",
        default=None,
        help='comma-separated type filter, e.g. "picture,chart,table" (default: all)',
    )
    parser.add_argument(
        "--min-area-ratio",
        type=float,
        default=0.0,
        help="drop non-manual bbox records smaller than this page-area fraction (default: 0)",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "docling", "pdffigures2", "none"),
        default="auto",
        help="layout extraction backend (default: auto = docling, then pdffigures2)",
    )
    parser.add_argument(
        "--docling-ocr",
        action="store_true",
        help="enable Docling OCR for scanned PDFs (default: off to avoid OCR model downloads)",
    )
    parser.add_argument(
        "--pdffigures2-page-base",
        choices=("auto", "zero", "one"),
        default="auto",
        help="interpret pdffigures2 page numbers (default: auto)",
    )
    args = parser.parse_args(argv[1:])

    if not os.path.isfile(args.pdf):
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        return 2
    try:
        selected_pages = parse_pages(args.pages)
        allowed_types = parse_type_filter(args.types)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.min_area_ratio < 0:
        print("ERROR: --min-area-ratio must be non-negative", file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    override_path = choose_default_override(args.out, args.overrides)

    try:
        rendered = render_pages(args.pdf, os.path.join(args.out, "pages"), dpi=args.dpi, pages=selected_pages)
    except Exception as exc:
        print(f"ERROR: could not render PDF pages: {exc}", file=sys.stderr)
        return 1

    detected, extractor_status, reason, primary_backend, attempts = run_layout_backend(
        args.pdf,
        args.backend,
        args.docling_ocr,
        args.pdffigures2_page_base,
    )
    if not detected:
        try:
            detected = discover_caption_records(args.pdf)
        except Exception as exc:
            detected = []
            reason = (reason or "layout extractor unavailable") + f"; caption scan failed: {exc}"

    try:
        overrides = load_overrides(override_path)
    except Exception as exc:
        print(f"ERROR: invalid override file: {exc}", file=sys.stderr)
        return 2

    figures = apply_overrides(detected, overrides)
    figures, filtered = filter_candidates(
        figures,
        rendered,
        allowed_types=allowed_types,
        min_area_ratio=args.min_area_ratio,
    )
    crop_candidates(args.pdf, args.out, figures, dpi=args.dpi)
    for idx, candidate in enumerate(figures, start=1):
        candidate.index = idx

    preview_path = write_preview(args.out, figures, rendered)
    override_example_path = write_override_example(args.out, figures, rendered)
    manifest = build_manifest(
        args.pdf,
        args.out,
        args.dpi,
        rendered,
        figures,
        extractor_status,
        reason,
        primary_backend,
        attempts,
        {
            "types": sorted(allowed_types) if allowed_types is not None else None,
            "min_area_ratio": args.min_area_ratio,
        },
        filtered,
        override_path,
    )
    manifest_path = os.path.join(args.out, "figures.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    ok = sum(1 for fig in figures if fig.status == "ok")
    review = sum(1 for fig in figures if fig.status != "ok")
    print(f"Rendered {len(rendered)} page(s) -> {os.path.join(args.out, 'pages')}")
    print(f"Wrote manifest -> {manifest_path}")
    print(f"Wrote preview -> {preview_path}")
    print(f"Wrote override example -> {override_example_path}")
    print(f"Figure records: {ok} ok, {review} needs_manual_review, {len(filtered)} filtered")
    if extractor_status == "fallback":
        print(
            "\nAutomatic layout extraction did not succeed. Inspect pages/ and "
            "previews/index.html, add figure_overrides.json with explicit bboxes, "
            "then rerun this command. No guessed crops were marked successful.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
