#!/usr/bin/env python3
"""Audit a research-paper-autopilot project for evidence/readiness gaps."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


CITE_RE = re.compile(r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear)\{([^}]+)\}")
NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?%?", re.IGNORECASE)
STAT_TERMS = ["p-value", "p value", "statistically significant", "t-test", "ttest", "anova", "confidence interval"]
EXPERIMENT_TERMS = ["experiment", "experiments", "baseline", "ablation", "dataset", "accuracy", "f1", "auc", "rmse", "coefficient", "regression"]
SUBMISSION_TERMS = ["submission-ready", "camera-ready", "accepted"]
GENERIC_NAME_RE = re.compile(r"\b(process_data|run_model|calculate_metric|main_pipeline|helper|utils|foo|bar|sample_data)\b")
MOCK_RESULT_RE = re.compile(r"\b(fake|mock|dummy|synthetic)_?(result|results|metric|metrics|accuracy|f1|auc|p_value|curve|loss|table)\b", re.IGNORECASE)
HARDCODED_METRIC_RE = re.compile(
    r"[\"']?\b(accuracy|f1|auc|rmse|mae|mse|p_value|pvalue|p|coef|coefficient|effect_size)\b[\"']?\s*[:=]\s*[\"']?[-+]?\d+(?:\.\d+)?",
    re.IGNORECASE,
)
CONSTANT_ARRAY_RE = re.compile(r"\b(scores|accuracies|f1s|aucs|p_values|coefficients|losses)\b\s*=\s*\[[^\]]*\d[^\]]*\]", re.IGNORECASE)
OBVIOUS_COMMENT_RE = re.compile(r"#\s*(assign|loop over|iterate over|initialize|create a|print|import|set the)\b", re.IGNORECASE)
REQUIRED_REVIEW_ROLES = [
    "Algorithm Reviewer",
    "Experiment Design Reviewer",
    "Data Leakage Reviewer",
    "Metrics & Statistics Reviewer",
    "Reproducibility Reviewer",
    "Code Quality Reviewer",
]
PLACEHOLDER_TEXT = {"", "tbd", "todo", "pending", "none", "false", "n/a", "na", "-", "- tbd", "not applicable"}
CODE_EXTS = {".py", ".yaml", ".yml", ".md", ".json", ".ipynb", ".r", ".R", ".do", ".m", ".jl", ".sql", ".sh", ".ps1", ".toml"}
RESULT_EXTS = {".json", ".jsonl", ".csv", ".md", ".txt"}
STATUS_FAILURES = {"failed", "failure", "error", "crashed", "aborted"}


def read_text(path: Path, decode_issues: list[dict[str, str]] | None = None) -> str:
    if not path.exists():
        return ""
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        if decode_issues is not None:
            decode_issues.append(issue("WARN", f"UTF-8 decode replacement used: {exc}", str(path)))
        return raw.decode("utf-8", errors="replace")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_text(root: Path, folders: list[str] | None = None) -> str:
    chunks: list[str] = []
    for folder in folders or ["paper", "docs", "submission"]:
        base = root / folder
        if not base.exists():
            continue
        for pattern in ["*.tex", "*.md"]:
            for path in base.rglob(pattern):
                chunks.append(f"\n\n<!-- {path.relative_to(root)} -->\n")
                chunks.append(read_text(path))
    return "".join(chunks)


def content_text(raw: str) -> str:
    kept: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%") or stripped.startswith("<!--"):
            continue
        if re.match(r"\\(?:documentclass|begin|end|title|maketitle|input|bibliographystyle|bibliography)\b", stripped):
            continue
        kept.append(stripped)
    return "\n".join(kept)


def extract_citations(text: str) -> set[str]:
    keys: set[str] = set()
    for match in CITE_RE.finditer(text):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def extract_bib_keys(root: Path) -> set[str]:
    keys: set[str] = set()
    for path in root.rglob("*.bib"):
        text = read_text(path)
        keys.update(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))
    return keys


def load_jsonl(path: Path, issues: list[dict[str, str]] | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line_no, line in enumerate(read_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            if issues is not None:
                issues.append(issue("CRITICAL", f"Malformed JSONL line {line_no}: {exc}", str(path)))
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def literature_keys(root: Path, issues: list[dict[str, str]]) -> set[str]:
    keys: set[str] = set()
    provenance_fields = ["source_db", "retrieved_at", "metadata_source"]
    verification_fields = ["doi_verified", "arxiv_verified", "url_verified", "verified"]
    for rel in ["literature/candidates.jsonl", "literature/screened.jsonl"]:
        for record in load_jsonl(root / rel, issues):
            for field in ["cite_key", "key", "id", "doi", "arxiv_id", "url"]:
                value = str(record.get(field) or "").strip()
                if value:
                    keys.add(value)
            if not any(record.get(field) for field in provenance_fields):
                issues.append(issue("WARN", "Literature record lacks provenance fields such as source_db/retrieved_at/metadata_source.", rel))
            if not any(field in record for field in verification_fields):
                issues.append(issue("WARN", "Literature record lacks DOI/arXiv/URL verification status.", rel))
    return keys


def flatten(value: Any) -> list[Any]:
    if isinstance(value, dict):
        out: list[Any] = []
        for child in value.values():
            out.extend(flatten(child))
        return out
    if isinstance(value, list):
        out = []
        for child in value:
            out.extend(flatten(child))
        return out
    return [value]


def canonical_number(value: Any) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def issue(severity: str, message: str, location: str = "") -> dict[str, str]:
    return {"severity": severity, "message": message, "location": location}


def collect_code_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for folder in ["code", "src", "analysis", "scripts"]:
        base = root / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in CODE_EXTS:
                files.append(path)
    return sorted(set(files))


def collect_result_files(root: Path) -> list[Path]:
    results = root / "results"
    if not results.exists():
        return []
    return sorted(path for path in results.rglob("*") if path.is_file() and path.suffix.lower() in RESULT_EXTS)


def validate_status(value: Any, path: Path, issues: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in {"status", "run_status"} and str(child).lower() in STATUS_FAILURES:
                issues.append(issue("CRITICAL", f"Result artifact contains failed status: {child}", str(path)))
            validate_status(child, path, issues)
    elif isinstance(value, list):
        for child in value:
            validate_status(child, path, issues)


def validate_finite(value: Any, path: Path, numbers: set[str], issues: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        for child in value.values():
            validate_finite(child, path, numbers, issues)
    elif isinstance(value, list):
        for child in value:
            validate_finite(child, path, numbers, issues)
    elif isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            issues.append(issue("CRITICAL", f"Non-finite result value found: {value}", str(path)))
        else:
            numbers.add(canonical_number(value))


def collect_result_numbers(root: Path, issues: list[dict[str, str]]) -> tuple[set[str], list[str], int, list[dict[str, Any]]]:
    numbers: set[str] = set()
    files: list[str] = []
    inferred_runs = 0
    result_records: list[dict[str, Any]] = []

    for path in collect_result_files(root):
        rel = str(path.relative_to(root))
        files.append(rel)
        if path.suffix.lower() in {".json", ".jsonl"}:
            values: list[Any] = []
            if path.suffix.lower() == ".jsonl":
                for line_no, line in enumerate(read_text(path).splitlines(), start=1):
                    if not line.strip():
                        continue
                    try:
                        values.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        issues.append(issue("CRITICAL", f"Malformed JSONL result line {line_no}: {exc}", rel))
            else:
                try:
                    values = [json.loads(read_text(path))]
                except json.JSONDecodeError as exc:
                    issues.append(issue("CRITICAL", f"Malformed JSON result file: {exc}", rel))
                    values = []
            for value in values:
                validate_status(value, path, issues)
                validate_finite(value, path, numbers, issues)
                if isinstance(value, dict):
                    value["_source_file"] = rel
                    result_records.append(value)
            inferred_runs += len(values)
        elif path.suffix.lower() == ".csv":
            try:
                with path.open("r", encoding="utf-8", newline="") as handle:
                    rows = list(csv.DictReader(handle))
            except UnicodeDecodeError as exc:
                issues.append(issue("WARN", f"CSV decode replacement needed: {exc}", rel))
                rows = []
            except OSError as exc:
                issues.append(issue("CRITICAL", f"Could not read CSV result: {exc}", rel))
                rows = []
            inferred_runs += len(rows)
            for row in rows:
                lowered_status = str(row.get("status") or row.get("run_status") or "").lower()
                if lowered_status in STATUS_FAILURES:
                    issues.append(issue("CRITICAL", f"CSV result row contains failed status: {lowered_status}", rel))
                for raw in row.values():
                    try:
                        value = float(str(raw).strip().rstrip("%"))
                    except ValueError:
                        continue
                    if not math.isfinite(value):
                        issues.append(issue("CRITICAL", f"Non-finite CSV result value found: {raw}", rel))
                    else:
                        numbers.add(canonical_number(value))
    return numbers, files, inferred_runs, result_records


def audit_result_schema(root: Path, result_records: list[dict[str, Any]], result_files: list[str], manuscript_lowered: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    needs_results = bool(result_files) or any(term in manuscript_lowered for term in EXPERIMENT_TERMS + STAT_TERMS)
    if not needs_results:
        return issues
    required = ["schema_version", "status", "seed", "command_line", "config_snapshot", "config_sha256", "log_path"]
    if result_records:
        for record in result_records:
            if "summary" in str(record.get("_source_file", "")).lower() and "raw_runs" not in record:
                issues.append(issue("CRITICAL", "Summary-like result file lacks raw run records.", "results/"))
            missing = [field for field in required if field not in record]
            if missing and str(record.get("schema_version", "")).startswith("autopilot-result"):
                issues.append(issue("CRITICAL", "Result artifact missing required schema fields: " + ", ".join(missing), "results/"))
            if str(record.get("status", "")).lower() in STATUS_FAILURES:
                issues.append(issue("CRITICAL", "Failed/crashed result artifact cannot support claims.", "results/"))
    elif result_files:
        issues.append(issue("CRITICAL", "Result files exist but no parseable result records were found.", "results/"))
    if any(term in manuscript_lowered for term in STAT_TERMS):
        support_text = "\n".join(json.dumps(record, ensure_ascii=False).lower() for record in result_records)
        stat_tokens = ["p_value", "p-value", "confidence_interval", "ci", "statistic", "sample_size", "test_name"]
        if not all(any(token in support_text for token in group) for group in [["p_value", "p-value"], ["sample_size", "n"], ["test_name", "statistic"]]):
            issues.append(issue("CRITICAL", "Statistical significance or intervals are claimed without archived statistical fields in result artifacts.", "results/"))
    return issues


def audit_code_quality(root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    code_files = collect_code_files(root)
    quality: list[dict[str, str]] = []
    naturalness: list[dict[str, str]] = []
    if not code_files:
        quality.append(issue("WARN", "No code files found; experiment code has not been scaffolded or archived.", "code/"))
        return quality, naturalness

    combined = "\n".join(read_text(path) for path in code_files)
    combined_lower = combined.lower()
    rels = [str(path.relative_to(root)) for path in code_files]

    config_path = root / "code" / "config.yaml"
    if not config_path.exists():
        quality.append(issue("WARN", "Missing code/config.yaml; experiments should expose seed, data paths, outputs, and mode.", "code/config.yaml"))
    if "seed" not in combined_lower:
        quality.append(issue("WARN", "No explicit seed found in code/config files.", "code/"))
    if "results" not in combined_lower or not re.search(r"(write_text|json\.dump|to_csv|open\()", combined):
        quality.append(issue("CRITICAL", "Experiment code does not show a clear result-saving path.", "code/"))
    if "logs" not in combined_lower and ".log" not in combined_lower:
        quality.append(issue("WARN", "No log path or log file convention found in code.", "code/"))
    if "time_estimate" not in combined_lower:
        quality.append(issue("WARN", "Pilot code should print or log TIME_ESTIMATE before main runs.", "code/"))
    if "raw_runs" not in combined_lower or "config_sha256" not in combined_lower or "command_line" not in combined_lower:
        quality.append(issue("WARN", "Code does not clearly write the required raw run/config/command evidence schema.", "code/"))

    for path in code_files:
        rel = str(path.relative_to(root))
        text = read_text(path)
        lower = text.lower()
        if MOCK_RESULT_RE.search(text):
            quality.append(issue("CRITICAL", "Mock/fake/dummy paper-facing result pattern detected.", rel))
        if path.suffix.lower() in {".py", ".r", ".R", ".do", ".m", ".jl"} and (HARDCODED_METRIC_RE.search(text) or CONSTANT_ARRAY_RE.search(text)):
            quality.append(issue("CRITICAL", "Hardcoded paper-facing metric or metric array detected in code.", rel))
        if ("random." in lower or "np.random" in lower) and "seed" not in lower:
            quality.append(issue("WARN", "Randomness appears without an obvious local seed.", rel))
        if path.suffix.lower() in {".py", ".yaml", ".yml", ".json"} and (
            "notimplementederror" in lower or "todo(project)" in lower or "replace_with" in lower
        ):
            quality.append(issue("WARN", "Code still contains explicit scaffold markers; do not cite outputs until real logic replaces them.", rel))

        generic_hits = GENERIC_NAME_RE.findall(text)
        if len(generic_hits) >= 3:
            naturalness.append(issue("WARN", "Several generic boilerplate names found: " + ", ".join(sorted(set(generic_hits))), rel))

        if path.suffix.lower() == ".py":
            lines = [line for line in text.splitlines() if line.strip()]
            comments = [line for line in lines if line.strip().startswith("#")]
            if len(lines) >= 20 and len(comments) / len(lines) > 0.35:
                naturalness.append(issue("WARN", "Comment density is high; keep comments focused on research choices and non-obvious assumptions.", rel))
            if any(OBVIOUS_COMMENT_RE.search(line) for line in comments):
                naturalness.append(issue("WARN", "Obvious narration comments detected; remove comments that restate simple code.", rel))

    if not any(path.name == "README.md" and "code" in path.parts for path in code_files):
        quality.append(issue("WARN", "Missing code/README.md with run commands and evidence policy.", "code/README.md"))
    if not any(path.name == "run_experiments.py" for path in code_files):
        quality.append(issue("WARN", "Missing a conventional experiment runner such as code/run_experiments.py.", "code/"))
    if not any(path.name == "analyze_results.py" for path in code_files):
        quality.append(issue("WARN", "Missing a result analysis/summarization script.", "code/"))

    if len(rels) == 1 and rels[0].endswith(".py") and len(read_text(code_files[0]).splitlines()) > 250:
        naturalness.append(issue("WARN", "A single large script may be mixing runner, method, metrics, and analysis.", rels[0]))

    return quality, naturalness


def normalize_role(role: str) -> str | None:
    cleaned = re.sub(r"\s+", " ", role.strip().strip(":")).lower()
    cleaned = re.sub(r"^role:\s*", "", cleaned)
    for required in REQUIRED_REVIEW_ROLES:
        if cleaned == required.lower():
            return required
    return None


def useful_text(value: Any) -> bool:
    text = str(value or "").strip()
    compact = re.sub(r"\s+", " ", text).strip().lower()
    if compact in PLACEHOLDER_TEXT:
        return False
    bullets = [line.strip().lstrip("-* ").strip().lower() for line in text.splitlines() if line.strip()]
    return any(line not in PLACEHOLDER_TEXT for line in bullets)


def extract_md_field(section: str, field: str) -> str:
    fields = ["Role", "Status", "Reviewer", "Reviewer run id", "Packet SHA256", "Evidence", "Findings", "Required fixes", "Accepted rationale"]
    pattern = re.compile(rf"(?im)^\s*{re.escape(field)}\s*:\s*(.*)$")
    match = pattern.search(section)
    if not match:
        return ""
    value = match.group(1).strip()
    start = match.end()
    next_field = re.search(r"(?im)^\s*(" + "|".join(re.escape(item) for item in fields) + r")\s*:", section[start:])
    end = start + next_field.start() if next_field else len(section)
    block = section[start:end].strip()
    return (value + "\n" + block).strip() if block else value


def parse_json_ledger(path: Path) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    warnings: list[str] = []
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}, [f"Malformed ledger JSON: {path}"]
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict) and isinstance(value.get("reviews"), list):
        rows = [item for item in value["reviews"] if isinstance(item, dict)]
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, dict):
                row = dict(item)
                row.setdefault("role", key)
                rows.append(row)
    elif isinstance(value, list):
        rows = [item for item in value if isinstance(item, dict)]

    parsed: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        role = normalize_role(str(row.get("role") or row.get("Role") or ""))
        if not role:
            continue
        record = {
            "role": role,
            "status": str(row.get("status") or row.get("Status") or "").strip().upper(),
            "reviewer": str(row.get("reviewer") or row.get("Reviewer") or "").strip(),
            "run_id": str(row.get("reviewer_run_id") or row.get("reviewerRunId") or row.get("Reviewer run id") or row.get("run_id") or "").strip(),
            "packet_sha256": str(row.get("packet_sha256") or row.get("Packet SHA256") or "").strip(),
            "evidence": row.get("evidence") or row.get("Evidence") or "",
            "findings": row.get("findings") or row.get("Findings") or "",
            "required_fixes": row.get("required_fixes") or row.get("Required fixes") or "",
            "accepted": row.get("accepted_rationale") or row.get("acceptedRationale") or row.get("Accepted rationale") or row.get("follow_up_plan") or "",
            "source": str(path),
        }
        parsed.setdefault(role, []).append(record)
    return parsed, warnings


def parse_markdown_ledger(path: Path) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    text = read_text(path)
    parsed: dict[str, list[dict[str, Any]]] = {}
    heading_re = re.compile(r"(?m)^#{2,}\s*(?:Role:\s*)?(.+?)\s*$")
    matches = list(heading_re.finditer(text))
    for index, match in enumerate(matches):
        role = normalize_role(match.group(1))
        if not role:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end]
        record = {
            "role": role,
            "status": extract_md_field(section, "Status").upper(),
            "reviewer": extract_md_field(section, "Reviewer"),
            "run_id": extract_md_field(section, "Reviewer run id"),
            "packet_sha256": extract_md_field(section, "Packet SHA256"),
            "evidence": extract_md_field(section, "Evidence"),
            "findings": extract_md_field(section, "Findings"),
            "required_fixes": extract_md_field(section, "Required fixes"),
            "accepted": extract_md_field(section, "Accepted rationale"),
            "source": str(path),
        }
        parsed.setdefault(role, []).append(record)
    return parsed, []


def load_code_review_ledgers(root: Path) -> tuple[list[Path], dict[str, list[dict[str, Any]]], list[str]]:
    paths = [path for path in [root / "audit" / "code_review_ledger.json", root / "audit" / "code_review_ledger.md"] if path.exists()]
    merged: dict[str, list[dict[str, Any]]] = {}
    warnings: list[str] = []
    for path in paths:
        parsed, local = parse_json_ledger(path) if path.suffix == ".json" else parse_markdown_ledger(path)
        warnings.extend(local)
        for role, records in parsed.items():
            merged.setdefault(role, []).extend(records)
    return paths, merged, warnings


def load_packet_hash(root: Path) -> str:
    manifest_path = root / "audit" / "code_review_packet_manifest.json"
    if manifest_path.exists():
        try:
            value = json.loads(read_text(manifest_path))
            packet_hash = str(value.get("packet_sha256") or "").strip()
            if packet_hash:
                return packet_hash
        except json.JSONDecodeError:
            return ""
    packet_path = root / "audit" / "code_review_packet.md"
    if packet_path.exists():
        return sha256_file(packet_path)
    return ""


def audit_packet_manifest(root: Path, required: bool) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not required:
        return issues
    manifest_path = root / "audit" / "code_review_packet_manifest.json"
    if not manifest_path.exists():
        issues.append(issue("CRITICAL", "Code review packet manifest is missing.", "audit/code_review_packet_manifest.json"))
        return issues
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(issue("CRITICAL", f"Malformed code review packet manifest: {exc}", "audit/code_review_packet_manifest.json"))
        return issues
    artifact_manifest = manifest.get("artifact_manifest")
    if not isinstance(artifact_manifest, list):
        issues.append(issue("CRITICAL", "Code review packet manifest lacks artifact_manifest list.", "audit/code_review_packet_manifest.json"))
        return issues
    for item in artifact_manifest:
        if not isinstance(item, dict):
            continue
        rel = str(item.get("path") or "")
        old_hash = str(item.get("sha256") or "")
        if not rel or not old_hash:
            continue
        path = root / rel
        if not path.exists():
            issues.append(issue("CRITICAL", f"Packet artifact is missing after review packet generation: {rel}", "audit/code_review_packet_manifest.json"))
            continue
        try:
            current_hash = sha256_file(path)
        except OSError as exc:
            issues.append(issue("CRITICAL", f"Could not hash packet artifact {rel}: {exc}", "audit/code_review_packet_manifest.json"))
            continue
        if current_hash != old_hash:
            issues.append(issue("CRITICAL", f"Packet artifact changed after review packet generation: {rel}", "audit/code_review_packet_manifest.json"))
    packet_path = root / "audit" / "code_review_packet.md"
    packet_hash = str(manifest.get("packet_sha256") or "")
    if packet_path.exists() and packet_hash and sha256_file(packet_path) != packet_hash:
        issues.append(issue("CRITICAL", "code_review_packet.md hash does not match manifest packet_sha256.", "audit/code_review_packet.md"))
    return issues


def code_review_required(root: Path, manuscript_lowered: str, result_files: list[str]) -> bool:
    has_result = bool(result_files)
    has_claims = any(term in manuscript_lowered for term in EXPERIMENT_TERMS + STAT_TERMS)
    code_text = "\n".join(read_text(path).lower() for path in collect_code_files(root))
    scaffold_only = "notimplementederror" in code_text and not has_result and not has_claims
    has_realish_code = bool(collect_code_files(root)) and not scaffold_only
    return has_realish_code or has_result or has_claims


def audit_multi_agent_code_review(root: Path, required: bool) -> tuple[dict[str, Any], list[dict[str, str]]]:
    ledger_paths, roles, parse_warnings = load_code_review_ledgers(root)
    packet_path = root / "audit" / "code_review_packet.md"
    packet_sha256 = load_packet_hash(root)
    review_issues: list[dict[str, str]] = []
    for warning in parse_warnings:
        review_issues.append(issue("CRITICAL", warning, "audit/code_review_ledger"))
    summary: dict[str, Any] = {
        "required": required,
        "ledger_paths": [str(path) for path in ledger_paths],
        "packet_path": str(packet_path) if packet_path.exists() else None,
        "packet_sha256": packet_sha256 or None,
        "roles_present": sorted(roles),
        "missing_roles": [],
        "role_statuses": {role: [record.get("status", "MISSING") for record in roles.get(role, [])] for role in REQUIRED_REVIEW_ROLES},
        "verdict": "NOT_REQUIRED" if not required else "PENDING",
    }
    if not required:
        return summary, review_issues

    review_issues.extend(audit_packet_manifest(root, required))

    if not packet_path.exists():
        review_issues.append(issue("CRITICAL", "Mandatory multi-agent code review packet is missing.", "audit/code_review_packet.md"))
    if not packet_sha256:
        review_issues.append(issue("CRITICAL", "Mandatory code review packet hash is missing.", "audit/code_review_packet_manifest.json"))
    if not ledger_paths:
        review_issues.append(issue("CRITICAL", "Mandatory multi-agent code review ledger is missing.", "audit/code_review_ledger.md"))
        summary["verdict"] = "BLOCK"
        return summary, review_issues
    if len(ledger_paths) > 1:
        review_issues.append(issue("CRITICAL", "Multiple code review ledgers exist; reconcile to one canonical ledger.", "audit/"))

    ledger_text = "\n".join(read_text(path).lower() for path in ledger_paths)
    if "single-agent" in ledger_text or "single agent" in ledger_text or "self-review" in ledger_text:
        review_issues.append(issue("CRITICAL", "Ledger appears to use single-agent self-review, which cannot satisfy the mandatory multi-agent gate.", "audit/"))

    missing = [role for role in REQUIRED_REVIEW_ROLES if role not in roles]
    summary["missing_roles"] = missing
    if missing:
        review_issues.append(issue("CRITICAL", "Code review ledger is missing mandatory roles: " + ", ".join(missing), "audit/code_review_ledger"))

    reviewers: list[str] = []
    run_ids: list[str] = []
    for role in REQUIRED_REVIEW_ROLES:
        records = roles.get(role, [])
        if len(records) > 1:
            review_issues.append(issue("CRITICAL", f"{role} appears more than once across ledgers.", "audit/code_review_ledger"))
        for record in records:
            status = str(record.get("status") or "").upper()
            reviewer = str(record.get("reviewer") or "").strip()
            run_id = str(record.get("run_id") or "").strip()
            packet_hash = str(record.get("packet_sha256") or "").strip()
            evidence = record.get("evidence")
            findings = record.get("findings")
            fixes = record.get("required_fixes")
            accepted = record.get("accepted")
            source = str(record.get("source") or "audit/code_review_ledger")

            if not useful_text(reviewer):
                review_issues.append(issue("CRITICAL", f"{role} lacks an independent reviewer identifier.", source))
            else:
                reviewers.append(reviewer.lower())
            if not useful_text(run_id):
                review_issues.append(issue("CRITICAL", f"{role} lacks a reviewer run/session id.", source))
            else:
                run_ids.append(run_id.lower())
            if packet_sha256 and packet_hash != packet_sha256:
                review_issues.append(issue("CRITICAL", f"{role} is not bound to the current packet SHA256.", source))
            if not useful_text(evidence):
                review_issues.append(issue("CRITICAL", f"{role} lacks non-placeholder evidence paths or commands.", source))
            if not useful_text(findings):
                review_issues.append(issue("CRITICAL", f"{role} lacks concrete findings.", source))
            if status in {"", "PENDING", "TODO", "TBD"}:
                review_issues.append(issue("CRITICAL", f"{role} is not complete: status is {status or 'MISSING'}.", source))
            elif status == "BLOCK":
                review_issues.append(issue("CRITICAL", f"{role} has unresolved BLOCK status.", source))
                if not useful_text(fixes):
                    review_issues.append(issue("CRITICAL", f"{role} has BLOCK status without required fixes.", source))
            elif status == "WARN":
                if not useful_text(accepted):
                    review_issues.append(issue("CRITICAL", f"{role} has WARN status without accepted rationale or follow-up test plan.", source))
            elif status == "PASS":
                if not useful_text(fixes):
                    # PASS may use "None", but only after evidence and findings are substantive.
                    pass
            else:
                review_issues.append(issue("CRITICAL", f"{role} has unknown status: {status}.", source))

    if len(set(run_ids)) < len(REQUIRED_REVIEW_ROLES):
        review_issues.append(issue("CRITICAL", "Ledger does not show six distinct reviewer run/session ids.", "audit/code_review_ledger"))
    if len(set(reviewers)) < len(REQUIRED_REVIEW_ROLES):
        review_issues.append(issue("CRITICAL", "Ledger does not show six distinct independent reviewers.", "audit/code_review_ledger"))

    summary["distinct_reviewer_count"] = len(set(reviewers))
    summary["distinct_run_id_count"] = len(set(run_ids))
    summary["verdict"] = "BLOCK" if any(item["severity"] == "CRITICAL" for item in review_issues) else "PASS"
    return summary, review_issues


def load_claim_map(root: Path, issues: list[dict[str, str]]) -> list[dict[str, Any]]:
    path = root / "docs" / "claim_evidence_map.json"
    if not path.exists():
        return []
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        issues.append(issue("CRITICAL", f"Malformed claim_evidence_map.json: {exc}", "docs/claim_evidence_map.json"))
        return []
    claims = value.get("claims") if isinstance(value, dict) else None
    if not isinstance(claims, list):
        issues.append(issue("CRITICAL", "claim_evidence_map.json must contain a claims list.", "docs/claim_evidence_map.json"))
        return []
    return [claim for claim in claims if isinstance(claim, dict)]


def audit_claim_map(root: Path, claims: list[dict[str, Any]]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not claims:
        issues.append(issue("WARN", "Structured claim-evidence map is empty.", "docs/claim_evidence_map.json"))
        return issues
    for claim in claims:
        claim_id = str(claim.get("id") or "unknown")
        status = str(claim.get("status") or "").upper()
        evidence = claim.get("evidence")
        if status in {"SUPPORTED", "PARTIAL"} and not evidence:
            issues.append(issue("CRITICAL", f"Claim {claim_id} is marked {status} without evidence.", "docs/claim_evidence_map.json"))
        if status == "UNSUPPORTED":
            issues.append(issue("CRITICAL", f"Claim {claim_id} is marked UNSUPPORTED.", "docs/claim_evidence_map.json"))
        if isinstance(evidence, list):
            for item in evidence:
                if not isinstance(item, dict):
                    continue
                path_value = str(item.get("path") or "").strip()
                if path_value and not (root / path_value).exists():
                    issues.append(issue("CRITICAL", f"Claim {claim_id} references missing evidence path: {path_value}", "docs/claim_evidence_map.json"))
    return issues


def safe_output_path(root: Path, out_arg: str | None, allow_outside: bool) -> Path:
    out = Path(out_arg).expanduser().resolve() if out_arg else root / "audit" / "audit_report.json"
    audit_root = (root / "audit").resolve()
    if not allow_outside and not (out == audit_root or audit_root in out.parents):
        raise SystemExit("Output path must be under <root>/audit unless --allow-outside-output is set.")
    return out


def write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    rows = [
        "# Audit Report",
        "",
        f"Verdict: {report['verdict']}",
        f"Root: {report['root']}",
        "",
        "## Summary",
        "",
        f"- Citations: {report['citation_count']}",
        f"- Screened literature records: {report['screened_literature_count']}",
        f"- Result files: {report['result_file_count']}",
        f"- Inferred runs: {report['inferred_run_count']}",
        "",
        "## Issues",
        "",
    ]
    for item in report["issues"]:
        rows.append(f"- {item['severity']}: {item['message']} ({item.get('location', '')})")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Project root to audit")
    parser.add_argument("--out", default=None, help="JSON report path; defaults to audit/audit_report.json")
    parser.add_argument("--no-write", action="store_true", help="Print only; do not write audit report files")
    parser.add_argument("--no-fail-on-block", action="store_true", help="Return exit code 0 even when verdict is BLOCK")
    parser.add_argument("--allow-outside-output", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_path = safe_output_path(root, args.out, args.allow_outside_output)
    md_out_path = out_path.with_suffix(".md")

    decode_issues: list[dict[str, str]] = []
    text = collect_text(root)
    manuscript_text = collect_text(root, ["paper", "submission"])
    lowered = text.lower()
    manuscript_lowered = content_text(manuscript_text).lower()
    citations = extract_citations(text)
    bib_keys = extract_bib_keys(root)

    issues: list[dict[str, str]] = []
    issues.extend(decode_issues)
    lit_keys = literature_keys(root, issues)
    screened = load_jsonl(root / "literature" / "screened.jsonl", issues)
    candidates = load_jsonl(root / "literature" / "candidates.jsonl", issues)
    result_numbers, result_files, inferred_runs, result_records = collect_result_numbers(root, issues)
    code_quality_issues, code_naturalness_warnings = audit_code_quality(root)
    multi_agent_code_review, code_review_issues = audit_multi_agent_code_review(
        root,
        code_review_required(root, manuscript_lowered, result_files),
    )
    claims = load_claim_map(root, issues)

    issues.extend(code_quality_issues)
    issues.extend(code_naturalness_warnings)
    issues.extend(code_review_issues)
    issues.extend(audit_result_schema(root, result_records, result_files, manuscript_lowered))
    issues.extend(audit_claim_map(root, claims))

    required = [
        "PROGRESS.md",
        "RESTRICTS.yaml",
        "research_manifest.json",
        "docs/claim_evidence_map.md",
        "docs/claim_evidence_map.json",
        "submission/submission_checklist.md",
    ]
    for rel in required:
        if not (root / rel).exists():
            issues.append(issue("CRITICAL", f"Missing required artifact: {rel}", rel))

    if len(candidates) == 0 and len(screened) == 0 and len(citations) > 0:
        issues.append(issue("CRITICAL", "Citations are present but no literature JSONL records were found.", "literature/"))

    if len(screened) < 10:
        issues.append(issue("WARN", f"Only {len(screened)} screened literature records found; broad papers usually need stronger coverage.", "literature/screened.jsonl"))

    missing_keys = sorted(key for key in citations if key not in bib_keys and key not in lit_keys)
    if missing_keys:
        issues.append(issue("CRITICAL", "Cited keys missing from BibTeX/literature records: " + ", ".join(missing_keys[:30]), "paper/"))

    if any(term in manuscript_lowered for term in EXPERIMENT_TERMS) and not result_files:
        issues.append(issue("CRITICAL", "Manuscript or docs discuss experiments/analysis but no result files were found.", "results/"))

    paper_numbers: set[str] = set()
    for raw in NUMBER_RE.findall(text):
        try:
            paper_numbers.add(canonical_number(float(raw.rstrip("%"))))
        except ValueError:
            continue
    allowed_context_numbers = {"0", "1", "2", "3", "4", "5", "6", "10", "15", "30", "64", "100", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"}
    unmatched = sorted(n for n in paper_numbers if n not in result_numbers and n not in allowed_context_numbers)
    if unmatched and result_numbers:
        issues.append(issue("WARN", "Numbers appear in text but were not matched in result files: " + ", ".join(unmatched[:40]), "paper/"))

    claim_map_md = read_text(root / "docs" / "claim_evidence_map.md").lower()
    if "unsupported" in claim_map_md:
        issues.append(issue("CRITICAL", "Claim-evidence map contains UNSUPPORTED claims.", "docs/claim_evidence_map.md"))

    if any(term in manuscript_lowered for term in SUBMISSION_TERMS):
        if len(screened) < 10:
            issues.append(issue("CRITICAL", "Submission readiness is claimed without enough screened literature records.", "literature/screened.jsonl"))
        for rel in ["submission/data_availability.md", "submission/code_availability.md", "submission/reproducibility_readme.md", "submission/submission_checklist.md"]:
            content = read_text(root / rel).strip()
            if len(content) < 80:
                issues.append(issue("CRITICAL", f"Submission readiness is claimed but {rel} is empty or too thin.", rel))

    verdict = "BLOCK" if any(item["severity"] == "CRITICAL" for item in issues) else "PASS_WITH_WARNINGS" if issues else "PASS"
    report = {
        "root": str(root),
        "verdict": verdict,
        "citation_count": len(citations),
        "bib_key_count": len(bib_keys),
        "literature_record_count": len(candidates) + len(screened),
        "screened_literature_count": len(screened),
        "result_file_count": len(result_files),
        "result_number_count": len(result_numbers),
        "inferred_run_count": inferred_runs,
        "code_quality_issues": code_quality_issues,
        "code_naturalness_warnings": code_naturalness_warnings,
        "multi_agent_code_review": multi_agent_code_review,
        "issues": issues,
    }

    if not args.no_write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_markdown_report(md_out_path, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if verdict == "BLOCK" and not args.no_fail_on_block:
        sys.exit(1)


if __name__ == "__main__":
    main()
