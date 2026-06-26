---
name: scientific-visualization
description: Use this skill for scientific figures, data visualization strategy, publication-quality plots, multi-panel figure planning, visual encoding choices, and figure audits for scientific manuscripts or presentations.
---

# Scientific Visualization

This skill turns scientific evidence into clear, publication-ready visual figures. Use it for deciding what figure to make, designing multi-panel figures, improving plots, checking figure logic, or generating Python/R visualization code.

## Workflow

1. Define the figure's scientific conclusion before choosing chart types.
2. Map each panel to evidence:
   - panel question
   - data source
   - statistical comparison
   - visual encoding
   - expected reader takeaway
3. Choose the simplest plot that supports the conclusion.
4. Use publication-quality defaults:
   - readable labels
   - colorblind-aware palettes
   - consistent scales and units
   - explicit sample sizes
   - uncertainty intervals where appropriate
   - no decorative clutter
5. For generated figures, ask whether the user wants Python or R when the backend is not clear, then coordinate with `nature-figure`.
6. Audit final figures for overlap, missing labels, misleading axes, low contrast, and mismatch between caption and data.

## Output Shape

- Figure plan: conclusion, panel list, required data, chart choices.
- Code: reproducible plotting script plus export settings.
- Review: concrete fixes ordered by scientific risk and visual polish.
- Manuscript support: figure title, legend draft, and source-data checklist.

## Guardrails

- Never make a plot imply stronger evidence than the data supports.
- Avoid 3D charts, dual axes, truncated axes, and excessive smoothing unless justified.
- Keep raw data visible when sample size is small.
- For Nature-style figures, use `nature-figure` as the plotting and QA backend.
