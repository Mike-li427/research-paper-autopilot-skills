#!/usr/bin/env python3
"""Verify a ``figures.json`` manifest before slide generation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

try:
    from .render_pages import import_fitz
except ImportError:  # pragma: no cover - direct CLI use
    from render_pages import import_fitz  # type: ignore


def load_manifest(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    return data


def verify_manifest(path: str, strict_review: bool = False) -> list[str]:
    root = os.path.dirname(path)
    manifest = load_manifest(path)
    issues = validate_schema_shape(manifest)
    page_bounds = {
        int(page["page"]): (float(page["width_pt"]), float(page["height_pt"]))
        for page in manifest.get("pages", [])
        if isinstance(page, dict) and "page" in page
    }
    figures = manifest.get("figures", [])
    if not isinstance(figures, list):
        return issues + ["figures must be a JSON array"]

    for figure in figures:
        if not isinstance(figure, dict):
            issues.append("figure record is not an object")
            continue
        label = figure.get("label") or f"index {figure.get('index', '?')}"
        status = figure.get("status")
        if status == "needs_manual_review":
            if strict_review:
                issues.append(f"{label}: still needs manual review")
            continue
        if status != "ok":
            issues.append(f"{label}: invalid status {status!r}")
            continue
        issues.extend(verify_ok_figure(root, figure, page_bounds, str(label)))
    return issues


def validate_schema_shape(manifest: dict[str, Any]) -> list[str]:
    """Small built-in schema validator for the stable fields.

    The repository also ships ``figures.schema.json`` for external validators,
    but this function keeps the CLI dependency-free.
    """
    issues: list[str] = []
    for key in ("schema_version", "source_pdf", "dpi", "bbox_units", "bbox_origin", "extractor", "pages", "figures"):
        if key not in manifest:
            issues.append(f"missing top-level key: {key}")
    if manifest.get("bbox_units") != "pdf_points":
        issues.append("bbox_units must be 'pdf_points'")
    if not isinstance(manifest.get("extractor"), dict):
        issues.append("extractor must be an object")
    if not isinstance(manifest.get("pages"), list):
        issues.append("pages must be an array")
    if not isinstance(manifest.get("figures"), list):
        issues.append("figures must be an array")
    return issues


def verify_ok_figure(
    root: str,
    figure: dict[str, Any],
    page_bounds: dict[int, tuple[float, float]],
    label: str,
) -> list[str]:
    issues: list[str] = []
    image_path = figure.get("image_path")
    if not image_path:
        issues.append(f"{label}: ok record has no image_path")
    else:
        full_path = os.path.join(root, image_path)
        if not os.path.exists(full_path):
            issues.append(f"{label}: image missing: {image_path}")
        else:
            issues.extend(verify_png_nonblank(full_path, label))

    bbox = figure.get("bbox")
    page = figure.get("page")
    if not isinstance(bbox, list) or len(bbox) != 4:
        issues.append(f"{label}: ok record has invalid bbox")
    elif page not in page_bounds:
        issues.append(f"{label}: page bounds unavailable for page {page}")
    else:
        width, height = page_bounds[int(page)]
        x0, y0, x1, y1 = [float(v) for v in bbox]
        if x1 <= x0 or y1 <= y0:
            issues.append(f"{label}: bbox has non-positive area")
        if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
            issues.append(f"{label}: bbox outside page bounds")
    return issues


def verify_png_nonblank(path: str, label: str) -> list[str]:
    try:
        fitz = import_fitz()
        pix = fitz.Pixmap(path)
    except Exception as exc:
        return [f"{label}: could not read image: {exc}"]
    if pix.width <= 0 or pix.height <= 0:
        return [f"{label}: image has invalid dimensions"]
    channels = pix.n
    samples = memoryview(pix.samples)
    step = max(1, len(samples) // 20000)
    # Treat an image as nonblank if sampled RGB bytes contain a dark-ish pixel.
    for i in range(0, len(samples), step * channels):
        pixel = samples[i : i + min(3, channels)]
        if pixel and any(value < 245 for value in pixel):
            return []
    return [f"{label}: image appears blank/near-white"]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Verify extracted figure manifest integrity.")
    parser.add_argument("figures_json", help="path to figures.json")
    parser.add_argument(
        "--strict-review",
        action="store_true",
        help="fail if any figure still has status needs_manual_review",
    )
    args = parser.parse_args(argv[1:])

    try:
        issues = verify_manifest(args.figures_json, strict_review=args.strict_review)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if issues:
        print("Figure verification failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("Figure verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
