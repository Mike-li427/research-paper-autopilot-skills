---
name: paper-beamer-deck
description: Use when the user asks to summarize, explain, teach, or build slides for ONE specific paper — e.g. "make slides for this paper", "create a Beamer presentation for paper X", "read ./papers/foo.pdf and generate a detailed slide deck". Produces a detailed, presentation-ready XeLaTeX Beamer deck (using the bundled Simple theme) plus speaker notes, built with a selectable visual-QA cadence (one-shot / risk-targeted / incremental) and a mandatory final PDF visual inspection.
---

# Single-Paper Deep-Dive Beamer Deck

Build a detailed Beamer slide deck for **one** paper, suitable for self-study, graduate-level paper reading, oral presentation, and seminar discussion.

The goal is **not** PDF-to-slides conversion or abstract-to-bullets conversion.
The goal is to read the paper carefully, understand it, reorganize the ideas into a teachable structure, and explain motivation, problem, method, evidence, results, limitations, and implications.
The deck should feel like a careful graduate student read the paper, understood it, and prepared a seminar talk — **not** like an LLM turned a PDF into shallow bullets.

The slides must be detailed enough for a real presentation, but still behave like slides: visual, structured, readable, and not overloaded with paragraphs.

> Audience model: by default, a general graduate-level research audience in the paper's own field — technical, but they may not have read the paper.
> Provide enough background to make the paper understandable without over-explaining basics that are standard in the field.
> If the workspace has a `domain.md` (or an audience/field note in its AGENTS.md), follow it to calibrate background depth, terminology, and examples to the actual research area.

This skill ships:
- `templates/main.tex`, `templates/Makefile`, `templates/notes.md` — copy these into the new deck directory.
- `scripts/check_latex_log.py` — fail-on-warning LaTeX log gate.
- `scripts/render_pdf_pages.py` — render PDF pages to images for visual inspection.
- `scripts/figure_extraction/extract_figures.py` — deterministic academic-PDF figure extraction, manifest generation, and preview HTML.
- `scripts/extract_pdf_figures.md` — manual fallback notes for unusual cases.
- `examples/README.md` — a worked end-to-end example.

---

## Visual QA mode — choose this first

Compiling and the log gate are **cheap**; reading rendered page images is the **expensive** step.
The log gate (`scripts/check_latex_log.py`) already catches errors, missing files, undefined refs/citations, and `Overfull \hbox`/`\vbox` (content spilling past the frame) — **without reading any image**.
Visual reading is only needed for problems the log cannot see: TikZ overlap/clipping, absolute-positioned content drawn outside the frame, distorted or badly cropped figures, unreadable fonts, and awkward spacing.

So the cost knob is **how often you read page images while building**, not compilation.
Three modes set that cadence:

| Mode | Compile + log gate | Read page images while building | End-of-deck pass |
|------|--------------------|---------------------------------|------------------|
| **one-shot** | every batch | never | one full-deck visual pass + aggressive repair/enhance until acceptable |
| **risk-targeted** (default) | every batch | only on high-risk slides | one full-deck visual pass |
| **incremental** | every batch | every batch | covered by the last batch (quick final sweep encouraged) |

**High-risk slides** (what risk-targeted reads mid-build): TikZ, complex `columns`, large figures, cropped paper figures, wide tables, multiline equations, result plots, dense comparison matrices.
Plain text / bullet slides are not image-read mid-build in risk-targeted or one-shot.

**Invariants for every mode:**
- The log gate must be clean before the deck is accepted — it is cheap, it catches frame overflow, and it is **never relaxed**.
- A **final full-deck visual pass is mandatory in all three modes** (Section 10). The mode only changes the *during-build* image-reading cadence (Section 6), never whether the finished deck is visually inspected.

**Selecting the mode.** Ask the user once, at the start, which cadence to use (default **risk-targeted**).
Skip the question and use the default when: the request already signals intent (e.g. "quick draft" / "one-shot" → one-shot; "thorough" / "for my defense" / "high-stakes talk" → incremental), the user defers the choice, or the run is non-interactive (subagent / batch).
Never block the build waiting for an answer that will not come.

---

## 1. Understand the paper first

Before writing any slide, inspect and understand the paper.
Identify:

* title; authors; venue/year if available; abstract;
* problem; motivation; main contribution;
* proposed method; implementation details;
* evaluation setup; key results;
* limitations; related work; possible implications.

If the paper cannot be fully read or parsed, record the limitation clearly.
Do not pretend to understand unreadable content.
Do not invent paper details not present in the source.

**Critical reading.** Do not treat the paper as automatically convincing.
Distinguish: what the paper *claims* vs. what it actually *demonstrates*; what assumptions the evaluation depends on; what remains unproven; what may not generalize.
A good reading explains both the contribution and the *boundary* of the contribution.
Be respectful but critical.

**Terminology consistency.** If the paper uses multiple terms for related concepts, define them once and use a consistent term throughout the deck and notes.

---

## 2. Outline first

Before writing `main.tex`, create a structured outline.
Do not start the deck until the structure is coherent.
The outline should include:

* proposed section structure;
* expected slide count per section;
* key figures and results to explain;
* diagrams that should be recreated or simplified;
* difficult concepts that need background slides;
* important evaluation results;
* likely limitations;
* discussion questions;
* possible research extensions.

---

## 3. Source traceability

For important claims, results, assumptions, and limitations, record their source location.
In `notes.md`, keep a section:

```markdown
## Source Traceability
```

listing: slide number/title · claim/result/assumption/limitation · source section, figure, table, or page.
This matters most for numerical results, stated assumptions, claimed improvements, missing evaluations, limitations, and any inferred extension.
Do not make strong claims without traceable support.

---

## 4. Output structure

Create one deck directory per paper:

```text
./slides/<paper-short-name>/
    main.tex
    notes.md
    Makefile
    figures/
```

Also maintain `./slides/README.md`, listing for each deck: paper title; authors; venue/year; source paper path; generated deck path; short summary; slide count; compilation status; visual inspection status; known issues.

### Required files

**`main.tex`** — the Beamer source.
It must: load the workspace theme (the template's `\InputIfFileExists{../../theme.tex}{}{\usetheme{Simple}}` uses the workspace's `theme.tex`, defaulting to the bundled Simple theme — see the workspace AGENTS.md "Theming"); compile with XeLaTeX; be a complete presentation-ready deck; use clear frame titles; avoid huge text blocks; use diagrams, tables, equations, and visual structure where helpful.
Start from `templates/main.tex`.

**`notes.md`** — detailed speaker/reading notes too verbose for slides: slide-by-slide speaker notes; background explanation; figure interpretation; important assumptions; source traceability; oral presentation script; possible Q&A; limitations; possible research extensions.
Start from `templates/notes.md`.

**`figures/`** — figures used by the deck: cropped/extracted images from the paper, redrawn or simplified diagrams, conceptual diagrams, or TikZ.
If a figure is taken or adapted from the paper, label it as such.
When a source PDF is available, first run `scripts/figure_extraction/extract_figures.py` and consume its `figures.json`.
See `scripts/figure_extraction/README.md` and `scripts/figure_extraction/schema.md`.

**`Makefile`** — build file supporting at least `make` and `make clean`.
The default target compiles `main.tex` with XeLaTeX and runs the log gate.
Start from `templates/Makefile`.
The Makefile gate is useful but **not sufficient**: the PDF must still be visually inspected, because many visual problems produce no LaTeX warning.

---

## 5. Required slide sections

Unless the paper clearly does not need a section, include:

1. **Title** — paper title; authors; venue/year; one-sentence takeaway.
2. **Motivation** — what problem; why it matters; why existing work was insufficient; what practical pressure motivated the work.
3. **Background** — necessary context so a graduate-level reader who has not read the paper can follow it: the concepts, prior methods, mechanisms, datasets, or metrics the paper builds on.
   Calibrate which concepts to define to the workspace's field (see the workspace `domain.md`).
4. **Problem Formulation** — exact research problem/question; target system or setting; assumptions; constraints; what is being optimized or tested.
5. **Key Insight** — the central, non-obvious observation; why the approach makes sense; the intellectual contribution.
   Prefer diagrams here.
6. **Design / Method** — the proposed design or method in detail (the model, system, algorithm, procedure, framework, protocol, or theoretical construction, as fits the paper).
   Break complex mechanisms across multiple slides; never compress a complicated method into one unreadable slide.
7. **Implementation / Materials** — how the proposal was realized (software, hardware, simulator, prototype, dataset, study protocol, or apparatus); what is modeled vs. actually built; what is approximate or idealized.
   Omit if the paper is purely theoretical.
8. **Evaluation Setup** — baselines/comparisons; data, workloads, or subjects; metrics; the experimental or computational environment; variables; methodology; fairness of comparison.
   The audience should understand the setup before seeing results.
9. **Results** — see the Result Interpretation rule below.
10. **Strengths** — what the paper does well (strong insight, clean abstraction, convincing evaluation, useful design, strong problem formulation, practical relevance, elegant mechanism).
11. **Limitations** — weaknesses/boundaries (strong assumptions, limited data or workloads, missing baselines, unclear cost or feasibility, scalability/generalization concerns, unrealistic setup, missing analyses, claimed-vs-evaluated mismatch).
    Be fair, not dismissive.
12. **Discussion Questions** — 3–6 graduate-seminar-style questions about assumptions, generality, scalability, methodology, hidden costs, alternative designs, future research.
    Avoid trivial questions answered directly in the paper.
13. **Takeaways** — 3–5 concise points plus one "If you remember only one thing…" slide.
14. **Research Extensions** — concrete follow-up directions, connected where relevant to the paper's field and adjacent areas (calibrate to the workspace `domain.md`).

### Expected depth

Aim for a deck suitable for a 30–45 minute talk.
Suggested counts: short/simple paper 20–30 slides; normal architecture/systems paper 35–60; dense paper 60+ if needed.
Do not artificially limit slide count, and do not compress content just to reduce it.
If a mechanism/graph/result needs multiple slides to be clear, split it.
Clarity beats brevity — but do not add filler slides.

**High-value priority.** Prioritize the slides that carry the intellectual value: problem formulation, key insight, design overview, main mechanism, evaluation setup, key results, limitations, takeaways.
Do not over-invest in title/outline/generic background while leaving results and limitations shallow.
The deck is not acceptable if the core contribution and evidence are weakly explained.

---

## 6. Build cadence and visual QA (critical)

Broken-layout debt is expensive and must be caught — but *how often* you read page images to catch it depends on the chosen mode (see "Visual QA mode — choose this first" above).
Compilation and the log gate are cheap and run **every batch in all modes**; reading page images is the expensive step whose frequency the mode controls.

Build in small batches regardless of mode:

1. Generate a small batch of slides (5–10; 3–5 for dense/TikZ-heavy decks).
2. Compile with XeLaTeX (`make`, or `xelatex` twice) and run the log gate (`scripts/check_latex_log.py`).
   Fix any errors or overfull-box warnings before continuing — this is cheap and **non-negotiable in every mode**.
3. **Read the rendered page images** (`scripts/render_pdf_pages.py`) according to the mode:
   - **one-shot:** skip image reading during the build.
   - **risk-targeted (default):** read images only for the high-risk slides in this batch (TikZ, complex `columns`, large/cropped figures, wide tables, multiline equations, result plots, dense comparison matrices).
   - **incremental:** read images for the whole batch.
4. Fix any layout, boundary, figure, table, and TikZ issues you find before adding more slides.

**Final visual pass.** After the full deck is built and the log gate is clean, render and visually inspect the whole deck once against the Section 10 checklist, then repair/enhance.
This pass is **mandatory in all modes**.
In one-shot it is the *first* time images are read, so be especially thorough and budget for repair.
In incremental the per-batch reads already cover the deck, so a quick final sweep is enough.

**Early failure is preferred.** Within whatever the mode inspects, fix layout problems before adding more slides.
Never let known layout problems accumulate.

---

## 7. Slide-authoring rules

**Slide purpose.** Every frame must have a clear purpose: motivate a problem, define a concept, explain a mechanism, interpret a result, compare alternatives, expose a limitation, transition between sections, or summarize a takeaway.
A slide should usually communicate one main idea; if it contains several independent ideas, split it.
Avoid slides that merely repeat paper text with no teaching purpose.

**Slide text vs. speaker notes.** Slides carry visual structure, short bullets, diagrams, equations, key comparisons, concise takeaways.
Speaker notes carry the full explanation, oral script, detailed reasoning, caveats, extra background, and Q&A.
Do not put the full explanation on the slide; if a paragraph is needed, move it to `notes.md` and keep only the key idea on the slide.

**Result interpretation.** For each important result figure/table, do not only show it.
Explain: (1) what question the experiment answers; (2) what is compared; (3) what the axes mean; (4) what trend or anomaly appears; (5) what conclusion the authors draw; (6) whether the result actually supports that conclusion; (7) any missing baseline, metric, or workload concern.
If a figure is too complex, split it:

```text
Result Setup → How to Read This Figure → Main Trend → Interpretation and Caveats
```

Never paste a graph with only "X improves performance by Y%".

**Visual design.** Prefer diagrams, flowcharts, architecture blocks, memory-hierarchy drawings, timelines, tables, equations, annotated figures, simplified recreations.
Avoid full paragraphs on slides, tiny fonts, dense unexplained screenshots, raw copied paper text, unexplained figures, too many bullet levels, and decorative visuals with no explanatory value.

---

## 8. Figures: original first, TikZ when useful

### Deterministic extraction first

When extracting figures from academic PDFs, do **not** ask the LLM/agent to visually guess figure boundaries as the primary method.
Always use the dedicated figure extraction pipeline first:

```bash
python3 skills/paper-beamer-deck/scripts/figure_extraction/extract_figures.py \
    papers/<paper>.pdf --out build/figures/<paper-short-name>
```

The pipeline must:

1. detect figure metadata and bounding boxes with Docling by default (`pdffigures2` is only a legacy fallback);
2. render the target PDF page at high resolution;
3. crop using the detected or manually specified bounding box;
4. save crops, full-page renders, preview HTML, and metadata to `figures.json`.

Before generating slides from a PDF, run the extractor and inspect `previews/index.html`.
Slide generation should consume `figures.json`, selecting figures by label, caption text, page number, and semantic relevance, and should refer to the listed `image_path` entries.
Run `verify_figures.py` before using the manifest in slides; use `select_figures.py` if figures need to be copied into the deck's local `figures/` directory.
Do not directly crop figures from the PDF during slide generation unless the extraction module failed and the user explicitly provides manual bounding boxes in `figure_overrides.json`.

If automatic extraction fails, use the rendered full pages for manual review and mark the relevant records as `needs_manual_review`.
Do not silently use approximate crops, low-quality screenshots, or embedded-image fragments as successful extracted figures.

Use `figures.json` status values strictly:

- `ok` — the crop may be used in slides after visual inspection.
- `needs_manual_review` — do not use as an extracted figure; add/fix `figure_overrides.json` and rerun the extractor.

**Default policy — prefer the original paper figure** (cropped screenshot or extracted image) when it is already clear, contains important results, contains detailed architecture, has many precise labels, is a graph/table/plot whose exact values matter, or where redrawing risks mistakes.
Original figures are especially right for evaluation graphs, result breakdowns, ablation/sensitivity studies, hardware-architecture diagrams, system-overview and workflow figures, and value-sensitive tables/plots.

**Required treatment for any reused figure** — using it is not enough.
The slide or notes must explain why it is shown, what question it answers, what the axes/labels/components/colors mean, what to focus on, what conclusion the authors draw, whether the figure supports that conclusion, and any caveat/missing baseline.
Label every reused figure `From the paper.` or `Adapted from the paper.` If cropped, do not remove important labels, legends, axes, captions, or annotations.

**Use TikZ when it improves teaching clarity** — when the original is too dense or detailed, when a simplified conceptual diagram teaches the idea better, when a clean abstraction is needed, when the paper has no suitable figure, or to show a mechanism step by step / a taxonomy / a layered view / a "before vs after".
Good uses: simplified block diagrams, dataflow or pipeline diagrams, layered/stack diagrams, process or state diagrams, timelines, taxonomies, problem-space maps.

**Do not use TikZ** merely to look polished — avoid it when the original is already better, when the TikZ version would be less accurate, when it needs too many nodes/arrows, when it becomes crowded, when labels overlap or arrows collide, or when it risks changing the meaning.
A bad TikZ diagram is worse than a well-cropped original.

**Figure quality priority:** (1) faithful to the paper; (2) easy to explain during a talk; (3) visually readable; (4) not broken/cluttered; (5) efficient to produce.

**Figure explanation rule.** A figure is never self-explanatory.
Every included figure must explain why it is shown, what each important component means, how to read it, what conclusion to draw, and what caveat it has.
Do not include figures as decoration or as proof the paper was read.
If a figure is too complex, show a simplified conceptual diagram first, then the original later if needed.

---

## 9. Beamer layout robustness

Layout robustness is a first-class requirement.

> Do not save slide count at the cost of broken slides.
> It is always better to split content into multiple readable slides than to create one dense or broken slide.

**Alignment and boundary requirements.** Every slide must respect frame boundaries.
Avoid: text overflowing the slide; figures/tables exceeding boundaries; TikZ clipped unintentionally; overlapping blocks; captions colliding with figures; bullets extending below the frame; uneven/broken columns; excessive whitespace from poor layout; tiny fonts used to force content onto one slide.

**Split-first policy.** When a slide is crowded, split it — do not fix overcrowding by shrinking all text, using tiny fonts, cutting margins aggressively, compressing diagrams until unreadable, or piling on columns.
Good splits:

```text
Motivation I: System Pressure / Motivation II: Why Existing Approaches Fall Short
Design Overview / Design Detail I … II … III
Evaluation Setup I: Workloads & Baselines / II: Metrics & Hardware
Result I: Overall / II: Breakdown / III: Sensitivity
```

**Figures/tables.** Keep aspect ratio; use `width=\linewidth` or a safe fraction; avoid hard-coded dimensions that may exceed the slide; crop margins; keep labels/legends readable.
For tables: avoid large raw tables; summarize/split; use comparison matrices only when readable; split wide tables; prefer small focused tables; never rely on tiny fonts.

**Columns.** Keep total width ≤ `\textwidth`; leave horizontal spacing; avoid >2 columns unless content is light; do not put dense bullet lists in both columns; align consistently; prefer one visual + one explanation column.
If crowded, split into slides.

**TikZ inspection.** A TikZ slide may compile and still be unacceptable.
Check every TikZ slide for overlapping nodes/labels, arrows crossing labels or colliding with nodes, excessive edge crossings, cramped spacing, clipped nodes/arrows, diagrams touching boundaries, inconsistent alignment/arrow directions, unreadable labels, visual imbalance, too many nodes/arrows, excessive absolute positioning.
Fix by redesigning or splitting — not merely shrinking.
Quality bar: *clean enough for a graduate-level oral presentation.*

**Overfull/underfull box policy.** Compilation warnings matter.
Inspect the log for `Overfull \hbox`, `Overfull \vbox`, clipped content, missing figures, unreadably small content, and margin overruns.
If overfull warnings hit important frames, revise the layout (split the frame, simplify the figure, reduce table columns, move details to `notes.md`, use better structure).
**Do not ignore severe overfull warnings.** The `scripts/check_latex_log.py` gate fails the build on these.

**No artificial slide limit.** There is no strict maximum.
Priority order: (1) correctness/faithful understanding; (2) readable structure; (3) no broken/overflowing slides; (4) visual clarity; (5) reasonable slide count.

---

## 10. PDF visual inspection is mandatory

PDF visual inspection is a **mandatory quality gate**.
A deck is *not* acceptable merely because `xelatex` succeeds, `main.pdf` exists, the log has no fatal errors, or the content is technically correct.

> Compilation success is not the same as presentation readiness.

This **final** visual gate applies to all three build modes (Section 6): one-shot and risk-targeted reach it as a single full-deck pass at the end; incremental reaches it through its per-batch reads plus a final sweep.
The chosen mode changes *how often* you read images while building — it never waives inspecting the finished deck.

A slide is **broken/unacceptable** if it has any of:

- **Boundary/overflow:** text outside the slide; bullets below the frame; equations exceeding width; tables/figures off the slide; clipped diagrams; colliding captions; overflowing footnotes/references; footer/header collisions.
- **Alignment/spacing:** misaligned columns; overlapping blocks; figure/text collision; cramped vertical/horizontal spacing; visual imbalance; large unused whitespace from poor layout; awkward-but-technically-inside elements.
- **Readability:** font too small for live use; unreadable figure/axis/legend/table text; too many bullets or nested bullets; paragraph dumps; slides that take too long to read during a talk.
- **Figures:** too large/clipped or too small; distorted aspect ratio; wasteful margins; multiple complex figures crammed together; figure shown without explanation; caption overlap; crop removing important labels/legends/axes; low-quality screenshot.
- **Tables:** wider than the slide; too dense; unreadable; too many columns; rows colliding; scaled until useless; raw paper table pasted unsimplified; matrix that should have been split.
- **TikZ:** overlapping nodes/labels; arrows crossing labels/nodes; edge crossings; cramped spacing; clipped nodes/arrows; touching boundaries; inconsistent alignment/directions; unreadable labels; imbalance; too many nodes/arrows; understandable but messy.
  Bar: clean enough for a graduate-level oral presentation.
- **Columns:** total width exceeds `\textwidth`; columns touch/overlap; dense bullets in both; one column much taller without purpose; visual imbalance; content below boundary; columns used where separate slides would be clearer.
- **Math:** equations exceeding width; poorly aligned multiline equations; tiny symbols; unexplained equations; too many equations per slide; numbers/annotations colliding; derivations compressed into one frame (split important derivations).
- **References/citations:** citations overflowing lines; tiny bibliography text; too many references per slide; references colliding with footer; unclear figure attribution; missing source labels for copied/adapted figures.

**Required fix strategy.** When a slide is crowded/broken/messy, redesign or split it.
Do **not** mainly fix by shrinking text, tiny fonts, aggressive margin cuts, compressing figures, scaling tables, forcing columns, hiding details in tiny captions, or accepting overlap "because it's still understandable."
Prefer: split into multiple slides; reduce to one idea; move long text to `notes.md`; replace paragraphs with structured bullets; use focused comparison tables; split wide tables; crop figure margins; recreate a simplified diagram; use progressive diagrams; increase TikZ spacing; cut TikZ node/arrow count; move secondary diagram detail to notes; separate "how to read" from "interpretation".

**Required workflow.**
1. Compile with XeLaTeX at least twice (or `make`).
2. Inspect the log (Overfull h/vbox, missing figures, undefined refs after 2nd pass, fatal/package errors, missing fonts/bibliography).
   Severe warnings must be fixed or explicitly documented if unavoidable.
   Use `scripts/check_latex_log.py`.
3. Inspect the actual PDF pages — dense-text, table, figure, TikZ, column, equation, result, and reference slides especially.
   Use `scripts/render_pdf_pages.py`.
4. Fix broken slides (usually split/simplify/redesign).
5. Recompile and reinspect the affected slides.
6. For final acceptance, run lightweight quality checks where applicable:
   `generate_quality_report.py`, `check_deck_sources.py`, `check_visual_qa.py`,
   and `figure_extraction/verify_figures.py`.

**Non-negotiable acceptance rule.** A deck is not complete if the PDF is visually broken, even if the content is correct.
When in doubt, split the slide.

### Visual inspection checklist

- [ ] No text overflows frame boundaries.
- [ ] No bullets continue below the bottom of a frame.
- [ ] No figures clipped unintentionally.
- [ ] No tables run off the slide.
- [ ] No table/figure scaled until unreadable.
- [ ] No blocks overlap.
- [ ] No captions collide with content.
- [ ] No columns exceed slide width.
- [ ] No slide relies on tiny fonts to fit too much content.
- [ ] No slide looks like a paragraph dump.
- [ ] All important figures readable.
- [ ] All important tables readable.
- [ ] All equations fit and are readable.
- [ ] All TikZ diagrams visually inspected.
- [ ] TikZ nodes/labels do not overlap.
- [ ] TikZ arrows do not collide with labels or nodes.
- [ ] TikZ diagrams not clipped.
- [ ] TikZ diagrams have clean spacing and alignment.
- [ ] Dense result figures explained clearly.
- [ ] Any crowded slide split or redesigned.
- [ ] Final PDF suitable for a live graduate-level oral presentation.

---

## 11. Compilation requirements

Before finishing, confirm the deck compiles with XeLaTeX:

```bash
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

or use the `Makefile`.
If compilation fails, fix it.
If it still fails, document the error clearly in `./slides/README.md` and the deck's `notes.md`.
Do not claim a deck is presentation-ready if it does not compile, or if the PDF has not been visually inspected.

---

## 12. Pilot-first when multiple papers are requested

Do not mass-produce decks.
If several papers are requested:

1. Generate one complete deck as a pilot.
2. Compile with XeLaTeX.
3. Visually inspect the PDF.
4. Report: paper processed; slide count; output path; compilation status; visual inspection status; known issues; quality notes.
5. Continue with remaining papers only if requested.

---

## 13. Final self-review

Before finishing, review the deck:

- Does every slide have a clear purpose?
- Are any slides too dense?
- Any likely overfull or clipped frames?
- Are figures readable?
  Tables split if too wide?
- Are original paper figures properly labeled, faithful, and readable?
- If source-PDF figures were used, were they selected from `figures.json` records with `status: ok` and inspected in `previews/index.html`?
- Is TikZ used only when it improves clarity, and visually inspected for overlap, collisions, clipping, and spacing?
- Are major results explained rather than merely shown?
- Is the contribution clearly separated from background?
- Are assumptions and limitations included?
- Are discussion questions and (where appropriate) research extensions included?
- Does the deck load the workspace theme (default Simple) and compile with XeLaTeX?
- Has the generated PDF been visually inspected?
- Can this deck support a real oral presentation?

---

## 14. Definition of Done

A single-paper deck is complete only if:

* `main.tex`, `notes.md`, `Makefile` exist; `figures/` exists if figures are used;
* the deck loads the workspace theme (default Simple, via `theme.tex`);
* the deck compiles with XeLaTeX, or the failure is clearly documented;
* the final PDF has had a mandatory full-deck visual pass (per the chosen mode, Section 6 / Section 10);
* the slides are detailed and presentation-ready;
* the slides explain, reorganize, and teach the paper;
* each slide has a clear purpose;
* major figures and results are interpreted;
* limitations and discussion questions are included;
* research extensions are included where appropriate;
* Beamer alignment/boundary problems have been checked;
* TikZ diagrams, if used, have been visually inspected;
* original paper figures, if used, are properly labeled and explained;
* `quality_report.md` is generated or any skipped quality checks are documented;
* `./slides/README.md` is updated.

> Final quality bar: the deck should be good enough to support a real graduate-level oral presentation, and should never feel like a shallow LLM-generated summary.

### What not to do

Do not: delete or modify original papers; move or modify `beamerthemeSimple.sty`; place generated slides outside `./slides/`; silently skip papers; generate shallow summaries; copy large chunks of paper text; create text-only decks; use unexplained screenshots; hide compilation failures; claim presentation-readiness without compiling or without visual inspection; invent paper details or citations; ignore severe overfull/clipping problems; reduce readability merely to reduce slide count; or redraw original figures in TikZ when a cropped original would be clearer and more faithful.
Do not bypass the figure extraction manifest by visually guessing PDF crop boundaries during slide generation; run the extraction pipeline first, consume `figures.json`, and use manual overrides when automatic bboxes are missing.
