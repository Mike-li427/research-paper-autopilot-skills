# `figures.json` schema

Schema version: `1.0`

Machine-readable schema: `figures.schema.json`.

`figures.json` is an object with a stable top-level structure:

```json
{
  "schema_version": "1.0",
  "source_pdf": "papers/foo.pdf",
  "dpi": 300,
  "bbox_units": "pdf_points",
  "bbox_origin": "top-left page coordinate system as used by PyMuPDF",
  "extractor": {
    "primary": "docling",
    "status": "ok",
    "reason": null,
    "attempts": [
      {
        "backend": "docling",
        "status": "ok",
        "reason": ""
      }
    ],
    "override_path": null
  },
  "pages": [],
  "figures": [],
  "filtered": [],
  "manual_review": {
    "instructions": "..."
  }
}
```

## Page records

Each `pages[]` entry describes a rendered page:

```json
{
  "page": 1,
  "image_path": "pages/page_001.png",
  "width_px": 2550,
  "height_px": 3300,
  "width_pt": 612.0,
  "height_pt": 792.0
}
```

## Successful figure records

Each successful figure has:

```json
{
  "index": 1,
  "label": "Figure 1",
  "page": 2,
  "bbox": [72, 120, 520, 430],
  "caption": "System overview.",
  "image_path": "figures/fig_001_page_002_system-overview.png",
  "method": "docling+render_crop",
  "status": "ok",
  "type": "picture",
  "confidence": 1.0
}
```

Required keys for every figure record:

- `index`: 1-based order in the manifest.
- `label`: paper label when known, such as `Figure 1`; may be `null`.
- `page`: 1-based PDF page number; may be `null` if unknown.
- `bbox`: `[x0, y0, x1, y1]` in PDF points; may be `null`.
- `caption`: caption text when known; otherwise an empty string.
- `image_path`: relative path to the PNG crop; `null` when no successful crop
  exists.
- `method`: provenance string, for example `docling+render_crop`,
  `pdffigures2+render_crop`, `manual_override+render_crop`,
  `caption_text_fallback`, or `none`.
- `status`: `ok` or `needs_manual_review`.

Optional keys:

- `type`: normalized item type such as `picture`, `chart`, or `table`.
- `confidence`: numeric confidence when the source provides one or a manual
  override is used.
- `reason`: explanation for failed or uncertain records.
- `source`: extractor-specific metadata provenance.

## Failed or uncertain records

Failures are explicit:

```json
{
  "index": 3,
  "label": "Figure 3",
  "page": 5,
  "bbox": null,
  "caption": "Ablation results.",
  "image_path": null,
  "method": "caption_text_fallback",
  "status": "needs_manual_review",
  "reason": "Layout extractor unavailable or failed; provide bbox in figure_overrides.json"
}
```

Slide generation must treat `needs_manual_review` as not extracted. It may use
the rendered full page for inspection, but it must not treat an approximate
visual guess as a successful crop.

## Filtered records

If `--type` or `--min-area-ratio` filters remove automatic detections, they are
recorded under top-level `filtered[]` instead of silently disappearing:

```json
{
  "index": 2,
  "label": "Figure 9",
  "page": 7,
  "bbox": [50, 50, 60, 60],
  "caption": "Tiny decorative mark.",
  "image_path": null,
  "method": "docling",
  "status": "pending_crop",
  "type": "picture",
  "filter_reason": "area ratio 0.0002 below min_area_ratio 0.0100"
}
```

Manual overrides are never filtered.
