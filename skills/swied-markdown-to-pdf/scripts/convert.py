#!/usr/bin/env python3
"""Convert Markdown to PDF with Pandoc and Typst."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Optional, Tuple


FENCE_OPEN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


def usage() -> str:
    return (
        "Usage: convert.py INPUT.md [OUTPUT.pdf] [PANDOC_OPTIONS...]\n"
        "\n"
        "Examples:\n"
        "  convert.py report.md\n"
        "  convert.py report.md report.pdf --toc --number-sections\n"
        "  convert.py report.md report.pdf --inspect\n"
        "  convert.py report.md report.pdf --no-mermaid\n"
        "\n"
        "Mermaid blocks are rendered when Mermaid CLI (mmdc) is available.\n"
        "Use --no-mermaid to preserve them as source code.\n"
        "--inspect reports PDF metadata and renders representative preview\n"
        "pages when Poppler PDF tools are available."
    )


def fail(message: str, exit_code: int = 1) -> int:
    print(message, file=sys.stderr)
    return exit_code


def is_mermaid_info(info: str) -> bool:
    """Return whether an info string is supported by Mermaid CLI."""
    return info.strip() == "mermaid"


def contains_mermaid_block(markdown: str) -> bool:
    """Detect Mermaid fences while respecting surrounding fenced code blocks."""
    open_fence: Optional[Tuple[str, int]] = None

    for line in markdown.splitlines():
        match = FENCE_OPEN.match(line)
        if match is None:
            continue

        fence = match.group("fence")
        marker = fence[0]
        length = len(fence)

        if open_fence is None:
            if marker == "`" and length == 3 and is_mermaid_info(
                match.group("info")
            ):
                return True
            open_fence = (marker, length)
            continue

        open_marker, open_length = open_fence
        if (
            marker == open_marker
            and length >= open_length
            and match.group("info").strip() == ""
        ):
            open_fence = None

    return False


def render_mermaid_markdown(
    mmdc: str, input_file: Path, temporary_directory: Path
) -> Tuple[Optional[Path], int]:
    """Render Mermaid blocks and return transformed Markdown for Pandoc."""
    transformed_file = temporary_directory / "mermaid-rendered.md"
    command = [
        mmdc,
        "--input",
        str(input_file),
        "--output",
        str(transformed_file),
        "--outputFormat",
        "png",
        "--scale",
        "2",
    ]

    try:
        completed = subprocess.run(command, check=False)
    except OSError as error:
        return None, fail(f"Unable to start Mermaid CLI: {error}")

    if completed.returncode != 0:
        return None, fail(
            "Mermaid CLI could not render the diagram blocks.",
            completed.returncode,
        )

    if not transformed_file.is_file() or transformed_file.stat().st_size == 0:
        return None, fail("Mermaid CLI produced no usable Markdown output.")

    try:
        transformed_markdown = transformed_file.read_text(encoding="utf-8")
        generated_images = sorted(
            temporary_directory.glob("mermaid-rendered-*.png")
        )
        if not generated_images:
            return None, fail("Mermaid CLI produced no diagram images.")

        for image_file in generated_images:
            relative_target = f"./{image_file.name}"
            resolved_target = image_file.relative_to(
                input_file.parent
            ).as_posix()
            transformed_markdown = transformed_markdown.replace(
                f"({relative_target}", f"(<{resolved_target}>"
            )

        transformed_file.write_text(transformed_markdown, encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return None, fail(f"Unable to prepare rendered Mermaid diagrams: {error}")

    return transformed_file, 0


def inspect_pdf(output_file: Path) -> None:
    """Report basic PDF checks and render representative pages when possible."""
    page_count: Optional[int] = None
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo is not None:
        completed = subprocess.run(
            [pdfinfo, str(output_file)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            details = {}
            for line in completed.stdout.splitlines():
                key, separator, value = line.partition(":")
                if separator:
                    details[key.strip()] = value.strip()
            try:
                page_count = int(details.get("Pages", ""))
            except ValueError:
                page_count = None
            summary = []
            if "Pages" in details:
                summary.append(f"pages={details['Pages']}")
            if "Page size" in details:
                summary.append(f"page-size={details['Page size']}")
            if "File size" in details:
                summary.append(f"file-size={details['File size']}")
            if summary:
                print(f"Inspection: {', '.join(summary)}")

    pdftotext = shutil.which("pdftotext")
    if pdftotext is not None:
        completed = subprocess.run(
            [pdftotext, str(output_file), "-"],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            character_count = len("".join(completed.stdout.split()))
            print(f"Extracted text: {character_count} non-whitespace characters")
            if character_count == 0:
                print(
                    "Warning: the PDF contains no extractable text.",
                    file=sys.stderr,
                )

    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        return

    preview_directory = Path(tempfile.mkdtemp(prefix="swied-markdown-to-pdf-preview-"))
    representative_pages = [1]
    if page_count is not None and page_count > 1:
        representative_pages.append(page_count)

    rendered_any = False
    for page_number in representative_pages:
        prefix = preview_directory / f"page-{page_number}"
        completed = subprocess.run(
            [
                pdftoppm,
                "-png",
                "-r",
                "130",
                "-f",
                str(page_number),
                "-l",
                str(page_number),
                "-singlefile",
                str(output_file),
                str(prefix),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        preview_file = prefix.with_suffix(".png")
        if (
            completed.returncode == 0
            and preview_file.is_file()
            and preview_file.stat().st_size > 0
        ):
            rendered_any = True
            print(f"Preview page {page_number}: {preview_file}")

    if not rendered_any:
        try:
            preview_directory.rmdir()
        except OSError:
            pass


def main(arguments: list[str]) -> int:
    if not arguments or arguments[0] in {"-h", "--help"}:
        print(usage())
        return 0 if arguments else 2

    input_file = Path(arguments[0]).expanduser()
    remaining = arguments[1:]

    if input_file.suffix.lower() not in {".md", ".markdown"}:
        return fail(
            f"Input must have a .md or .markdown extension: {input_file}", 2
        )

    if not input_file.is_file():
        return fail(f"Markdown file not found: {input_file}")

    if remaining and remaining[0].lower().endswith(".pdf"):
        output_file = Path(remaining[0]).expanduser()
        pandoc_options = remaining[1:]
    else:
        output_file = input_file.with_suffix(".pdf")
        pandoc_options = remaining

    inspect_output = "--inspect" in pandoc_options
    render_mermaid = "--no-mermaid" not in pandoc_options
    pandoc_options = [
        option
        for option in pandoc_options
        if option not in {"--inspect", "--no-mermaid"}
    ]

    if shutil.which("pandoc") is None:
        return fail("Pandoc is not installed or is not available on PATH.")

    if shutil.which("typst") is None:
        return fail("Typst is not installed or is not available on PATH.")

    input_file = input_file.resolve()
    output_file = output_file.resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    template_file = (
        Path(__file__).resolve().parent.parent / "templates" / "default.typst"
    )

    try:
        markdown = input_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return fail(f"Unable to read Markdown file: {error}")

    with ExitStack() as stack:
        pandoc_input = input_file
        resource_paths = [input_file.parent]

        if render_mermaid and contains_mermaid_block(markdown):
            mmdc = shutil.which("mmdc")
            if mmdc is None:
                return fail(
                    "Mermaid diagram blocks were found, but Mermaid CLI "
                    "(mmdc) is unavailable.\n\n"
                    "Install it with:\n"
                    "  npm install --global @mermaid-js/mermaid-cli\n\n"
                    "Then rerun the conversion. To preserve Mermaid blocks "
                    "as source code instead,\n"
                    "rerun with --no-mermaid."
                )

            try:
                temporary_directory = Path(
                    stack.enter_context(
                        tempfile.TemporaryDirectory(
                            prefix=".swied-markdown-to-pdf-",
                            dir=str(input_file.parent),
                        )
                    )
                )
            except OSError as error:
                return fail(
                    "Unable to create a temporary Mermaid working "
                    f"directory beside the input file: {error}"
                )
            pandoc_input, render_exit_code = render_mermaid_markdown(
                mmdc, input_file, temporary_directory
            )
            if pandoc_input is None:
                return render_exit_code
            resource_paths.insert(0, temporary_directory)

        resource_path = os.pathsep.join(str(path) for path in resource_paths)
        command = [
            "pandoc",
            str(pandoc_input),
            "--from=gfm+yaml_metadata_block",
            "--standalone",
            "--pdf-engine=typst",
            f"--template={template_file}",
            f"--resource-path={resource_path}",
            "--variable=papersize:us-letter",
            f"--output={output_file}",
            *pandoc_options,
        ]

        try:
            completed = subprocess.run(
                command, check=False, cwd=input_file.parent
            )
        except OSError as error:
            return fail(f"Unable to start Pandoc: {error}")

        if completed.returncode != 0:
            return completed.returncode

        if not output_file.is_file() or output_file.stat().st_size == 0:
            return fail(f"PDF generation produced no usable file: {output_file}")

    print(f"Created: {output_file}")
    if inspect_output:
        inspect_pdf(output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
