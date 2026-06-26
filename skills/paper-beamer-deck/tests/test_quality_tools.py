from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def load_script(name: str) -> ModuleType:
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS_DIR))
    return module


class QualityToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = load_script("generate_quality_report")
        self.sources = load_script("check_deck_sources")
        self.visual = load_script("check_visual_qa")
        self.doctor = load_script("doctor")

    def make_deck(self, root: str) -> str:
        deck = os.path.join(root, "slides", "demo")
        os.makedirs(os.path.join(deck, "_preview"), exist_ok=True)
        with open(os.path.join(deck, "main.tex"), "w", encoding="utf-8") as fh:
            fh.write("\\includegraphics{figures/fig.png}\n% From the paper.\n")
        with open(os.path.join(deck, "notes.md"), "w", encoding="utf-8") as fh:
            fh.write(
                "## Source Traceability\n\n"
                "| Slide (number / title) | Claim / Result / Assumption / Limitation | Source (section / figure / table / page) |\n"
                "|---|---|---|\n"
                "| 1 / Result | Synthetic claim | Figure 1, p. 1 |\n"
            )
        with open(os.path.join(deck, "main.log"), "w", encoding="utf-8") as fh:
            fh.write("Output written on main.pdf (1 page).\n")
        with open(os.path.join(deck, "main.pdf"), "wb") as fh:
            fh.write(b"%PDF-1.4\n")
        with open(os.path.join(deck, "_preview", "main-page-001.png"), "wb") as fh:
            fh.write(b"not-a-real-png-but-name-is-enough")
        return deck

    def test_quality_report_and_checks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            deck = self.make_deck(d)
            out = os.path.join(deck, "quality_report.md")
            self.assertEqual(self.report.main(["generate_quality_report.py", deck, "--out", out]), 0)
            self.assertTrue(os.path.exists(out))
            self.assertEqual(self.sources.main(["check_deck_sources.py", deck]), 0)
            self.assertEqual(self.visual.main(["check_visual_qa.py", deck]), 0)

    def test_doctor_reports_workspace_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            for rel in ("papers", "slides", "analysis", "skills"):
                os.makedirs(os.path.join(d, rel), exist_ok=True)
            for rel in ("theme.tex", "beamerthemeSimple.sty"):
                Path(os.path.join(d, rel)).write_text("", encoding="utf-8")
            ok, issues = self.doctor.check_workspace(d)
            self.assertTrue(any("papers/" in item for item in ok))
            self.assertTrue(any("xelatex" in item for item in issues + ok))


if __name__ == "__main__":
    unittest.main()
