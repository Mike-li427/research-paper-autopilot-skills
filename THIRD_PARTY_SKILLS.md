# Third-Party / Vendored Skills Notice

This repository vendors a curated subset of skills from the local Codex skills directory so users can clone the repository and install a working research-paper workflow.

Before publishing this repository publicly, verify the upstream source and redistribution license for every directory listed in `skills_manifest.json`.

## Included Skill Groups

- Main orchestrator: `research-paper-autopilot`
- General academic research and writing pipelines
- CCF/AI conference workflow skills
- Nature/SCI search, writing, figure, data, and response skills
- PaperSpine writing/build helpers
- Literature review, survey, citation, visualization, and statistical analysis helpers
- Personal paper library/RAG helper skills
- PDF support skills useful for research artifacts

## Publisher Checklist

Before pushing to GitHub:

- Confirm each vendored skill can be redistributed.
- Pay special attention to large vendored suites and copied web snapshots, especially `academic-research-suite` and `nature-figure`.
- Preserve any upstream license files that are present inside skill directories.
- Remove any private data, local credentials, generated caches, or personal paths.
- Run `python scripts/validate_bundle.py`.
- Run a secret scan with your preferred tool.

The top-level `LICENSE` applies to the bundle files authored for this repository. It does not override upstream licenses for vendored skills.
