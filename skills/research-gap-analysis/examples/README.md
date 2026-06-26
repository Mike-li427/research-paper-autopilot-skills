# Example: a multi-paper research-gap analysis

A worked, end-to-end walkthrough of the `research-gap-analysis` skill.
Illustrative — the content cells are sketched, not filled.
The accelerator-virtualization topic below is just a sample; the skill is field-agnostic (set your area in the workspace `domain.md`).

## Scenario

The user says:

> "Compare `papers/accel-virt-A.pdf`, `papers/accel-virt-B.pdf`, and `papers/sched-C.pdf` and tell me what research gaps remain."

Topic short name: `accelerator-virtualization`.

## Step 1 — Understand each paper, then outline the comparison

Read all three.
For each, note problem / contribution / method / evaluation / limitations.
Normalize terminology (e.g. "resource abstraction" vs. "device multiplexing" → one term).
Then outline the intended comparison dimensions, likely candidate gaps, and claims that need verification.

## Step 2 — Scaffold from templates

```bash
mkdir -p analysis/accelerator-virtualization/reading-notes
mkdir -p analysis/accelerator-virtualization/figures
cp skills/research-gap-analysis/templates/research-gap-analysis.md analysis/accelerator-virtualization/
cp skills/research-gap-analysis/templates/paper-matrix.md          analysis/accelerator-virtualization/
for p in accel-virt-A accel-virt-B sched-C; do
  cp skills/research-gap-analysis/templates/reading-note.md \
     analysis/accelerator-virtualization/reading-notes/$p.md
done
```

Layout:

```text
analysis/accelerator-virtualization/
├── research-gap-analysis.md
├── paper-matrix.md
├── reading-notes/
│   ├── accel-virt-A.md
│   ├── accel-virt-B.md
│   └── sched-C.md
└── figures/
```

## Step 3 — Build the matrix (forces a direct comparison)

Fill `paper-matrix.md` so overlaps and holes become visible.
Sketch:

| Paper | Problem | Target system | Workload | Mechanism | …does NOT cover |
|-------|---------|---------------|----------|-----------|-----------------|
| A | static accel sharing | edge SoC | DNN inference | space partition | multi-tenant, real-time |
| B | dynamic scheduling | datacenter | DNN inference | time-multiplex | energy/area, robotics |
| C | RT scheduling | embedded | mixed RT tasks | EDF variant | accelerator-aware placement |

The right-most column feeds the candidate gaps.

## Step 4 — Draft the memo with graded gaps

In `research-gap-analysis.md`, synthesize **across** the papers (not one-by-one).
Classify each gap and rate it:

- **Implied gap (Strong):** none study accelerator-aware *real-time* scheduling under *multi-tenant* contention — A ignores RT, C ignores accelerators.
  Evaluable on an edge SoC with mixed DNN+RT workloads.
- **Methodology gap (Medium):** all three report throughput; none report tail latency or deadline-miss rate.
- **Opportunity gap (Weak):** "combine A+B+C" — too broad, weakly motivated as stated.

Ground each claim (section/figure/table); mark uncertain ones "needs verification against broader related work".
Don't overclaim novelty.

## Step 5 — Build the presentation deck (default output)

Turn the memo into a Beamer deck for the seminar/demo.
Reuse the `paper-beamer-deck` build machinery (theme, Makefile, log gate, PDF inspection); the content is analysis-shaped (see `research-gap-analysis/SKILL.md` §13).

```bash
mkdir -p slides/accelerator-virtualization-gap-analysis/figures
cp skills/research-gap-analysis/templates/slides-main.tex \
   slides/accelerator-virtualization-gap-analysis/main.tex
cp skills/research-gap-analysis/templates/slides-notes.md \
   slides/accelerator-virtualization-gap-analysis/notes.md
cp skills/paper-beamer-deck/templates/Makefile \
   slides/accelerator-virtualization-gap-analysis/

cd slides/accelerator-virtualization-gap-analysis
make                        # xelatex ×2 + fail-on-warning log gate
python3 ../../skills/paper-beamer-deck/scripts/render_pdf_pages.py main.pdf --pages 1-12
# -> open the PNGs and LOOK. The simplified comparison matrix is the usual trouble
#    spot: split or trim it rather than shrinking the font.
```

The deck presents the synthesis: Scope/Summary → Papers → Landscape → Taxonomy → (simplified) Comparison → Coverage → graded Gaps → Directions → Next Papers → Takeaway.
One synthesis deck for the whole analysis — not one deck per paper.
Skip this step only if the user asked for memo-only output.

## Step 6 — Report

State: papers analyzed; memo output path; deck output path + slide count; compilation status; visual inspection status; major candidate gaps (with strength); uncertain or weakly supported claims; recommended next steps / next papers (mark unverified ones "to verify").
