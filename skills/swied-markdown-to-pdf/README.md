# Markdown to PDF

**swied-markdown-to-pdf** turns a Markdown file into a polished PDF while
leaving the original Markdown unchanged.

The skill uses a bundled, cross-platform converter built on Pandoc and Typst.
It handles local images, can render Mermaid diagrams, accepts familiar Pandoc
options, and can inspect the finished PDF for common problems.

You can ask your CLI assistant to perform the conversion, or run the converter
directly when you want manual control.

## Quick start

### 1. Check the required tools

The converter needs:

- Python 3.9 or newer.
- Pandoc.
- Typst.

Confirm that all three are available in your terminal:

~~~bash
python3 --version
pandoc --version
typst --version
~~~

On Windows, use **python** if **python3** is unavailable:

~~~powershell
python --version
pandoc --version
typst --version
~~~

If a command is missing, follow the
[installation instructions](#install-the-required-tools) below.

### 2. Install the skill

Run the command from the root of this repository.

On macOS or Linux:

~~~bash
bash installers/install.sh codex swied-markdown-to-pdf
~~~

On Windows PowerShell:

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-markdown-to-pdf
~~~

This example installs the skill for Codex. Replace **codex** with your own
[supported harness name](../../README.md#supported-harnesses).

### 3. Create a PDF

Start a new session in your CLI harness. In Codex:

~~~text
$swied-markdown-to-pdf Convert report.md to report.pdf and inspect the result.
~~~

For a dependency-friendly test using the sample in this repository:

~~~text
$swied-markdown-to-pdf Convert tests/fixtures/sample-document.md to sample-document.pdf with --no-mermaid, then inspect it.
~~~

The **--no-mermaid** option keeps the sample's Mermaid block as source code, so
the optional Mermaid CLI is not required for this first test.

## Install the required tools

Python, Pandoc, and Typst must be available on your system **PATH**. The PATH is
the list of places your terminal searches for commands.

### macOS

Install all three with [Homebrew](https://brew.sh/):

~~~bash
brew install python pandoc typst
~~~

Open a new terminal after installation, then rerun the three version commands
from the quick start.

### Windows

Install each tool from its official download page:

- [Python for Windows](https://www.python.org/downloads/windows/)
- [Pandoc installation](https://pandoc.org/installing.html)
- [Typst releases](https://github.com/typst/typst/releases)

When installing Python, enable the option that adds Python to **PATH**. Open a
new PowerShell window after installing the tools, then rerun the version
commands.

### Linux

Use your distribution's package manager when possible. On Debian or Ubuntu:

~~~bash
sudo apt update
sudo apt install python3 pandoc
~~~

Install Typst through your package manager or from the
[official Typst releases](https://github.com/typst/typst/releases). Ubuntu users
can also install it as a snap:

~~~bash
sudo snap install typst
~~~

## Use the skill

Explicit invocation varies by harness:

| Harness | Example |
| --- | --- |
| Codex | **$swied-markdown-to-pdf Convert report.md to report.pdf.** |
| Claude Code | **/swied-markdown-to-pdf Convert report.md to report.pdf.** |
| Pi | **/skill:swied-markdown-to-pdf Convert report.md to report.pdf.** |
| AGY / Antigravity | Ask naturally, or select the skill with **/skills**. |

Many harnesses can also select the skill from an ordinary request:

~~~text
Turn meeting-notes.md into a polished PDF.
~~~

~~~text
Convert proposal.md to proposal.pdf with a table of contents and numbered sections.
~~~

~~~text
Export docs/handbook.md as a PDF and check the result for layout problems.
~~~

### What happens by default?

- The PDF is created beside the source Markdown.
- If you do not name an output file, it uses the same base name. For example,
  **report.md** becomes **report.pdf**.
- Pages use US Letter paper with one-inch margins unless you request something
  different.
- Relative image paths are resolved from the Markdown file's directory.
- The source Markdown is not changed.

If the destination PDF already exists, the skill overwrites it only when your
request clearly names that destination. Otherwise, it chooses a new name or
asks what you prefer.

### Ask for common options

You can describe the result in ordinary language:

~~~text
Convert report.md to report.pdf with a table of contents.
~~~

~~~text
Create a PDF from handbook.md, number the sections, and inspect the first and last pages.
~~~

~~~text
Convert report.md to report.pdf using A4 paper instead of US Letter.
~~~

The skill passes supported formatting requests to Pandoc and Typst.

## Mermaid diagrams

Markdown can contain diagrams in fenced **mermaid** blocks. The converter
automatically renders those blocks when
[Mermaid CLI](https://github.com/mermaid-js/mermaid-cli) is installed.

Install Mermaid CLI with npm:

~~~bash
npm install --global @mermaid-js/mermaid-cli
~~~

This optional feature also requires Node.js, npm, and a compatible headless
browser. A normal Mermaid CLI installation usually provides the browser it
needs.

You do not need Node.js or Mermaid CLI for documents without Mermaid blocks.

If a document contains Mermaid but the **mmdc** command is unavailable, choose
one of these options:

- Install Mermaid CLI, then retry.
- Use **--no-mermaid** to show the Mermaid block as source code instead of a
  rendered diagram.

The original Markdown is preserved either way.

## Run the converter directly

You can use the bundled converter without an AI harness. Run these commands from
the repository root.

### Basic conversion

Create **report.pdf** beside **report.md**:

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py report.md
~~~

Choose an output name:

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py report.md finished-report.pdf
~~~

On Windows, replace **python3** with **python** when needed.

### Add a table of contents and numbered sections

Pandoc options go after the input and output filenames:

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  report.md report.pdf \
  --toc --number-sections
~~~

### Inspect the result

The converter always confirms that it created a nonempty PDF. Add **--inspect**
to report whatever additional inspection information is available:

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  report.md report.pdf \
  --inspect
~~~

When Poppler tools are installed, inspection can also report page metadata,
check extractable text, and render previews of the first and last pages. The
converter prints the temporary preview paths so they can be opened or inspected.

Poppler is helpful for deeper inspection, but it is not required to create a
PDF.

### Keep Mermaid as source code

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  report.md report.pdf \
  --inspect --no-mermaid
~~~

### Use the Bash wrapper

On macOS and Linux, the wrapper provides the same interface:

~~~bash
bash skills/swied-markdown-to-pdf/scripts/convert.sh \
  report.md report.pdf --inspect
~~~

Important: the direct converter can replace an existing destination PDF. Check
the output path before running it.

## Test with the included sample

The repository includes a Markdown document with headings, tables, links, code,
and a Mermaid diagram.

Test without optional Mermaid support:

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  tests/fixtures/sample-document.md sample-document.pdf \
  --inspect --no-mermaid
~~~

If Mermaid CLI is installed, remove **--no-mermaid** to render the diagram:

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  tests/fixtures/sample-document.md sample-document.pdf \
  --inspect
~~~

The generated **sample-document.pdf** is placed in the repository root. It is a
test output and can be deleted when you are finished with it.

## Troubleshooting

### “Pandoc is not installed” or “Typst is not installed”

Run the version commands from the quick start. Install the missing tool, open a
new terminal so PATH changes take effect, and retry.

### Mermaid blocks are found, but **mmdc** is unavailable

Install Mermaid CLI or rerun with **--no-mermaid**.

### An image is missing from the PDF

Check that the image path in the Markdown is correct relative to the Markdown
file itself. For example, an image referenced as **images/chart.png** should be
inside an **images** folder beside the Markdown file.

### The PDF exists but the layout looks wrong

Run again with **--inspect** and review the preview pages when available. Long
tables, very wide code blocks, and oversized images are common causes of
clipping.

### The input is rejected

The converter accepts files ending in **.md** or **.markdown**. It is not
intended for editing existing PDFs or converting other source formats.

### The harness cannot find the skill

Start a new harness session, then check the install destination and invocation
syntax in the [repository troubleshooting guide](../../README.md#troubleshooting).

## Update or uninstall

The repository installer can safely refresh or remove the skill:

- [Update an installed skill](../../README.md#update)
- [Uninstall a skill](../../README.md#uninstall-or-delete)
- [Use a development symlink](../../README.md#use-a-symlink-while-editing-a-skill)
