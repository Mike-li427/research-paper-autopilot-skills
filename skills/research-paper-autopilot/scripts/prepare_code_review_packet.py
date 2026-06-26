#!/usr/bin/env python3
"""Prepare a compact packet for mandatory multi-agent experiment-code review."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


REVIEW_ROLES = [
    "Algorithm Reviewer",
    "Experiment Design Reviewer",
    "Data Leakage Reviewer",
    "Metrics & Statistics Reviewer",
    "Reproducibility Reviewer",
    "Code Quality Reviewer",
]

EXPERIMENT_TERMS = [
    "experiment",
    "experiments",
    "baseline",
    "ablation",
    "dataset",
    "accuracy",
    "f1",
    "auc",
    "rmse",
    "coefficient",
    "regression",
    "p-value",
    "statistically significant",
]

TEXT_PATTERNS = [
    "*.py",
    "*.yaml",
    "*.yml",
    "*.json",
    "*.jsonl",
    "*.csv",
    "*.md",
    "*.txt",
    "*.log",
    "*.tex",
    "*.bib",
    "*.r",
    "*.R",
    "*.do",
    "*.m",
    "*.jl",
    "*.sql",
    "*.sh",
    "*.ps1",
    "*.toml",
    "*.ini",
    "*.cfg",
    "*.ipynb",
    "Dockerfile",
    "requirements*.txt",
    "environment*.yml",
    "pyproject.toml",
]

PACKET_FOLDERS = ["code", "src", "analysis", "scripts", "results", "logs", "docs", "paper", "audit", "figures"]
DENY_NAMES = {".env", ".netrc", "credentials", "credentials.json", "secrets.json", "token.json"}
GENERATED_AUDIT_NAMES = {
    "audit_report.json",
    "audit_report.md",
    "code_review_packet.md",
    "code_review_packet_manifest.json",
    "code_review_ledger.md",
    "code_review_ledger.json",
}
SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|authorization|bearer)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{8,})"
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def read_text(path: Path, limit: int = 12000) -> tuple[str, bool, list[str]]:
    warnings: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return f"[UNREADABLE: {exc}]", False, [f"unreadable:{path}"]
    truncated = len(raw) > limit
    raw = raw[:limit] if truncated else raw
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
        warnings.append(f"decode-replaced:{path}")
    redacted = redact(text)
    if redacted != text:
        warnings.append(f"redacted:{path}")
    if truncated:
        redacted += "\n\n[TRUNCATED: file exceeds packet limit]\n"
    return redacted, truncated, warnings


def redact(text: str) -> str:
    text = SECRET_RE.sub(lambda m: f"{m.group(1)}=<REDACTED>", text)
    text = EMAIL_RE.sub("<REDACTED_EMAIL>", text)
    return text


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def include_file(path: Path) -> bool:
    if "__pycache__" in path.parts:
        return False
    lowered = path.name.lower()
    if lowered in DENY_NAMES:
        return False
    if "audit" in path.parts and lowered in GENERATED_AUDIT_NAMES:
        return False
    if lowered.endswith((".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".7z", ".pkl", ".pickle", ".pt", ".pth", ".parquet", ".feather")):
        return False
    return True


def matches_patterns(path: Path) -> bool:
    for pattern in TEXT_PATTERNS:
        if path.match(pattern) or path.name == pattern:
            return True
    return False


def list_files(root: Path, folder: str) -> list[Path]:
    base = root / folder
    if not base.exists():
        return []
    files: list[Path] = []
    for path in base.rglob("*"):
        if path.is_file() and include_file(path) and matches_patterns(path):
            files.append(path)
    return sorted(files)


def artifact_manifest(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for folder in PACKET_FOLDERS:
        for path in list_files(root, folder):
            try:
                stat = path.stat()
                rows.append(
                    {
                        "path": str(path.relative_to(root)),
                        "size": stat.st_size,
                        "mtime_ns": stat.st_mtime_ns,
                        "sha256": sha256_file(path),
                    }
                )
            except OSError:
                rows.append({"path": str(path.relative_to(root)), "error": "stat_failed"})
    return rows


def fenced(path: Path, root: Path, limit: int = 12000, warnings: list[str] | None = None, truncations: list[str] | None = None) -> str:
    suffix = path.suffix.lstrip(".") or "text"
    text, truncated, local_warnings = read_text(path, limit)
    if warnings is not None:
        warnings.extend(str(item) for item in local_warnings)
    if truncated and truncations is not None:
        truncations.append(str(path.relative_to(root)))
    return f"### {path.relative_to(root)}\n\n```{suffix}\n{text}\n```\n"


def summarize_json(path: Path, root: Path, warnings: list[str], truncations: list[str]) -> str:
    text, truncated, local_warnings = read_text(path, 8000)
    warnings.extend(local_warnings)
    if truncated:
        truncations.append(str(path.relative_to(root)))
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return f"### {path.relative_to(root)}\n\n```text\n{text}\n```\n"
    rendered = json.dumps(value, indent=2, ensure_ascii=False)
    if len(rendered) > 8000:
        rendered = rendered[:8000] + "\n[TRUNCATED]\n"
        truncations.append(str(path.relative_to(root)))
    return f"### {path.relative_to(root)}\n\n```json\n{rendered}\n```\n"


def manuscript_experiment_passages(root: Path, warnings: list[str], truncations: list[str]) -> str:
    chunks: list[str] = []
    for path in list_files(root, "paper"):
        if path.suffix.lower() not in {".tex", ".md"}:
            continue
        text, truncated, local_warnings = read_text(path, 20000)
        warnings.extend(local_warnings)
        if truncated:
            truncations.append(str(path.relative_to(root)))
        lines = text.splitlines()
        hits: list[str] = []
        for idx, line in enumerate(lines, start=1):
            lowered = line.lower()
            if any(term in lowered for term in EXPERIMENT_TERMS):
                hits.append(f"{idx}: {line}")
        if hits:
            chunks.append(f"### {path.relative_to(root)}\n\n```text\n" + "\n".join(hits[:80]) + "\n```\n")
    return "\n".join(chunks) if chunks else "No manuscript experiment/statistics passages detected.\n"


def tree_from_manifest(manifest: list[dict[str, Any]]) -> str:
    rows = [str(item.get("path")) for item in manifest]
    return "\n".join(rows[:500]) if rows else "No project files found."


def packet_body(root: Path) -> tuple[str, dict[str, Any]]:
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    manifest = artifact_manifest(root)
    warnings: list[str] = []
    truncations: list[str] = []

    parts: list[str] = [
        "# Code Review Packet\n\n",
        "This packet is for mandatory multi-agent code review before experiment or analysis results can support paper claims.\n\n",
        "## Packet Metadata\n\n",
        "```json\n"
        + json.dumps(
            {
                "generated_at": generated,
                "root": str(root),
                "artifact_count": len(manifest),
                "note": "The final packet_sha256 is stored in audit/code_review_packet_manifest.json and printed by this script.",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n```\n\n",
        "## Required Reviewer Roles\n\n",
        "\n".join(f"- {role}" for role in REVIEW_ROLES) + "\n\n",
        "## Artifact Manifest\n\n```json\n" + json.dumps(manifest, indent=2, ensure_ascii=False) + "\n```\n\n",
        "## Project File Index\n\n```text\n" + tree_from_manifest(manifest) + "\n```\n\n",
    ]

    for rel in [
        "research_manifest.json",
        "RESTRICTS.yaml",
        "docs/claim_evidence_map.json",
        "docs/claim_evidence_map.md",
        "docs/experiment_or_analysis_plan.md",
        "audit/audit_report.json",
    ]:
        path = root / rel
        if path.exists() and include_file(path):
            parts.append(fenced(path, root, 10000, warnings, truncations))

    for title, folder in [
        ("Code And Analysis Files", "code"),
        ("Source Or Analysis Files", "src"),
        ("Analysis Directory", "analysis"),
        ("Result Files", "results"),
        ("Logs", "logs"),
    ]:
        files = list_files(root, folder)
        parts.append(f"## {title}\n\n")
        if files:
            for path in files[:80]:
                if path.suffix == ".json":
                    parts.append(summarize_json(path, root, warnings, truncations))
                else:
                    parts.append(fenced(path, root, 16000 if folder in {"code", "src", "analysis"} else 8000, warnings, truncations))
        else:
            parts.append(f"No {folder} files found.\n\n")

    parts.append("## Manuscript Experiment/Statistics Passages\n\n")
    parts.append(manuscript_experiment_passages(root, warnings, truncations))

    parts.append(
        "\n## Reviewer Output Contract\n\n"
        "Each reviewer must return Role, Status (PASS/WARN/BLOCK), Reviewer, Reviewer run id, Packet SHA256, Evidence, Findings, Required fixes, and Accepted rationale.\n"
        "Any BLOCK, unresolved WARN, missing evidence/findings, missing reviewer run id, or stale Packet SHA256 prevents result-to-paper transfer.\n"
    )

    parts.append("## Truncation Inventory\n\n```json\n" + json.dumps(sorted(set(truncations)), indent=2, ensure_ascii=False) + "\n```\n\n")
    parts.append("## Redaction And Decode Warnings\n\n```json\n" + json.dumps(sorted(set(warnings)), indent=2, ensure_ascii=False) + "\n```\n")

    packet = "".join(parts)
    packet = re.sub(r"\n{4,}", "\n\n\n", packet)
    metadata = {
        "generated_at": generated,
        "artifact_manifest": manifest,
        "truncations": sorted(set(truncations)),
        "warnings": sorted(set(warnings)),
    }
    return packet, metadata


def safe_output_path(root: Path, out_arg: str | None, allow_outside: bool) -> Path:
    out = Path(out_arg).expanduser().resolve() if out_arg else root / "audit" / "code_review_packet.md"
    audit_root = (root / "audit").resolve()
    if not allow_outside and not (out == audit_root or audit_root in out.parents):
        raise SystemExit("Output path must be under <root>/audit unless --allow-outside-output is set.")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Research project root")
    parser.add_argument("--out", default=None, help="Output packet path; defaults to audit/code_review_packet.md")
    parser.add_argument("--manifest-out", default=None, help="Metadata JSON path; defaults to audit/code_review_packet_manifest.json")
    parser.add_argument("--allow-outside-output", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print packet JSON summary without writing files")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out = safe_output_path(root, args.out, args.allow_outside_output)
    manifest_out = safe_output_path(root, args.manifest_out, args.allow_outside_output) if args.manifest_out else root / "audit" / "code_review_packet_manifest.json"
    packet, metadata = packet_body(root)
    packet_bytes = packet.encode("utf-8")
    packet_sha256 = hashlib.sha256(packet_bytes).hexdigest()
    metadata["packet_sha256"] = packet_sha256

    if not args.dry_run:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(packet_bytes)
        manifest_out.parent.mkdir(parents=True, exist_ok=True)
        manifest_out.write_bytes((json.dumps(metadata, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    print(
        json.dumps(
            {
                "root": str(root),
                "out": str(out),
                "manifest_out": str(manifest_out),
                "packet_sha256": packet_sha256,
                "chars": len(packet),
                "artifact_count": len(metadata["artifact_manifest"]),
                "truncations": metadata["truncations"],
                "warnings": metadata["warnings"],
                "dry_run": args.dry_run,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
