#!/usr/bin/env python3
"""Unit tests for the generalized Markdown renderer."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List, Sequence
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
RENDERER_PATH = (
    REPO_ROOT / "skills/swied-markdown-renderer/scripts/render.py"
)
SPEC = importlib.util.spec_from_file_location(
    "swied_markdown_renderer", RENDERER_PATH
)
assert SPEC is not None and SPEC.loader is not None
RENDERER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RENDERER
SPEC.loader.exec_module(RENDERER)


def code_block(language: str, code: str) -> dict:
    return {
        "t": "CodeBlock",
        "c": [["", [language], []], code],
    }


class OptionTests(unittest.TestCase):
    def test_defaults_to_pdf_when_output_is_omitted(self) -> None:
        source, output, remaining = RENDERER.determine_paths(
            ["notes.md", "--toc"]
        )

        self.assertEqual(source, Path("notes.md"))
        self.assertEqual(output, Path("notes.pdf"))
        self.assertEqual(remaining, ["--toc"])

    def test_custom_options_are_removed_from_pandoc_options(self) -> None:
        options, remaining = RENDERER.parse_custom_options(
            [
                "--inspect",
                "--diagram-format=png",
                "--render-math",
                "native",
                "--toc",
            ]
        )

        self.assertTrue(options.inspect)
        self.assertEqual(options.diagram_format, "png")
        self.assertEqual(options.math_rendering, "native")
        self.assertEqual(remaining, ["--toc"])

    def test_rejects_pandoc_output_override(self) -> None:
        with self.assertRaises(RENDERER.RenderError):
            RENDERER.validate_pandoc_options(["--output=other.docx"])

    def test_supports_curated_extensions(self) -> None:
        expected = {
            ".md",
            ".markdown",
            ".pdf",
            ".docx",
            ".odt",
            ".rtf",
            ".html",
            ".htm",
            ".epub",
            ".pptx",
            ".tex",
            ".typ",
        }

        self.assertEqual(set(RENDERER.FORMAT_BY_EXTENSION), expected)


class RichContentTests(unittest.TestCase):
    def make_renderer(
        self,
        directory: Path,
        profile: object = None,
    ) -> object:
        return RENDERER.RichContentRenderer(
            pandoc="/tools/pandoc",
            profile=profile or RENDERER.DOCX,
            custom_options=RENDERER.CustomOptions(),
            working_directory=directory,
            output_file=directory / "output.docx",
            script_root=REPO_ROOT / "skills/swied-markdown-renderer",
            api_version=[1, 23, 1],
        )

    def test_math_fence_becomes_native_display_math(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            renderer = self.make_renderer(Path(directory))

            transformed = renderer.transform(
                code_block("math", r"\int_0^1 x^2\,dx")
            )

        math = transformed["c"][0]
        self.assertEqual(math["t"], "Math")
        self.assertEqual(math["c"][0]["t"], "DisplayMath")

    def test_ordinary_code_is_not_executed_or_transformed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            renderer = self.make_renderer(Path(directory))
            original = code_block("python", "print('hello')")

            transformed = renderer.transform(original)

        self.assertEqual(transformed, original)

    def test_mermaid_uses_svg_for_docx(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_directory = Path(directory)
            renderer = self.make_renderer(test_directory)
            commands: List[List[str]] = []

            def fake_run(
                command: Sequence[str], *, cwd: Path, label: str
            ) -> subprocess.CompletedProcess[str]:
                commands.append(list(command))
                output = Path(command[command.index("--output") + 1])
                output.write_text("<svg/>", encoding="utf-8")
                return subprocess.CompletedProcess(
                    list(command), 0, stdout="", stderr=""
                )

            with mock.patch.object(
                RENDERER.shutil, "which", return_value="/tools/mmdc"
            ), mock.patch.object(
                RENDERER, "run_process", side_effect=fake_run
            ):
                transformed = renderer.transform(
                    code_block(
                        "mermaid",
                        "graph TD\naccTitle: Flow\nA-->B",
                    )
                )

        command = commands[0]
        self.assertEqual(
            command[command.index("--outputFormat") + 1], "svg"
        )
        image = transformed["c"][0]
        self.assertEqual(image["t"], "Image")
        self.assertTrue(image["c"][2][0].endswith(".svg"))

    def test_graphviz_uses_png_for_pptx(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_directory = Path(directory)
            renderer = self.make_renderer(
                test_directory, profile=RENDERER.PPTX
            )
            commands: List[List[str]] = []

            def fake_run(
                command: Sequence[str], *, cwd: Path, label: str
            ) -> subprocess.CompletedProcess[str]:
                commands.append(list(command))
                output = Path(command[command.index("-o") + 1])
                output.write_bytes(b"fake PNG")
                return subprocess.CompletedProcess(
                    list(command), 0, stdout="", stderr=""
                )

            with mock.patch.object(
                RENDERER.shutil, "which", return_value="/tools/dot"
            ), mock.patch.object(
                RENDERER, "run_process", side_effect=fake_run
            ):
                transformed = renderer.transform(
                    code_block("dot", "digraph { A -> B }")
                )

        self.assertIn("-Tpng", commands[0])
        image = transformed["c"][0]
        self.assertTrue(image["c"][2][0].endswith(".png"))

    def test_rtf_auto_converts_math_to_an_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            renderer = self.make_renderer(
                Path(directory), profile=RENDERER.RTF
            )
            replacement = {
                "t": "Image",
                "c": [["", [], []], [], ["equation.png", ""]],
            }

            with mock.patch.object(
                renderer, "render_math", return_value=replacement
            ) as render_math:
                transformed = renderer.transform(
                    {
                        "t": "Math",
                        "c": [{"t": "InlineMath"}, "x^2"],
                    }
                )

        self.assertEqual(transformed, replacement)
        render_math.assert_called_once()

    def test_rendered_markdown_embeds_mermaid_svg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_directory = Path(directory)
            renderer = self.make_renderer(
                test_directory, profile=RENDERER.RENDERED_MARKDOWN
            )

            def fake_run(
                command: Sequence[str], *, cwd: Path, label: str
            ) -> subprocess.CompletedProcess[str]:
                output = Path(command[command.index("--output") + 1])
                output.write_text("<svg/>", encoding="utf-8")
                return subprocess.CompletedProcess(
                    list(command), 0, stdout="", stderr=""
                )

            with mock.patch.object(
                RENDERER.shutil, "which", return_value="/tools/mmdc"
            ), mock.patch.object(
                RENDERER, "run_process", side_effect=fake_run
            ):
                transformed = renderer.transform(
                    code_block("mermaid", "graph TD\nA-->B")
                )

        raw_image = transformed["c"][0]
        self.assertEqual(raw_image["t"], "RawInline")
        self.assertIn(
            "data:image/svg+xml;base64,PHN2Zy8+",
            raw_image["c"][1],
        )
        self.assertIn('class="rendered-diagram"', raw_image["c"][1])

    def test_rendered_markdown_embeds_math_svg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_directory = Path(directory)
            renderer = self.make_renderer(
                test_directory, profile=RENDERER.RENDERED_MARKDOWN
            )

            def fake_run(
                command: Sequence[str], *, cwd: Path, label: str
            ) -> subprocess.CompletedProcess[str]:
                if label == "Pandoc equation conversion":
                    output_option = next(
                        item
                        for item in command
                        if item.startswith("--output=")
                    )
                    Path(output_option.partition("=")[2]).write_text(
                        "equation", encoding="utf-8"
                    )
                else:
                    Path(command[-1]).write_text("<svg/>", encoding="utf-8")
                return subprocess.CompletedProcess(
                    list(command), 0, stdout="", stderr=""
                )

            with mock.patch.object(
                RENDERER.shutil, "which", return_value="/tools/typst"
            ), mock.patch.object(
                RENDERER, "run_process", side_effect=fake_run
            ):
                transformed = renderer.transform(
                    {
                        "t": "Math",
                        "c": [{"t": "InlineMath"}, "E=mc^2"],
                    }
                )

        self.assertEqual(transformed["t"], "RawInline")
        self.assertIn(
            "data:image/svg+xml;base64,PHN2Zy8+",
            transformed["c"][1],
        )
        self.assertIn('class="rendered-equation"', transformed["c"][1])


class PipelineTests(unittest.TestCase):
    def test_docx_pipeline_does_not_require_typst_or_diagram_tools(self) -> None:
        document = {
            "pandoc-api-version": [1, 23, 1],
            "meta": {},
            "blocks": [
                {
                    "t": "Para",
                    "c": [{"t": "Str", "c": "Hello"}],
                }
            ],
        }
        looked_up: List[str] = []
        labels: List[str] = []

        with tempfile.TemporaryDirectory() as directory:
            test_directory = Path(directory)
            source = test_directory / "source.md"
            output = test_directory / "output.docx"
            source.write_text("# Hello\n", encoding="utf-8")

            def find_command(name: str) -> str:
                looked_up.append(name)
                return f"/tools/{name}"

            def fake_run(
                command: Sequence[str], *, cwd: Path, label: str
            ) -> subprocess.CompletedProcess[str]:
                labels.append(label)
                if label == "Pandoc Markdown parsing":
                    return subprocess.CompletedProcess(
                        list(command),
                        0,
                        stdout=json.dumps(document),
                        stderr="",
                    )
                output_option = next(
                    item
                    for item in command
                    if item.startswith("--output=")
                )
                Path(output_option.partition("=")[2]).write_bytes(
                    b"fake DOCX"
                )
                return subprocess.CompletedProcess(
                    list(command), 0, stdout="", stderr=""
                )

            with mock.patch.object(
                RENDERER.shutil, "which", side_effect=find_command
            ), mock.patch.object(
                RENDERER, "run_process", side_effect=fake_run
            ):
                result = RENDERER.main([str(source), str(output)])

            self.assertEqual(result, 0)
            self.assertTrue(output.is_file())

        self.assertEqual(looked_up, ["pandoc"])
        self.assertEqual(
            labels,
            ["Pandoc Markdown parsing", "Pandoc DOCX rendering"],
        )

    def test_existing_output_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_directory = Path(directory)
            source = test_directory / "source.md"
            output = test_directory / "output.html"
            source.write_text("# Source\n", encoding="utf-8")
            output.write_text("existing", encoding="utf-8")

            result = RENDERER.main([str(source), str(output)])

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
