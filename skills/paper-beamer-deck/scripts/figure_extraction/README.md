# Figure extraction pipeline

Deterministic figure extraction for academic PDFs used by the
`paper-beamer-deck` skill.

The LLM/agent should orchestrate this workflow, not visually guess figure
boundaries. Academic paper figures are often vector drawings, plots composed of
many PDF objects, or mixed vector/raster regions. Extracting embedded images
with `pdfimages` is useful for some photographs and screenshots, but it misses
or fragments many real paper figures.

This pipeline instead:

1. detects figure metadata and bounding boxes with a layout-aware extractor
   (Docling by default, `pdffigures2` as a legacy fallback);
2. renders the relevant PDF page at high resolution with PyMuPDF;
3. crops using detected or manually supplied bounding boxes;
4. writes stable metadata to `figures.json`;
5. renders full pages and a preview HTML for validation.

If automatic layout extraction is unavailable or fails, the CLI still renders
all pages and writes a fallback manifest with `needs_manual_review` records. It
does not mark approximate guessed crops as successful.
The preview HTML shows both the crop and a red bbox overlay on the rendered
page, so bad detections are visible before slide generation.

## Install dependencies

Required:

```bash
python3 -m pip install pymupdf
python3 -m pip install docling
```

Optional:

```bash
# Legacy layout-aware figure metadata fallback.
pdffigures2

# Useful for debugging or alternate page rendering workflows.
sudo apt-get install poppler-utils
```

The CLI degrades gracefully when optional tools are missing.
Docling is the default backend. Its first run may download layout model
artifacts; OCR is disabled by default to avoid extra OCR model downloads for
normal text-based academic PDFs. Pass `--docling-ocr` only for scanned PDFs.
For offline machines, warm the Docling cache while online or configure Docling
to use pre-downloaded artifacts before running this workflow offline.

## Run manually

From a paper-reading workspace root:

```bash
python3 skills/paper-beamer-deck/scripts/figure_extraction/extract_figures.py \
  papers/foo.pdf --out build/figures
```

Backend selection:

```bash
--backend auto        # default: Docling, then pdffigures2, then fallback review
--backend docling     # Docling only
--backend pdffigures2 # legacy fallback only
--backend none        # render pages + caption/manual-review manifest only
--docling-ocr         # enable Docling OCR for scanned PDFs
--type picture,table  # keep only specific detected item types
--min-area-ratio .01  # filter out tiny non-manual bboxes
```

Expected output:

```text
build/figures/
  figures.json
  figures/
    fig_001_page_002_overview.png
  pages/
    page_001.png
    page_002.png
  previews/
    index.html
  figure_overrides.example.json
```

Open `build/figures/previews/index.html` and inspect every figure before using
the crops in slides.

## Manual bbox overrides

Create `figure_overrides.json` in the current directory or in the output
directory, or pass it explicitly with `--overrides`.

```json
[
  {
    "label": "Figure 3",
    "page": 5,
    "bbox": [72, 120, 520, 430],
    "caption": "Manually corrected Figure 3"
  }
]
```

Bounding boxes use PDF points in PyMuPDF's page coordinate system: `[x0, y0, x1,
y1]`, origin at the top-left of the page. If an override has the same label as
an automatically detected record, the override wins. If it has a new label, it
is added as a manual figure record.

Rerun the CLI after adding overrides:

```bash
python3 skills/paper-beamer-deck/scripts/figure_extraction/extract_figures.py \
  papers/foo.pdf --out build/figures --overrides build/figures/figure_overrides.json
```

## Verification and selection helpers

Before slide generation, verify that successful records have valid bboxes and
real crop files:

```bash
python3 skills/paper-beamer-deck/scripts/figure_extraction/verify_figures.py \
  build/figures/figures.json
```

To copy selected figures into a Beamer deck:

```bash
python3 skills/paper-beamer-deck/scripts/figure_extraction/select_figures.py \
  build/figures/figures.json --labels "Figure 1,Table 2" --copy-to slides/foo/figures
```

For Docling tables, the extractor also tries to save structure sidecars under
`tables/` (`.md`, `.html`, and `.csv` when the Docling table object supports
those exports). The crop remains the slide-friendly visual; the sidecars are
mainly for notes, inspection, and reproducible interpretation.

## Slide workflow integration

Before generating a paper Beamer deck from a PDF, run this extractor. During
slide authoring, consume `figures.json`: select figures by label, caption, page,
and semantic relevance, then copy or reference the listed `image_path` entries.

Do not crop figures directly from the PDF during slide generation unless this
pipeline failed and the user has explicitly supplied manual bounding boxes.

## Smoke test

Run the hermetic regression suite from the repository root:

```bash
python3 -m unittest discover -s skills/paper-beamer-deck/tests
```

To test the CLI manually without a successful layout backend, run it on any
valid PDF with `--backend none`. It should create the output directory, render
`pages/page_*.png`, write `figures.json`, write `previews/index.html`, and
report fallback/manual-review status instead of successful guessed crops.

The automated fixture PDFs are generated in tests from synthetic text/shapes,
not copied from real papers. To run the optional live Docling smoke test on a
synthetic PDF, set `PAPER_BEAMER_RUN_DOCLING_SMOKE=1`.
