---
name: swied-markdown-renderer
description: Convert Markdown or .md files into polished rendered Markdown, PDF, DOCX, ODT, RTF, HTML, EPUB, PPTX, LaTeX, or Typst documents with native or embedded math, rendered Mermaid and Graphviz diagrams, syntax-highlighted code, and format-aware inspection. Use when the user asks to convert, export, render, typeset, publish, or save Markdown in one of these document formats, including Markdown-to-Markdown conversion with inline SVG or PNG graphics. Do not use for editing an existing non-Markdown output document or converting a non-Markdown source.
---

# Markdown Renderer

Use the bundled deterministic renderer:

```bash
python3 scripts/render.py INPUT.md [OUTPUT] --inspect [PANDOC_OPTIONS...]
```

Resolve the script path relative to this `SKILL.md`, not relative to the user's
working directory. On POSIX systems, `scripts/render.sh` is an equivalent
wrapper. Infer the format from the output extension; PDF is the default when no
output is named.

Read [format-support.md](references/format-support.md) only when choosing among
formats, explaining fidelity tradeoffs, or considering another rich-block
renderer.

## Workflow

1. Resolve the input Markdown and output path. Keep output beside the source by
   default and never overwrite the source.
2. Run `render.py` once with `--inspect`. Add `--force` only when the user's
   request clearly authorizes replacing that exact output.
3. Let Pandoc preserve math semantically: Typst typesetting for PDF, OMML for
   DOCX/PPTX, MathML for ODT/HTML/EPUB, and native source for LaTeX/Typst. RTF
   equations automatically become local PNG graphics because RTF lacks a
   dependable equation representation. Rendered Markdown embeds equations as
   SVG data by default so the output does not need MathJax.
4. Render `mermaid` and `dot`/`graphviz` fences automatically. The renderer uses
   SVG when the destination supports it and PNG for RTF, PPTX, and LaTeX.
5. If Mermaid CLI or Graphviz is missing only when its matching fence occurs,
   ask whether to install the dependency or preserve that fence with
   `--no-mermaid` or `--no-graphviz`. Do not require optional tools for ordinary
   Markdown.
6. Inspect the reported file structure and extractable-text count. For PDFs,
   inspect the representative preview paths for clipping, broken tables,
   missing images, and poor page breaks.
7. Return the completed document and leave the Markdown unchanged. Mention the
   sibling `*-media` directory when exporting LaTeX or Typst with rendered
   diagrams.

## Rich content

- Recognize `$...$`, `$$...$$`, `\(...\)`, and `\[...\]` as TeX math. Treat
  fenced `math`, `latex-math`, and `tex-math` blocks as display equations.
- Do not interpret generic `latex` or `tex` fences as equations; they may contain
  complete documents or illustrative source code.
- Keep ordinary code blocks as syntax-highlighted code. Never execute Python,
  R, shell, Jupyter, or other general-purpose code to produce document content.
- Use `--render-math=native`, `svg`, or `png` only when the user requests a
  specific math representation. Prefer `auto`.
- Use `--diagram-format=svg` or `png` only for an explicit compatibility need.
  Prefer the destination-specific default.

## Output behavior

- Supported extensions are `.pdf`, `.docx`, `.odt`, `.rtf`, `.html`, `.htm`,
  `.epub`, `.pptx`, `.tex`, `.typ`, `.md`, and `.markdown`.
- Use a distinct rendered Markdown name such as `report.rendered.md`; never
  replace the source Markdown in place.
- Use US Letter and one-inch margins for PDF unless requested otherwise.
- Embed generated graphics directly into rendered Markdown as SVG or PNG data
  URIs. Keep existing ordinary image links unchanged. Embed resources into HTML
  and binary document formats. LaTeX and Typst source exports keep generated
  diagrams in a sibling `<output-stem>-media` directory.
- Accept normal Pandoc writer options after the output path, such as `--toc`,
  `--number-sections`, `--citeproc`, `--bibliography`, or `--reference-doc`.
- Refuse Pandoc options that replace the selected input/output format or output
  path; choose those through the positional output filename.

## Boundaries

- Never install Pandoc, Typst, Mermaid CLI, Graphviz, or their dependencies
  without approval.
- Never silently substitute a remote rendering service. Equation and diagram
  preprocessing must remain local so private document content is not uploaded.
- Do not promise identical layout across formats. Use native semantics first,
  then the documented SVG/PNG compatibility fallback.
- When sandbox escalation is needed, request the narrow reusable prefix
  `python3 ABSOLUTE_SKILL_PATH/scripts/render.py`, not a broad Python prefix.
