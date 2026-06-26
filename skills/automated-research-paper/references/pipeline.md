# Research Pipeline Reference

Use this reference when the project requires a full automated research loop.

## Stage Groups

### A. Research Definition

1. `TOPIC_INIT`: create a SMART research goal, topic boundary, venue constraints, and success criteria.
2. `PROBLEM_DECOMPOSE`: break the topic into prioritized sub-questions, risks, and required evidence.
3. `HARDWARE_CHECK`: detect CPU/GPU/MPS and set experiment scale accordingly.

### B. Literature Discovery

4. `SEARCH_STRATEGY`: define keyword families, sources, date ranges, and inclusion criteria.
5. `LITERATURE_COLLECT`: collect real records from APIs or official proceedings. No LLM-generated metadata.
6. `LITERATURE_SCREEN` gate: keep only genuinely relevant and sufficiently high-quality records.
7. `KNOWLEDGE_EXTRACT`: produce evidence cards preserving cite keys, DOI, arXiv id, venue, year, URL, problem, method, data, metrics, findings, and limitations.

### C. Knowledge Synthesis

8. `SYNTHESIS`: cluster findings and identify gaps.
9. `HYPOTHESIS_GEN`: generate falsifiable hypotheses with measurable predictions and failure conditions.
10. `THEORETICAL_BOUNDS`: sketch complexity, assumptions, or formal claims only when supported.

### D. Experiment Design

11. `EXPERIMENT_DESIGN` gate: define objectives, datasets, baselines, proposed methods, ablations, metrics, risks, compute budget.
12. `CODE_GENERATION`: implement runnable code with real math, deterministic seeds, convergence checks, and logging.
13. `RESOURCE_PLANNING`: estimate runtime, storage, API cost, and hardware requirements.

### E. Experiment Execution

14. `PILOT_RUN`: run one small condition, log `TIME_ESTIMATE`, and adjust scale.
15. `EXPERIMENT_RUN`: execute the approved sweep, save raw logs and structured results.
16. `ITERATIVE_REFINE`: fix runtime or numerical problems at the root cause; do not mask NaN/Inf.

### F. Analysis and Decision

17. `RESULT_ANALYSIS`: analyze exact result values, variance, failures, ablations, and limitations.
18. `RESEARCH_DECISION`: choose `PROCEED`, `REFINE`, or `PIVOT`.

Loop rules:

- `REFINE` returns to `ITERATIVE_REFINE` or `EXPERIMENT_DESIGN`.
- `PIVOT` returns to `HYPOTHESIS_GEN` or `PAPER_OUTLINE`.
- Each loop increments the version (`v1`, `v2`, ...), preserves prior artifacts, and records what changed.

### G. Paper Writing

19. `PAPER_OUTLINE`: build the narrative, evidence map, Figure 1 concept, and section plan.
20. `PAPER_DRAFT`: write full draft using only verified claims.
21. `PEER_REVIEW`: simulate strict reviews with special attention to method-evidence consistency.
22. `PAPER_REVISION`: revise for evidence, clarity, page limit, and contribution focus.

### H. Final Manuscript

23. `QUALITY_GATE`: block overclaims, unsupported claims, weak baselines, missing ablations, and topic drift.
24. `KNOWLEDGE_ARCHIVE`: archive reproducibility notes, configs, commands, failures, and lessons.
25. `EXPORT_PUBLISH`: export LaTeX/PDF using the target venue template.
26. `CITATION_VERIFY`: verify references are real, relevant, cited, and formatted.

### I. External Review and Rebuttal

27. `3RD_PARTY_REVIEW`: obtain a fresh, strict review if the user explicitly requests delegated review or if a separate context is available.
28. `REBUTTAL`: turn review objections into targeted paper edits or new experiments.

## PROGRESS.md Entry Template

```markdown
## v1 - STAGE_NAME - YYYY-MM-DD HH:MM

Status: completed | blocked | refine | pivot
Inputs:
- ...
Actions:
- ...
Artifacts:
- ...
Evidence:
- ...
Decision:
- ...
Next:
- ...
```

## Minimal Viable Pass

For small projects, use a compact pass:

1. Define topic and success criteria.
2. Collect and screen real literature.
3. Design one feasible experiment with baselines and ablations.
4. Run pilot and main results.
5. Write evidence-mapped paper.
6. Audit claims and citations.

Do not perform ceremonial stages that add no evidence.
