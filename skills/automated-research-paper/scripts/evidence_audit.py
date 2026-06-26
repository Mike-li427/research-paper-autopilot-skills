#!/usr/bin/env python3
"""Heuristic method-evidence consistency audit for research paper projects."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any


CITE_RE = re.compile(r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear)\{([^}]+)\}")
NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?%?", re.IGNORECASE)
STAT_TERMS = ["t-test", "ttest", "anova", "p-value", "p value", "statistically significant"]


def read_text_files(root: Path) -> str:
    chunks: list[str] = []
    for suffix in ("*.tex", "*.md"):
        for path in root.rglob(suffix):
            chunks.append(f"\n\n<!-- {path} -->\n")
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "".join(chunks)


def extract_citations(text: str) -> set[str]:
    keys: set[str] = set()
    for match in CITE_RE.finditer(text):
        for key in match.group(1).split(","):
            cleaned = key.strip()
            if cleaned:
                keys.add(cleaned)
    return keys


def extract_bib_keys(root: Path) -> set[str]:
    keys: set[str] = set()
    for path in root.rglob("*.bib"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        keys.update(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))
    return keys


def flatten_json(value: Any) -> list[Any]:
    if isinstance(value, dict):
        out: list[Any] = []
        for child in value.values():
            out.extend(flatten_json(child))
        return out
    if isinstance(value, list):
        out = []
        for child in value:
            out.extend(flatten_json(child))
        return out
    return [value]


def load_result_numbers(root: Path) -> tuple[set[str], int, list[str]]:
    numbers: set[str] = set()
    result_files: list[str] = []
    run_count = 0
    if not root.exists():
        return numbers, run_count, result_files

    for path in list(root.rglob("*.json")) + list(root.rglob("*.jsonl")):
        result_files.append(str(path))
        try:
            if path.suffix == ".jsonl":
                values = []
                with path.open("r", encoding="utf-8") as fh:
                    for line in fh:
                        if line.strip():
                            values.append(json.loads(line))
            else:
                values = [json.loads(path.read_text(encoding="utf-8"))]
        except (json.JSONDecodeError, OSError):
            continue
        for value in flatten_json(values):
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                numbers.add(canonical_number(value))
        run_count += count_runs(values)

    for path in root.rglob("*.csv"):
        result_files.append(str(path))
        try:
            with path.open("r", encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
        except OSError:
            continue
        run_count += len(rows)
        for row in rows:
            for value in row.values():
                try:
                    number = float(str(value).strip().rstrip("%"))
                except ValueError:
                    continue
                if math.isfinite(number):
                    numbers.add(canonical_number(number))

    return numbers, run_count, result_files


def canonical_number(value: Any) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def count_runs(values: Any) -> int:
    flat = flatten_json(values)
    count = 0
    for item in flat:
        if isinstance(item, str) and item.lower() in {"completed", "success", "failed"}:
            count += 1
    if count:
        return count
    if isinstance(values, list):
        return len(values)
    return 1


def load_literature_keys(path: Path | None) -> set[str]:
    keys: set[str] = set()
    if path is None or not path.exists():
        return keys
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = str(record.get("cite_key") or "").strip()
            if key:
                keys.add(key)
    return keys


def severity(issue: str) -> str:
    if issue.startswith("CRITICAL"):
        return "CRITICAL"
    if issue.startswith("WARN"):
        return "WARN"
    return "INFO"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--literature", default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    paper_root = Path(args.paper)
    results_root = Path(args.results)
    literature_path = Path(args.literature) if args.literature else None

    text = read_text_files(paper_root)
    citations = extract_citations(text)
    bib_keys = extract_bib_keys(paper_root.parent)
    literature_keys = load_literature_keys(literature_path)
    result_numbers, run_count, result_files = load_result_numbers(results_root)

    issues: list[str] = []
    if not result_files:
        issues.append("CRITICAL: no result files found for paper evidence.")

    missing_bib = sorted(key for key in citations if key not in bib_keys and key not in literature_keys)
    if missing_bib:
        issues.append(f"CRITICAL: cited keys missing from .bib/literature records: {', '.join(missing_bib[:30])}")

    if len(citations) < 15:
        issues.append(f"WARN: only {len(citations)} citation keys detected; top-conference papers usually need broader related work.")

    lowered = text.lower()
    if any(term in lowered for term in STAT_TERMS):
        stat_evidence = any(
            token in lowered or token in " ".join(result_files).lower()
            for token in ["p_value", "p-value", "anova", "ttest", "t_test"]
        )
        if not stat_evidence:
            issues.append("CRITICAL: paper mentions statistical testing/significance but no obvious statistical evidence was found.")

    paper_numbers = set()
    for raw in NUMBER_RE.findall(text):
        stripped = raw.rstrip("%")
        try:
            paper_numbers.add(canonical_number(float(stripped)))
        except ValueError:
            continue
    suspicious = sorted(
        n for n in paper_numbers
        if n not in result_numbers and n not in {"0", "1", "2", "3", "4", "5", "10", "100", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"}
    )
    if suspicious and result_numbers:
        issues.append(
            "WARN: numeric values appear in the paper but were not matched exactly in result files: "
            + ", ".join(suspicious[:40])
        )

    if re.search(r"\b(we run|we ran|experiments? include|trials?|seeds?)\b", lowered) and run_count == 0:
        issues.append("CRITICAL: paper appears to discuss experiments but no run count could be inferred from results.")

    report = {
        "paper": str(paper_root),
        "results": str(results_root),
        "literature": str(literature_path) if literature_path else None,
        "result_files": result_files,
        "result_number_count": len(result_numbers),
        "inferred_run_count": run_count,
        "citation_count": len(citations),
        "issues": [{"severity": severity(issue), "message": issue} for issue in issues],
        "verdict": "BLOCK" if any(issue.startswith("CRITICAL") for issue in issues) else "PASS_WITH_WARNINGS" if issues else "PASS",
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
