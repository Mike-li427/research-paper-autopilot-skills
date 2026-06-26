# Research Gap Analysis: <Topic>

> Structured research memo, not a casual summary.
> Ground every nontrivial claim in the papers (cite section/figure/table/page).
> Mark uncertain claims as uncertain.
> Do not overclaim novelty.
> See `research-gap-analysis/SKILL.md` §3 and §8.

## 1. Scope

- What papers are included?
- What research area is being analyzed?
- What is intentionally out of scope?

## 2. One-Paragraph Executive Summary

<The single most important finding of this gap analysis, in one paragraph.>

## 3. Paper List

| # | Title | Authors | Venue / Year | Local path |
|---|-------|---------|--------------|------------|
| 1 |       |         |              | `./papers/…` |
| 2 |       |         |              | `./papers/…` |

## 4. Problem Landscape

- What broader problem do these papers collectively address?
- Why does this area matter?

## 5. Taxonomy

Organize the papers by meaningful dimensions for your field (pick those that apply): problem type; setting or population; method family; key assumptions; data or materials; evaluation methodology.
Choose axes that actually separate these papers.
A table often works well here — see `paper-matrix.md` for the detailed comparison.

| Paper | Dimension A | Dimension B | Dimension C |
|-------|-------------|-------------|-------------|
|       |             |             |             |

## 6. Paper-by-Paper Summary

A concise but meaningful summary per paper.
Keep this short — it is not the whole document.
Full per-paper detail lives in `reading-notes/<paper-short-name>.md`.

- **Paper 1 — <short name>:** <2–4 sentences>
- **Paper 2 — <short name>:** <2–4 sentences>

## 7. Cross-Paper Comparison

Compare the papers **directly** (not one-by-one).
Focus on: assumptions; mechanisms; workloads; evaluation; claimed benefits; limitations.
Surface hidden assumptions, mismatched claims vs. evidence, ignored system layers, excluded workloads, and abstractions that do not compose.

## 8. What Is Already Well Covered?

Problems or techniques that appear relatively mature across the set.

## 9. What Is Not Covered?

Missing cases, missing assumptions, missing evaluations, or missing system settings.

## 10. Candidate Research Gaps

For each candidate gap, classify the kind (explicit / implied / methodology / deployment / opportunity) and rate its strength (Strong / Medium / Weak).

### Gap 1: <Gap Name>

- **Kind:** <explicit / implied / methodology / deployment / opportunity>
- **Gap statement:**
- **Why it matters:**
- **Why existing work does not solve it:**
- **Evidence (paper §/fig/table/page):** <cite the specific passages this gap rests on; mark anything inferred as "inferred">
- **Possible research question:**
- **Possible approach:**
- **Possible evaluation:**
- **Risks:**
- **Strength:** Strong / Medium / Weak

### Gap 2: <Gap Name>

- **Kind:**
- **Gap statement:**
- **Why it matters:**
- **Why existing work does not solve it:**
- **Evidence (paper §/fig/table/page):** <cite the specific passages this gap rests on; mark anything inferred as "inferred">
- **Possible research question:**
- **Possible approach:**
- **Possible evaluation:**
- **Risks:**
- **Strength:** Strong / Medium / Weak

## 11. Most Promising Directions

Rank the most promising directions.
Explain why they are promising and what would be needed to make them publishable.

## 12. Dangerous or Weak Directions

Identify tempting but weak directions.
Explain why each may be too broad, too incremental, too hard to evaluate, or already solved.

## 13. Recommended Next Papers

Suggest additional papers to read next.
**Do not fabricate citations.** If unsure, mark as "to verify".

| Paper / lead | Why relevant | Status |
|--------------|--------------|--------|
|              |              | to verify |

## 14. Final Takeaway

A concise statement of what the selected papers collectively imply.
