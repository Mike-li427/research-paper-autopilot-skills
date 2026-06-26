# Experiment Code Standard

Use this standard before generating or repairing experiment, empirical-analysis, simulation, plotting, or result-summary code.

## Quality Priority

Prefer plain, project-specific research code over polished but hollow templates. The goal is not detector evasion; the goal is code that a careful researcher could maintain, rerun, and defend in review.

## Required Evidence Properties

- Implement real algorithms, objectives, estimators, metrics, and baselines; never mock paper-facing results.
- Use explicit seeds for stochastic algorithms, data splits, bootstraps, and simulations.
- Save raw per-condition outputs, aggregate summaries, configs, command lines, and logs.
- Save a machine-checkable result schema with raw run records, aggregate summaries, config snapshot/hash, seed, command line, log path, environment or git metadata, and code/result hashes.
- Run a pilot before a full sweep and print or log `TIME_ESTIMATE: <seconds>`.
- Add convergence or stopping checks for iterative methods.
- Validate final arrays and metrics for finite values.
- Treat malformed result files, failed/crashed status, NaN, Inf, or silent JSON/CSV parse errors as blockers.
- Save partial results before a runtime budget is exhausted.
- Tune baselines with comparable care and record selected hyperparameters.
- Pass the mandatory multi-agent code review before transferring any output into manuscript claims, tables, or figures.
- Bind every code review ledger to the current packet hash and reviewer run/session ids.

## Natural Research-Code Constraints

- Make names reflect the project: dataset, treatment, model, retrieval setting, benchmark, metric, or estimator should appear in names where relevant.
- Avoid generic chains such as `process_data`, `run_model`, `calculate_metric`, `helper`, `utils`, and `main_pipeline` unless the project already uses them.
- Keep comments sparse and useful. Explain design choices, failure modes, assumptions, or reviewer-relevant details; do not narrate obvious assignments or loops.
- Avoid broad unused abstractions, configuration frameworks, factories, or plugin systems unless the project needs them.
- Split code only where it helps the research workflow: experiment runner, methods/baselines, metrics, analysis, plotting, or data preparation.
- Leave explicit `NotImplementedError` or stage notes for missing real logic rather than filling fake outputs.
- Let the code show its research context: result schema, log fields, metric labels, and output filenames should match the paper's claim-evidence map.

## Recommended Layout

```text
code/
  README.md
  config.yaml
  run_experiments.py
  analyze_results.py
results/
  pilot_*.json
  run_*.json
  summary.csv
logs/
  pilot_*.log
  run_*.log
```

Add extra files only when the project needs them, for example `baselines.py`, `metrics.py`, `estimators.py`, `plot_figures.py`, or `data_prep.py`.

## Blockers

- Randomly generated trends, losses, accuracies, coefficients, p-values, or figures used as evidence.
- Hardcoded result numbers meant to appear in the paper.
- Silent NaN/Inf clipping, broad `try/except`, or dropped rows without a written reason.
- A manuscript claim that cannot be traced to code, raw output, result summary, citation, or derivation.
- Code that can only be understood as a generic AI-generated scaffold and not as this project's experiment.
- Experiment or analysis results used in the paper without a complete multi-agent code-review ledger.
