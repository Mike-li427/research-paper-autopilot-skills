---
name: research-paper-autopilot
description: Orchestrate an evidence-grounded, end-to-end research-to-paper project package from idea to auditable manuscript, reproducibility pack, and submission materials. Use when the user asks for research-to-publication, idea-to-paper, literature-to-experiment-to-paper pipelines, submission packages, reproducibility packs, full research workflows, SCI/CCF paper projects, 全自动写论文但必须基于真实文献和真实数据/实验结果, 从idea到投稿, 科研全流程, 高水平论文项目包, 从选题到成稿, 投稿材料与复现包, or 自动生成可审计论文项目包.
---

# Research Paper Autopilot

## Core Rule

Run a research production workflow, not a paper-fabrication workflow. Never invent literature, data, experiments, results, citations, p-values, reviewer outcomes, or submission status. If evidence is missing, route back to literature, method design, experiment/analysis, citation support, or downgrade the claim.

## Quick Start

1. Intake the research idea, target field, venue/journal, deadline, existing material paths, data/code/results status, and desired output language.
2. If no compatible project exists, run `scripts/scaffold_autopilot_project.py` to create the project package.
3. Read `PROGRESS.md`, `RESTRICTS.yaml`, available docs, literature records, code, results, and paper files before changing claims or drafting text.
4. Detect the track with `references/track-routing.md`: CCF/AI, Nature/SCI, review/survey, or generic academic.
5. Run the state machine in `references/orchestration.md`, applying the gates in `references/quality-gates.md`.
6. Before generating or repairing experiment code, read `references/experiment-code-standard.md`.
7. Before transferring any experiment or analysis result into the paper, run the mandatory multi-agent code review in `references/multi-agent-code-review.md`.
8. Before finalizing, run `scripts/audit_autopilot_project.py` and treat `BLOCK` findings as mandatory repair work.

Default interaction is in the user's language. Unless the user explicitly requests a Chinese manuscript or a target venue requires Chinese, write manuscripts, abstracts, cover letters, and submission materials in English.

## Orchestration

Use this skill as the top-level controller. Load existing specialist skills only when their stage is active:

- General pipeline: use `academic-pipeline`, `deep-research`, `academic-paper`, and `academic-paper-reviewer`.
- Reproducible auto-projects: use `automated-research-paper`.
- Paper architecture and prose: use `paper-spine`, `paper-writing`, `nature-writing`, and `nature-polishing`.
- CCF/AI conference work: use `ccf-idea-optimizer`, `ccf-literature-searcher`, `ccf-experiment-designer`, `ccf-paper-writer`, `ccf-paper-reviewer`, `ccf-integrity-auditor`, `ccf-submission-checker`, and `ccf-rebuttal-writer`.
- Nature/SCI work: use `nature-academic-search`, `nature-citation`, `nature-figure`, `nature-data`, `nature-reviewer`, and `nature-response`.
- Personal paper library/RAG: use `papi`, `papi-ask`, `papi-ground`, `papi-compare`, `papi-curate`, and `papi-verify`.
- Citation and hallucination checks: use `citation-check-skill`.

When activating a specialist stage, load the named specialist skill through the normal Codex skill mechanism before acting. Do not treat these names as informal labels.

## Default Outputs

Produce a complete project package unless the user asks for a narrower artifact:

```text
<project>/
  PROGRESS.md
  RESTRICTS.yaml
  research_manifest.json
  docs/
  literature/
  plans/
  code/
  data/
  results/
  paper/
  figures/
  submission/
  audit/
  logs/
```

Each stage must record `stage`, `inputs`, `actions`, `artifacts`, `evidence`, `decision`, and `next`. Valid decisions are `PROCEED`, `REFINE`, `PIVOT`, and `BLOCKED`.

## Hard Evidence Rules

- Treat `HARD_BLOCK` findings as non-deferable for submission-ready outputs.
- Permit provisional drafts only when they visibly mark unsupported or unreviewed claims as provisional.
- Require packet hashes, artifact hashes, and independent reviewer run IDs before experiment results can enter manuscript claims.
- Prefer removing or weakening a claim over inventing support.

## References

- Read `references/orchestration.md` for the state machine, dispatch table, and loop rules.
- Read `references/track-routing.md` before choosing a specialist path.
- Read `references/quality-gates.md` before drafting, finalizing, or claiming submission readiness.
- Read `references/experiment-code-standard.md` before writing code, experiment scripts, analysis scripts, or reproducibility commands.
- Read `references/multi-agent-code-review.md` before interpreting results, drafting result claims, or auditing any project with experiment/analysis code.
- Read `references/artifact-contract.md` before creating or auditing a project package.
- Read `references/anti-fabrication.md` whenever evidence is weak, missing, or contradictory.

## Scripts

- `scripts/scaffold_autopilot_project.py`: create the full project structure, manifest, restrictions, progress log, stage plans, code templates, and audit templates.
- `scripts/prepare_code_review_packet.py`: collect redacted code, configs, logs, results, claim-evidence map, hashes, and manuscript experiment passages for mandatory multi-agent code review.
- `scripts/audit_autopilot_project.py`: check whether literature, citations, results, figures, reviewer ledgers, and manuscript claims support one another.
