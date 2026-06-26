#!/usr/bin/env python3
"""Create a research-paper-autopilot project scaffold."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


STAGES = [
    "01_intake",
    "02_track_detect",
    "03_project_scaffold",
    "04_literature_discovery",
    "05_literature_screen",
    "06_gap_synthesis",
    "07_method_or_experiment_design",
    "08_execution_or_analysis",
    "09_multi_agent_code_review",
    "10_result_interpretation",
    "11_paper_architecture",
    "12_drafting",
    "13_review_simulation",
    "14_revision",
    "15_integrity_audit",
    "16_submission_package",
]


def write_if_missing(path: Path, text: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def yaml_dump(value: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        rows: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                rows.append(f"{pad}{key}:")
                rows.append(yaml_dump(child, indent + 2))
            else:
                rows.append(f"{pad}{key}: {yaml_scalar(child)}")
        return "\n".join(rows)
    if isinstance(value, list):
        if not value:
            return f"{pad}[]"
        rows = []
        for child in value:
            if isinstance(child, (dict, list)):
                rows.append(f"{pad}-")
                rows.append(yaml_dump(child, indent + 2))
            else:
                rows.append(f"{pad}- {yaml_scalar(child)}")
        return "\n".join(rows)
    return f"{pad}{yaml_scalar(value)}"


def ledger_template() -> str:
    sections = []
    for role in [
        "Algorithm Reviewer",
        "Experiment Design Reviewer",
        "Data Leakage Reviewer",
        "Metrics & Statistics Reviewer",
        "Reproducibility Reviewer",
        "Code Quality Reviewer",
    ]:
        sections.append(
            f"""## Role: {role}
Status: PENDING
Reviewer: TBD
Reviewer run id: TBD
Packet SHA256: TBD
Evidence:
- TBD
Findings:
- TBD
Required fixes:
- TBD
Accepted rationale:
- TBD
"""
        )
    return (
        "# Code Review Ledger\n\n"
        "Mandatory gate: all six independent reviewer roles must complete before experiment or analysis results can support paper claims.\n\n"
        "Every role must bind to the current `audit/code_review_packet.md` via `Packet SHA256` and a distinct `Reviewer run id`.\n\n"
        + "\n".join(sections)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Project root to create")
    parser.add_argument("--topic", required=True, help="Research topic or paper idea")
    parser.add_argument("--project-name", default="research-paper-project")
    parser.add_argument("--target-venue", default="AUTO")
    parser.add_argument("--track", default="AUTO", choices=["AUTO", "CCF_AI", "NATURE_SCI", "REVIEW_SURVEY", "GENERIC"])
    parser.add_argument("--deadline", default="TBD")
    parser.add_argument("--output-language", default="English")
    parser.add_argument("--page-limit", default="TBD")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    created: list[str] = []
    existing: list[str] = []
    skipped_files: list[str] = []
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    dirs = [
        "audit",
        "code",
        "data",
        "docs",
        "figures",
        "literature",
        "logs",
        "paper/sections",
        "plans",
        "results",
        "submission",
    ]
    for rel in dirs:
        path = root / rel
        if path.exists():
            existing.append(str(path))
        else:
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path))

    manifest = {
        "project_name": args.project_name,
        "topic": args.topic,
        "target_venue": args.target_venue,
        "track": args.track,
        "route": {
            "primary_track": args.track,
            "secondary_tracks": [],
            "active_gate_sets": ["generic"],
            "reason": ["Initial scaffold; rerun track detection before evidence work."],
        },
        "deadline": args.deadline,
        "output_language": args.output_language,
        "page_limit": args.page_limit,
        "generated": generated,
        "state": {
            "project_version": "v0",
            "stage": "INTAKE",
            "decision": "PROCEED",
        },
    }
    if write_if_missing(root / "research_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"):
        created.append(str(root / "research_manifest.json"))
    else:
        skipped_files.append(str(root / "research_manifest.json"))

    progress = f"""# PROGRESS

Project: {args.project_name}
Topic: {args.topic}
Target venue: {args.target_venue}
Track: {args.track}
Deadline: {args.deadline}
Output language: {args.output_language}
Page limit: {args.page_limit}
Generated: {generated}

## State Machine

Current project_version: v0
Current stage: INTAKE
Decision: PROCEED
Multi-agent code review required before experiment results enter paper claims: true

Allowed decisions:
- PROCEED
- REFINE
- PIVOT
- BLOCKED

## v0 - Scaffold - {generated}

Status: completed
Inputs:
- Topic: {args.topic}
Actions:
- Created the research-paper-autopilot project layout.
Artifacts:
- `research_manifest.json`
- `RESTRICTS.yaml`
- stage plans under `plans/`
Evidence:
- User-provided topic only.
Decision: PROCEED
Next:
- Complete intake, detect track, and collect real literature.
"""
    if write_if_missing(root / "PROGRESS.md", progress):
        created.append(str(root / "PROGRESS.md"))
    else:
        skipped_files.append(str(root / "PROGRESS.md"))

    restricts = {
        "topic": {
            "statement": args.topic,
            "target_venue": args.target_venue,
            "track": args.track,
            "output_language": args.output_language,
            "prohibit": [
                "Treating environment setup, dependency failures, or agent workflow as research contributions.",
                "Inventing literature, datasets, experiments, metrics, p-values, or reviewer outcomes.",
                "Claiming submission readiness while any hard quality gate is blocked.",
            ],
        },
        "evidence": {
            "literature_must_be_real": True,
            "experiments_or_analysis_must_be_archived": True,
            "unsupported_claims_block_submission": True,
            "result_schema_required": True,
        },
        "experiments": {
            "require_pilot_when_experiments_exist": True,
            "require_time_estimate": True,
            "require_seeds_configs_logs": True,
            "require_ablations_for_claimed_components": True,
            "multi_agent_code_review_required": True,
            "packet_hash_required": True,
        },
        "code_style": {
            "project_specific": True,
            "no_fake_results": True,
            "avoid_ai_template_style": True,
            "comments_explain_research_choices": True,
        },
        "writing": {
            "core_innovations_max": 2,
            "require_claim_evidence_map": True,
            "require_figure_1_plan": True,
            "page_limit": args.page_limit,
        },
    }
    if write_if_missing(root / "RESTRICTS.yaml", yaml_dump(restricts) + "\n"):
        created.append(str(root / "RESTRICTS.yaml"))
    else:
        skipped_files.append(str(root / "RESTRICTS.yaml"))

    config = {
        "project": {
            "name": args.project_name,
            "topic": args.topic,
            "target_venue": args.target_venue,
            "track": args.track,
        },
        "paths": {
            "data_dir": "data",
            "results_dir": "results",
            "logs_dir": "logs",
        },
        "run": {
            "seed": 2026,
            "mode": "pilot",
            "runtime_budget_seconds": 3600,
            "save_partial_at_fraction": 0.8,
        },
        "experiment": {
            "dataset_name": "REPLACE_WITH_REAL_DATASET",
            "conditions": [],
            "baselines": [],
            "ablations": [],
            "notes": "Replace placeholders before using any output as paper evidence.",
        },
        "metrics": {
            "primary": "REPLACE_WITH_PROJECT_METRIC",
            "secondary": [],
            "higher_is_better": True,
            "schema_ready": False,
        },
        "evidence": {
            "claim_evidence_map": "docs/claim_evidence_map.json",
            "result_schema_version": "autopilot-result-v1",
        },
    }

    docs = {
        "docs/overall_concept.md": "# Overall Concept\n\nState thesis, audience, venue, contribution, and hard topic boundary.\n",
        "docs/claim_evidence_map.md": "# Claim-Evidence Map\n\n| Claim ID | Claim | Evidence artifact | Evidence level | Status |\n| --- | --- | --- | --- | --- |\n",
        "docs/claim_evidence_map.json": json.dumps({"claims": []}, indent=2, ensure_ascii=False) + "\n",
        "docs/literature_synthesis.md": "# Literature Synthesis\n\nRecord search strategy, clusters, gaps, and reviewer objections.\n",
        "docs/experiment_or_analysis_plan.md": "# Experiment Or Analysis Plan\n\nDefine data, method, baselines, metrics, ablations, robustness, and compute constraints.\n",
        "docs/reviewer_objections.md": "# Reviewer Objections\n\nConvert simulated or external review comments into required repairs.\n",
        "code/README.md": f"""# Experiment Code

Project: {args.project_name}
Topic: {args.topic}

This directory is a scaffold for real experiment or analysis code. Do not use generated numbers, mock curves, or hardcoded metrics as paper evidence.

## Expected workflow

1. Edit `config.yaml` with real data paths, baselines, metrics, and runtime budget.
2. Replace the `NotImplementedError` in `run_experiments.py` with project-specific method and baseline logic.
3. Run a pilot first from the project root:

```bash
python code/run_experiments.py --config code/config.yaml --mode pilot
```

4. Inspect logs and result JSON before running the main sweep:

```bash
python code/run_experiments.py --config code/config.yaml --mode main
python code/analyze_results.py --config code/config.yaml --results results --out results/summary.json
```

5. Run mandatory multi-agent code review before transferring results into paper claims:

```bash
python <installed-skill>/scripts/prepare_code_review_packet.py --root .
```

Keep names, metrics, and logs tied to this paper's claim-evidence map.
""",
        "audit/code_review_ledger.md": ledger_template(),
        "audit/audit_report.md": "# Audit Report\n\nGenerated by `scripts/audit_autopilot_project.py` after evidence exists.\n",
        "code/config.yaml": yaml_dump(config) + "\n",
        "code/run_experiments.py": '''#!/usr/bin/env python3
"""Run this project's pilot or main experiment.

Replace the project-specific condition logic before citing any output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass
    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return loaded
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "Install PyYAML or keep config.yaml in JSON-compatible YAML. "
            f"Could not parse {path}: {exc}"
        ) from exc
    raise SystemExit(f"Config did not parse into an object: {path}")


def project_root_from_config(config_path: Path) -> Path:
    parent = config_path.resolve().parent
    return parent.parent if parent.name.lower() == "code" else Path.cwd().resolve()


def project_path(root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def seed_everything(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np  # type: ignore

        np.random.seed(seed)
    except Exception:
        pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()
    except Exception:
        return "unavailable"


def require_finite_metrics(value: Any, prefix: str = "result") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require_finite_metrics(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_finite_metrics(child, f"{prefix}[{index}]")
    elif isinstance(value, (int, float)) and not math.isfinite(float(value)):
        raise ValueError(f"non-finite metric {prefix}={value}")


def run_project_specific_condition(config: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    # TODO(project): implement the real method, baselines, metrics, and ablations for this paper.
    raise NotImplementedError(
        "Replace run_project_specific_condition with real experiment or analysis logic before running."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="code/config.yaml")
    parser.add_argument("--mode", choices=["pilot", "main"], default=None)
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    root = project_root_from_config(config_path)
    config = load_config(config_path)
    mode = args.mode or str(config.get("run", {}).get("mode", "pilot"))
    seed = int(config.get("run", {}).get("seed", 2026))
    seed_everything(seed)

    results_dir = project_path(root, str(config.get("paths", {}).get("results_dir", "results")))
    logs_dir = project_path(root, str(config.get("paths", {}).get("logs_dir", "logs")))
    results_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    run_id = time.strftime("%Y%m%d_%H%M%S") + "_" + mode
    config_snapshot = results_dir / (run_id + "_config.json")
    config_snapshot.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")

    command_line = " ".join(sys.argv)
    started = time.time()
    status = "started"
    raw_runs: list[dict[str, Any]] = []
    try:
        raw_runs = run_project_specific_condition(config, mode)
        require_finite_metrics(raw_runs)
        status = "completed"
    except Exception:
        status = "failed"
        partial = {
            "schema_version": "autopilot-result-v1",
            "status": status,
            "mode": mode,
            "seed": seed,
            "command_line": command_line,
            "config_snapshot": str(config_snapshot.relative_to(root)),
            "config_sha256": sha256_file(config_snapshot),
            "raw_runs": raw_runs,
            "error_type": sys.exc_info()[0].__name__ if sys.exc_info()[0] else "unknown",
        }
        partial_path = results_dir / (run_id + "_partial_result.json")
        partial_path.write_text(json.dumps(partial, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
        raise
    finally:
        elapsed = time.time() - started
        estimate = max(1, int(elapsed * 20)) if mode == "pilot" else None
        log_path = logs_dir / (run_id + ".log")
        log_rows = [
            f"status={status}",
            f"mode={mode}",
            f"seed={seed}",
            f"elapsed_seconds={elapsed}",
            f"command_line={command_line}",
            f"config_snapshot={config_snapshot}",
        ]
        if estimate is not None:
            log_rows.append(f"TIME_ESTIMATE: {estimate}")
            print("TIME_ESTIMATE: " + str(estimate))
        log_path.write_text("\\n".join(log_rows) + "\\n", encoding="utf-8")

    elapsed = time.time() - started
    payload = {
        "schema_version": "autopilot-result-v1",
        "status": status,
        "mode": mode,
        "seed": seed,
        "command_line": command_line,
        "config_snapshot": str(config_snapshot.relative_to(root)),
        "config_sha256": sha256_file(config_snapshot),
        "log_path": str((logs_dir / (run_id + ".log")).relative_to(root)),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "git_head": git_head(root),
        },
        "elapsed_seconds": elapsed,
        "raw_runs": raw_runs,
        "summary": {
            "run_count": len(raw_runs),
            "metric_schema_ready": bool(config.get("metrics", {}).get("schema_ready", False)),
        },
    }
    out = results_dir / (run_id + "_result.json")
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    print("wrote " + str(out))


if __name__ == "__main__":
    main()
''',
        "code/analyze_results.py": '''#!/usr/bin/env python3
"""Summarize archived result files without inventing missing evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass
    return json.loads(text)


def load_result_files(results_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(results_dir.glob("*_result.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        item["_source_file"] = str(path)
        records.append(item)
    return records


def require_completed_schema(record: dict[str, Any]) -> None:
    required = ["schema_version", "status", "seed", "command_line", "config_snapshot", "config_sha256", "log_path", "raw_runs", "summary"]
    missing = [key for key in required if key not in record]
    if missing:
        raise SystemExit(f"Result file lacks required schema fields {missing}: {record.get('_source_file')}")
    if str(record.get("status")) != "completed":
        raise SystemExit(f"Result file is not completed: {record.get('_source_file')}")


def finite_numbers(value: Any) -> list[float]:
    out: list[float] = []
    if isinstance(value, dict):
        for child in value.values():
            out.extend(finite_numbers(child))
    elif isinstance(value, list):
        for child in value:
            out.extend(finite_numbers(child))
    elif isinstance(value, (int, float)):
        number = float(value)
        if not math.isfinite(number):
            raise SystemExit(f"Non-finite number in result artifact: {value}")
        out.append(number)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="code/config.yaml")
    parser.add_argument("--results", default="results")
    parser.add_argument("--out", default="results/summary.json")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    metrics = config.get("metrics", {}) if isinstance(config, dict) else {}
    if not metrics.get("schema_ready"):
        raise SystemExit("Metric schema is not ready. Set metrics.schema_ready only after defining real project metrics.")

    results_dir = Path(args.results)
    records = load_result_files(results_dir)
    if not records:
        raise SystemExit("No result files found. Run a real pilot/main experiment first.")
    for record in records:
        require_completed_schema(record)
        finite_numbers(record)

    summary = {
        "schema_version": "autopilot-summary-v1",
        "result_files": [item["_source_file"] for item in records],
        "modes": sorted({str(item.get("mode", "unknown")) for item in records}),
        "seeds": sorted({int(item.get("seed", -1)) for item in records}),
        "primary_metric": metrics.get("primary"),
        "notes": "Project-specific metric aggregation must be implemented before paper claims cite this summary.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    print("wrote " + str(out))


if __name__ == "__main__":
    main()
''',
        "literature/candidates.jsonl": "",
        "literature/screened.jsonl": "",
        "literature/knowledge_cards.md": "# Knowledge Cards\n\n",
        "literature/references.bib": "",
        "paper/main.tex": "\\documentclass{article}\n\\begin{document}\n\\title{TBD}\n\\maketitle\n\\input{sections/introduction}\n\\input{sections/related_work}\n\\input{sections/method}\n\\input{sections/experiments}\n\\input{sections/results}\n\\input{sections/discussion}\n\\input{sections/limitations}\n\\input{sections/conclusion}\n\\bibliographystyle{plain}\n\\bibliography{../literature/references}\n\\end{document}\n",
        "paper/README.md": "# Paper Build\n\nCompile from the `paper/` directory unless a venue template provides a different build command.\n",
        "submission/cover_letter.md": "# Cover Letter\n\n",
        "submission/data_availability.md": "# Data Availability\n\n",
        "submission/code_availability.md": "# Code Availability\n\n",
        "submission/reproducibility_readme.md": "# Reproducibility README\n\n",
        "submission/submission_checklist.md": "# Submission Checklist\n\n| Item | Status | Evidence |\n| --- | --- | --- |\n| Venue rules checked | TBD | TBD |\n| Page limit checked | TBD | TBD |\n| Anonymity checked | TBD | TBD |\n| Figures checked | TBD | TBD |\n| Data/code availability checked | TBD | TBD |\n| Supplementary files checked | TBD | TBD |\n",
        "submission/response_or_rebuttal.md": "# Response Or Rebuttal\n\n",
    }
    for rel, text in docs.items():
        if write_if_missing(root / rel, text):
            created.append(str(root / rel))
        else:
            skipped_files.append(str(root / rel))

    for section in ["introduction", "related_work", "method", "experiments", "results", "discussion", "limitations", "conclusion"]:
        rel = root / "paper" / "sections" / f"{section}.tex"
        if write_if_missing(rel, f"% {section.replace('_', ' ').title()}\n"):
            created.append(str(rel))
        else:
            skipped_files.append(str(rel))

    for index, stage in enumerate(STAGES, start=1):
        text = f"""# {stage}

Project version: v0
Template version: v1
Stage: {stage.upper()}
Status: planned
Order: {index}
Decision: TBD

## Inputs

- `PROGRESS.md`
- `RESTRICTS.yaml`
- upstream artifacts

## Actions

- TBD

## Evidence Required

- TBD

## Gate Criteria

- PROCEED only when evidence is adequate.
- REFINE when upstream repair can resolve the issue.
- PIVOT when the research question or contribution must change.
- BLOCKED when external input, data, compute, independent reviewer agents, or a user decision is required.

## Expected Artifacts

- TBD

## Next

- TBD
"""
        stage_path = root / "plans" / f"{stage}.md"
        if write_if_missing(stage_path, text):
            created.append(str(stage_path))
        else:
            skipped_files.append(str(stage_path))

    print(json.dumps({"root": str(root), "created": created, "existing": existing, "skipped_files": skipped_files}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
