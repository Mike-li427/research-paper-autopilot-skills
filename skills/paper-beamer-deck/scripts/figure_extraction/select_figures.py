#!/usr/bin/env python3
"""Copy selected manifest figures into a Beamer deck figure directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from typing import Any


def load_manifest(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    return data


def split_spec(spec: str | None) -> set[str]:
    if spec is None or not spec.strip():
        return set()
    return {part.strip().lower() for part in spec.split(",") if part.strip()}


def parse_indices(spec: str | None) -> set[int]:
    return {int(part) for part in split_spec(spec)}


def select_figures(
    manifest_path: str,
    labels: set[str],
    indices: set[int],
    out_dir: str,
) -> list[dict[str, Any]]:
    manifest = load_manifest(manifest_path)
    root = os.path.dirname(manifest_path)
    selected: list[dict[str, Any]] = []
    for figure in manifest.get("figures", []):
        if not isinstance(figure, dict) or figure.get("status") != "ok":
            continue
        label = str(figure.get("label") or "").lower()
        index = int(figure.get("index") or 0)
        if labels and label not in labels:
            continue
        if indices and index not in indices:
            continue
        if not labels and not indices:
            continue
        image_path = figure.get("image_path")
        if not image_path:
            raise ValueError(f"selected figure {index} has no image_path")
        src = os.path.join(root, image_path)
        if not os.path.exists(src):
            raise FileNotFoundError(src)
        os.makedirs(out_dir, exist_ok=True)
        dest = os.path.join(out_dir, os.path.basename(image_path))
        shutil.copy2(src, dest)
        selected.append({**figure, "copied_to": dest})
    return selected


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Copy selected extracted figures into a deck.")
    parser.add_argument("figures_json", help="path to figures.json")
    parser.add_argument("--labels", default=None, help='comma-separated labels, e.g. "Figure 1,Table 2"')
    parser.add_argument("--indices", default=None, help='comma-separated manifest indices, e.g. "1,3,5"')
    parser.add_argument("--copy-to", required=True, help="destination figure directory")
    args = parser.parse_args(argv[1:])

    try:
        selected = select_figures(
            args.figures_json,
            labels=split_spec(args.labels),
            indices=parse_indices(args.indices),
            out_dir=args.copy_to,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not selected:
        print("No status=ok figures matched the selection.", file=sys.stderr)
        return 1

    for figure in selected:
        rel = os.path.relpath(figure["copied_to"], args.copy_to).replace(os.sep, "/")
        print(f"{figure.get('label') or figure.get('index')}: {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
