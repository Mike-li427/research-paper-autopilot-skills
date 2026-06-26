# Artifact Contract

Use this structure unless an existing project already has a compatible layout.

## Project Layout

```text
<project>/
  PROGRESS.md
  RESTRICTS.yaml
  research_manifest.json
  docs/
    overall_concept.md
    claim_evidence_map.md
    claim_evidence_map.json
    literature_synthesis.md
    experiment_or_analysis_plan.md
    reviewer_objections.md
  literature/
    candidates.jsonl
    screened.jsonl
    knowledge_cards.md
    references.bib
  plans/
  code/
    README.md
    config.yaml
    run_experiments.py
    analyze_results.py
  data/
  results/
  figures/
  paper/
    main.tex
    sections/
  submission/
    cover_letter.md
    data_availability.md
    code_availability.md
    reproducibility_readme.md
    submission_checklist.md
    response_or_rebuttal.md
  audit/
    audit_report.json
    audit_report.md
    code_review_packet.md
    code_review_ledger.md
  logs/
```

## Progress Entry

Each stage entry in `PROGRESS.md` must include:

```markdown
## vN - STAGE_NAME - YYYY-MM-DD HH:MM

Status: completed | refine | pivot | blocked
Inputs:
- ...
Actions:
- ...
Artifacts:
- ...
Evidence:
- ...
Decision: PROCEED | REFINE | PIVOT | BLOCKED
Next:
- ...
```

## Claim-Evidence Map

Every major claim must map to at least one support:

- Literature record, citation key, DOI/arXiv/URL, or user-provided PDF.
- Result file, table, figure source, raw log, or code path.
- Dataset card, data provenance note, or repository record.
- Mathematical derivation with assumptions.
- Official documentation or standard.

If no support exists, mark the claim as `UNSUPPORTED` and route to evidence generation or removal.

Prefer `docs/claim_evidence_map.json` for machine checks:

```json
{
  "claims": [
    {
      "id": "C1",
      "claim": "Precise claim text",
      "status": "SUPPORTED",
      "evidence": [
        {
          "path": "results/summary.json",
          "type": "result",
          "hash": "sha256...",
          "locator": "metric.primary"
        }
      ]
    }
  ]
}
```

Do not mark a claim `SUPPORTED` when every evidence path is missing, stale, or unrelated.

## Result Artifact Schema

Experiment or statistical claims should trace to result artifacts with:

- raw per-condition records
- aggregate summary
- config snapshot or config hash
- command line
- seed
- log path
- environment or code metadata
- source code/result hashes
- status fields that distinguish completed, failed, crashed, and partial runs

Statistical support should include test name, statistic, p-value or confidence interval, sample size, command/hash, and source result path.

## Final Package

The final package should include:

- Manuscript source and compiled output when a build system exists.
- Bibliography and citation audit.
- Figures and figure source files.
- Results and analysis scripts.
- Reproducibility README.
- Data/code availability statements.
- Submission checklist for the selected venue/track.
- Revision ledger or rebuttal/response file when review comments exist.
