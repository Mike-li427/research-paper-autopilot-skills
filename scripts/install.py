#!/usr/bin/env python3
"""Install bundled Codex skills into a local Codex home."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"


def default_codex_home() -> Path:
    return Path.home() / ".codex"


def load_manifest() -> dict:
    path = REPO_ROOT / "skills_manifest.json"
    if not path.exists():
        return {"skills": []}
    return json.loads(path.read_text(encoding="utf-8"))


def copy_skill(src: Path, dst: Path, force: bool) -> str:
    if dst.exists():
        if not force:
            return "skipped"
        shutil.rmtree(dst)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db")
    shutil.copytree(src, dst, ignore=ignore)
    return "installed"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", default=None, help="Codex home directory. Defaults to ~/.codex")
    parser.add_argument("--skills-dir", default=None, help="Destination skills directory. Overrides --codex-home")
    parser.add_argument("--only", nargs="*", default=None, help="Install only these skill directory names")
    parser.add_argument("--force", action="store_true", help="Replace existing installed skill directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed")
    args = parser.parse_args()

    if not SKILLS_DIR.exists():
        raise SystemExit(f"Bundled skills directory not found: {SKILLS_DIR}")

    dest_skills = Path(args.skills_dir).expanduser().resolve() if args.skills_dir else Path(args.codex_home).expanduser().resolve() / "skills" if args.codex_home else default_codex_home() / "skills"
    selected = set(args.only or [])
    manifest = load_manifest()
    manifest_names = [item["directory"] for item in manifest.get("skills", []) if isinstance(item, dict) and item.get("directory")]
    skill_dirs = [SKILLS_DIR / name for name in manifest_names if (SKILLS_DIR / name).is_dir()]
    if not skill_dirs:
        skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if selected:
        skill_dirs = [path for path in skill_dirs if path.name in selected]
        missing = sorted(selected - {path.name for path in skill_dirs})
        if missing:
            raise SystemExit("Requested skills not found in bundle: " + ", ".join(missing))

    actions = []
    for src in skill_dirs:
        if not (src / "SKILL.md").exists():
            continue
        dst = dest_skills / src.name
        status = "would-install" if args.dry_run and not dst.exists() else "would-replace" if args.dry_run and args.force else "would-skip" if args.dry_run else copy_skill(src, dst, args.force)
        actions.append({"skill": src.name, "destination": str(dst), "status": status})

    if not args.dry_run:
        dest_skills.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"destination": str(dest_skills), "actions": actions}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
