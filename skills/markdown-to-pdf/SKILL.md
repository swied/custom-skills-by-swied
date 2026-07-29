---
name: markdown-to-pdf
description: Convert Markdown or .md files into polished PDF documents using the locally installed Pandoc and Typst command-line programs. Use when the user asks to convert, export, render, typeset, or save Markdown as PDF. Do not use for editing an existing PDF or converting non-Markdown source files.
---

# Markdown to PDF

Use the bundled cross-platform deterministic converter:

```bash
python3 scripts/convert.py INPUT.md [OUTPUT.pdf] [PANDOC_OPTIONS...]
```

Resolve the script path relative to this `SKILL.md`, not relative to the
user's current working directory. On POSIX systems, `scripts/convert.sh`
provides an equivalent wrapper when preferred.

## Workflow

1. Resolve the input Markdown file and requested output filename.
2. Confirm the input exists and has a `.md` or `.markdown` extension.
3. Check referenced local images when practical. Preserve relative paths.
4. Use US Letter paper and one-inch margins unless the user requests
   alternatives.
5. Run `scripts/convert.py` with Python. Pass requested Pandoc options after
   the output filename, such as `--toc`, `--number-sections`, or metadata
   variables.
6. Confirm the resulting PDF exists and is nonempty.
7. When PDF rendering tools are available, render representative pages and
   inspect them for clipped text, broken tables, missing images, or poor page
   breaks. Correct the Markdown or options and rerun when necessary.
8. Return the completed PDF and leave the source Markdown unchanged unless the
   user explicitly requested source edits.

## Boundaries

- Never overwrite the input Markdown file.
- Never silently replace Pandoc or Typst with a different conversion engine.
- If a dependency is unavailable, report which command is missing.
- If the destination PDF already exists, overwrite it only when the user's
  request clearly identifies that destination; otherwise choose a new name or
  ask.
- Keep generated PDFs beside the source by default unless the user specifies a
  different destination.
