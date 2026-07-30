#!/usr/bin/env python3
"""Unit tests for the Markdown-to-PDF converter."""

from __future__ import annotations

import importlib.util
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from typing import List, Optional
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
CONVERTER_PATH = REPO_ROOT / "skills/markdown-to-pdf/scripts/convert.py"
SPEC = importlib.util.spec_from_file_location("markdown_to_pdf_convert", CONVERTER_PATH)
assert SPEC is not None and SPEC.loader is not None
CONVERTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONVERTER)


class MermaidDetectionTests(unittest.TestCase):
    def test_detects_supported_mermaid_fences(self) -> None:
        examples = [
            "```mermaid\ngraph TD\n```\n",
            "   ```mermaid\ngraph TD\n   ```\n",
        ]

        for markdown in examples:
            with self.subTest(markdown=markdown):
                self.assertTrue(CONVERTER.contains_mermaid_block(markdown))

    def test_ignores_mermaid_example_inside_larger_fence(self) -> None:
        markdown = """````markdown
```mermaid
graph TD
```
````
"""

        self.assertFalse(CONVERTER.contains_mermaid_block(markdown))

    def test_ignores_ordinary_code_blocks(self) -> None:
        self.assertFalse(
            CONVERTER.contains_mermaid_block("```python\nprint('hello')\n```\n")
        )


class MermaidConversionTests(unittest.TestCase):
    def test_mermaid_document_is_preprocessed_before_pandoc(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            test_directory = Path(directory)
            input_file = test_directory / "diagram.md"
            output_file = test_directory / "diagram.pdf"
            original = "# Diagram\n\n```mermaid\ngraph TD\nA-->B\n```\n"
            input_file.write_text(original, encoding="utf-8")
            commands: List[List[str]] = []

            def find_command(name: str) -> str:
                return f"/tools/{name}"

            def run_command(
                command: List[str], check: bool, cwd: Optional[Path] = None
            ) -> subprocess.CompletedProcess:
                self.assertFalse(check)
                commands.append(command)
                if command[0] == "/tools/mmdc":
                    self.assertEqual(
                        command[command.index("--outputFormat") + 1], "png"
                    )
                    self.assertEqual(command[command.index("--scale") + 1], "2")
                    transformed = Path(command[command.index("--output") + 1])
                    transformed.write_text(
                        "# Diagram\n\n![diagram](./mermaid-rendered-1.png)\n",
                        encoding="utf-8",
                    )
                    transformed.with_name("mermaid-rendered-1.png").write_text(
                        "fake PNG",
                        encoding="utf-8",
                    )
                else:
                    self.assertEqual(cwd, input_file.parent)
                    resource_option = next(
                        option
                        for option in command
                        if option.startswith("--resource-path=")
                    )
                    self.assertIn(str(input_file.parent), resource_option)
                    self.assertIn(".markdown-to-pdf-", resource_option)
                    transformed_markdown = Path(command[1]).read_text(
                        encoding="utf-8"
                    )
                    self.assertIn(
                        "![diagram](<.markdown-to-pdf-", transformed_markdown
                    )
                    Path(
                        next(
                            option.removeprefix("--output=")
                            for option in command
                            if option.startswith("--output=")
                        )
                    ).write_bytes(b"%PDF-test")
                return subprocess.CompletedProcess(command, 0)

            with mock.patch.object(
                CONVERTER.shutil, "which", side_effect=find_command
            ), mock.patch.object(
                CONVERTER.subprocess, "run", side_effect=run_command
            ):
                result = CONVERTER.main([str(input_file), str(output_file)])

            self.assertEqual(result, 0)
            self.assertEqual(input_file.read_text(encoding="utf-8"), original)
            self.assertEqual(
                [command[0] for command in commands],
                ["/tools/mmdc", "pandoc"],
            )
            self.assertTrue(output_file.is_file())

    def test_ordinary_document_does_not_require_mermaid_cli(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_file = Path(directory) / "ordinary.md"
            output_file = Path(directory) / "ordinary.pdf"
            input_file.write_text("# Ordinary Markdown\n", encoding="utf-8")
            looked_up: List[str] = []

            def find_command(name: str) -> str:
                looked_up.append(name)
                return f"/tools/{name}"

            def run_command(
                command: List[str], check: bool, cwd: Optional[Path] = None
            ) -> subprocess.CompletedProcess:
                Path(
                    next(
                        option.removeprefix("--output=")
                        for option in command
                        if option.startswith("--output=")
                    )
                ).write_bytes(b"%PDF-test")
                return subprocess.CompletedProcess(command, 0)

            with mock.patch.object(
                CONVERTER.shutil, "which", side_effect=find_command
            ), mock.patch.object(
                CONVERTER.subprocess, "run", side_effect=run_command
            ):
                result = CONVERTER.main([str(input_file), str(output_file)])

            self.assertEqual(result, 0)
            self.assertNotIn("mmdc", looked_up)

    def test_missing_mermaid_cli_reports_install_and_opt_out(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_file = Path(directory) / "diagram.md"
            output_file = Path(directory) / "diagram.pdf"
            input_file.write_text(
                "```mermaid\ngraph TD\nA-->B\n```\n", encoding="utf-8"
            )

            def find_command(name: str) -> Optional[str]:
                if name == "mmdc":
                    return None
                return f"/tools/{name}"

            stderr = io.StringIO()
            with mock.patch.object(
                CONVERTER.shutil, "which", side_effect=find_command
            ), mock.patch.object(CONVERTER.subprocess, "run") as run, redirect_stderr(
                stderr
            ):
                result = CONVERTER.main([str(input_file), str(output_file)])

            self.assertEqual(result, 1)
            self.assertIn("npm install --global", stderr.getvalue())
            self.assertIn("--no-mermaid", stderr.getvalue())
            run.assert_not_called()

    def test_no_mermaid_flag_preserves_existing_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_file = Path(directory) / "diagram.md"
            output_file = Path(directory) / "diagram.pdf"
            input_file.write_text(
                "```mermaid\ngraph TD\nA-->B\n```\n", encoding="utf-8"
            )
            looked_up: List[str] = []

            def find_command(name: str) -> str:
                looked_up.append(name)
                return f"/tools/{name}"

            def run_command(
                command: List[str], check: bool, cwd: Optional[Path] = None
            ) -> subprocess.CompletedProcess:
                self.assertNotIn("--no-mermaid", command)
                Path(
                    next(
                        option.removeprefix("--output=")
                        for option in command
                        if option.startswith("--output=")
                    )
                ).write_bytes(b"%PDF-test")
                return subprocess.CompletedProcess(command, 0)

            with mock.patch.object(
                CONVERTER.shutil, "which", side_effect=find_command
            ), mock.patch.object(
                CONVERTER.subprocess, "run", side_effect=run_command
            ):
                result = CONVERTER.main(
                    [str(input_file), str(output_file), "--no-mermaid"]
                )

            self.assertEqual(result, 0)
            self.assertNotIn("mmdc", looked_up)


if __name__ == "__main__":
    unittest.main()
