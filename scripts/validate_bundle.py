#!/usr/bin/env python3
"""Validate the open-source research skills bundle."""

from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return [f"{path.name}: missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return [f"{path.name}: missing YAML frontmatter"]
    frontmatter = match.group(1)
    if not re.search(r"(?m)^name:\s*\S+", frontmatter):
        errors.append(f"{path.name}: missing frontmatter name")
    if not re.search(r"(?m)^description:\s*.+", frontmatter):
        errors.append(f"{path.name}: missing frontmatter description")
    return errors


def main() -> None:
    errors: list[str] = []
    if not SKILLS_DIR.exists():
        errors.append(f"missing skills directory: {SKILLS_DIR}")
    else:
        for path in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
            errors.extend(validate_skill(path))

    autopilot_scripts = SKILLS_DIR / "research-paper-autopilot" / "scripts"
    for script in [
        "scaffold_autopilot_project.py",
        "prepare_code_review_packet.py",
        "audit_autopilot_project.py",
    ]:
        path = autopilot_scripts / script
        if path.exists():
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"{script}: {exc.msg}")
        else:
            errors.append(f"missing autopilot script: {script}")

    if errors:
        print("Bundle validation failed:")
        for item in errors:
            print(f"- {item}")
        sys.exit(1)
    print("Bundle validation passed.")


if __name__ == "__main__":
    main()
