# Anti-Fabrication Rules

These are hard blockers.

## Literature

- Do not invent paper titles, authors, venues, years, DOIs, arXiv IDs, URLs, or BibTeX.
- Do not use LLM-generated metadata as a source.
- Do not treat a BibTeX key alone as proof that a paper exists. Preserve source database, retrieval date, metadata source, and DOI/arXiv/URL verification status whenever possible.
- If only an abstract or metadata is available, mark the evidence level accordingly.
- Do not cite a source for a claim it does not support.
- Do not claim exhaustive search unless the search strategy and results are archived.

## Data And Results

- Do not fake datasets, benchmarks, samples, random curves, losses, accuracies, coefficients, p-values, confidence intervals, or qualitative examples.
- Do not report unrun experiments or analyses.
- Use randomness only for legitimate simulation, initialization, sampling, splitting, or stochastic algorithms; log the seed.
- Do not hardcode metrics to fit a story.
- Do not hide failed runs, NaN/Inf, dropped data, or missingness.
- Do not treat a hand-written summary file as experiment evidence unless raw runs, config snapshot, command line, seed, log path, and code/result hashes are archived.
- Do not claim statistical significance from manuscript text alone; p-values, confidence intervals, sample sizes, and test commands must be archived outside the prose.

## Writing

- Do not present the agent workflow as the scientific contribution.
- Do not inflate novelty, generality, causal interpretation, or real-world impact beyond the evidence.
- Do not remove limitations merely to sound stronger.
- Do not mark a manuscript submission-ready while any hard quality gate is blocked.
- Do not claim submitted, accepted, revised, or camera-ready status without explicit user-provided or external evidence.

## Repair Policy

When evidence is missing:

1. Name the missing evidence.
2. Route to the exact upstream stage that can produce it.
3. If evidence cannot be produced now, weaken or remove the claim.
4. Log the decision in `PROGRESS.md`.
