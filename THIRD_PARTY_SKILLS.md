# Third-Party / Vendored Skills Notice

This repository vendors a curated subset of skills from a local Codex skills directory so users can clone the repository and install a working research-paper workflow.

Important: this repository is a bundle and integration layer. It does not claim original authorship of every bundled skill. Many supporting skills under `skills/` were copied from pre-existing local/community/third-party Codex skill installations, then packaged together so the main `research-paper-autopilot` workflow can be installed in one step.

Before publishing, redistributing, or using this bundle commercially, verify the upstream source and redistribution license for every directory listed in `skills_manifest.json`.

## Authorship Scope

The repository-level files are bundle/integration material:

- `README.md`
- `README.zh-CN.md`
- `INCLUDED_SKILLS.md`
- `scripts/install.py`
- `scripts/validate_bundle.py`
- `.codex-plugin/plugin.json`
- `skills_manifest.json`
- the local `research-paper-autopilot` orchestration/hardening files

The supporting skills under `skills/` may include work authored by other people, projects, or communities. Their presence in this repository should be read as vendoring/packaging, not as an authorship claim.

If a bundled skill includes its own `LICENSE`, `NOTICE`, `README`, or attribution file, that file should be preserved and treated as authoritative for that skill.

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
- Add missing upstream links, author names, or license notes when known.
- Pay special attention to large vendored suites and copied web snapshots, especially `academic-research-suite` and `nature-figure`.
- Preserve any upstream license files that are present inside skill directories.
- Remove any private data, local credentials, generated caches, or personal paths.
- Run `python scripts/validate_bundle.py`.
- Run a secret scan with your preferred tool.

The top-level `LICENSE` applies to the bundle files authored for this repository. It does not override upstream licenses for vendored skills.

## Upstream Author Requests

If you are the author or maintainer of a bundled skill and want attribution corrected, license text added, a link changed, or a skill removed from the public bundle, please open an issue or pull request in the GitHub repository.

Recommended issue title:

```text
Attribution / license request for <skill-name>
```
