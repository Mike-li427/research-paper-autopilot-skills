# Anti-Fabrication Rules

These are hard blockers.

## Topic Discipline

- The paper must be about the stated topic.
- Do not treat environment setup, dependency installation, tool crashes, or configuration failures as research contributions.
- Methods must describe technical ideas, not the agent workflow.
- Results must report quantitative research outcomes, not status logs.

## Literature Integrity

- Do not invent references.
- Do not let an LLM create candidate paper metadata.
- Preserve DOI, arXiv id, URL, year, venue, and cite key when available.
- Reject off-topic papers even when prestigious.
- If the full paper is unavailable, mark the evidence level as metadata/abstract only.

## Experimental Integrity

- Do not use random number generation to fake trends, losses, accuracies, or tables.
- Use randomness only for legitimate data generation, initialization, train/test splitting, or stochastic algorithms, and log the seed.
- Do not hardcode metric values.
- Do not report unrun experiments.
- Do not claim statistical tests unless the code computed them and the output is archived.
- Do not claim datasets, baselines, model variants, hardware, or hyperparameters that are absent from configs/logs.

## Numerical Repair

When NaN/Inf or runtime warnings occur:

1. Locate the source operation and input values.
2. Identify the cause, such as overflow, zero division, unstable learning rate, bad normalization, or invalid domain.
3. Fix the algorithm or preprocessing.
4. Re-run the failed condition.
5. Document the change in `PROGRESS.md`.

Do not hide problems with broad `try/except`, `np.nan_to_num`, silent clipping, or deleted rows unless the method explicitly justifies it and the paper reports it.

## Claim-Evidence Rule

Every important paper claim must be backed by at least one of:

- Experiment result file.
- Raw log.
- Source code.
- Dataset card or data file.
- Literature record.
- Official project documentation/source.
- Mathematical derivation with stated assumptions.

Unsupported claims must be removed, weakened, or routed back to evidence generation.
