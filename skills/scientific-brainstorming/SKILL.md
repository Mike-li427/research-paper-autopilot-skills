---
name: scientific-brainstorming
description: Use this skill for scientific topic ideation, research-question generation, hypothesis refinement, project framing, novelty analysis, experiment direction brainstorming, and turning broad interests into tractable research plans.
---

# Scientific Brainstorming

This skill helps turn a broad scientific interest into concrete, testable, and publishable research directions. It should be used before heavy literature search or manuscript writing when the user is still choosing the question, angle, mechanism, dataset, method, or contribution.

## Workflow

1. Clarify the user's field, constraints, available data or instruments, target venue or journal tier, and timeline.
2. Generate several candidate directions with a clear claim, why it matters, what evidence would support it, and what could falsify it.
3. Assess novelty, feasibility, risk, and expected payoff for each direction.
4. Convert the strongest direction into:
   - research question
   - hypothesis or central claim
   - minimal experiment or analysis plan
   - required literature search terms
   - expected figures or tables
5. When the user wants literature grounding, hand off to `nature-academic-search`, `deep-research`, or `academic-research-suite`.

## Output Shape

Prefer concise, decision-oriented outputs:

- 3-6 candidate ideas.
- A comparison table for novelty, feasibility, risk, and evidence needs.
- One recommended direction with next actions.
- Search queries and inclusion/exclusion criteria when literature review should follow.

## Guardrails

- Do not invent evidence. Mark unsupported ideas as hypotheses.
- Separate "interesting" from "publishable".
- Favor questions that can be answered with the user's available resources.
- If the topic has human, animal, clinical, or dual-use risks, flag ethics and safety review needs early.
