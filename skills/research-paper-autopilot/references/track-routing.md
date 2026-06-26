# Track Routing

Use this file before choosing specialist skills.

## Route Record

Write a route record before running specialist stages:

```yaml
primary_track: CCF_AI | NATURE_SCI | REVIEW_SURVEY | GENERIC
secondary_tracks: []
active_gate_sets:
  - generic
reason:
  - "venue or method evidence"
```

For mixed projects, choose the target venue or output format as `primary_track`, then add method/evidence tracks as `secondary_tracks`. Apply all relevant `active_gate_sets`. Example: a Nature-targeted ML benchmark paper uses `primary_track: NATURE_SCI` with `secondary_tracks: [CCF_AI]`.

## Routing Rules

### CCF/AI Conference

Choose this track when the project concerns AI, machine learning, systems, security, databases, HCI, software engineering, computer vision, NLP, robotics, algorithms, benchmarks, ablations, conference rebuttals, anonymity, or artifact evaluation.

Default specialists: `ccf-idea-optimizer`, `ccf-literature-searcher`, `ccf-experiment-designer`, `ccf-paper-writer`, `ccf-paper-reviewer`, `ccf-integrity-auditor`, `ccf-submission-checker`, `ccf-rebuttal-writer`.

Extra gates: baseline fairness, dataset/benchmark legitimacy, ablation coverage, statistical variance, reproducibility artifact, anonymization, page limit, and rebuttal readiness.

### Nature/SCI Journal

Choose this track when the project targets Nature-family, Cell/Science-style, SCI journals, biomedical/scientific experiments, high-impact journal narrative, figure polish, data availability, reviewer response, or English academic polishing.

Default specialists: `nature-academic-search`, `nature-writing`, `nature-polishing`, `nature-citation`, `nature-figure`, `nature-data`, `nature-reviewer`, `nature-response`.

Extra gates: story significance, figure conclusion clarity, data availability, source data, ethics/repository needs, strict citation support, and reviewer-style novelty assessment.

### Review Or Survey

Choose this track when the output is a literature review, survey, systematic review, related work, meta-analysis, research gap map, or reading corpus synthesis.

Default specialists: `deep-research`, `literature-review`, `research-gap-analysis`, `survey`, `nature-academic-search`, `papi`, `papi-ask`, `papi-ground`, `papi-compare`, `papi-curate`, `papi-verify`.

Extra gates: search strategy, inclusion/exclusion rules, corpus coverage, evidence levels, synthesis rather than annotated bibliography, and citation traceability.

### Generic Academic

Choose this track when no domain-specific track dominates.

Default specialists: `academic-pipeline`, `deep-research`, `academic-paper`, `academic-paper-reviewer`, `paper-spine`, `paper-writing`, `citation-check-skill`.

## Tie Breakers

- If a venue is named, use venue first as `primary_track`.
- If the manuscript depends on benchmark experiments and ablations, add `CCF_AI` gates even when the venue is a journal.
- If the primary risk is journal storytelling, figures, and data availability, add `NATURE_SCI` gates.
- If the user asks for "all tracks", use `GENERIC` as primary and add all relevant track gates.

## Evidence Floors

- Generic paper: at least a documented search strategy, screened corpus, claim-evidence map, and integrity audit.
- CCF/AI: include datasets/benchmarks, comparable baselines, ablations for named components, variance or repeated-run evidence when stochastic, and reproducibility notes.
- Nature/SCI: include figure-source traceability, data availability/source-data plan, ethics/privacy/licensing notes when relevant, and strict citation support for broad claims.
- Review/survey: include inclusion/exclusion rules, corpus coverage rationale, evidence levels, and citation traceability.
