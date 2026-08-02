#!/usr/bin/env python3
"""Render Markdown into curated document formats with Pandoc."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from html import escape as escape_html
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


MARKDOWN_FORMAT = (
    "markdown+autolink_bare_uris+emoji+gfm_auto_identifiers"
    "+tex_math_single_backslash+tex_math_double_backslash"
)
MATH_FENCE_CLASSES = {"math", "latex-math", "tex-math"}
MERMAID_CLASS = "mermaid"
GRAPHVIZ_CLASSES = {"dot", "graphviz"}
LOCKED_PANDOC_OPTIONS = {
    "-f",
    "--from",
    "-o",
    "--output",
    "-t",
    "--to",
    "--pdf-engine",
}


@dataclass(frozen=True)
class FormatProfile:
    name: str
    writer: str
    diagram_format: str
    default_math_image: Optional[str] = None
    writer_options: Tuple[str, ...] = ()
    archive_entries: Tuple[str, ...] = ()
    persistent_media: bool = False
    supports_svg: bool = True
    inline_media: bool = False


PDF = FormatProfile("PDF", "pdf", "svg")
DOCX = FormatProfile(
    "DOCX",
    "docx",
    "svg",
    archive_entries=("[Content_Types].xml", "word/document.xml"),
)
ODT = FormatProfile(
    "ODT", "odt", "svg", archive_entries=("mimetype", "content.xml")
)
RTF = FormatProfile(
    "RTF", "rtf", "png", default_math_image="png", supports_svg=False
)
HTML = FormatProfile(
    "HTML", "html5", "svg", writer_options=("--embed-resources", "--mathml")
)
EPUB = FormatProfile(
    "EPUB3",
    "epub3",
    "svg",
    writer_options=("--mathml",),
    archive_entries=("mimetype", "META-INF/container.xml"),
)
PPTX = FormatProfile(
    "PPTX",
    "pptx",
    "png",
    archive_entries=("[Content_Types].xml", "ppt/presentation.xml"),
    supports_svg=False,
)
LATEX = FormatProfile(
    "LaTeX", "latex", "png", persistent_media=True, supports_svg=False
)
TYPST = FormatProfile("Typst", "typst", "svg", persistent_media=True)
RENDERED_MARKDOWN = FormatProfile(
    "rendered Markdown",
    "gfm",
    "svg",
    default_math_image="svg",
    writer_options=("--wrap=none",),
    inline_media=True,
)

FORMAT_BY_EXTENSION = {
    ".md": RENDERED_MARKDOWN,
    ".markdown": RENDERED_MARKDOWN,
    ".pdf": PDF,
    ".docx": DOCX,
    ".odt": ODT,
    ".rtf": RTF,
    ".html": HTML,
    ".htm": HTML,
    ".epub": EPUB,
    ".pptx": PPTX,
    ".tex": LATEX,
    ".typ": TYPST,
}


class RenderError(RuntimeError):
    """A user-facing rendering failure."""


@dataclass
class CustomOptions:
    inspect: bool = False
    force: bool = False
    render_mermaid: bool = True
    render_graphviz: bool = True
    diagram_format: Optional[str] = None
    math_rendering: str = "auto"


def usage() -> str:
    extensions = ", ".join(sorted(FORMAT_BY_EXTENSION))
    return (
        "Usage: render.py INPUT.md [OUTPUT] [RENDERER_OPTIONS] "
        "[PANDOC_OPTIONS...]\n\n"
        "Output format is inferred from OUTPUT; PDF is the default.\n"
        f"Supported extensions: {extensions}\n\n"
        "Renderer options:\n"
        "  --inspect                 Validate and inspect the result\n"
        "  --force                   Replace an existing output\n"
        "  --no-diagrams             Preserve all diagram fences as code\n"
        "  --no-mermaid              Preserve Mermaid fences as code\n"
        "  --no-graphviz             Preserve dot/Graphviz fences as code\n"
        "  --diagram-format=FORMAT   Force svg or png diagrams\n"
        "  --render-math=MODE        Use auto, native, svg, or png\n\n"
        "Examples:\n"
        "  render.py report.md\n"
        "  render.py report.md report.rendered.md --inspect\n"
        "  render.py report.md report.docx --inspect\n"
        "  render.py handbook.md handbook.epub --toc\n"
        "  render.py legacy.md legacy.rtf --inspect\n"
    )


def fail(message: str, exit_code: int = 1) -> int:
    print(message, file=sys.stderr)
    return exit_code


def parse_custom_options(options: Sequence[str]) -> Tuple[CustomOptions, List[str]]:
    parsed = CustomOptions()
    pandoc_options: List[str] = []
    index = 0
    while index < len(options):
        option = options[index]
        if option == "--inspect":
            parsed.inspect = True
        elif option == "--force":
            parsed.force = True
        elif option == "--no-diagrams":
            parsed.render_mermaid = False
            parsed.render_graphviz = False
        elif option == "--no-mermaid":
            parsed.render_mermaid = False
        elif option == "--no-graphviz":
            parsed.render_graphviz = False
        elif option.startswith("--diagram-format="):
            parsed.diagram_format = option.partition("=")[2].lower()
        elif option == "--diagram-format":
            index += 1
            if index >= len(options):
                raise RenderError("--diagram-format requires svg or png.")
            parsed.diagram_format = options[index].lower()
        elif option.startswith("--render-math="):
            parsed.math_rendering = option.partition("=")[2].lower()
        elif option == "--render-math":
            index += 1
            if index >= len(options):
                raise RenderError(
                    "--render-math requires auto, native, svg, or png."
                )
            parsed.math_rendering = options[index].lower()
        else:
            pandoc_options.append(option)
        index += 1

    if parsed.diagram_format not in {None, "svg", "png"}:
        raise RenderError("--diagram-format must be svg or png.")
    if parsed.math_rendering not in {"auto", "native", "svg", "png"}:
        raise RenderError(
            "--render-math must be auto, native, svg, or png."
        )
    return parsed, pandoc_options


def validate_pandoc_options(options: Sequence[str]) -> None:
    for option in options:
        name = option.partition("=")[0]
        if name in LOCKED_PANDOC_OPTIONS:
            raise RenderError(
                f"Use the positional output filename instead of {name}."
            )
        if len(option) > 2 and option.startswith("-o"):
            raise RenderError(
                "Use the positional output filename instead of Pandoc -o."
            )


def run_process(
    command: Sequence[str], *, cwd: Path, label: str
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise RenderError(f"Unable to start {label}: {error}") from error
    if completed.returncode != 0:
        details = completed.stderr.strip() or completed.stdout.strip()
        suffix = f"\n{details}" if details else ""
        raise RenderError(
            f"{label} failed with exit code {completed.returncode}.{suffix}"
        )
    return completed


def text_to_inlines(text: str) -> List[Dict[str, Any]]:
    inlines: List[Dict[str, Any]] = []
    for part in re.split(r"(\s+)", text.strip()):
        if not part:
            continue
        if part.isspace():
            if inlines and inlines[-1].get("t") != "Space":
                inlines.append({"t": "Space"})
        else:
            inlines.append({"t": "Str", "c": part})
    return inlines or [{"t": "Str", "c": "rendered content"}]


def code_block_parts(
    node: Dict[str, Any]
) -> Tuple[List[str], Dict[str, str], str]:
    try:
        attributes, code = node["c"]
        _, classes, pairs = attributes
        return list(classes), dict(pairs), str(code)
    except (KeyError, TypeError, ValueError) as error:
        raise RenderError(
            "Pandoc returned a malformed fenced code block."
        ) from error


def mermaid_description(
    code: str, attributes: Dict[str, str]
) -> Tuple[str, str]:
    title = attributes.get("title", "")
    alt = attributes.get("alt", attributes.get("caption", ""))
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("accTitle:") and not title:
            title = stripped.partition(":")[2].strip()
        if stripped.startswith("accDescr:") and not alt:
            alt = stripped.partition(":")[2].strip().strip("{}")
    return alt or title or "Mermaid diagram", title


def png_width_points(path: Path, pixels_per_inch: int) -> Optional[float]:
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width = struct.unpack(">I", header[16:20])[0]
    return width * 72.0 / pixels_per_inch


class RichContentRenderer:
    def __init__(
        self,
        *,
        pandoc: str,
        profile: FormatProfile,
        custom_options: CustomOptions,
        working_directory: Path,
        output_file: Path,
        script_root: Path,
        api_version: List[int],
    ) -> None:
        self.pandoc = pandoc
        self.profile = profile
        self.custom_options = custom_options
        self.working_directory = working_directory
        self.output_file = output_file
        self.script_root = script_root
        self.api_version = api_version
        self.diagram_format = (
            custom_options.diagram_format or profile.diagram_format
        )
        if self.diagram_format == "svg" and not profile.supports_svg:
            raise RenderError(
                f"{profile.name} does not reliably support SVG; use PNG."
            )
        if custom_options.math_rendering == "auto":
            self.math_image_format = profile.default_math_image
        elif custom_options.math_rendering == "native":
            self.math_image_format = None
        else:
            self.math_image_format = custom_options.math_rendering
        if self.math_image_format == "svg" and not profile.supports_svg:
            raise RenderError(
                f"{profile.name} does not reliably support SVG equations; use PNG."
            )
        self.media_directory = working_directory
        if profile.persistent_media:
            self.media_directory = output_file.with_name(
                f"{output_file.stem}-media"
            )
        self.diagram_count = 0
        self.math_count = 0
        self.math_cache: Dict[
            Tuple[str, str], Tuple[Path, Optional[float]]
        ] = {}

    def tool(self, command: str, missing_message: str) -> str:
        resolved = shutil.which(command)
        if resolved is None:
            raise RenderError(missing_message)
        return resolved

    def image_target(self, image_path: Path) -> str:
        if self.profile.persistent_media:
            return os.path.relpath(image_path, start=self.output_file.parent)
        return str(image_path)

    def image_node(
        self,
        image_path: Path,
        *,
        alt: str,
        title: str = "",
        width_points: Optional[float] = None,
        css_class: str = "",
    ) -> Dict[str, Any]:
        if self.profile.inline_media:
            return self.inline_image_node(
                image_path,
                alt=alt,
                title=title,
                width_points=width_points,
                css_class=css_class,
            )
        attributes: List[List[str]] = []
        if width_points is not None:
            attributes.append(["width", f"{width_points:.2f}pt"])
        return {
            "t": "Image",
            "c": [
                ["", [], attributes],
                text_to_inlines(alt),
                [self.image_target(image_path), title],
            ],
        }

    def inline_image_node(
        self,
        image_path: Path,
        *,
        alt: str,
        title: str = "",
        width_points: Optional[float] = None,
        css_class: str = "",
    ) -> Dict[str, Any]:
        mime_types = {
            ".png": "image/png",
            ".svg": "image/svg+xml",
        }
        mime_type = mime_types.get(image_path.suffix.lower())
        if mime_type is None:
            raise RenderError(
                f"Cannot embed unsupported image type: {image_path.suffix}"
            )
        try:
            encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        except OSError as error:
            raise RenderError(
                f"Unable to embed rendered image: {error}"
            ) from error
        attributes = [
            f'src="data:{mime_type};base64,{encoded}"',
            f'alt="{escape_html(alt, quote=True)}"',
        ]
        if title:
            attributes.append(
                f'title="{escape_html(title, quote=True)}"'
            )
        if css_class:
            attributes.append(
                f'class="{escape_html(css_class, quote=True)}"'
            )
        if width_points is not None:
            attributes.append(f'style="width: {width_points:.2f}pt"')
        return {
            "t": "RawInline",
            "c": ["html", f"<img {' '.join(attributes)} />"],
        }

    def render_mermaid(
        self, code: str, attributes: Dict[str, str]
    ) -> Dict[str, Any]:
        mmdc = self.tool(
            "mmdc",
            "Mermaid fences were found, but Mermaid CLI (mmdc) is unavailable.\n"
            "Install @mermaid-js/mermaid-cli or rerun with --no-mermaid.",
        )
        self.diagram_count += 1
        self.media_directory.mkdir(parents=True, exist_ok=True)
        source = self.working_directory / f"mermaid-{self.diagram_count}.mmd"
        output = self.media_directory / (
            f"mermaid-{self.diagram_count}.{self.diagram_format}"
        )
        source.write_text(code, encoding="utf-8")
        command = [
            mmdc,
            "--input",
            str(source),
            "--output",
            str(output),
            "--outputFormat",
            self.diagram_format,
            "--backgroundColor",
            "transparent",
        ]
        if self.diagram_format == "png":
            command.extend(["--scale", "2"])
        run_process(
            command, cwd=self.working_directory, label="Mermaid CLI"
        )
        if not output.is_file() or output.stat().st_size == 0:
            raise RenderError(
                "Mermaid CLI produced no usable diagram image."
            )
        alt, title = mermaid_description(code, attributes)
        return self.image_node(
            output,
            alt=alt,
            title=title,
            css_class="rendered-diagram",
        )

    def render_graphviz(
        self, code: str, attributes: Dict[str, str]
    ) -> Dict[str, Any]:
        dot = self.tool(
            "dot",
            "Graphviz fences were found, but the dot command is unavailable.\n"
            "Install Graphviz or rerun with --no-graphviz.",
        )
        self.diagram_count += 1
        self.media_directory.mkdir(parents=True, exist_ok=True)
        source = (
            self.working_directory / f"graphviz-{self.diagram_count}.dot"
        )
        output = self.media_directory / (
            f"graphviz-{self.diagram_count}.{self.diagram_format}"
        )
        source.write_text(code, encoding="utf-8")
        command = [dot, f"-T{self.diagram_format}"]
        if self.diagram_format == "png":
            command.append("-Gdpi=192")
        command.extend(["-o", str(output), str(source)])
        run_process(command, cwd=self.working_directory, label="Graphviz")
        if not output.is_file() or output.stat().st_size == 0:
            raise RenderError("Graphviz produced no usable diagram image.")
        alt = attributes.get(
            "alt",
            attributes.get(
                "caption", attributes.get("title", "Graphviz diagram")
            ),
        )
        return self.image_node(
            output,
            alt=alt,
            title=attributes.get("title", ""),
            css_class="rendered-diagram",
        )

    def render_math(self, math_node: Dict[str, Any]) -> Dict[str, Any]:
        if self.math_image_format is None:
            return math_node
        try:
            math_kind, source_text = math_node["c"]
            kind = str(math_kind["t"])
            source_text = str(source_text)
        except (KeyError, TypeError, ValueError) as error:
            raise RenderError(
                "Pandoc returned a malformed math expression."
            ) from error

        cache_key = (kind, source_text)
        cached = self.math_cache.get(cache_key)
        if cached is not None:
            image_path, width_points = cached
            return self.image_node(
                image_path,
                alt=source_text,
                width_points=width_points,
                css_class="rendered-equation",
            )

        typst = self.tool(
            "typst",
            "Equation graphics are required for this output, but Typst is "
            "unavailable. Install Typst or rerun with --render-math=native.",
        )
        self.math_count += 1
        self.media_directory.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(
            f"{kind}\0{source_text}".encode("utf-8")
        ).hexdigest()[:12]
        base_name = f"equation-{self.math_count}-{digest}"
        json_path = self.working_directory / f"{base_name}.json"
        typst_path = self.working_directory / f"{base_name}.typ"
        image_path = self.media_directory / (
            f"{base_name}.{self.math_image_format}"
        )
        equation_document = {
            "pandoc-api-version": self.api_version,
            "meta": {},
            "blocks": [{"t": "Para", "c": [math_node]}],
        }
        json_path.write_text(json.dumps(equation_document), encoding="utf-8")
        template = self.script_root / "templates" / "equation.typst"
        run_process(
            [
                self.pandoc,
                str(json_path),
                "--from=json",
                "--to=typst",
                "--standalone",
                f"--template={template}",
                f"--output={typst_path}",
            ],
            cwd=self.working_directory,
            label="Pandoc equation conversion",
        )
        compile_command = [typst, "compile"]
        pixels_per_inch = 288
        if self.math_image_format == "png":
            compile_command.extend(["--ppi", str(pixels_per_inch)])
        compile_command.extend([str(typst_path), str(image_path)])
        run_process(
            compile_command,
            cwd=self.working_directory,
            label="Typst equation rendering",
        )
        if not image_path.is_file() or image_path.stat().st_size == 0:
            raise RenderError("Typst produced no usable equation image.")
        width_points = None
        if self.math_image_format == "png":
            width_points = png_width_points(image_path, pixels_per_inch)
        self.math_cache[cache_key] = (image_path, width_points)
        return self.image_node(
            image_path,
            alt=source_text,
            width_points=width_points,
            css_class="rendered-equation",
        )

    def transform(self, value: Any) -> Any:
        if isinstance(value, list):
            return [self.transform(item) for item in value]
        if not isinstance(value, dict):
            return value

        node_type = value.get("t")
        if node_type == "CodeBlock":
            classes, attributes, code = code_block_parts(value)
            class_set = set(classes)
            if (
                MERMAID_CLASS in class_set
                and self.custom_options.render_mermaid
            ):
                image = self.render_mermaid(code, attributes)
                return {"t": "Para", "c": [image]}
            if (
                class_set & GRAPHVIZ_CLASSES
                and self.custom_options.render_graphviz
            ):
                image = self.render_graphviz(code, attributes)
                return {"t": "Para", "c": [image]}
            if class_set & MATH_FENCE_CLASSES:
                math_node = {
                    "t": "Math",
                    "c": [{"t": "DisplayMath"}, code.strip()],
                }
                return {
                    "t": "Para",
                    "c": [self.render_math(math_node)],
                }
            return value
        if node_type == "Math":
            return self.render_math(value)
        return {key: self.transform(item) for key, item in value.items()}


def load_pandoc_document(
    pandoc: str, input_file: Path, working_directory: Path
) -> Dict[str, Any]:
    resource_path = os.pathsep.join(
        [str(input_file.parent), str(working_directory)]
    )
    completed = run_process(
        [
            pandoc,
            str(input_file),
            f"--from={MARKDOWN_FORMAT}",
            "--to=json",
            f"--resource-path={resource_path}",
        ],
        cwd=input_file.parent,
        label="Pandoc Markdown parsing",
    )
    try:
        document = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RenderError("Pandoc returned invalid document data.") from error
    if not isinstance(document, dict) or "pandoc-api-version" not in document:
        raise RenderError("Pandoc returned an incomplete document tree.")
    return document


def write_document(
    *,
    pandoc: str,
    document: Dict[str, Any],
    input_file: Path,
    output_file: Path,
    profile: FormatProfile,
    working_directory: Path,
    script_root: Path,
    pandoc_options: Sequence[str],
    media_directory: Path,
) -> None:
    transformed = working_directory / "document.json"
    transformed.write_text(json.dumps(document), encoding="utf-8")
    resource_paths = [
        working_directory,
        input_file.parent,
        output_file.parent,
    ]
    if media_directory not in resource_paths:
        resource_paths.insert(0, media_directory)
    command = [
        pandoc,
        str(transformed),
        "--from=json",
        f"--to={profile.writer}",
        "--standalone",
        (
            "--resource-path="
            + os.pathsep.join(str(path) for path in resource_paths)
        ),
    ]
    if profile is PDF:
        template = script_root / "templates" / "default.typst"
        command.extend(
            [
                "--pdf-engine=typst",
                f"--template={template}",
                "--variable=papersize:us-letter",
            ]
        )
    command.extend(profile.writer_options)
    command.extend([f"--output={output_file}", *pandoc_options])
    completed = run_process(
        command,
        cwd=input_file.parent,
        label=f"Pandoc {profile.name} rendering",
    )
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)


def inspect_pdf(output_file: Path) -> None:
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
            details: Dict[str, str] = {}
            for line in completed.stdout.splitlines():
                key, separator, value = line.partition(":")
                if separator:
                    details[key.strip()] = value.strip()
            try:
                page_count = int(details.get("Pages", ""))
            except ValueError:
                page_count = None
            summary = []
            for key in ("Pages", "Page size", "File size"):
                if key in details:
                    normalized = key.lower().replace(" ", "-")
                    summary.append(f"{normalized}={details[key]}")
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
            report_text_count(completed.stdout)

    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        return
    preview_directory = Path(
        tempfile.mkdtemp(prefix="swied-markdown-renderer-preview-")
    )
    pages = [1]
    if page_count is not None and page_count > 1:
        pages.append(page_count)
    rendered_any = False
    for page in pages:
        prefix = preview_directory / f"page-{page}"
        completed = subprocess.run(
            [
                pdftoppm,
                "-png",
                "-r",
                "130",
                "-f",
                str(page),
                "-l",
                str(page),
                "-singlefile",
                str(output_file),
                str(prefix),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        preview = prefix.with_suffix(".png")
        if (
            completed.returncode == 0
            and preview.is_file()
            and preview.stat().st_size
        ):
            rendered_any = True
            print(f"Preview page {page}: {preview}")
    if not rendered_any:
        try:
            preview_directory.rmdir()
        except OSError:
            pass


def report_text_count(text: str) -> None:
    character_count = len("".join(text.split()))
    print(
        f"Extracted text: {character_count} non-whitespace characters"
    )
    if character_count == 0:
        print(
            "Warning: the output contains no extractable text.",
            file=sys.stderr,
        )


def inspect_archive(output_file: Path, profile: FormatProfile) -> None:
    if not zipfile.is_zipfile(output_file):
        raise RenderError(
            f"{profile.name} output is not a valid ZIP container."
        )
    with zipfile.ZipFile(output_file) as archive:
        damaged = archive.testzip()
        if damaged is not None:
            raise RenderError(f"Damaged archive member: {damaged}")
        names = set(archive.namelist())
        missing = [
            entry
            for entry in profile.archive_entries
            if entry not in names
        ]
        if missing:
            raise RenderError(
                f"{profile.name} output is missing: {', '.join(missing)}"
            )
        print(
            f"Archive inspection: {len(names)} members, structure valid"
        )


def inspect_with_pandoc(pandoc: str, output_file: Path) -> None:
    completed = subprocess.run(
        [pandoc, str(output_file), "--to=plain"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        report_text_count(completed.stdout)
    else:
        print(
            "Warning: Pandoc could not re-read the output for text inspection.",
            file=sys.stderr,
        )


def inspect_output(
    pandoc: str, output_file: Path, profile: FormatProfile
) -> None:
    print(f"Output size: {output_file.stat().st_size} bytes")
    if profile is PDF:
        inspect_pdf(output_file)
        return
    if profile.archive_entries:
        inspect_archive(output_file, profile)
    if profile is RTF:
        try:
            if not output_file.read_bytes().startswith(b"{\\rtf"):
                raise RenderError("RTF output has an invalid header.")
        except OSError as error:
            raise RenderError(
                f"Unable to inspect RTF output: {error}"
            ) from error
    if profile is HTML:
        try:
            html = output_file.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeError) as error:
            raise RenderError(
                f"Unable to inspect HTML output: {error}"
            ) from error
        if "<html" not in html:
            raise RenderError(
                "HTML output is missing its document element."
            )
    inspect_with_pandoc(pandoc, output_file)


def determine_paths(
    arguments: Sequence[str],
) -> Tuple[Path, Path, List[str]]:
    input_file = Path(arguments[0]).expanduser()
    remaining = list(arguments[1:])
    if remaining and not remaining[0].startswith("-"):
        output_file = Path(remaining.pop(0)).expanduser()
    else:
        output_file = input_file.with_suffix(".pdf")
    return input_file, output_file, remaining


def main(arguments: Sequence[str]) -> int:
    if not arguments or arguments[0] in {"-h", "--help"}:
        print(usage())
        return 0 if arguments else 2

    try:
        input_file, output_file, remaining = determine_paths(arguments)
        custom_options, pandoc_options = parse_custom_options(remaining)
        validate_pandoc_options(pandoc_options)

        if input_file.suffix.lower() not in {".md", ".markdown"}:
            raise RenderError(
                f"Input must have a .md or .markdown extension: {input_file}"
            )
        if not input_file.is_file():
            raise RenderError(f"Markdown file not found: {input_file}")
        profile = FORMAT_BY_EXTENSION.get(output_file.suffix.lower())
        if profile is None:
            supported = ", ".join(sorted(FORMAT_BY_EXTENSION))
            raise RenderError(
                f"Unsupported output extension "
                f"{output_file.suffix or '(none)'}. "
                f"Choose one of: {supported}"
            )

        input_file = input_file.resolve()
        output_file = output_file.resolve()
        if input_file == output_file:
            raise RenderError(
                "Output must not overwrite the input Markdown file."
            )
        if output_file.exists() and not custom_options.force:
            raise RenderError(
                f"Output already exists: {output_file}\n"
                "Rerun with --force only when replacing it is intentional."
            )
        output_file.parent.mkdir(parents=True, exist_ok=True)

        pandoc = shutil.which("pandoc")
        if pandoc is None:
            raise RenderError(
                "Pandoc is not installed or is unavailable on PATH."
            )
        if profile is PDF and shutil.which("typst") is None:
            raise RenderError(
                "Typst is required for PDF output but is unavailable on PATH."
            )

        try:
            temporary = tempfile.TemporaryDirectory(
                prefix=".swied-markdown-renderer-",
                dir=str(input_file.parent),
            )
        except OSError as error:
            raise RenderError(
                "Unable to create a rendering directory beside the input: "
                f"{error}"
            ) from error

        with temporary:
            working_directory = Path(temporary.name)
            document = load_pandoc_document(
                pandoc, input_file, working_directory
            )
            api_version = document.get("pandoc-api-version")
            if not isinstance(api_version, list):
                raise RenderError(
                    "Pandoc returned an invalid API version."
                )
            script_root = Path(__file__).resolve().parent.parent
            renderer = RichContentRenderer(
                pandoc=pandoc,
                profile=profile,
                custom_options=custom_options,
                working_directory=working_directory,
                output_file=output_file,
                script_root=script_root,
                api_version=api_version,
            )
            transformed = renderer.transform(document)
            write_document(
                pandoc=pandoc,
                document=transformed,
                input_file=input_file,
                output_file=output_file,
                profile=profile,
                working_directory=working_directory,
                script_root=script_root,
                pandoc_options=pandoc_options,
                media_directory=renderer.media_directory,
            )

        if not output_file.is_file() or output_file.stat().st_size == 0:
            raise RenderError(
                f"{profile.name} rendering produced no usable file: "
                f"{output_file}"
            )
        print(f"Created {profile.name}: {output_file}")
        if custom_options.inspect:
            inspect_output(pandoc, output_file, profile)
        return 0
    except RenderError as error:
        return fail(str(error))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
