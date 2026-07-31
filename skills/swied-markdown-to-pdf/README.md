# Markdown to PDF

`swied-markdown-to-pdf` converts Markdown documents into polished PDFs with a bundled,
cross-platform converter built on Pandoc and Typst. It preserves the source
Markdown, supports Pandoc options, renders Mermaid diagrams when Mermaid CLI is
available, and can inspect the generated PDF.

## Requirements

The required commands are:

- Python 3.9 or newer
- Pandoc
- Typst

All three must be available on the system `PATH`. Check the environment from
the repository root:

```bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py --check
```

On Windows, use `python` if `python3` is unavailable:

```powershell
python skills\swied-markdown-to-pdf\scripts\convert.py --check
```

### macOS

Install the requirements with [Homebrew](https://brew.sh/):

```bash
brew install python pandoc typst
```

### Windows

Install each application from its official download page:

- [Python for Windows](https://www.python.org/downloads/windows/)
- [Pandoc installation](https://pandoc.org/installing.html)
- [Typst releases](https://github.com/typst/typst/releases)

When installing Python, enable the option that adds it to `PATH`. Open a new
PowerShell window before running the check command.

### Linux

Install Python and Pandoc through the distribution package manager when
available. For Debian or Ubuntu:

```bash
sudo apt update
sudo apt install python3 pandoc
```

Install Typst through the distribution package manager or from the
[official releases](https://github.com/typst/typst/releases). On Ubuntu, it is
also available as a snap:

```bash
sudo snap install typst
```

## Optional Mermaid support

Documents containing fenced `mermaid` blocks require
[Mermaid CLI](https://github.com/mermaid-js/mermaid-cli), Node.js, npm, and a
compatible headless browser:

```bash
npm install --global @mermaid-js/mermaid-cli
```

A normal Mermaid CLI installation generally provides the required browser.
Documents without Mermaid blocks do not require any Node tooling. If `mmdc` is
unavailable, use `--no-mermaid` to preserve Mermaid blocks as source code.

## Install the skill

Install for every supported harness:

```bash
./installers/install.sh all swied-markdown-to-pdf
```

On Windows PowerShell:

```powershell
.\installers\install.ps1 -Harness all -Skill swied-markdown-to-pdf
```

For single-harness installation, updates, uninstallation, development symlinks,
and discovery locations, see the [repository installation guide](../../README.md#install).

## Invoke

```text
Codex:       $swied-markdown-to-pdf Convert report.md to report.pdf.
Claude Code: /swied-markdown-to-pdf Convert report.md to report.pdf.
Pi:          /skill:swied-markdown-to-pdf Convert report.md to report.pdf.
AGY:         Ask for Markdown-to-PDF conversion or select it with /skills.
```

Each harness may also select the skill automatically from its description.

## Use the converter directly

Convert and inspect a document:

```bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  INPUT.md [OUTPUT.pdf] --inspect [PANDOC_OPTIONS...]
```

If the output path is omitted, the PDF is created beside the source Markdown.
Pass Pandoc options after the output filename:

```bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  report.md report.pdf --inspect --toc --number-sections
```

Preserve Mermaid blocks as source code instead of rendering them:

```bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  report.md report.pdf --inspect --no-mermaid
```

On macOS and Linux, the Bash wrapper provides the same interface:

```bash
skills/swied-markdown-to-pdf/scripts/convert.sh \
  report.md report.pdf --inspect
```

The `--inspect` option verifies nonempty output, reports PDF metadata and
extractable text, and renders representative preview pages when the relevant
Poppler utilities are available.

## Test with the included fixture

```bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  tests/fixtures/sample-document.md sample-document.pdf \
  --inspect
```

Mermaid diagrams in the fixture render automatically when `mmdc` is installed.
Use `--no-mermaid` when testing without Mermaid CLI.
