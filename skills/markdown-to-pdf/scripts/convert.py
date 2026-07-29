#!/usr/bin/env python3
"""Convert Markdown to PDF with Pandoc and Typst."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def usage() -> str:
    return (
        "Usage: convert.py INPUT.md [OUTPUT.pdf] [PANDOC_OPTIONS...]\n"
        "\n"
        "Examples:\n"
        "  convert.py report.md\n"
        "  convert.py report.md report.pdf --toc --number-sections"
    )


def fail(message: str, exit_code: int = 1) -> int:
    print(message, file=sys.stderr)
    return exit_code


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

    if shutil.which("pandoc") is None:
        return fail("Pandoc is not installed or is not available on PATH.")

    if shutil.which("typst") is None:
        return fail("Typst is not installed or is not available on PATH.")

    input_file = input_file.resolve()
    output_file = output_file.resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "pandoc",
        str(input_file),
        "--from=gfm+yaml_metadata_block",
        "--standalone",
        "--pdf-engine=typst",
        f"--resource-path={input_file.parent}",
        "--variable=papersize:us-letter",
        "--variable=margin:1in",
        f"--output={output_file}",
        *pandoc_options,
    ]

    try:
        completed = subprocess.run(command, check=False)
    except OSError as error:
        return fail(f"Unable to start Pandoc: {error}")

    if completed.returncode != 0:
        return completed.returncode

    if not output_file.is_file() or output_file.stat().st_size == 0:
        return fail(f"PDF generation produced no usable file: {output_file}")

    print(f"Created: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

