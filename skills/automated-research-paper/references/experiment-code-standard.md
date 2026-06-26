# Experiment Code Standard

Use this standard before generating or repairing experiment code.

## Required Files

Recommended layout:

```text
code/
  README.md
  run_experiments.py
  objectives.py
  methods.py
  baselines.py
  metrics.py
  config.py
results/
  pilot_*.json
  run_*.json
  summary.csv
logs/
  pilot_*.log
  run_*.log
```

## Main Requirements

- Prefer Python stdlib, NumPy, SciPy, pandas, matplotlib, and scikit-learn unless the task truly requires a larger framework.
- Keep runs deterministic with explicit seeds.
- Implement actual algorithms and objectives, not mocked curves.
- Implement convergence checks for iterative algorithms.
- Save raw per-condition results, aggregate summaries, configs, and command lines.
- Print or log `TIME_ESTIMATE: <seconds>` after the pilot.
- Include a time guard that saves partial results at 80 percent of the runtime budget.
- Validate all final arrays and metrics for finite values.

## NumPy 2.x Compatibility

- Use `np.trapezoid`, not `np.trapz`.
- Use `scipy.special.erfinv`, not `np.erfinv`.
- Use `bool`, `int`, `float`, `complex`, `str`, and `object`, not removed NumPy aliases.
- Use the standard `math` module, not `np.math`.

## Minimum Experiment Evidence

For a claim about a method component:

- Include the full method.
- Include a baseline without that component.
- Use the same datasets/splits/budget where possible.
- Report exact metrics and uncertainty if multiple seeds are used.

For a claim about outperforming baselines:

- Tune baselines with comparable effort.
- Record hyperparameter search ranges and selected values.
- Report failures honestly.

## Runtime Scaling

- If conditions exceed 100, reduce seed count to 3-5 unless the user approves more compute.
- If time is tight, reduce optimization steps, conditions, or datasets before compromising logging or baselines.
- Save partial results instead of losing completed runs.
