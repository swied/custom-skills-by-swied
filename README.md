# Portable Agent Skills

A collection of focused, reusable skills built on the open Agent Skills
`SKILL.md` format. The canonical skill files live under `skills/`; installer
scripts link or copy them into the discovery locations used by Codex (`codex`), Claude
Code (`claude`), Pi (`pi`), and Google Antigravity CLI (`agy`).

## Included skills

- `markdown-to-pdf`: Convert Markdown files into polished PDF documents with Pandoc and Typst.

## Prerequisites

The `markdown-to-pdf` skill requires:

- Python 3.9 or newer
- Pandoc
- Typst

All three programs must be installed and available on your system `PATH`.
Check the environment after cloning the repository:

```bash
python3 skills/markdown-to-pdf/scripts/convert.py --check
```

On Windows, use `python` if your installation does not provide `python3`:

```powershell
python skills\markdown-to-pdf\scripts\convert.py --check
```

### macOS

Install the prerequisites with [Homebrew](https://brew.sh/):

```bash
brew install python pandoc typst
```

### Windows

Install each application from its official download page:

- [Python for Windows](https://www.python.org/downloads/windows/)
- [Pandoc installation](https://pandoc.org/installing.html)
- [Typst releases](https://github.com/typst/typst/releases)

When installing Python, enable the option that adds Python to `PATH`. Open a
new PowerShell window after installation and run the check command above.

### Linux

Install Python and Pandoc through your distribution's package manager when
available. For Debian or Ubuntu:

```bash
sudo apt update
sudo apt install python3 pandoc
```

Install Typst through your distribution's package manager when available, or
use an official binary from the
[Typst releases](https://github.com/typst/typst/releases) page.

You can also verify each program individually:

```bash
python3 --version
pandoc --version
typst --version
```

If an installed program is reported as missing, confirm that its installation
directory is included in `PATH`.

## Install

### macOS or Linux

Install the skill for every supported harness:

```bash
./installers/install.sh all markdown-to-pdf
```

Install for only one harness:

```bash
./installers/install.sh codex markdown-to-pdf
./installers/install.sh claude markdown-to-pdf
./installers/install.sh pi markdown-to-pdf
./installers/install.sh agy markdown-to-pdf
```

The POSIX installer creates symbolic links, so edits in this repository become
available immediately.

### Windows PowerShell

```powershell
.\installers\install.ps1 -Harness all -Skill markdown-to-pdf
```

The PowerShell installer copies the skill by default for broad Windows
compatibility. Rerun it after updating the repository. Pass `-UseSymlink` if
your Windows configuration permits symbolic links.

### Discovery locations

| Harness | Personal/global skill directory |
| --- | --- |
| Codex | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| Pi | `~/.agents/skills/` |
| Antigravity/AGY | `~/.gemini/config/skills/` |

Codex and Pi intentionally share the same installation.

## Invoke the skill

Harnesses use different explicit-invocation syntax:

```text
Codex:       $markdown-to-pdf Convert report.md to report.pdf.
Claude Code: /markdown-to-pdf Convert report.md to report.pdf.
Pi:          /skill:markdown-to-pdf Convert report.md to report.pdf.
AGY:         Ask for Markdown-to-PDF conversion or select it with /skills.
```

All four may also select the skill automatically from its description.

## Test the converter directly

Check the prerequisites:

```bash
python3 skills/markdown-to-pdf/scripts/convert.py --check
```

Convert the included example:

```bash
python3 skills/markdown-to-pdf/scripts/convert.py \
  tests/fixtures/sample-document.md sample-document.pdf
```

Add `--toc` or any other Pandoc option after the output filename:

```bash
python3 skills/markdown-to-pdf/scripts/convert.py \
  tests/fixtures/sample-document.md sample-document.pdf \
  --toc --number-sections
```

On macOS and Linux, the Bash wrapper provides the same interface:

```bash
skills/markdown-to-pdf/scripts/convert.sh \
  tests/fixtures/sample-document.md sample-document.pdf
```

## Repository design

Keep each skill under `skills/<skill-name>/` as the single source of truth.
Add harness-specific installation or packaging logic under `installers/`
instead of maintaining multiple copies of a skill.
