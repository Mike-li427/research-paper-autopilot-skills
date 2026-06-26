---
name: statistical-analysis
description: Use this skill for statistical analysis planning, test selection, model interpretation, power analysis, reproducible analysis scripts, result reporting, and checking whether quantitative claims match data and methods.
---

# Statistical Analysis

This skill helps design, execute, and audit statistical analysis for scientific work. Use it when the user asks what test to use, how to analyze data, how to report statistics, whether a result is significant, or how to build reproducible R/Python analysis.

## Workflow

1. Identify the study design:
   - experimental, observational, longitudinal, paired, repeated measures, survival, diagnostic, survey, or simulation
   - independent/dependent variables
   - sample size and missingness
   - outcome type: continuous, binary, count, ordinal, time-to-event, compositional, or high-dimensional
2. Check assumptions and risks:
   - independence
   - distribution and variance
   - confounding
   - multiple comparisons
   - batch effects
   - outliers and missing data
3. Recommend an analysis plan:
   - primary model or test
   - effect size and confidence interval
   - sensitivity analyses
   - correction method when needed
   - visualization needed to diagnose and explain the result
4. If data files are available, write reproducible Python or R code and save outputs.
5. Report results in manuscript-ready language with exact test names, estimates, intervals, p-values, and assumptions.

## Preferred Tools

- Python: pandas, numpy, scipy, statsmodels, scikit-learn, seaborn, matplotlib.
- R: tidyverse, ggplot2, lme4, survival, broom, rstatix when available.
- For publication plots, coordinate with `nature-figure` or `scientific-visualization`.

## Guardrails

- Do not treat p-values as effect sizes.
- Do not infer causality from observational data without a defensible design.
- Do not choose tests only after seeing significance.
- Flag underpowered, overfit, or non-independent analyses.
- For medical or clinical decisions, frame output as analytical support, not medical advice.
