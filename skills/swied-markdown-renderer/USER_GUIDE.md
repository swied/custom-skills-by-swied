# Markdown Renderer User Guide

This guide explains how to install and use **swied-markdown-renderer**, choose
an output format, author renderable diagrams and equations, inspect results,
and troubleshoot optional tools.

## Contents

- [Overview](#overview)
- [How rendering works](#how-rendering-works)
- [Requirements](#requirements)
- [Install the skill](#install-the-skill)
- [Use the skill through an AI harness](#use-the-skill-through-an-ai-harness)
- [Run the renderer directly](#run-the-renderer-directly)
- [Choose an output format](#choose-an-output-format)
- [Author rich Markdown](#author-rich-markdown)
- [Rendered Markdown output](#rendered-markdown-output)
- [Renderer options](#renderer-options)
- [Pandoc options](#pandoc-options)
- [Inspection](#inspection)
- [Common recipes](#common-recipes)
- [Files and overwrite behavior](#files-and-overwrite-behavior)
- [Troubleshooting](#troubleshooting)
- [Privacy and safety](#privacy-and-safety)
- [Update or uninstall](#update-or-uninstall)
- [Contributor checks](#contributor-checks)

## Overview

The renderer accepts one **.md** or **.markdown** source and writes a new
document selected by the output extension. It leaves the source unchanged.

Supported outputs are:

- Rendered Markdown: **.md** and **.markdown**
- Fixed-layout document: **.pdf**
- Editable word-processing documents: **.docx**, **.odt**, and **.rtf**
- Web and ebook documents: **.html**, **.htm**, and **.epub**
- Presentation: **.pptx**
- Editable typesetting sources: **.tex** and **.typ**

The renderer can preprocess declarative fenced blocks:

- Mermaid diagrams
- Graphviz diagrams
- TeX display equations

It also recognizes inline and display TeX math. Ordinary code remains source
code and is never executed.

## How rendering works

The bundled Python program coordinates the complete pipeline:

1. Validate the input, output extension, overwrite policy, and renderer
   options.
2. Ask Pandoc to parse Markdown into its document tree.
3. Replace supported diagram fences with locally generated SVG or PNG images.
4. Preserve equations natively when the destination has a dependable equation
   representation.
5. Generate local SVG or PNG equation graphics when the destination needs
   them.
6. Ask Pandoc to write the requested output.
7. Confirm that a nonempty output was created.
8. When **--inspect** is present, validate structure and extractable text, then
   create representative PDF previews when the required tools are available.

The source Markdown is never rewritten during this process.

## Requirements

Dependencies are conditional. You do not need every optional tool for every
document.

| Tool | When it is required |
| --- | --- |
| Python 3.9 or newer | Every conversion |
| Pandoc | Every conversion |
| Typst | PDF output; RTF documents containing math; SVG or PNG equation rendering |
| Mermaid CLI | A rendered **mermaid** fence |
| Graphviz | A rendered **dot** or **graphviz** fence |
| Poppler tools | Optional deeper PDF inspection and preview images |
| rsvg-convert | Optional PNG fallback for SVG images in older Word readers |

Check installed versions:

~~~bash
python3 --version
pandoc --version
typst --version
mmdc --version
dot -V
~~~

On Windows, use **python** if **python3** is unavailable.

### macOS

Homebrew can install the core renderer and Graphviz:

~~~bash
brew install python pandoc typst graphviz
~~~

Install Mermaid CLI after installing Node.js and npm:

~~~bash
npm install --global @mermaid-js/mermaid-cli
~~~

Install Poppler only when PDF preview inspection is useful:

~~~bash
brew install poppler
~~~

### Windows

Install the required tools from their official distributions:

- [Python for Windows](https://www.python.org/downloads/windows/)
- [Pandoc installation](https://pandoc.org/installing.html)
- [Typst releases](https://github.com/typst/typst/releases)
- [Graphviz downloads](https://graphviz.org/download/)
- [Node.js downloads](https://nodejs.org/en/download)

Enable the installer option that adds a program to **PATH** when one is
offered. Open a new PowerShell window after installation, then rerun the version
checks.

Install Mermaid CLI from PowerShell after npm is available:

~~~powershell
npm install --global @mermaid-js/mermaid-cli
~~~

### Linux

Use the distribution package manager for Python, Pandoc, and Graphviz when
possible. On Debian or Ubuntu:

~~~bash
sudo apt update
sudo apt install python3 pandoc graphviz
~~~

Install Typst through the distribution package manager or from the
[official Typst releases](https://github.com/typst/typst/releases).

Install Node.js and npm through the distribution or Node.js installation
instructions, then install Mermaid CLI:

~~~bash
npm install --global @mermaid-js/mermaid-cli
~~~

## Install the skill

Run installer commands from the root of this repository.

### macOS or Linux

Install for Codex:

~~~bash
bash installers/install.sh codex swied-markdown-renderer
~~~

Install for another harness by replacing **codex** with a
[supported alias](../../README.md#supported-harnesses):

~~~bash
bash installers/install.sh claude swied-markdown-renderer
bash installers/install.sh pi swied-markdown-renderer
~~~

### Windows PowerShell

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-markdown-renderer
~~~

Start a new harness session after installation so the harness discovers the
skill.

## Use the skill through an AI harness

Explicit invocation differs by harness:

| Harness | Example |
| --- | --- |
| Codex | **$swied-markdown-renderer Convert report.md to report.docx.** |
| Claude Code | **/swied-markdown-renderer Convert report.md to report.docx.** |
| Pi | **/skill:swied-markdown-renderer Convert report.md to report.docx.** |
| AGY / Antigravity | Ask naturally, or select the skill with **/skills**. |

Many harnesses can select the skill from a natural-language request:

~~~text
Convert docs/handbook.md to a standalone HTML document and inspect it.
~~~

~~~text
Turn architecture.md into architecture.rendered.md with inline SVG diagrams.
~~~

~~~text
Export proposal.md as proposal.pdf with a table of contents.
~~~

~~~text
Create slides.pptx from slides.md and preserve Mermaid blocks as source.
~~~

The harness controls filesystem access and command approvals. The skill
provides the workflow and deterministic renderer.

## Run the renderer directly

The command form is:

~~~text
render.py INPUT.md [OUTPUT] [RENDERER_OPTIONS] [PANDOC_OPTIONS...]
~~~

Run from the repository root:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  INPUT.md OUTPUT --inspect
~~~

The output extension selects the writer. If **OUTPUT** is omitted, the renderer
creates a PDF with the source basename.

Examples:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py report.md
python3 skills/swied-markdown-renderer/scripts/render.py report.md report.docx
python3 skills/swied-markdown-renderer/scripts/render.py report.md report.epub
python3 skills/swied-markdown-renderer/scripts/render.py report.md report.rendered.md
~~~

On macOS or Linux, the Bash wrapper is equivalent:

~~~bash
bash skills/swied-markdown-renderer/scripts/render.sh \
  report.md report.pdf --inspect
~~~

## Choose an output format

| Extension | Intended use | Equation behavior | Diagram behavior |
| --- | --- | --- | --- |
| **.md**, **.markdown** | Self-contained rendered Markdown | Embedded SVG by default | Embedded SVG by default |
| **.pdf** | Printing and fixed layout | Native Typst typesetting | SVG |
| **.docx** | Microsoft Word editing | Native OMML | SVG with an optional PNG fallback |
| **.odt** | LibreOffice and OpenDocument editing | Native MathML | SVG |
| **.rtf** | Legacy interchange | PNG graphics | PNG |
| **.html**, **.htm** | Standalone browser document | Embedded MathML | Embedded SVG |
| **.epub** | EPUB3 ebook | MathML | SVG |
| **.pptx** | PowerPoint slides | Native OMML | PNG |
| **.tex** | Editable LaTeX source | Native LaTeX | PNG in a media directory |
| **.typ** | Editable Typst source | Native Typst | SVG in a media directory |

### PDF

PDF output uses the bundled Typst template. The default is US Letter paper with
one-inch margins. Use Pandoc variables when another paper size is required.

PDF is the default when no output name is supplied.

### DOCX and ODT

These formats are appropriate when the recipient should edit the result.
Equations remain native document objects. Use a Pandoc reference document when
you need organization-specific styles.

### RTF

RTF has limited equation support, so math becomes local PNG graphics. Typst is
required only when the source actually contains math that must be rendered.

### HTML

HTML output is standalone and embeds resources. Equations use MathML, avoiding
a runtime MathJax dependency.

### EPUB

The renderer writes EPUB3 and uses MathML for equations. Test the result in the
reader applications that matter to your audience because EPUB rendering engines
vary.

### PPTX

PowerPoint output works best when the source is written as slides. Headings
define slide structure according to Pandoc presentation rules. Converting a
long-form report directly may produce an awkward deck.

### LaTeX and Typst source

These outputs are editable typesetting source rather than finished documents.
Generated diagrams are stored in a sibling directory named after the output,
such as **report-media**. Keep that directory with the generated source.

## Author rich Markdown

### Metadata

Pandoc YAML metadata is supported:

~~~markdown
---
title: Quarterly Architecture Review
author: Example Team
date: 2026-08-02
---

# Introduction
~~~

Metadata support varies by output format. Title, author, date, language,
bibliography, and other Pandoc metadata can influence templates and writers.

### Mermaid diagrams

Use a fence named **mermaid**:

~~~~markdown
~~~mermaid
graph TD
    accTitle: Rendering pipeline
    accDescr: Markdown is converted into a finished document
    A[Markdown] --> B[Renderer]
    B --> C[Document]
~~~
~~~~

The renderer uses **accTitle** and **accDescr** when available to improve image
titles and alternative text.

Mermaid requires the **mmdc** command and a compatible headless browser. If the
dependency is unavailable, install it or preserve the fence with
**--no-mermaid**.

### Graphviz diagrams

Use **dot** or **graphviz**:

~~~~markdown
~~~dot
digraph {
    Markdown -> Renderer;
    Renderer -> Document;
}
~~~
~~~~

Graphviz requires the **dot** command. Use **--no-graphviz** to preserve the
fence as source.

### Inline and display math

Dollar-delimited TeX math is supported:

~~~markdown
Einstein's equation is $E = mc^2$.

$$
\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}
$$
~~~

Backslash delimiters are also supported:

~~~markdown
Inline: \(a^2 + b^2 = c^2\)

Display:
\[
\sum_{k=1}^{n} k = \frac{n(n+1)}{2}
\]
~~~

### Fenced display equations

Use **math**, **latex-math**, or **tex-math**:

~~~~markdown
~~~math
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
~~~
~~~~

Generic **latex** and **tex** fences remain code because they may contain a
complete document rather than one equation.

### Ordinary code

Other fences remain syntax-highlighted source:

~~~~markdown
~~~python
def square(value: int) -> int:
    return value * value
~~~
~~~~

The renderer never executes Python, R, shell, JavaScript, Jupyter, or another
general-purpose language.

### Existing images

Relative image paths are resolved from the source Markdown directory:

~~~markdown
![Architecture](images/architecture.png)
~~~

Binary document formats and standalone HTML embed referenced resources where
Pandoc supports it. Rendered Markdown embeds newly generated diagram and
equation graphics, but it leaves existing image links unchanged.

## Rendered Markdown output

Markdown-to-Markdown rendering replaces supported rich blocks with graphics
while preserving the rest of the document as Markdown.

Use a distinct output name:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  architecture.md architecture.rendered.md --inspect
~~~

Generated equations and diagrams become HTML image elements whose source is a
base64 data URI. SVG is the default:

~~~text
<img src="data:image/svg+xml;base64,..." alt="..." />
~~~

Choose PNG when the destination Markdown viewer does not accept SVG:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  architecture.md architecture.rendered.md \
  --diagram-format=png --render-math=png --inspect
~~~

Preserve TeX math instead of converting it to pictures:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  architecture.md architecture.rendered.md \
  --render-math=native --inspect
~~~

Data URIs make generated graphics self-contained, but some hosted Markdown
platforms sanitize them. Use standalone HTML when the target platform strips
data images.

## Renderer options

### Inspect the result

~~~text
--inspect
~~~

Validate output structure and report extractable text. PDF inspection can also
produce preview PNGs when Poppler is installed.

### Replace an existing output

~~~text
--force
~~~

Without this option, an existing output causes the conversion to stop. Use it
only when replacing that exact destination is intentional.

### Preserve every diagram fence

~~~text
--no-diagrams
~~~

Do not invoke Mermaid CLI or Graphviz. Leave matching blocks as source code.

### Preserve one diagram language

~~~text
--no-mermaid
--no-graphviz
~~~

Disable one renderer while allowing the other.

### Select the diagram image type

~~~text
--diagram-format=svg
--diagram-format=png
~~~

The default is format-aware. SVG is preferred where dependable; RTF, PPTX, and
LaTeX use PNG. The renderer rejects a forced SVG target when that output does
not reliably support it.

### Select math behavior

~~~text
--render-math=auto
--render-math=native
--render-math=svg
--render-math=png
~~~

- **auto** uses native equations where possible and graphics where necessary.
- **native** asks Pandoc to preserve the equation semantically.
- **svg** creates local scalable equation graphics.
- **png** creates local raster equation graphics.

Rendered Markdown defaults to SVG equation graphics. RTF defaults to PNG.

## Pandoc options

Arguments not recognized as renderer options are passed to the Pandoc writer.
Common examples include:

### Table of contents

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  handbook.md handbook.pdf --toc
~~~

### Numbered sections

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  handbook.md handbook.docx --number-sections
~~~

### Citations

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  paper.md paper.pdf \
  --citeproc --bibliography=references.bib
~~~

### Reference document

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  report.md report.docx \
  --reference-doc=company-reference.docx
~~~

The renderer owns the input reader, output writer, PDF engine, and destination.
Do not pass Pandoc **--from**, **--to**, **--output**, **-f**, **-t**, **-o**, or
**--pdf-engine**. Select the output through its positional filename.

## Inspection

Inspection always reports output size when **--inspect** is present.

Additional checks depend on the format:

| Format | Inspection |
| --- | --- |
| PDF | Metadata, page count, page size, extractable text, and representative previews when Poppler is available |
| DOCX, ODT, EPUB, PPTX | ZIP-container integrity and required members |
| RTF | RTF header validation |
| HTML | Standalone document-element validation |
| Other readable outputs | Pandoc plain-text extraction when supported |

Inspection confirms deterministic structure and catches empty output. It does
not replace opening a document in the application used by the recipient.
Review layout-sensitive DOCX, ODT, PPTX, and EPUB outputs in their target
applications when presentation quality is important.

## Common recipes

### Dependency-friendly first test

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  tests/fixtures/renderer-document.md renderer-test.pdf \
  --no-diagrams --inspect
~~~

### Standalone HTML

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  handbook.md handbook.html --toc --inspect
~~~

### Editable Word report

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  report.md report.docx \
  --number-sections --reference-doc=reference.docx --inspect
~~~

### EPUB ebook

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  book.md book.epub --toc --inspect
~~~

### PowerPoint with diagrams preserved as source

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  slides.md slides.pptx --no-diagrams --inspect
~~~

### Legacy RTF with equation graphics

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  legacy.md legacy.rtf --inspect
~~~

### Rendered Markdown with PNG graphics

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  architecture.md architecture.rendered.md \
  --diagram-format=png --render-math=png --inspect
~~~

## Files and overwrite behavior

- Keep output beside the source unless another destination is requested.
- Omitted output means a PDF beside the source.
- Never use the source itself as the output.
- Existing output is refused unless **--force** is supplied.
- Temporary renderer files are removed after conversion.
- Rendered Markdown embeds generated media and needs no generated media
  directory.
- LaTeX and Typst source exports may create a sibling media directory.
- The renderer does not delete older user files or unrelated media.

## Troubleshooting

### Pandoc is unavailable

Run:

~~~bash
pandoc --version
~~~

Install Pandoc, open a new terminal, and retry.

### Typst is unavailable

Typst is required for PDF and equation graphics. Run:

~~~bash
typst --version
~~~

Install Typst or, for a format with native math support, retry with
**--render-math=native**.

### Mermaid CLI is unavailable

Install Mermaid CLI:

~~~bash
npm install --global @mermaid-js/mermaid-cli
~~~

Or preserve Mermaid as source:

~~~text
--no-mermaid
~~~

### Mermaid cannot launch its browser

Mermaid CLI uses a headless browser. Container policies, Linux user-namespace
restrictions, or browser sandbox configuration can prevent it from starting.
Follow the Mermaid CLI and Puppeteer guidance for the operating environment.
Do not disable browser security casually. Use **--no-mermaid** when rendering is
not safe or available.

### Graphviz is unavailable

Install Graphviz so **dot** is on **PATH**, or retry with
**--no-graphviz**.

### An output already exists

Choose another output name. Use **--force** only when replacing that exact file
is intentional.

### The input is rejected

Input must end in **.md** or **.markdown**. The skill does not convert arbitrary
source formats.

### The output extension is rejected

Choose one of the documented supported extensions. The renderer intentionally
does not expose every Pandoc writer without a tested fidelity contract.

### An existing image is missing

Resolve relative image links from the source Markdown directory. If the source
contains **images/chart.png**, that path should exist relative to the source.

### Rendered Markdown images do not display

Check whether the Markdown viewer permits data URI images. Some hosted
platforms sanitize them. Try PNG, preserve the source blocks, or use standalone
HTML.

### An equation appears as source

Confirm that it uses one of the supported delimiters or an equation fence.
Generic **latex** and **tex** fences intentionally remain code. For RTF or
rendered Markdown, confirm Typst is available.

### PPTX layout is poor

Rewrite the source as a presentation with meaningful heading boundaries and
concise slide content. A long-form report is rarely a good slide deck without
adaptation.

### Inspection warns that it cannot re-read an output

Some installed Pandoc versions can write formats they cannot read. Archive and
header validation still runs where supported. Open the document in its target
application for the final layout check.

### The harness cannot find the skill

Start a new session, confirm the installer destination, and check the
[repository troubleshooting guide](../../README.md#troubleshooting).

## Privacy and safety

- Diagram and equation definitions are rendered locally.
- The renderer does not silently use a remote diagram or equation service.
- The input is not modified.
- General-purpose code blocks are never executed.
- Missing optional dependencies produce a clear error and an opt-out path.
- Browser sandbox changes for Mermaid CLI remain an operator decision.
- The harness still controls filesystem and command permissions.

Remote images or other remote resources referenced explicitly by the source or
Pandoc options remain subject to Pandoc behavior. Review untrusted Markdown and
command options before conversion.

## Update or uninstall

Refresh a copied Codex installation:

~~~bash
bash installers/install.sh update codex swied-markdown-renderer
~~~

On Windows PowerShell:

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-markdown-renderer -Update
~~~

Uninstall from Codex:

~~~bash
bash installers/install.sh uninstall codex swied-markdown-renderer
~~~

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-markdown-renderer -Uninstall
~~~

See the repository guides for [updates](../../README.md#update),
[uninstallation](../../README.md#uninstall-or-delete), and
[development symlinks](../../README.md#use-a-symlink-while-editing-a-skill).

## Contributor checks

Run the renderer unit and integration tests:

~~~bash
python3 -m unittest tests.test_swied_markdown_renderer
bash tests/swied-markdown-renderer-test.sh
~~~

Run the complete repository validation from the repository root:

~~~bash
python3 scripts/validate_skills.py skills
python3 scripts/audit_harness_docs.py --check-config-only
python3 -m unittest discover -s tests -p 'test_*.py'
bash tests/installers-test.sh
bash tests/swied-markdown-to-pdf-test.sh
bash tests/swied-markdown-renderer-test.sh
~~~

The integration test creates temporary output for every supported format
family. The Mermaid browser smoke test is opt-in because headless-browser
sandbox support varies by environment:

~~~bash
SWIED_RUN_MERMAID_INTEGRATION=1 \
  bash tests/swied-markdown-renderer-test.sh
~~~
