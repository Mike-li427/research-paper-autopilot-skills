# Example: building a single-paper Beamer deck

A worked, end-to-end walkthrough of the `paper-beamer-deck` skill.
This is illustrative — no compiled PDF is committed.
The computer-architecture paper below is just a sample; the skill is field-agnostic (set your area in the workspace `domain.md`).

## Scenario

The user drops a paper in a workspace and says:

> "Read `papers/elastic-accel.pdf` and make a detailed Beamer deck for a seminar."

Short name chosen: `elastic-accel`.

## Step 1 — Understand the paper, then outline (before any LaTeX)

Identify problem, motivation, contribution, method, implementation, evaluation setup, key results, limitations.
Then write a structured outline, e.g.:

```text
Title (1)            Motivation I–II (2)     Background (2)
Problem (1)          Key Insight (2, 1 TikZ) Design Overview + Detail I–III (4)
Implementation (1)   Eval Setup I–II (2)     Results: overall / breakdown / sensitivity (4)
Strengths (1)        Limitations (2)         Discussion Qs (1)  Takeaways (2)  Extensions (1)
≈ 33 slides; high-risk slides: the Key-Insight TikZ + the 3 result figures.
```

## Step 2 — Scaffold the deck from templates

```bash
mkdir -p slides/elastic-accel/figures
cp skills/paper-beamer-deck/templates/{main.tex,Makefile,notes.md} slides/elastic-accel/
```

Resulting layout:

```text
slides/
├── README.md                 # index row added in Step 5
└── elastic-accel/
    ├── main.tex
    ├── Makefile
    ├── notes.md
    └── figures/              # cropped paper figures + any TikZ assets live here
```

## Step 3 — Author in small batches (this example uses the default risk-targeted cadence)

Generate ~5–10 slides, then:

```bash
cd slides/elastic-accel
make                        # xelatex ×2 + fail-on-warning log gate (every batch, all modes)
python3 ../../skills/paper-beamer-deck/scripts/render_pdf_pages.py main.pdf --pages 1-10 --dpi 150
# -> open _preview/*.png and LOOK at them
```

The log gate runs every batch in all modes. **Reading the PNGs** is the expensive step the mode controls — here, in risk-targeted, read images for the high-risk slides only: the Key-Insight TikZ slide and each result figure. (In `one-shot` you would skip the mid-build reads entirely and rely on the Step 4 final pass; in `incremental` you would read every batch.)
Fix any broken slide by splitting/redesigning — not by shrinking fonts.
Don't accumulate layout debt before moving on.

Pull figures from the PDF as needed (see `../scripts/extract_pdf_figures.md`), and label reused figures "From the paper." / "Adapted from the paper."

## Step 4 — Final pass

```bash
make                        # full-deck compile; log gate must be clean
python3 ../../skills/paper-beamer-deck/scripts/render_pdf_pages.py main.pdf   # all pages
```

Walk the SKILL.md §10 visual-inspection checklist.
Write up `notes.md` (speaker notes
+ the Source Traceability table).

## Step 5 — Update `slides/README.md`

| Paper | Authors | Venue/Year | Source | Deck | Slides | Compiles | Inspected | Issues |
|-------|---------|-----------|--------|------|--------|----------|-----------|--------|
| Elastic Accelerator Sharing | … | ASPLOS 2025 | `papers/elastic-accel.pdf` | `slides/elastic-accel/` | 33 | yes | yes | none |

## Pilot-first reminder

If asked for several decks at once, finish and inspect **one** pilot deck, report (paper, slide count, output path, compile status, inspection status, known issues), then continue only if the user asks.
