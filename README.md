# Research Paper Autopilot Skills Bundle

[中文文档](README.zh-CN.md)

Research Paper Autopilot is an evidence-grounded Codex skills bundle for building research paper project packages from an idea to an auditable manuscript, reproducibility package, and submission checklist.

The main skill is `research-paper-autopilot`. It works as an orchestrator over the bundled specialist skills for literature search, gap analysis, experiment planning, experiment code, analysis, writing, review simulation, citation checking, figure/data support, integrity audit, and final packaging.

This is not a paper fabrication tool. It is designed to help produce research work only when claims are backed by real literature, real data, real code, real logs, and auditable results. When evidence is missing, the workflow must fall back to more search, more analysis, more experiments, claim downgrading, or a blocked/provisional package.

## What You Get

This repository currently bundles 58 installable Codex skills under `skills/`.

The bundle is centered on:

- `research-paper-autopilot`: the end-to-end project orchestrator.
- General research workflows: `academic-pipeline`, `deep-research`, `academic-paper`, `academic-paper-reviewer`, `academic-research-suite`, `automated-research-paper`.
- Literature and idea work: `literature-review`, `literature-survey-skill`, `research-gap-analysis`, `scientific-brainstorming`.
- CCF/AI paper workflows: idea optimization, literature search, experiment design, paper writing, review, integrity audit, submission checks, and rebuttal support.
- Nature/SCI workflows: literature search, citation support, figure planning, data availability, manuscript writing, polishing, reviewer simulation, and response drafting.
- Paper writing stack: `paper-spine` and its internal build, citation, LaTeX, research, rewrite, translation, audit, and update helpers.
- Evidence and verification tools: `citation-check-skill`, `statistical-analysis`, `papi-*` paper database/RAG helpers, and `papi-verify` for checking code against papers.
- Research artifact utilities: `pdf`, `scientific-visualization`, and `PaperBanana`.

The exact skill list is maintained in `skills_manifest.json`. Redistribution and provenance notes are in `THIRD_PARTY_SKILLS.md`.

## Who This Is For

Use this bundle if you want Codex to help with:

- Turning a rough research idea into a structured paper project.
- Building a literature-backed gap and contribution story.
- Designing experiments, baselines, metrics, ablations, and analysis plans.
- Generating project-specific experiment code scaffolds with configs, logs, result schemas, and reproducibility hooks.
- Auditing whether code, results, figures, citations, and manuscript claims support each other.
- Producing a full project directory that a human researcher can inspect, run, revise, and submit responsibly.

Do not use it to:

- Invent citations, datasets, results, p-values, reviewer outcomes, or submission status.
- Present unrun code as completed experiments.
- Convert unsupported claims into a submission-ready paper.
- Replace domain expert judgment, research ethics review, venue rules, or coauthor approval.

## Requirements

- Codex with local skill support.
- Python 3.9 or newer for the installer and validation scripts.
- A terminal that can run Python commands.

No package install is required for the bundle installer itself. Individual research projects created by the skills may require their own Python/R/LaTeX or domain packages depending on the task.

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-name>/<your-repo>.git
cd <your-repo>
```

Validate the bundle before installing:

```bash
python scripts/validate_bundle.py
```

Preview what would be installed:

```bash
python scripts/install.py --dry-run
```

Install all bundled skills into the default Codex skills directory:

```bash
python scripts/install.py
```

By default, skills are copied into:

```text
~/.codex/skills
```

On Windows, this usually resolves to:

```text
C:\Users\<you>\.codex\skills
```

### Install Options

Install to a custom Codex home:

```bash
python scripts/install.py --codex-home /path/to/.codex
```

Install to an explicit skills directory:

```bash
python scripts/install.py --skills-dir /path/to/.codex/skills
```

Install only the main autopilot skill:

```bash
python scripts/install.py --only research-paper-autopilot
```

Install several selected skills:

```bash
python scripts/install.py --only research-paper-autopilot deep-research academic-paper citation-check-skill
```

Replace already installed bundled skills:

```bash
python scripts/install.py --force
```

Preview a replacement without changing files:

```bash
python scripts/install.py --dry-run --force
```

After installation, start a new Codex session if the skills do not appear immediately.

## Quick Start

After installing, ask Codex:

```text
Use $research-paper-autopilot to turn my research idea into an evidence-grounded paper project package.
```

Chinese prompts also work:

```text
从 idea 到投稿，帮我做一个基于真实文献和真实实验结果的论文项目包。
```

```text
帮我做 CCF/SCI 论文全流程，包含文献、实验、审稿模拟和复现材料。
```

```text
审核我的论文项目：检查引用、实验结果、代码、图表和正文 claim 是否互相支撑。
```

The default interaction language follows the user. Unless the target venue or the user requires Chinese, paper drafts and submission-facing materials default to English.

## Recommended Input

For the best result, provide as many of these as possible:

- Research idea or draft title.
- Target field, venue, journal, or conference type.
- Existing files or folders: notes, PDFs, BibTeX, datasets, code, logs, previous drafts.
- Whether data already exists and whether experiments have already been run.
- Expected method family, baseline models, metrics, or constraints.
- Deadline and compute budget.
- Any claims that must be proven, weakened, or avoided.

Minimal input is allowed, but the skill will mark unsupported parts as open work instead of pretending they are finished.

## Default Project Output

`research-paper-autopilot` is designed to create or maintain a project directory like this:

```text
paper-project/
  PROGRESS.md
  RESTRICTS.yaml
  literature/
  plans/
  code/
    README.md
    config.yaml
    run_experiments.py
    analyze_results.py
  results/
  figures/
  paper/
  submission/
  audit/
    audit_report.json
    claim_evidence_map.json
    code_review_packet.md
    code_review_ledger.md
```

Common artifacts include:

- A stage-by-stage plan and progress log.
- Literature search notes and citation support.
- Gap analysis and contribution framing.
- Method and experiment design.
- Experiment code scaffold with config, seed, logs, and result output conventions.
- Raw result files, summaries, figures, and claim-to-evidence mappings.
- Draft manuscript sections.
- Simulated reviewer feedback and revision ledger.
- Integrity audit report.
- Reproducibility and submission checklists.

## Workflow

The main workflow is a state machine:

```text
Intake
-> Track Detect
-> Literature
-> Gap
-> Method / Experiment
-> Execution / Analysis
-> Multi-Agent Code Review
-> Writing
-> Review
-> Revision
-> Integrity Audit
-> Submission Package
```

Each stage records:

- `stage`: current stage name.
- `inputs`: files, notes, data, and user requirements used by the stage.
- `actions`: what was done.
- `artifacts`: files created or updated.
- `evidence`: citations, logs, result files, or review records supporting the stage.
- `decision`: `PROCEED`, `REFINE`, `PIVOT`, or `BLOCKED`.
- `next`: the next action or repair route.

## Track Routing

The orchestrator detects the paper track and activates the matching specialist skills and quality gates.

Typical tracks:

- `CCF_AI`: AI, ML, systems, data mining, security, NLP, CV, or related conference-style projects.
- `NATURE_SCI`: high-impact science or interdisciplinary journal-style projects.
- `REVIEW_SURVEY`: literature review, survey, taxonomy, or perspective articles.
- `GENERIC_RESEARCH`: general research reports or papers that do not match a specialized track.

Routing should produce:

- `primary_track`: the main path.
- `secondary_tracks`: extra gate sets if the project overlaps multiple paper styles.
- `active_gate_sets`: the quality gates that must pass before the project can move forward.

Mixed projects are allowed. For example, a biomedical AI project may use both CCF/AI experiment gates and Nature/SCI figure/data availability gates.

## Evidence and Anti-Fabrication Rules

The skill must not fabricate:

- Literature, citations, DOIs, paper titles, author lists, or quotations.
- Data, datasets, sample sizes, labels, or collection procedures.
- Experimental results, metrics, p-values, confidence intervals, or logs.
- Reviewer comments, acceptance status, submission status, or venue decisions.
- Repository, environment, or compute details that were not actually observed.

If evidence is missing, the correct behavior is one of:

- Search for more literature.
- Ask for or locate real data.
- Generate an experiment or analysis plan instead of claiming results.
- Run code and archive logs/results when the environment permits.
- Downgrade wording from a result claim to a hypothesis or plan.
- Mark the project `BLOCKED` or `PROVISIONAL`.

No stage should mark a package as submission-ready when a hard evidence gate is still open.

## Experiment Code Standard

The autopilot includes a dedicated experiment-code standard. Generated or revised code should feel like maintainable research project code, not a generic template.

Required properties:

- Project-specific file names, function names, config fields, log fields, metrics, and result schemas.
- Explicit config loading and config snapshots.
- Seed handling for legal random initialization, data splitting, bootstrap, or simulation.
- Structured logs with command line, time estimate, run status, and output paths.
- Raw outputs and summary outputs saved to disk.
- NaN/Inf checks and failed/crashed run detection.
- Baseline, ablation, and metric hooks when relevant.
- Clear run commands in `code/README.md`.

Blocked patterns:

- Mock results presented as experiments.
- Hardcoded accuracy, F1, p-values, or paper-ready numbers.
- Randomly generated curves or trends used as evidence.
- Empty universal helper functions unrelated to the research task.
- Mechanical names such as `process_data`, `run_model`, and `calculate_metric` throughout the project.
- Over-commented code that explains obvious operations while missing research assumptions.
- One giant script with no project structure when the task needs reproducibility.

The priority is correctness first, then reproducibility, then natural maintainability. Style must never override evidence.

## Mandatory Multi-Agent Code Review Gate

Any project with experiment code, analysis code, result files, statistical claims, or metric-based manuscript claims must pass a mandatory six-role code review before results can enter the paper.

This is not optional and cannot be replaced by a single self-check.

The six required reviewer roles are:

- Algorithm Reviewer: checks whether implementation matches the method, equations, pseudocode, and manuscript description.
- Experiment Design Reviewer: checks datasets, baselines, ablations, budgets, and fairness of comparisons.
- Data Leakage Reviewer: checks splits, labels, preprocessing, caches, tuning sets, and test contamination risk.
- Metrics & Statistics Reviewer: checks metric definitions, aggregation, statistical tests, confidence intervals, and p-values.
- Reproducibility Reviewer: checks seeds, config, logs, environment, output paths, and run commands.
- Code Quality Reviewer: checks maintainability, naming, error handling, project fit, and non-template code quality.

The review protocol is:

1. Freeze current code and results.
2. Run the static audit.
3. Generate `audit/code_review_packet.md` with `prepare_code_review_packet.py`.
4. Run six independent reviewer agents or sessions.
5. Record each review in `audit/code_review_ledger.md` or `.json`.
6. Fix all unresolved `BLOCK` items.
7. Re-run audit before writing result claims into the manuscript.

The ledger must include:

- Reviewer role.
- `PASS`, `WARN`, or `BLOCK`.
- Evidence locations.
- Findings.
- Required fixes.
- Reviewer run/session ID.
- `packet_sha256` matching the current review packet.

Hard blocks include:

- Missing ledger.
- Fewer than six required roles.
- Duplicate or conflicting roles.
- Empty `PASS` entries.
- Evidence listed as `TBD`, `none`, or other placeholders.
- Unresolved `BLOCK`.
- `WARN` without accepted rationale or follow-up plan.
- Stale packet hash after code/results changed.

If the environment cannot run multiple independent reviewers, the stage must be recorded as `BLOCKED`. It must not silently downgrade to a single-agent review.

## Result Artifact Schema

Experiment or analysis results should be stored as auditable artifacts, not only as prose.

A result package should include:

- Raw run outputs.
- Summary table or metrics file.
- Config snapshot.
- Seed.
- Command line.
- Log path.
- Code hash.
- Result hash.
- Environment metadata.
- Git metadata when available.
- Run status such as `completed`, `failed`, or `crashed`.

The audit blocks malformed JSON/CSV, NaN/Inf values, failed runs used as evidence, stale summaries, and p-value/statistical claims that are not backed by archived result/code/log/audit artifacts.

## Integrity Audit

The audit checks whether the project is internally consistent.

It looks for:

- Manuscript claims without citations or result support.
- Citations that are missing, malformed, or unsupported.
- Numerical claims that do not match result artifacts.
- Figures or tables without source data or generation scripts.
- Experiment sections written before code/results/reviews are complete.
- Code quality issues and suspicious template patterns.
- Missing multi-agent code review packet or ledger.
- Submission checklist gaps.

Possible outcomes:

- `PROCEED`: evidence is sufficient for the next stage.
- `REFINE`: work exists but needs revision.
- `PIVOT`: the current idea or method should change.
- `BLOCKED`: the project must not move forward as a completed paper package.

## Useful Commands

Validate the bundle:

```bash
python scripts/validate_bundle.py
```

Preview installation:

```bash
python scripts/install.py --dry-run
```

Install only the autopilot:

```bash
python scripts/install.py --only research-paper-autopilot
```

Compile the autopilot scripts directly:

```bash
python -m py_compile \
  skills/research-paper-autopilot/scripts/scaffold_autopilot_project.py \
  skills/research-paper-autopilot/scripts/prepare_code_review_packet.py \
  skills/research-paper-autopilot/scripts/audit_autopilot_project.py
```

On Windows PowerShell, use:

```powershell
python -m py_compile `
  skills\research-paper-autopilot\scripts\scaffold_autopilot_project.py `
  skills\research-paper-autopilot\scripts\prepare_code_review_packet.py `
  skills\research-paper-autopilot\scripts\audit_autopilot_project.py
```

## Repository Layout

```text
.
├─ .codex-plugin/
│  └─ plugin.json
├─ scripts/
│  ├─ install.py
│  └─ validate_bundle.py
├─ skills/
│  ├─ research-paper-autopilot/
│  └─ ...
├─ skills_manifest.json
├─ THIRD_PARTY_SKILLS.md
├─ README.md
├─ README.zh-CN.md
└─ LICENSE
```

Inside the main skill:

```text
skills/research-paper-autopilot/
├─ SKILL.md
├─ agents/
├─ references/
│  ├─ anti-fabrication.md
│  ├─ artifact-contract.md
│  ├─ experiment-code-standard.md
│  ├─ multi-agent-code-review.md
│  ├─ orchestration.md
│  ├─ quality-gates.md
│  └─ track-routing.md
└─ scripts/
   ├─ scaffold_autopilot_project.py
   ├─ prepare_code_review_packet.py
   └─ audit_autopilot_project.py
```

## Updating

Pull the latest repository changes:

```bash
git pull
```

Validate:

```bash
python scripts/validate_bundle.py
```

Reinstall:

```bash
python scripts/install.py --force
```

If you maintain your own local versions of some skills, avoid `--force` or install only selected skills with `--only`.

## Publishing Checklist

Before publishing this repository publicly:

- Review `THIRD_PARTY_SKILLS.md`.
- Confirm redistribution rights for every vendored skill.
- Remove private notes, tokens, credentials, local datasets, and unpublished sensitive material.
- Run `python scripts/validate_bundle.py`.
- Run `python scripts/install.py --dry-run`.
- Test install in a clean Codex home if possible.
- Start a new Codex session and verify `research-paper-autopilot` appears in the available skills list.

## Troubleshooting

### Codex does not see the skills

Check the install destination printed by `scripts/install.py`. It should end with `.codex/skills`. Start a new Codex session after installation.

### The installer says a skill was skipped

The destination directory already exists. Use `--force` to replace it, or install into a different directory with `--skills-dir`.

### I only want the main skill

Run:

```bash
python scripts/install.py --only research-paper-autopilot
```

The main skill is most useful with the supporting skills installed, but it can still be inspected or developed alone.

### The autopilot blocks my project

That usually means a required evidence gate failed. Check `audit/audit_report.json`, `PROGRESS.md`, and any stage plan files. A block is expected when literature, code, results, citations, logs, or multi-agent code review records are missing.

### The code review gate blocks my results

Generate a packet, run all six required reviewer roles independently, fix unresolved `BLOCK` findings, then regenerate the packet and ledger if code or results changed.

### Chinese text looks garbled in the terminal

The Markdown files are UTF-8. If your terminal displays garbled text, switch the terminal encoding to UTF-8 or inspect the file in an editor that supports UTF-8.

## License and Third-Party Notice

The top-level `LICENSE` covers files authored specifically for this bundle. Vendored skills may have their own upstream licenses or redistribution terms.

Before public redistribution, review `THIRD_PARTY_SKILLS.md` and confirm that you have the right to publish each bundled skill.
