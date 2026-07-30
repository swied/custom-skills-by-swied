---
name: markdown-to-pdf
description: Convert Markdown or .md files into polished PDF documents using the locally installed Pandoc and Typst command-line programs. Use when the user asks to convert, export, render, typeset, or save Markdown as PDF. Do not use for editing an existing PDF or converting non-Markdown source files.
---

# Markdown to PDF

Use the bundled cross-platform deterministic converter:

```bash
python3 scripts/convert.py INPUT.md [OUTPUT.pdf] --inspect [PANDOC_OPTIONS...]
```

Resolve the script path relative to this `SKILL.md`, not relative to the
user's current working directory. On POSIX systems, `scripts/convert.sh`
provides an equivalent wrapper when preferred.

## Approval-efficient execution

Perform conversion, deterministic validation, and preview rendering with one
invocation of `convert.py --inspect`. The converter already validates the input,
checks required dependencies, confirms nonempty output, reports PDF metadata and
extractable text, and renders representative pages when Poppler tools are
available.

Do not run separate shell commands for preflight checks, `pdfinfo`, `pdftotext`,
`pdftoppm`, `identify`, file-size checks, or Git status. Do not read the bundled
converter or template unless conversion fails in a way that requires debugging.

When sandbox escalation is required because the input or output is outside the
workspace, request approval for the narrow reusable command prefix
`python3 ABSOLUTE_SKILL_PATH/scripts/convert.py`. This lets the initial run and
any necessary correction reuse one approval. Do not request a broad Python
prefix.

## Workflow

1. Resolve the input Markdown file and requested output filename.
2. Run the converter once with `--inspect`; preserve relative image paths.
3. When Mermaid blocks are present, render them automatically with Mermaid CLI
   (`mmdc`). If it is unavailable, ask whether the user wants to install it or
   preserve the blocks as source code with `--no-mermaid`. Do not require Mermaid
   CLI for documents without Mermaid blocks.
4. Use US Letter paper and one-inch margins unless the user requests
   alternatives.
5. Pass requested Pandoc options after the output filename, such as `--toc`,
   `--number-sections`, or metadata variables.
6. Inspect the preview paths printed by the converter for clipped text, broken
   tables, missing images, or poor page breaks. A valid, readable render is
   complete; rerun only for a visible defect, using the same approved command
   prefix.
7. Return the completed PDF and leave the source Markdown unchanged unless the
   user explicitly requested source edits.

## Boundaries

- Never overwrite the input Markdown file.
- Never silently replace Pandoc or Typst with a different conversion engine.
- If a dependency is unavailable, report which command is missing. Ask before
  installing Mermaid CLI or its Node.js dependencies.
- If the destination PDF already exists, overwrite it only when the user's
  request clearly identifies that destination; otherwise choose a new name or
  ask.
- Keep generated PDFs beside the source by default unless the user specifies a
  different destination.
