# Manual and debug figure extraction notes

These are fallback/debug workflows for getting figures out of a paper and into
a deck's `figures/` directory.
For normal source-PDF slide generation, use the deterministic pipeline first:

```bash
python3 skills/paper-beamer-deck/scripts/figure_extraction/extract_figures.py \
    papers/foo.pdf --out build/figures/foo
```

Then inspect `build/figures/foo/previews/index.html` and consume
`build/figures/foo/figures.json`.
Prefer the **original paper figure** when it is already clear and its exact values/labels matter (see `paper-beamer-deck/SKILL.md` §8).
Whatever method you use, label reused figures in the slide or notes as **"From the paper."** or **"Adapted from the paper."**, and never crop away axes, legends, captions, or labels that the figure needs to be understood.

Do not use these manual methods to bypass `figures.json`.
If automatic extraction cannot find a reliable bbox, add explicit bboxes to
`figure_overrides.json` and rerun the extraction CLI.

There is no single best manual tool — pick by what you have installed and what the figure is.
The common fallback approaches:

---

## 1. Render the page, then crop — PyMuPDF / `pdftoppm` / `pdftocairo`

Best for **vector figures** (diagrams, line plots) and for figures that mix vector + raster.
This is the strategy used by the deterministic extraction CLI after it has a layout-tool or manual bbox.
Render the whole page to a high-DPI image, then crop the explicit bbox.

```bash
# Preferred: render all pages and create a manifest/preview for review.
python3 skills/paper-beamer-deck/scripts/figure_extraction/extract_figures.py \
    papers/foo.pdf --out build/figures/foo

# Manual debug render for page 5 to a 300-DPI PNG:
pdftoppm -png -r 300 -f 5 -l 5 papers/foo.pdf figures/page5
# -> figures/page5-05.png

# Crop with ImageMagick (WIDTHxHEIGHT+XOFF+YOFF, in pixels):
magick figures/page5-05.png -crop 1600x1000+200+450 +repage figures/system-overview.png
```

Tip: use a high DPI (300+) before cropping so the cropped figure stays sharp on a projector.
When using the extraction CLI, write bboxes in PDF points, not rendered pixels.

---

## 2. Extract embedded raster images — `pdfimages` (poppler-utils)

Best when the figure is a photograph, screenshot, or raster plot embedded in the PDF.
Pulls images out at their original resolution (no re-rasterization quality loss).

```bash
# List images and which page each is on (inspect before extracting):
pdfimages -list papers/foo.pdf

# Extract every image as PNG, prefixed "fig":
pdfimages -png papers/foo.pdf figures/fig

# Extract only pages 4-6:
pdfimages -png -f 4 -l 6 papers/foo.pdf figures/fig
```

Caveats: a single visual figure may be stored as several tiles or as a vector + raster mix; `pdfimages` only pulls the raster parts.
Vector figures (most architecture/dataflow diagrams and many line plots) will not appear here — use method 2 or 3 instead.
Some figures come out as CMYK or with a separate soft mask; re-check the PNG.
Do not use raw embedded-image extraction as the primary method for academic-paper figures.

---

## 3. Render deck/PDF pages for visual inspection

```bash
python3 ../../skills/paper-beamer-deck/scripts/render_pdf_pages.py \
    papers/foo.pdf --pages 5 --dpi 300 --out figures
```

This script is for visual inspection and debugging. For extraction metadata,
prefer `figure_extraction/extract_figures.py`.

---

## 4. Crop a vector region losslessly — `pdfcrop` / Ghostscript

Best when you want to keep the figure as **vector PDF** (stays crisp at any zoom) and embed it directly with `\includegraphics{figures/fig.pdf}`.

```bash
# Extract a single page, then auto-trim its margins to the content bounding box:
pdftk papers/foo.pdf cat 5 output figures/page5.pdf      # or: qpdf --pages ...
pdfcrop figures/page5.pdf figures/fig.pdf                # needs TeXLive's pdfcrop

# Ghostscript alternative to pull one page:
gs -sDEVICE=pdfwrite -dFirstPage=5 -dLastPage=5 \
   -o figures/page5.pdf papers/foo.pdf
```

If the page has multiple figures, pre-crop the bounding box (a viewer's crop tool, or `\includegraphics[trim=… ,clip]{}` in LaTeX) before/after `pdfcrop`.

---

## 5. Screenshot + manual crop (last resort)

No tools required beyond a PDF viewer.
Reliable fallback for human inspection, but not a substitute for manifest-based extraction.

1. Open the PDF, zoom in until the figure is large and crisp.
2. Use the OS screenshot tool (region capture) or the viewer's built-in snapshot.
3. Crop tightly to the figure, keeping axes, legends, units, and the caption if it is needed to read the figure.
4. Save into `figures/` with a descriptive name (`result-throughput.png`, not `screenshot1.png`).

Quality tips: capture at a high zoom level (the screenshot resolution is what you get); avoid scaling a small capture up later; keep the aspect ratio when placing it on a slide (`width=…\linewidth`, never force both width and height).

---

## Faithfulness checklist (all methods)

- [ ] Axes, tick labels, and units are still present and readable.
- [ ] Legends and color keys are intact.
- [ ] No data series or annotation was cropped off.
- [ ] The caption is included or paraphrased in the slide/notes if needed to read it.
- [ ] The figure is labeled "From the paper." / "Adapted from the paper."
- [ ] The extracted image is sharp at projector size (re-render at higher DPI if not).
