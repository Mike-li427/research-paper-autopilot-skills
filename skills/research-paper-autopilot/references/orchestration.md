# Orchestration Reference

Use this file when running the full automatic research-paper workflow.

## Output Modes

- `plan-only`: produce topic, literature plan, gap, method/evidence plan, and blocking checklist. Do not claim a draft is submission-ready.
- `draft-package`: produce a provisional manuscript package with visible evidence gaps and no submission-ready claim.
- `submission-package`: require every hard gate to pass, including mandatory multi-agent code review when experiment/analysis evidence exists.

If a hard gate is blocked, downgrade to `plan-only` or `draft-package` instead of presenting the package as ready to submit.

## State Machine

1. `INTAKE`: capture idea, audience, target track, target venue, deadlines, material paths, evidence status, compute/data constraints, output language, and forbidden claims.
2. `TRACK_DETECT`: classify the project and write a structured route: `primary_track`, `secondary_tracks`, `active_gate_sets`, and `reason`.
3. `PROJECT_SCAFFOLD`: create or normalize the project package. Preserve existing files and log any inferred structure.
4. `LITERATURE_DISCOVERY`: use real sources and/or the user's paper library. Preserve DOI, arXiv id, venue, year, URL, cite key, source database, retrieval date, and verification status when available.
5. `LITERATURE_SCREEN`: remove off-topic padding. Keep enough records to explain the research gap and likely reviewer objections.
6. `GAP_SYNTHESIS`: cluster prior work, identify gaps, and write falsifiable claims with required evidence.
7. `METHOD_OR_EXPERIMENT_DESIGN`: define method, data, baselines, metrics, ablations, robustness, risks, success criteria, and project-specific code structure using `experiment-code-standard.md`.
8. `EXECUTION_OR_ANALYSIS`: run or inspect real code, empirical analysis, simulations, proofs, or qualitative evidence. Archive commands, configs, logs, raw outputs, result schema records, and code-quality decisions.
9. `MULTI_AGENT_CODE_REVIEW`: freeze the code/result state, prepare the review packet, run all required code-review roles, and resolve every `BLOCK` before result interpretation.
10. `RESULT_INTERPRETATION`: convert evidence into cautious claims, limitations, tables, and figures only after mandatory code review passes.
11. `PAPER_ARCHITECTURE`: build title, abstract, contribution stack, Figure 1 plan, section outline, and claim-evidence map.
12. `DRAFTING`: write only evidence-grounded text. Keep claims narrow and mark evidence gaps explicitly.
13. `REVIEW_SIMULATION`: run field-appropriate reviewer simulation and convert objections into revision tasks.
14. `REVISION`: repair evidence, experiments, citations, writing logic, and formatting. Loop until hard blockers are fixed. Do not defer a hard blocker into a submission-ready package.
15. `INTEGRITY_AUDIT`: run automated and manual checks for citation reality, claim support, numeric consistency, figure/table consistency, code review validity, and reproducibility.
16. `SUBMISSION_PACKAGE`: produce manuscript, source files, references, figures, supplementary material, data/code availability, reproducibility notes, cover/rebuttal material when relevant.

## Dispatch Table

| Stage | Primary specialists | Required artifacts | Gate | Repair route |
| --- | --- | --- | --- | --- |
| `INTAKE` | `academic-pipeline`, `paper-spine-intake` when available | `research_manifest.json`, `RESTRICTS.yaml`, `PROGRESS.md` | Writing Gate | Ask for missing external constraints or mark `TBD` |
| `TRACK_DETECT` | `ccf-pipeline-orchestrator`, `nature-academic-search`, or generic route | route record in `research_manifest.json` | Track Routing Gate | Return to `INTAKE` if venue/field is ambiguous |
| `PROJECT_SCAFFOLD` | `ccf-project-scaffolder` for CCF, otherwise this skill's scaffold script | canonical directories and stage plans | Artifact Gate | Repair scaffold only; preserve user files |
| `LITERATURE_DISCOVERY` | `deep-research`, `literature-review`, `nature-academic-search`, `ccf-literature-searcher`, `papi`, `papi-ask` | `literature/candidates.jsonl`, `references.bib`, search notes | Literature Gate | Repeat search or add user PDFs |
| `LITERATURE_SCREEN` | `deep-research`, `literature-review`, `research-gap-analysis`, `papi-ground` | `literature/screened.jsonl`, `knowledge_cards.md` | Literature Gate | Return to discovery or narrow scope |
| `GAP_SYNTHESIS` | `scientific-brainstorming`, `ccf-idea-optimizer`, `research-gap-analysis` | `docs/literature_synthesis.md`, gap claims | Evidence Gate | Return to screening or pivot topic |
| `METHOD_OR_EXPERIMENT_DESIGN` | `ccf-experiment-designer`, `statistical-analysis` | `docs/experiment_or_analysis_plan.md`, code plan | Method And Experiment Gate | Repair design, baselines, metrics, or evidence source |
| `EXECUTION_OR_ANALYSIS` | `automated-research-paper`, track-specific analysis skills | raw runs, summaries, configs, commands, logs | Code Quality Gate and Evidence Gate | Repair code/results or downgrade claims |
| `MULTI_AGENT_CODE_REVIEW` | six independent reviewer agents | `audit/code_review_packet.md`, `audit/code_review_ledger.md/.json` | Multi-Agent Code Review Gate | Fix code/results and regenerate packet |
| `RESULT_INTERPRETATION` | `nature-figure`, `scientific-visualization` | tables, figure sources, result notes | Evidence Gate | Return to execution or review ledger |
| `PAPER_ARCHITECTURE` | `paper-spine`, `paper-writing`, `nature-writing`, `ccf-paper-writer` | outline, claim-evidence map, Figure 1 plan | Writing Gate | Repair claim hierarchy |
| `DRAFTING` | `academic-paper`, `paper-spine`, `nature-writing`, `ccf-paper-writer` | manuscript sections | Writing Gate | Return to architecture or evidence |
| `REVIEW_SIMULATION` | `academic-paper-reviewer`, `ccf-paper-reviewer`, `nature-reviewer` | `docs/reviewer_objections.md` | Review Gate | Convert objections into repairs |
| `REVISION` | writing/review specialists for the active track | revised manuscript and artifacts | Review Gate | Return to the exact failed upstream stage |
| `INTEGRITY_AUDIT` | `citation-check-skill`, `ccf-integrity-auditor`, this skill's audit script | audit reports | All hard gates | Repair exact blocked artifact |
| `SUBMISSION_PACKAGE` | `ccf-submission-checker`, `nature-data`, `nature-response` | submission checklist and package | Submission Gate | Return to audit or venue-specific repair |

## Loop Rules

- `PROCEED`: move to the next state and record evidence.
- `REFINE`: return to the exact upstream state listed in the repair route.
- `PIVOT`: preserve prior artifacts, redefine the question or contribution, and restart from `GAP_SYNTHESIS` or `METHOD_OR_EXPERIMENT_DESIGN`.
- `BLOCKED`: stop claiming readiness and list the missing external input, data, compute, reviewer agent capacity, or user decision.

Increment the project version on every major loop. Never overwrite prior evidence; write new artifacts or note supersession in `PROGRESS.md`.

## Blocker Semantics

- `HARD_BLOCK`: cannot be deferred into a submission package.
- `WARN_DEFERRED`: may remain in a provisional draft only when the claim is downgraded and the follow-up plan is explicit.
- `OUT_OF_SCOPE`: allowed only when the claim, venue requirement, or artifact has been removed from the package.

## Minimal Viable Pass

For small projects, run a compact pass: intake, track detect, literature, gap, method/evidence plan, mandatory multi-agent code review when real code/results/claims exist, draft, review, integrity audit. Label the result as `draft-package` unless all submission gates pass.
