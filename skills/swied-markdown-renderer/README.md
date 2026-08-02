# Markdown Renderer

**swied-markdown-renderer** converts Markdown into polished documents while
leaving the source file unchanged. It supports rendered Markdown, PDF, Word,
OpenDocument, RTF, standalone HTML, EPUB, PowerPoint, LaTeX, and Typst output.

The renderer understands TeX math and can turn Mermaid and Graphviz code blocks
into graphics. It prefers native equation objects and SVG graphics when the
destination supports them, then uses PNG where compatibility requires it.

For complete installation, format, option, recipe, and troubleshooting
documentation, read the [Markdown Renderer User Guide](USER_GUIDE.md).

## Highlights

- Convert one Markdown source into ten output families.
- Render Mermaid and Graphviz fences without changing the source.
- Typeset inline and display TeX equations.
- Create self-contained rendered Markdown with embedded SVG or PNG data.
- Preserve ordinary code as syntax-highlighted source; never execute it.
- Inspect output structure and extractable text.
- Add familiar Pandoc options such as a table of contents, numbered sections,
  citations, or a reference document.

## Supported outputs

| Extension | Typical use |
| --- | --- |
| **.md**, **.markdown** | Rendered Markdown with generated graphics embedded inline |
| **.pdf** | Fixed-layout reading and printing |
| **.docx** | Editable Microsoft Word document |
| **.odt** | Editable OpenDocument text |
| **.rtf** | Legacy rich-text interchange |
| **.html**, **.htm** | Standalone web document |
| **.epub** | EPUB3 ebook |
| **.pptx** | PowerPoint presentation |
| **.tex** | Editable LaTeX source |
| **.typ** | Editable Typst source |

The output extension selects the format. If no output is supplied, the
renderer creates a PDF beside the source.

## Quick start

### 1. Check the core tools

Python 3.9 or newer and Pandoc are required for every conversion:

~~~bash
python3 --version
pandoc --version
~~~

On Windows, use **python** if **python3** is unavailable.

Typst is also required for PDF output and whenever equations must become SVG or
PNG graphics.

~~~bash
typst --version
~~~

Mermaid CLI and Graphviz are optional. They are checked only when the source
contains a matching diagram fence that should be rendered.

### 2. Install the skill

Run from the repository root.

On macOS or Linux:

~~~bash
bash installers/install.sh codex swied-markdown-renderer
~~~

On Windows PowerShell:

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-markdown-renderer
~~~

Replace **codex** with another
[supported harness name](../../README.md#supported-harnesses) when needed.

### 3. Ask your assistant to render a document

In Codex:

~~~text
$swied-markdown-renderer Convert report.md to report.docx and inspect it.
~~~

Other examples:

~~~text
$swied-markdown-renderer Turn handbook.md into a standalone HTML document.
~~~

~~~text
$swied-markdown-renderer Render architecture.md as architecture.rendered.md with inline SVG diagrams.
~~~

~~~text
$swied-markdown-renderer Export proposal.md as proposal.pdf with a table of contents and numbered sections.
~~~

## Run the renderer directly

Run commands from the repository root.

Create the default PDF:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py report.md
~~~

Create a Word document:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  report.md report.docx --inspect
~~~

Create self-contained rendered Markdown:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  report.md report.rendered.md --inspect
~~~

Use PNG instead of SVG for rendered Markdown:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  report.md report.rendered.md \
  --diagram-format=png --render-math=png --inspect
~~~

The macOS/Linux wrapper exposes the same interface:

~~~bash
bash skills/swied-markdown-renderer/scripts/render.sh \
  report.md report.epub --inspect
~~~

## Rich content

The renderer recognizes:

- Mermaid fences named **mermaid**.
- Graphviz fences named **dot** or **graphviz**.
- Display-equation fences named **math**, **latex-math**, or **tex-math**.
- TeX math delimited by dollar signs, backslash-parentheses, or
  backslash-brackets.

General-purpose code such as Python, R, JavaScript, or shell remains source
code. The renderer never executes those blocks.

Mermaid rendering requires
[Mermaid CLI](https://github.com/mermaid-js/mermaid-cli). Graphviz rendering
requires the **dot** command. Use **--no-mermaid**, **--no-graphviz**, or
**--no-diagrams** to preserve diagram fences as source.

## Output safety

- The input must end in **.md** or **.markdown**.
- The output must use a supported extension.
- The renderer never overwrites the input.
- An existing output is refused unless **--force** is supplied.
- Rendered Markdown should use a distinct name such as
  **report.rendered.md**.
- Diagram and equation preprocessing is local; the renderer does not upload
  document content to a rendering service.

## Test the skill

The included fixture exercises formatting, math, Mermaid, and Graphviz:

~~~bash
python3 skills/swied-markdown-renderer/scripts/render.py \
  tests/fixtures/renderer-document.md renderer-test.docx \
  --no-diagrams --inspect
~~~

Use **--no-diagrams** for a dependency-friendly first test. Remove it after
installing Mermaid CLI and Graphviz.

Contributors can run the dedicated integration test:

~~~bash
bash tests/swied-markdown-renderer-test.sh
~~~

## Learn more

- [Detailed user guide](USER_GUIDE.md)
- [Format and rich-content support](references/format-support.md)
- [Update an installed skill](../../README.md#update)
- [Uninstall a skill](../../README.md#uninstall-or-delete)
- [Repository troubleshooting](../../README.md#troubleshooting)
