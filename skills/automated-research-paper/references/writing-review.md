# Writing and Review Standard

Use this reference before drafting, revising, or reviewing the paper.

## Narrative

- Center the paper on one or two core technical ideas.
- Make the abstract and introduction state the problem, why it matters, the gap, the method, and exact evidence.
- Keep every section connected to the stated topic.
- Explain limitations explicitly.

## Figure 1

Before drafting the full paper, define Figure 1:

- What core contribution should a reader understand in 30 seconds?
- What inputs, mechanism, and outputs are shown?
- Which result or contrast is visually encoded?
- What should the caption claim, and which result supports it?

If the user will generate artwork later, place a detailed prompt in a LaTeX comment near the figure placeholder.

## Section Expectations

Typical top-conference structure:

- Abstract: 150-250 words.
- Introduction: 800-1000 words when page budget allows.
- Related Work: organized by themes, not a list of papers.
- Method: formal problem definition, algorithm, equations, complexity, and design rationale.
- Experiments: datasets, preprocessing, baselines, hyperparameters, metrics, hardware, and runtime.
- Results: main table, ablations, statistical/variance discussion, failure analysis.
- Discussion: interpretation, implications, and relation to prior work.
- Limitations: honest scope and generalization limits.
- Conclusion: concrete summary and future work.

Adjust length to the venue page limit after compiling LaTeX. The compiled PDF is authoritative.

## Review Checklist

Flag as critical:

- Claims not present in results/logs/code.
- Claimed statistical tests absent from code.
- Missing ablations for named components.
- Weak or untuned baselines.
- Off-topic references used as padding.
- Environment issues framed as research findings.
- Paper says "submission-ready" without passing evidence and citation gates.

## Revision Policy

When evidence is weak, weaken the claim or run more experiments. Do not make prose more confident than the data.
