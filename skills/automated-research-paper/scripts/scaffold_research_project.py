#!/usr/bin/env python3
"""Create a reproducible research paper project scaffold."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


STAGES = [
    "01_topic_init",
    "02_problem_decompose",
    "03_search_strategy",
    "04_literature_collect",
    "05_literature_screen_gate",
    "06_knowledge_extract",
    "07_synthesis",
    "08_hypothesis_gen",
    "09_theoretical_bounds",
    "10_experiment_design_gate",
    "11_code_generation",
    "12_resource_planning",
    "13_pilot_run",
    "14_experiment_run",
    "15_iterative_refine",
    "16_result_analysis",
    "17_research_decision",
    "18_paper_outline",
    "19_paper_draft",
    "20_peer_review",
    "21_paper_revision",
    "22_quality_gate",
    "23_knowledge_archive",
    "24_export_publish",
    "25_citation_verify",
    "26_external_review",
    "27_rebuttal",
]


def write_if_missing(path: Path, text: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Project root to create")
    parser.add_argument("--topic", required=True, help="Research topic")
    parser.add_argument("--project-name", default="research-project")
    parser.add_argument("--target-venue", default="TBD")
    parser.add_argument("--deadline", default="TBD")
    parser.add_argument("--page-limit", default="TBD")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    created = []

    dirs = [
        "code",
        "data",
        "docs",
        "literature",
        "logs",
        "paper/mypaper/figures",
        "paper/mypaper/sections",
        "plans",
        "results",
    ]
    for rel in dirs:
        path = root / rel
        path.mkdir(parents=True, exist_ok=True)
        created.append(str(path))

    generated = dt.datetime.now(dt.timezone.utc).isoformat()

    progress = f"""# PROGRESS

Project: {args.project_name}
Topic: {args.topic}
Target venue: {args.target_venue}
Deadline: {args.deadline}
Page limit: {args.page_limit}
Generated: {generated}

## State Machine

Current version: v0
Current stage: TOPIC_INIT
Decision: not_started

Loop rules:
- REFINE returns to experiment design, code repair, or analysis.
- PIVOT returns to hypothesis generation or paper outline.
- Every loop increments the version and preserves prior artifacts.

## v0 - Scaffold - {generated}

Status: completed
Inputs:
- Topic: {args.topic}
Artifacts:
- Project layout
- RESTRICTS.yaml
- MEGA_PROMPT.md
- Stage plan placeholders
Decision:
- Ready for TOPIC_INIT.
Next:
- Fill docs with the user's research concept and constraints.
"""
    if write_if_missing(root / "PROGRESS.md", progress):
        created.append(str(root / "PROGRESS.md"))

    mega_prompt = f"""# MEGA_PROMPT

This project uses the `automated-research-paper` skill.

Topic: {args.topic}
Target venue: {args.target_venue}
Deadline: {args.deadline}
Page limit: {args.page_limit}

Hard rule: generate only evidence-grounded research artifacts. Literature must come from real sources; experiments must be runnable and logged; paper claims must match results, code, and citations.

Before each stage:
1. Create or update the corresponding file in `plans/`.
2. Read `RESTRICTS.yaml`.
3. Record inputs, actions, artifacts, evidence, decision, and next step in `PROGRESS.md`.
"""
    if write_if_missing(root / "MEGA_PROMPT.md", mega_prompt):
        created.append(str(root / "MEGA_PROMPT.md"))

    restricts = f"""topic:
  statement: "{args.topic}"
  prohibit:
    - Treating environment setup or dependency failures as research contributions.
    - Presenting debugging logs or system errors as experimental findings.
    - Drifting to tangential topics.
evidence:
  literature_must_be_real: true
  experiments_must_be_run: true
  unsupported_claims_block_submission: true
experiments:
  require_pilot: true
  require_time_estimate: true
  require_convergence_checks: true
  require_ablations_for_claimed_components: true
  forbid_fake_random_curves: true
writing:
  core_innovations_max: 2
  require_figure_1_plan: true
  compiled_pdf_page_limit: "{args.page_limit}"
"""
    if write_if_missing(root / "RESTRICTS.yaml", restricts):
        created.append(str(root / "RESTRICTS.yaml"))

    doc_templates = {
        "docs/overall_concept.md": "# Overall Concept\n\nFill in the paper thesis, target audience, contributions, and outline.\n",
        "docs/experiment_plan.md": "# Experiment Plan\n\nFill in datasets, baselines, proposed method, ablations, metrics, and compute budget.\n",
        "docs/literature_and_questions.md": "# Literature and Reviewer Questions\n\nFill in related work clusters, likely reviewer objections, and defense evidence.\n",
        "code/README.md": "# Experiment Code\n\nDocument commands, dependencies, configs, and expected outputs.\n",
        "paper/mypaper/main.tex": "\\documentclass{article}\n\\begin{document}\n\\title{TBD}\n\\maketitle\n\\input{sections/introduction}\n\\input{sections/related_work}\n\\input{sections/method}\n\\input{sections/experiments}\n\\input{sections/results}\n\\input{sections/discussion}\n\\input{sections/limitations}\n\\input{sections/conclusion}\n\\end{document}\n",
    }
    for rel, text in doc_templates.items():
        path = root / rel
        if write_if_missing(path, text):
            created.append(str(path))

    for section in [
        "introduction",
        "related_work",
        "method",
        "experiments",
        "results",
        "discussion",
        "limitations",
        "conclusion",
    ]:
        path = root / "paper" / "mypaper" / "sections" / f"{section}.tex"
        if write_if_missing(path, f"% {section.replace('_', ' ').title()}\n"):
            created.append(str(path))

    for stage in STAGES:
        text = f"""# {stage}

Version: v1
Status: planned

## Goals

- TBD

## Inputs

- `MEGA_PROMPT.md`
- `RESTRICTS.yaml`

## Tasks

- TBD

## Gate Criteria

- TBD

## Expected Artifacts

- TBD
"""
        path = root / "plans" / f"{stage}.md"
        if write_if_missing(path, text):
            created.append(str(path))

    manifest = {
        "project_name": args.project_name,
        "topic": args.topic,
        "target_venue": args.target_venue,
        "deadline": args.deadline,
        "page_limit": args.page_limit,
        "generated": generated,
    }
    manifest_path = root / "research_manifest.json"
    if write_if_missing(manifest_path, json.dumps(manifest, indent=2) + "\n"):
        created.append(str(manifest_path))

    print(json.dumps({"root": str(root), "created": created}, indent=2))


if __name__ == "__main__":
    main()
