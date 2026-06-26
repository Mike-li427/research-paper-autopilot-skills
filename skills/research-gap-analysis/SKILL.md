---
name: research-gap-analysis
description: Use when the user asks to analyze, compare, or synthesize MULTIPLE specified papers together — e.g. "analyze these papers and find research gaps", "compare paper A, B, and C", "what has been done and what remains open", "find research directions from these papers". Produces a structured research-gap memo (research-gap-analysis.md), a paper comparison matrix, per-paper reading notes, and — by default — a presentation Beamer slide deck summarizing the analysis — not independent per-paper summaries.
---

# Multi-Paper Research Gap Analysis

Analyze a set of specified papers **together** to understand the research landscape they collectively form.
The goal is **not** to summarize each paper independently.
The goal is to understand the research landscape and answer:

* What problem space do these papers collectively address?
* What assumptions do they share?
  Where do they differ?
* What systems, workloads, or constraints are covered?
* What important cases are missing?
  What gaps remain open?
* Which gaps are realistic research opportunities?
* Which gaps are too broad, already solved, weakly motivated, or hard to evaluate?

The output should feel like a careful graduate student read the papers, understood them, prepared a research memo, and thought critically about what the work means — **not** like an LLM produced shallow per-paper bullets.

> Audience model: by default, a general graduate-level research audience in the papers' field — technical, but may not have read the papers.
> If the workspace has a `domain.md` (or an audience/field note in its AGENTS.md), follow it to calibrate background depth, terminology, and examples to the actual research area.

This skill ships:
- `templates/research-gap-analysis.md` — the memo skeleton.
- `templates/paper-matrix.md` — the comparison-matrix template.
- `templates/reading-note.md` — the per-paper reading-note template.
- `templates/slides-main.tex` — the gap-analysis Beamer deck skeleton (Simple theme).
- `templates/slides-notes.md` — speaker notes for the gap-analysis deck.
- `examples/README.md` — a worked end-to-end example.

## Output modes

This skill has two output modes.
Confirm which one the user wants before starting; if they do not say, default to `memo+deck`.

| Mode | Produces | Cost | Use when |
|------|----------|------|----------|
| **`memo+deck`** (default) | The memo (with matrix + reading notes) **and** a presentation Beamer deck summarizing the analysis | Higher: also writes, compiles, and **visually inspects** a LaTeX deck (needs XeLaTeX; adds an iterative build/QA loop) | You will present or demo the analysis |
| **`memo-only`** | Just the memo, matrix, and reading notes (Markdown) | Lower: no LaTeX, no compile/inspect loop | You only need the written analysis, or XeLaTeX is unavailable |

The deck (when produced) reuses the Beamer mechanics, build/QA discipline, and scripts of the [`paper-beamer-deck`](../paper-beamer-deck/SKILL.md) skill (Simple theme, XeLaTeX, fail-on-warning log gate, **mandatory PDF visual inspection**) — see §13 below.
In `memo-only` mode, skip §13 and the `./slides/...` output entirely.

---

## 1. Understand the papers first

Before writing any output, inspect and understand each paper.
For each, identify: title; authors; venue/year; abstract; problem; motivation; main contribution; proposed method; implementation details; evaluation setup; key results; limitations; related work; possible implications.

If a paper cannot be fully read or parsed, record the limitation clearly.
Do not pretend to understand unreadable content.
Do not invent paper details not present in the source.

**Critical reading.** Do not treat every paper as equally convincing.
For each, separate what it *claims* from what it actually *demonstrates*, what assumptions the evaluation depends on, what remains unproven, and what may not generalize.

**Terminology normalization.** Papers often use different names for the same concept, or the same name for different concepts.
Explicitly normalize terminology when papers diverge, and define each normalized term once (use the workspace `domain.md` to record the field's preferred wording where it exists).

---

## 2. Outline first

Before writing the memo, create a short outline.
Do not jump straight to a shallow summary.
The outline should include:

* selected papers;
* comparison dimensions;
* expected taxonomy;
* likely candidate gaps;
* known uncertainties;
* claims that require careful verification.

The point is to force a structured analysis before writing.

---

## 3. Claim-evidence discipline (critical)

Every nontrivial claim about a paper must be grounded in the paper.
When you say "this paper assumes X", "does not evaluate Y", "improves Z", "targets workload W", "this gap is not covered", you should be able to point to the relevant section, figure, table, experiment, or statement.
Cite which paper section/figure/table/page supports each major comparison or gap claim when possible — especially for numerical results, stated assumptions, claimed improvements, missing evaluations, limitations, and inferred gaps.

**Mark uncertainty.** Use careful language:

* "The selected papers do not appear to cover…"
* "Based on the analyzed set, a possible gap is…"
* "This needs verification against broader related work…"
* "The paper demonstrates X under the evaluated setting, but does not establish Y."

**Do not overclaim novelty.** Do not infer novelty too aggressively.
Do not claim a research gap is novel unless the analyzed evidence supports it.
It is acceptable — and expected — to mark a claim as uncertain or a gap as not-yet-well-formed.

---

## 4. Output structure

For each multi-paper analysis task, create:

```text
./analysis/<topic-short-name>/
    research-gap-analysis.md
    paper-matrix.md
    reading-notes/
        <paper-short-name>.md   (one per paper)
    figures/
```

**In `memo+deck` mode (the default), also produce a presentation deck** that summarizes the analysis (in `memo-only` mode, omit this directory):

```text
./slides/<topic-short-name>-gap-analysis/
    main.tex
    notes.md
    Makefile
    figures/
```

Build this deck with the `paper-beamer-deck` skill's mechanics and quality bar (Simple theme, XeLaTeX, selectable visual-QA cadence (one-shot / risk-targeted / incremental), log gate, mandatory final PDF visual inspection).
Its content is structured around the *analysis* (landscape → taxonomy → comparison → gaps → directions), not around a single paper — see §13.
Do **not** produce one deck per paper; produce a single synthesis deck for the whole analysis.

### Required files

**`research-gap-analysis.md`** — the main memo, written as a structured research memo (not a casual summary).
Start from `templates/research-gap-analysis.md`.
It should include: topic overview; analyzed-paper list; problem landscape; taxonomy; cross-paper comparison; common assumptions; common evaluation methods; covered workloads/platforms; missing workloads/platforms; unresolved problems; possible research gaps; gap-strength evaluation; suggested future directions; recommended next papers.

**`paper-matrix.md`** — a comparison matrix.
Start from `templates/paper-matrix.md`.
At minimum compare papers by: problem addressed; target system; workload; proposed mechanism; software-stack assumptions; hardware assumptions; evaluation platform; metrics; baselines; strengths; limitations; what the paper does not cover.

**`reading-notes/<paper-short-name>.md`** — one note per paper.
Start from `templates/reading-note.md`.
Each note includes: bibliographic metadata; one-paragraph summary; key contributions; assumptions; method; evaluation; key results; limitations; relevance to the gap analysis.

**`figures/`** — taxonomy diagrams, comparison diagrams, conceptual maps.
Prefer simple diagrams, tables, and structured visual summaries.

---

## 5. Gap taxonomy

The analysis must distinguish different kinds of gaps.

**Explicit gaps** — directly acknowledged by the papers (e.g. authors name a case, population, or condition they do not handle; leave something as future work; do not measure a relevant quantity; do not test a relevant setting).

**Implied gaps** — inferred by comparing the papers (e.g. Paper A assumes a fixed setting while Paper B varies it, but none study the case in between; several works optimize one objective but none jointly with another; papers report one metric but not a second that matters for the claim).

**Methodology gaps** — gaps in how the papers evaluate their claims (weak baselines; unrealistic assumptions; no ablation; no sensitivity analysis; insufficient modeling; missing measurements; no end-to-end or real-setting evaluation).

**Deployment / external-validity gaps** — gaps between the research setting and real use (assumes resources or conditions that real settings lack; assumes perfect inputs or knowledge; ignores integration, contention, or cost; ignores constraints that matter in practice).

**Opportunity gaps** — potential research directions worth pursuing.
Evaluate each carefully; for each include: gap statement; why it matters; why existing papers do not solve it; possible research question; possible method; possible evaluation plan; risk level; expected contribution type; and whether it is likely strong, medium, or weak.

---

## 6. Gap strength evaluation

For each proposed gap, classify it:

* **Strong gap** — clear problem, important motivation, insufficiently solved, evaluable, likely to yield insight.
* **Medium gap** — interesting but needs sharper framing, stronger motivation, or better evaluation design.
* **Weak gap** — mostly engineering, already addressed, too incremental, too vague, or not clearly important.

Do not overclaim.
It is acceptable to say a proposed gap is weak or not yet well-formed.

---

## 7. Memo structure

Use this structure for `research-gap-analysis.md` unless the user requests otherwise (see `templates/research-gap-analysis.md`):

1. **Scope** — which papers; which area; what is intentionally out of scope.
2. **One-Paragraph Executive Summary** — the main finding.
3. **Paper List** — title, authors, venue/year, local path.
4. **Problem Landscape** — the broader problem; why it matters.
5. **Taxonomy** — organize by meaningful dimensions for the field (e.g. problem type, setting or population, method family, assumptions, data or materials, evaluation methodology).
   Choose the axes that actually separate these papers.
6. **Paper-by-Paper Summary** — concise but meaningful; not the whole document.
7. **Cross-Paper Comparison** — compare directly on assumptions, mechanisms, workloads, evaluation, claimed benefits, limitations.
8. **What Is Already Well Covered?** — relatively mature problems/techniques.
9. **What Is Not Covered?** — missing cases, assumptions, evaluations, system settings.
10. **Candidate Research Gaps** — for each: gap statement; why it matters; why existing work does not solve it; possible research question; possible approach; possible evaluation; risks; strength (Strong/Medium/Weak).
11. **Most Promising Directions** — ranked, with what would make them publishable.
12. **Dangerous or Weak Directions** — tempting but weak; explain why.
13. **Recommended Next Papers** — do not fabricate citations; mark unsure ones "to verify".
14. **Final Takeaway** — what the selected papers collectively imply.

---

## 8. Cross-paper synthesis quality bar

A good analysis must not be shallow like:

```text
Paper A does X. Paper B does Y. Paper C does Z. Therefore future work is combining X, Y, Z.
```

Instead, identify: hidden assumptions; missing evaluation dimensions; mismatched claims and evidence; system layers that are ignored; workloads that are excluded; abstractions that do not compose; deployment constraints that are not modeled; and why a new research question would matter.

---

## 9. Visual requirements

Include visual structure where useful: taxonomy tables; comparison matrices; problem-space maps; layered system diagrams; timelines of related work; claim-vs-evidence tables; workload/platform coverage maps.
For Markdown, use tables.
For the Beamer deck, use diagrams and tables rather than long text (see §13).

---

## 10. Pilot-first workflow

1. Identify the specified papers.
2. Create a short outline of the intended comparison dimensions.
3. Build the paper matrix.
4. Draft the research-gap analysis (memo).
5. Build the presentation deck from the memo (§13): outline the slides, generate them in small batches, compile with XeLaTeX, and **visually inspect the PDF**.
6. Report: papers analyzed; memo output path; deck output path; slide count; compilation status; visual inspection status; major candidate gaps; uncertain or weakly supported claims; recommended next steps.

---

## 11. Final self-review

Before finishing, review the analysis:

- Are papers compared directly rather than summarized separately?
- Are candidate gaps grounded in evidence?
- Are weak gaps identified honestly?
- Are hidden assumptions discussed?
- Are evaluation-methodology gaps considered?
- Are deployment gaps considered?
- Are proposed directions concrete and evaluable?
- Are uncertain claims marked as uncertain?
- Are recommended next papers clearly marked if not verified?
- Does the presentation deck exist, compile with XeLaTeX, and present the synthesis (not one deck per paper)?
- Has the deck's PDF been visually inspected, and is the comparison matrix readable (simplified/split rather than shrunk)?

---

## 12. Definition of Done

A research-gap analysis is complete only if:

* `research-gap-analysis.md` exists;
* `paper-matrix.md` exists;
* one reading note exists per analyzed paper;
* the analyzed paper set is clearly listed;
* the scope is clearly defined;
* the taxonomy is explicit;
* papers are compared directly;
* candidate gaps are evaluated by strength;
* weak or risky directions are identified;
* unsupported claims are marked as uncertain;
* methodology gaps are considered;
* deployment gaps are considered;
* recommended next papers are listed when appropriate;
* in `memo+deck` mode, **the presentation deck exists** under `./slides/<topic-short-name>-gap-analysis/`, uses the Simple theme, compiles with XeLaTeX (or the failure is documented), and **its PDF has been visually inspected**;
* in `memo+deck` mode, the deck presents the synthesis (landscape, taxonomy, comparison, graded gaps, directions) — not one deck per paper, and not a shallow bullet dump (in `memo-only` mode, no deck is expected).

> Final quality bar: the result should help a researcher understand the landscape, avoid weak directions, and identify concrete next research questions — and the deck should be good enough to present the analysis in a seminar or demo.
> It should never feel like a shallow LLM-generated summary.

### What not to do

Do not: place gap analysis outside `./analysis/` or its deck outside `./slides/`; silently skip papers; generate shallow per-paper summaries instead of synthesis; produce one deck per paper instead of a single synthesis deck; copy large chunks of paper text; invent paper details not present in the source; invent citations; overclaim that a research gap is novel without evidence; or claim the deck is presentation-ready if it does not compile or its PDF has not been visually inspected.

---

## 13. Slides for the gap analysis (presentation deck)

By default, turn the finished memo into a presentation Beamer deck.
**Reuse the [`paper-beamer-deck`](../paper-beamer-deck/SKILL.md) skill for all Beamer mechanics and quality discipline** — do not reinvent them.
That skill governs: the Simple theme, the selectable visual-QA cadence (one-shot / risk-targeted / incremental) with its build-check-fix loop, the fail-on-warning log gate, and the **mandatory final PDF visual inspection** gate.
This section only specifies what is *different* for a gap-analysis deck: its content and structure.

### Setup

Create the deck directory and copy the starter files:

```bash
mkdir -p slides/<topic-short-name>-gap-analysis/figures
# gap-analysis content skeleton + speaker notes (from THIS skill):
cp skills/research-gap-analysis/templates/slides-main.tex  slides/<topic-short-name>-gap-analysis/main.tex
cp skills/research-gap-analysis/templates/slides-notes.md  slides/<topic-short-name>-gap-analysis/notes.md
# Beamer build machinery (reused from the paper-beamer-deck skill):
cp skills/paper-beamer-deck/templates/Makefile            slides/<topic-short-name>-gap-analysis/
```

The deck lives under `./slides/` (two levels below the workspace root), so the reused `Makefile` resolves the theme via `TEXINPUTS=../../` and the template's `\graphicspath{{figures/}{../../}}` finds local figures, exactly like a single-paper deck.
Build with `make`, and render pages for inspection with `skills/paper-beamer-deck/scripts/render_pdf_pages.py`.

### Deck structure (analysis-shaped, not paper-shaped)

Mirror the memo, one main idea per slide.
Suggested sections:

1. **Title** — topic; one-line takeaway; "N papers analyzed".
2. **Outline**.
3. **Scope & Executive Summary** — what is and isn't covered; the headline finding.
4. **Papers Analyzed** — compact list (title, authors, venue/year).
5. **Problem Landscape** — the shared problem; why it matters (prefer a diagram).
6. **Taxonomy** — the organizing dimensions, as a diagram or table.
7. **Cross-Paper Comparison** — a *simplified* matrix; split or trim columns so it stays readable on a slide (the full matrix stays in `paper-matrix.md`).
8. **Coverage** — what is already well covered vs. what is missing (a coverage map works well here).
9. **Candidate Gaps** — one slide per Strong gap (statement · why it matters · why unsolved · strength badge); group Medium/Weak gaps compactly.
10. **Most Promising Directions** — ranked, with what would make them publishable.
11. **Weak / Dangerous Directions** — tempting but weak, and why.
12. **Recommended Next Papers** — mark unverified entries "to verify".
13. **Final Takeaway** — what the set collectively implies.

### Slide quality rules (inherited)

All of `paper-beamer-deck`'s rules apply: slide purpose; slide-text-vs-speaker-notes (put long reasoning in `notes.md`); figure/table explanation; layout robustness and split-first; fail-on-overfull log checking; and **PDF visual inspection is mandatory**.
A big wide comparison matrix is the most common failure mode here — simplify or split it rather than shrinking the font.
Keep claim–evidence discipline and uncertainty marking on the slides too: don't let the deck overstate a gap the memo carefully qualified.
