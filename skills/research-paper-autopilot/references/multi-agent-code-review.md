# Mandatory Multi-Agent Code Review

Use this reference whenever a project has experiment code, analysis code, result files, or manuscript claims about experiments, metrics, coefficients, statistical tests, or quantitative findings.

## Core Rule

Multi-agent code review is a mandatory gate. It is not optional, and it does not depend on the user asking for it. Do not move experiment results into paper claims, tables, figures, abstracts, or conclusions until this gate passes.

If the current runtime cannot start independent review agents, mark the stage `BLOCKED`. A single-agent role-play review is useful preparation, but it does not satisfy this gate.

## Required Roles

All six roles are required:

1. `Algorithm Reviewer`: verify that formulas, pseudocode, model logic, estimators, and implementation match the paper's method.
2. `Experiment Design Reviewer`: verify datasets, baselines, ablations, hyperparameter budgets, and fairness of comparison.
3. `Data Leakage Reviewer`: verify splits, labels, preprocessing, caching, feature construction, tuning sets, and test-set isolation.
4. `Metrics & Statistics Reviewer`: verify metric definitions, aggregation, uncertainty, statistical tests, p-values, confidence intervals, and table values.
5. `Reproducibility Reviewer`: verify seeds, configs, environment notes, commands, logs, result persistence, and rerun path.
6. `Code Quality Reviewer`: verify structure, naming, maintainability, non-template style, error handling, and finite-value checks.

## Required Inputs

Before review, run:

```bash
python scripts/prepare_code_review_packet.py --root <project>
```

Reviewers must receive `audit/code_review_packet.md`, the current `audit/audit_report.json` when available, and any project-specific instructions. Reviewers should not invent missing logs, results, or test outcomes.

## Packet Binding

The packet must include:

- `packet_sha256`
- generated timestamp
- artifact manifest with file paths, sizes, mtimes, and SHA-256 hashes
- truncation inventory
- redaction inventory
- current audit report when available

Any code, result, log, paper, or claim-evidence-map change after packet generation invalidates the ledger. Regenerate the packet and rerun all required roles.

## Ledger Contract

Write the final review record to `audit/code_review_ledger.md` or `audit/code_review_ledger.json`.

Each role must include:

- `Role`: one of the required role names.
- `Status`: `PASS`, `WARN`, or `BLOCK`.
- `Reviewer`: identifier for the independent reviewing agent.
- `Reviewer run id`: independent agent/thread/session/run identifier.
- `Packet SHA256`: exact hash from the reviewed `audit/code_review_packet.md`.
- `Evidence`: non-placeholder file paths, line references, result files, logs, commands, or hashes inspected.
- `Findings`: concrete issues or confirmations.
- `Required fixes`: mandatory changes for `BLOCK`; use `None` only for `PASS` after evidence and findings are substantive.
- `Accepted rationale`: required for every `WARN`, explaining why it is acceptable now or what follow-up test is planned.

Placeholder values such as `TBD`, `TODO`, `none`, `n/a`, or empty bullets do not satisfy this contract.

## Passing Rule

- All six roles must be present.
- All six roles must bind to the current `packet_sha256`.
- All six roles must show distinct `Reviewer run id` values.
- Any `BLOCK` blocks the paper result pipeline until fixed and re-reviewed.
- Any `PENDING` or missing status blocks the pipeline.
- Any `WARN` without accepted rationale or follow-up test plan blocks the pipeline.
- `PASS` roles must still list what they inspected and what they found.
- Multiple ledgers, duplicate role sections, or stale packet hashes block the pipeline until reconciled.

## Review Prompt Pattern

Give each independent reviewer only the packet and its role:

```text
Review this research project as the <Role>. Use audit/code_review_packet.md as your source.
Return Role, Status (PASS/WARN/BLOCK), Reviewer, Reviewer run id, Packet SHA256, Evidence, Findings, Required fixes, and Accepted rationale.
Do not rewrite code unless explicitly assigned; focus on whether the experiment can support paper claims.
```
