"""Smoke tests for the deterministic figure extraction CLI.

These tests exercise fallback behavior without requiring pdffigures2/GROBID.
They do require PyMuPDF, which is the required dependency for this pipeline.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
FIGURE_EXTRACTION_DIR = ROOT / "scripts" / "figure_extraction"


def load_figure_extraction_script(name: str) -> ModuleType:
    path = FIGURE_EXTRACTION_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(FIGURE_EXTRACTION_DIR))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(FIGURE_EXTRACTION_DIR))
    return module


class FigureExtractionFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            import fitz  # type: ignore
        except ImportError as exc:
            self.skipTest(f"PyMuPDF not installed: {exc}")
        self.fitz = fitz
        self.extract_figures = load_figure_extraction_script("extract_figures")
        self.verify_figures = load_figure_extraction_script("verify_figures")
        self.select_figures = load_figure_extraction_script("select_figures")

    def make_sample_pdf(self, path: str) -> None:
        doc = self.fitz.open()
        page = doc.new_page(width=300, height=240)
        page.draw_rect(self.fitz.Rect(72, 60, 220, 150), color=(0, 0, 0), width=1.5)
        page.insert_text((72, 180), "Figure 1: A vector-only test figure.", fontsize=10)
        doc.save(path)
        doc.close()

    def make_synthetic_academic_pdf(self, path: str) -> None:
        """Create a copyright-safe mini paper-like PDF fixture."""
        doc = self.fitz.open()
        page = doc.new_page(width=420, height=560)
        page.insert_text((54, 54), "A Tiny Synthetic Paper for Figure Extraction", fontsize=14)
        page.insert_text((54, 84), "Abstract. This fixture is generated in tests and contains no copied paper text.", fontsize=9)
        page.draw_rect(self.fitz.Rect(70, 130, 350, 250), color=(0, 0, 0), width=1.2)
        page.draw_line((90, 230), (330, 150), color=(0, 0, 0), width=1)
        page.insert_text((72, 270), "Figure 1: Synthetic trend plot generated for smoke testing.", fontsize=9)
        page.draw_rect(self.fitz.Rect(70, 330, 350, 430), color=(0, 0, 0), width=1)
        for y in (355, 380, 405):
            page.draw_line((70, y), (350, y), color=(0, 0, 0), width=0.6)
        for x in (160, 255):
            page.draw_line((x, 330), (x, 430), color=(0, 0, 0), width=0.6)
        page.insert_text((72, 452), "Table 1: Synthetic table generated for smoke testing.", fontsize=9)
        doc.save(path)
        doc.close()

    def test_fallback_renders_pages_and_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "paper.pdf")
            out = os.path.join(d, "build", "figures")
            self.make_sample_pdf(pdf)

            with mock.patch.object(self.extract_figures, "run_docling", return_value=([], "docling unavailable")):
                with mock.patch.object(self.extract_figures.shutil, "which", return_value=None):
                    rc = self.extract_figures.main(
                        ["extract_figures.py", pdf, "--out", out, "--dpi", "72"]
                    )

            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isdir(out))
            self.assertTrue(os.path.exists(os.path.join(out, "pages", "page_001.png")))
            self.assertTrue(os.path.exists(os.path.join(out, "previews", "index.html")))

            manifest_path = os.path.join(out, "figures.json")
            self.assertTrue(os.path.exists(manifest_path))
            with open(manifest_path, "r", encoding="utf-8") as fh:
                manifest = json.load(fh)

            self.assertEqual(manifest["extractor"]["primary"], "docling")
            self.assertEqual(manifest["extractor"]["status"], "fallback")
            self.assertEqual(manifest["extractor"]["attempts"][0]["backend"], "docling")
            self.assertEqual(len(manifest["pages"]), 1)
            self.assertGreaterEqual(len(manifest["figures"]), 1)
            self.assertEqual(manifest["figures"][0]["status"], "needs_manual_review")
            self.assertIsNone(manifest["figures"][0]["image_path"])
            self.assertTrue(os.path.exists(os.path.join(out, "figure_overrides.example.json")))

    def test_pdffigures2_backend_can_skip_docling(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "paper.pdf")
            out = os.path.join(d, "build", "figures")
            self.make_sample_pdf(pdf)

            with mock.patch.object(self.extract_figures, "run_docling") as run_docling:
                with mock.patch.object(self.extract_figures.shutil, "which", return_value=None):
                    rc = self.extract_figures.main(
                        [
                            "extract_figures.py",
                            pdf,
                            "--out",
                            out,
                            "--dpi",
                            "72",
                            "--backend",
                            "pdffigures2",
                        ]
                    )

            self.assertEqual(rc, 0)
            run_docling.assert_not_called()
            with open(os.path.join(out, "figures.json"), "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            self.assertEqual(manifest["extractor"]["primary"], "pdffigures2")
            self.assertEqual(manifest["extractor"]["status"], "fallback")

    def test_docling_document_records_become_crop_candidates(self) -> None:
        class FakeBBox:
            def __init__(self) -> None:
                self.values = [70.0, 181.0, 221.0, 88.0]

            def to_top_left_origin(self, page_height: float) -> "FakeBBox":
                converted = FakeBBox()
                converted.values = [
                    self.values[0],
                    page_height - self.values[1],
                    self.values[2],
                    page_height - self.values[3],
                ]
                return converted

            def as_tuple(self) -> tuple[float, float, float, float]:
                return tuple(self.values)

        class FakeProv:
            page_no = 1
            bbox = FakeBBox()

        class FakeLabel:
            value = "picture"

        class FakeText:
            text = "Figure 1: A vector-only test figure."

        class FakeRef:
            def resolve(self, document):
                return FakeText()

        class FakePicture:
            self_ref = "#/pictures/0"
            label = FakeLabel()
            prov = [FakeProv()]
            captions = [FakeRef()]

        class FakeTable:
            self_ref = "#/tables/0"
            label = type("FakeLabel", (), {"value": "table"})()
            prov = [FakeProv()]
            captions = [type("FakeRef", (), {"resolve": lambda self, document: type("FakeText", (), {"text": "Table 1: Synthetic results."})()})()]

            def export_to_markdown(self) -> str:
                return "| A | B |\n|---|---|\n| 1 | 2 |"

            def export_to_html(self) -> str:
                return "<table><tr><td>1</td><td>2</td></tr></table>"

        class FakeSize:
            height = 240.0

        class FakePage:
            size = FakeSize()

        class FakeDocument:
            pictures = [FakePicture()]
            tables = [FakeTable()]
            pages = {1: FakePage()}

        candidates = self.extract_figures.parse_docling_document(FakeDocument())

        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].label, "Figure 1")
        self.assertEqual(candidates[0].page, 1)
        self.assertEqual(candidates[0].bbox, [70.0, 59.0, 221.0, 152.0])
        self.assertEqual(candidates[0].method, "docling")
        self.assertEqual(candidates[0].status, "pending_crop")
        self.assertEqual(candidates[1].label, "Table 1")
        self.assertEqual(candidates[1].kind, "table")
        self.assertIn("markdown", candidates[1].sidecar_data)

    def test_docling_backend_crop_success(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "paper.pdf")
            out = os.path.join(d, "build", "figures")
            self.make_sample_pdf(pdf)
            candidate = self.extract_figures.FigureCandidate(
                index=1,
                label="Figure 1",
                page=1,
                bbox=[72, 60, 220, 150],
                caption="Figure 1: A vector-only test figure.",
                kind="picture",
                method="docling",
                status="pending_crop",
            )

            with mock.patch.object(self.extract_figures, "run_docling", return_value=([candidate], None)):
                rc = self.extract_figures.main(
                    ["extract_figures.py", pdf, "--out", out, "--dpi", "72"]
                )

            self.assertEqual(rc, 0)
            with open(os.path.join(out, "figures.json"), "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            figure = manifest["figures"][0]
            self.assertEqual(manifest["extractor"]["primary"], "docling")
            self.assertEqual(figure["status"], "ok")
            self.assertEqual(figure["method"], "docling+render_crop")
            self.assertTrue(os.path.exists(os.path.join(out, figure["image_path"])))
            with open(os.path.join(out, "previews", "index.html"), "r", encoding="utf-8") as fh:
                preview = fh.read()
            self.assertIn("BBox on rendered page", preview)

    def test_manual_override_crops_without_layout_extractor(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "paper.pdf")
            out = os.path.join(d, "build", "figures")
            overrides = os.path.join(d, "figure_overrides.json")
            self.make_sample_pdf(pdf)
            with open(overrides, "w", encoding="utf-8") as fh:
                json.dump(
                    [
                        {
                            "label": "Figure 1",
                            "page": 1,
                            "bbox": [72, 60, 220, 150],
                            "caption": "A vector-only test figure.",
                        }
                    ],
                    fh,
                )

            with mock.patch.object(self.extract_figures, "run_docling", return_value=([], "docling unavailable")):
                with mock.patch.object(self.extract_figures.shutil, "which", return_value=None):
                    rc = self.extract_figures.main(
                        [
                            "extract_figures.py",
                            pdf,
                            "--out",
                            out,
                            "--overrides",
                            overrides,
                            "--dpi",
                            "72",
                        ]
                    )

            self.assertEqual(rc, 0)
            with open(os.path.join(out, "figures.json"), "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            figure = manifest["figures"][0]
            self.assertEqual(figure["status"], "ok")
            self.assertEqual(figure["method"], "manual_override+render_crop")
            self.assertTrue(os.path.exists(os.path.join(out, figure["image_path"])))
            self.assertEqual(self.verify_figures.main(["verify_figures.py", os.path.join(out, "figures.json")]), 0)

            deck_figures = os.path.join(d, "slides", "demo", "figures")
            rc = self.select_figures.main(
                [
                    "select_figures.py",
                    os.path.join(out, "figures.json"),
                    "--labels",
                    "Figure 1",
                    "--copy-to",
                    deck_figures,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(os.listdir(deck_figures))

    def test_manual_override_crops_with_backend_none(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "paper.pdf")
            out = os.path.join(d, "build", "figures")
            overrides = os.path.join(d, "figure_overrides.json")
            self.make_sample_pdf(pdf)
            with open(overrides, "w", encoding="utf-8") as fh:
                json.dump(
                    [
                        {
                            "label": "Figure 1",
                            "page": 1,
                            "bbox": [72, 60, 220, 150],
                            "caption": "A vector-only test figure.",
                        }
                    ],
                    fh,
                )


            rc = self.extract_figures.main(
                [
                    "extract_figures.py",
                    pdf,
                    "--out",
                    out,
                    "--overrides",
                    overrides,
                    "--dpi",
                    "72",
                    "--backend",
                    "none",
                ]
            )

            self.assertEqual(rc, 0)
            with open(os.path.join(out, "figures.json"), "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            figure = manifest["figures"][0]
            self.assertEqual(figure["status"], "ok")
            self.assertEqual(figure["method"], "manual_override+render_crop")
            self.assertTrue(os.path.exists(os.path.join(out, figure["image_path"])))

    def test_type_and_area_filters_record_filtered_entries(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "paper.pdf")
            out = os.path.join(d, "build", "figures")
            self.make_sample_pdf(pdf)
            small = self.extract_figures.FigureCandidate(
                index=1,
                label="Figure 1",
                page=1,
                bbox=[72, 60, 75, 63],
                caption="Figure 1: Too small.",
                kind="picture",
                method="docling",
                status="pending_crop",
            )
            table = self.extract_figures.FigureCandidate(
                index=2,
                label="Table 1",
                page=1,
                bbox=[72, 60, 220, 150],
                caption="Table 1: Kept.",
                kind="table",
                method="docling",
                status="pending_crop",
                sidecar_data={"markdown": "| A | B |\n|---|---|\n| 1 | 2 |"},
            )

            with mock.patch.object(self.extract_figures, "run_docling", return_value=([small, table], None)):
                rc = self.extract_figures.main(
                    [
                        "extract_figures.py",
                        pdf,
                        "--out",
                        out,
                        "--dpi",
                        "72",
                        "--type",
                        "table",
                        "--min-area-ratio",
                        "0.001",
                    ]
                )

            self.assertEqual(rc, 0)
            with open(os.path.join(out, "figures.json"), "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            self.assertEqual(len(manifest["figures"]), 1)
            self.assertEqual(manifest["figures"][0]["label"], "Table 1")
            self.assertIn("markdown", manifest["figures"][0]["data_paths"])
            self.assertTrue(os.path.exists(os.path.join(out, manifest["figures"][0]["data_paths"]["markdown"])))
            self.assertEqual(len(manifest["filtered"]), 1)
            self.assertIn("type", manifest["filtered"][0]["filter_reason"])

    def test_copyright_safe_synthetic_pdf_fixture_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "synthetic-paper.pdf")
            out = os.path.join(d, "build", "figures")
            self.make_synthetic_academic_pdf(pdf)

            rc = self.extract_figures.main(
                ["extract_figures.py", pdf, "--out", out, "--dpi", "72", "--backend", "none"]
            )

            self.assertEqual(rc, 0)
            with open(os.path.join(out, "figures.json"), "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            labels = {figure["label"] for figure in manifest["figures"]}
            self.assertIn("Figure 1", labels)
            self.assertIn("Table 1", labels)

    @unittest.skipUnless(
        os.environ.get("PAPER_BEAMER_RUN_DOCLING_SMOKE") == "1",
        "set PAPER_BEAMER_RUN_DOCLING_SMOKE=1 to run Docling on the synthetic PDF fixture",
    )
    def test_optional_docling_synthetic_pdf_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdf = os.path.join(d, "synthetic-paper.pdf")
            out = os.path.join(d, "build", "figures")
            self.make_synthetic_academic_pdf(pdf)

            rc = self.extract_figures.main(
                ["extract_figures.py", pdf, "--out", out, "--dpi", "72", "--backend", "docling"]
            )

            self.assertEqual(rc, 0)
            with open(os.path.join(out, "figures.json"), "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            self.assertEqual(manifest["extractor"]["primary"], "docling")


if __name__ == "__main__":
    unittest.main()
