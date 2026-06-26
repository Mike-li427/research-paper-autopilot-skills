---
name: automated-research-paper
description: Build and run an evidence-grounded automated research paper pipeline. Use when Codex is asked to turn a research idea into a reproducible paper project, scaffold a conference paper workflow, conduct real literature discovery, design and run truthful experiments, audit method-evidence consistency, write or revise LaTeX/Markdown papers, or convert a large "AI writes my paper" prompt into a disciplined research skill.
---

# Automated Research Paper

## Core Rule

Treat this as a research automation workflow, not a paper-fabrication workflow. Never invent literature, datasets, results, baselines, p-values, capabilities, or claims. If evidence is missing, say what is missing and route the project back to literature, experiment design, or implementation.

## Quick Start

1. Identify the topic, target venue, deadline, page limit, existing docs, codebase paths, data paths, and claimed contributions.
2. If the project folder is not structured, run `scripts/scaffold_research_project.py` to create the reproducible layout.
3. Read `MEGA_PROMPT.md`, `RESTRICTS.yaml`, `docs/*.md`, and any project/source documentation before changing experiments or paper text.
4. Use real retrieval APIs for literature. Use LLMs only to plan, rank, summarize, and critique records returned by real sources.
5. Run a pilot before any main experiment. Log `TIME_ESTIMATE: <seconds>` and scale conditions/seeds to the actual compute budget.
6. Before writing or revising the paper, audit that every major claim is backed by code, logs, result files, citations, or source documentation.

## Project Layout

Use this layout unless the user provides an existing compatible structure:

```text
<project>-paper/
  MEGA_PROMPT.md
  RESTRICTS.yaml
  PROGRESS.md
  code/
  data/
  docs/
  literature/
  paper/
    <venue-template>/
    mypaper/
      figures/
      sections/
      main.tex
  plans/
  results/
  logs/
```

Use `PROGRESS.md` as the state machine log. Record stage, version, evidence, decision, next loop target, and changed artifacts after every stage.

## Pipeline

Run the pipeline as gates and loops, not as a rigid checklist:

1. Define: topic, scope, research questions, success criteria, hard topic boundary.
2. Literature: search strategy, real API collection, screening, knowledge cards.
3. Synthesis: clusters, gaps, falsifiable hypotheses, theory or complexity sketch.
4. Experiment design: datasets, baselines, proposed method, ablations, metrics, compute budget.
5. Implementation: deterministic runnable code with real objectives and convergence criteria.
6. Execution: pilot, time estimate, main runs, runtime/NaN/Inf repair, result archival.
7. Analysis: exact metrics, uncertainty, ablations, limitations, decision to proceed/refine/pivot.
8. Writing: outline, Figure 1 concept, draft, review, revision.
9. Audit: quality gate, citation verification, third-party style review, rebuttal-driven refinements.

Read `references/pipeline.md` when a project needs the full stage map or loop rules.

## Gates

Pause or self-repair at these gates:

- Literature gate: fewer than 30 relevant real records, missing DOI/arXiv/source URLs where available, or obvious off-topic padding.
- Experiment gate: no pilot, no time estimate, no ablations for named components, weak or untuned baselines, missing convergence criteria, missing logs.
- Evidence gate: paper claims do not match results, logs, code, citations, or source documentation.
- Quality gate: paper drifts away from the stated topic, treats environment setup as a contribution, overclaims beyond evidence, or cannot fit the venue format.

## Literature Rules

Prefer OpenAlex, Semantic Scholar, arXiv, Crossref, venue proceedings, and official project documentation. Do not ask an LLM to generate paper metadata. For each kept paper preserve source URL plus DOI, arXiv id, venue, year, and cite key when available.

Use:

```bash
python scripts/collect_literature.py --topic "<topic>" --out literature/candidates.jsonl --year-min 2018 --limit-per-source 40
```

Then screen records for topical relevance and quality. LLM summaries must be grounded in the returned title, abstract, metadata, and accessible paper text when available.

## Experiment Rules

Use real algorithms and real metrics. Synthetic data is acceptable only when the paper's claim is explicitly about controlled algorithmic behavior and the limitation is stated.

Required implementation properties:

- Deterministic seeds and logged configuration.
- A pilot condition before the main sweep.
- `TIME_ESTIMATE: <seconds>` printed or logged before full execution.
- Resource guard that saves partial results before the budget is exhausted.
- Convergence stopping criteria for iterative algorithms.
- NaN/Inf checks that trace and fix the root cause rather than hiding failures.
- Ablations for every effective component claimed in the paper.
- Baselines tuned with comparable care.

Read `references/anti-fabrication.md` and `references/experiment-code-standard.md` before generating or repairing experiment code.

## Writing Rules

Before drafting, re-read `RESTRICTS.yaml`, the final experiment analysis, and `references/writing-review.md`.

Write the paper around one or two core innovations. Draft Figure 1 before the full paper and include a detailed image-generation prompt as a LaTeX comment if the user wants later visual generation. Keep claims narrow, quantitative, and traceable.

Use the venue template in `paper/<venue-template>/` and write the submission in `paper/mypaper/`. Put major sections in separate files under `paper/mypaper/sections/`.

## Evidence Audit

Run the audit script before final revision:

```bash
python scripts/evidence_audit.py --paper paper/mypaper --results results --literature literature/candidates.jsonl --out results/evidence_audit.json
```

Treat `CRITICAL` findings as blockers. Route back to experiments, citations, or paper revision before final export.

## Useful Scripts

- `scripts/scaffold_research_project.py`: create the project layout, `RESTRICTS.yaml`, `PROGRESS.md`, and stage plan placeholders.
- `scripts/collect_literature.py`: collect real candidate records from public scholarly APIs into JSONL.
- `scripts/evidence_audit.py`: perform heuristic checks for unsupported numeric claims, missing citations, and result-paper inconsistencies.

## Failure Policy

If the requested automation would fabricate science, do the nearest honest thing: scaffold the project, identify missing evidence, run feasible pilot experiments, or produce a research plan with explicit blockers. Never present a generated paper as submission-ready unless the evidence gate passes.
