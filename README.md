# Portable agent skills, without the harness lock-in

Skills give command-line AI assistants a repeatable way to handle a task. A
skill can teach an assistant how to make a careful Git commit, create a polished
PDF, or follow any other reusable workflow.

The awkward part is portability. Many skill repositories are built around one
particular CLI harness. That works well until you use a different harness—or
several of them—and discover that each one looks for skills in a different
place or invokes them differently.

This repository solves that installation problem. It keeps one portable source
for each skill and provides installers for a wide range of CLI harnesses,
including Codex, Claude Code, Pi, OpenCode, GitHub Copilot, Gemini CLI, Kiro,
Qwen Code, Factory Droid, and more. You choose a harness; the installer puts the
skill where that harness expects to find it.

Hi, I'm [Scott Wied](https://www.linkedin.com/in/scottwied/), the maintainer of this project.
I created this collection to make useful agent workflows easier to reuse
without tying them to a single tool. The canonical skills follow the open
[Agent Skills specification](https://agentskills.io/specification), while the
small installation layer handles the harness-specific differences.

## What's included?

| Skill | What it helps with | Learn more |
| --- | --- | --- |
| **swied-git-commit** | Reviews, stages, validates, and commits a Git working tree with a repository-aware message. | [Git Commit guide](skills/swied-git-commit/README.md) |
| **swied-markdown-to-pdf** | Turns Markdown into a polished PDF using Pandoc and Typst. | [Markdown to PDF guide](skills/swied-markdown-to-pdf/README.md) |

Each skill has its own guide with requirements, examples, and detailed
behavior. This README covers the shared install, test, update, and uninstall
workflow.

## Quick start

The quickest path is to install one skill for the CLI harness you already use.
The example below uses Codex, but you can replace **codex** with another
[supported harness name](#supported-harnesses).

### 1. Get the repository

If you have Git installed, open a terminal and run:

~~~bash
git clone https://github.com/swied/custom-skills-by-swied.git
cd custom-skills-by-swied
~~~

You can also download the repository as a ZIP from GitHub, extract it, and open
a terminal in the extracted folder. The remaining commands work either way.

### 2. Install a skill

On macOS or Linux:

~~~bash
bash installers/install.sh codex swied-git-commit
~~~

On Windows PowerShell:

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-git-commit
~~~

The installer prints the destination it created. By default, it copies the
skill there, so the installed skill keeps working even if you move or delete
this repository later.

### 3. Try the skill

Start a new session in your CLI harness so it can discover the newly installed
skill. In Codex, for example:

~~~text
$swied-git-commit Explain what you would check before making a commit. Do not change anything.
~~~

For a practical test in a Git repository with changes you are ready to commit:

~~~text
$swied-git-commit Commit my current changes.
~~~

That's it. The source remains in this repository, and the installer can safely
refresh or remove the installed copy later.

## Install

Run installation commands from the repository root—the folder containing this
README.

### Install one skill for one harness

Use the harness you actually run. Here are a few macOS and Linux examples:

~~~bash
bash installers/install.sh claude swied-git-commit
bash installers/install.sh pi swied-markdown-to-pdf
bash installers/install.sh opencode swied-git-commit
bash installers/install.sh factory swied-markdown-to-pdf
~~~

The same examples in Windows PowerShell are:

~~~powershell
.\installers\install.ps1 -Harness claude -Skill swied-git-commit
.\installers\install.ps1 -Harness pi -Skill swied-markdown-to-pdf
.\installers\install.ps1 -Harness opencode -Skill swied-git-commit
.\installers\install.ps1 -Harness factory -Skill swied-markdown-to-pdf
~~~

Tip: start with one harness and one skill. You can add other combinations at
any time.

### Install both skills

There is one install command per skill. For Codex:

~~~bash
bash installers/install.sh codex swied-git-commit
bash installers/install.sh codex swied-markdown-to-pdf
~~~

On Windows PowerShell:

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-git-commit
.\installers\install.ps1 -Harness codex -Skill swied-markdown-to-pdf
~~~

### Install for every supported harness

Use **all** when you intentionally want a skill installed in every supported
discovery location:

~~~bash
bash installers/install.sh all swied-git-commit
bash installers/install.sh all swied-markdown-to-pdf
~~~

~~~powershell
.\installers\install.ps1 -Harness all -Skill swied-git-commit
.\installers\install.ps1 -Harness all -Skill swied-markdown-to-pdf
~~~

This is convenient when you regularly switch among harnesses. It is not
required for normal use.

### See the available harness names

On macOS or Linux, ask the installer for the current list:

~~~bash
bash installers/install.sh list
~~~

You can use a harness name such as **codex**, a group name such as **agents**,
or **all**. Harnesses in the same group share one discovery directory, so
installing for Codex also makes that installation visible to other harnesses
that read the same directory.

## Use the skills

Harnesses use different explicit invocation syntax:

| Harness | Example |
| --- | --- |
| Codex | **$swied-git-commit Commit the changes for the login fix.** |
| Claude Code | **/swied-git-commit Commit the changes for the login fix.** |
| Pi | **/skill:swied-git-commit Commit the changes for the login fix.** |
| AGY / Antigravity | Ask naturally, or select the skill with **/skills**. |

Many harnesses can also choose a skill automatically from an ordinary request.
For example:

~~~text
Review my changes, write an appropriate commit message, and commit them.
~~~

~~~text
Convert docs/project-plan.md to a polished PDF with a table of contents.
~~~

~~~text
Turn meeting-notes.md into meeting-notes.pdf and inspect the result.
~~~

If your harness does not select the skill automatically, use its skill picker
or the explicit syntax shown by that harness.

A skill is a set of instructions for your assistant; it is not a background
service. Your harness still controls file access, command approval, and other
permissions.

## Test

There are three useful levels of testing. Most users only need the first one.

### Check that your harness found the skill

After installation, start a new harness session and ask the skill a read-only
question:

~~~text
$swied-git-commit Summarize your commit workflow. Do not make any changes.
~~~

For Claude Code, start with **/swied-git-commit**. For Pi, start with
**/skill:swied-git-commit**.

### Check Markdown-to-PDF requirements

The PDF skill requires Python 3.9 or newer, Pandoc, and Typst. Check all three
from a terminal:

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

You can then make a real PDF from the included sample:

~~~bash
python3 skills/swied-markdown-to-pdf/scripts/convert.py \
  tests/fixtures/sample-document.md sample-document.pdf \
  --inspect --no-mermaid
~~~

The **--no-mermaid** option makes this test work without the optional Mermaid
CLI. See the [Markdown to PDF guide](skills/swied-markdown-to-pdf/README.md) for
dependency installation and Mermaid support.

### Run the repository test suite

Contributors and curious users can validate every skill and installer. First,
install the development dependency:

~~~bash
python3 -m pip install -r requirements-dev.txt
~~~

Then run the checks from the repository root:

~~~bash
python3 scripts/validate_skills.py skills
python3 scripts/audit_harness_docs.py --check-config-only
python3 -m unittest discover -s tests -p 'test_*.py'
bash tests/installers-test.sh
bash tests/swied-markdown-to-pdf-test.sh
~~~

These commands check the portable skill structure, harness configuration,
Python behavior, installer lifecycle, and end-to-end PDF conversion. The PDF
test skips cleanly if Pandoc or Typst is unavailable. Tests use temporary
folders and do not change your real harness installations. On Windows, run the
two Bash test scripts from Git Bash or WSL.

## Update

An installed copy does not update automatically. Refresh the repository first,
then ask the installer to replace its copy.

If you cloned with Git:

~~~bash
git pull
bash installers/install.sh update codex swied-git-commit
~~~

On Windows PowerShell:

~~~powershell
git pull
.\installers\install.ps1 -Harness codex -Skill swied-git-commit -Update
~~~

If you downloaded a ZIP instead, download and extract the latest ZIP, open a
terminal in the new folder, and run the same installer **update** command.

Update the PDF skill in the same way:

~~~bash
bash installers/install.sh update codex swied-markdown-to-pdf
~~~

Use the same harness or group target you originally installed. If you installed
with **all**, update with **all**:

~~~bash
bash installers/install.sh update all swied-git-commit
~~~

Important: updating a copied installation replaces edits made inside the
installed copy. Make lasting changes under **skills/<skill-name>/** in this
repository, not in the harness discovery directory.

The installer refuses to update a directory or symbolic link it does not own.
That guard protects unrelated files and manually installed skills.

## Uninstall or delete

Uninstalling removes the skill from a harness while leaving this repository
and its source files alone.

On macOS or Linux:

~~~bash
bash installers/install.sh uninstall codex swied-git-commit
~~~

On Windows PowerShell:

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-git-commit -Uninstall
~~~

Remove a skill from every supported discovery location with **all**:

~~~bash
bash installers/install.sh uninstall all swied-git-commit
~~~

Running uninstall again is safe; the installer simply reports that the skill
is not installed. It also refuses to delete a path it did not create.

Remember that harnesses in the same group share one installation. For example,
uninstalling through the **codex** alias also removes that skill for Pi,
OpenCode, and the other harnesses that use the **agents** group.

### Can I delete the cloned repository?

Yes, if you used the default copied installation. The installed skills will
keep working, but you will need to download or clone the repository again to
receive updates or use its uninstall commands.

If you used a development symlink, uninstall the symlink before deleting or
moving the repository. Otherwise, your harness will be left with a broken link.

## Tips and tricks

### Use a symlink while editing a skill

Contributors can install a symbolic link instead of a copy. Source edits then
appear in the harness immediately:

~~~bash
bash installers/install.sh --symlink codex swied-git-commit
~~~

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-git-commit -UseSymlink
~~~

Windows may require Developer Mode or elevated permissions to create a
symlink. Symlinks are intended for development; copies are simpler for normal
use.

You normally do not need to update a symlink—**git pull** changes the linked
source directly. If you do run update and want to keep the symlink, include
**--symlink** on macOS/Linux or **-UseSymlink** on Windows. A normal update
converts an installer-owned symlink back to a copy.

### Know when harness names share an installation

Codex, Pi, OpenCode, Gemini CLI, and several other harnesses use the **agents**
group. Installing the same skill once with any of those aliases creates one
copy in **~/.agents/skills/**; there is no need to install it repeatedly for
every alias in that group.

### Keep the source easy to update

If you plan to pull updates, keep the clone somewhere stable rather than in a
temporary downloads folder. The installed copies will work either way, but a
stable clone makes updates much easier.

### Let the installer protect existing files

If an install says **Refusing to replace existing path**, a skill with that
name already exists at the destination. The installer will not guess whether
it is safe to replace. Back up and inspect that directory before deciding what
to do with it.

## Troubleshooting

### The skill is installed, but my harness cannot find it

1. Start a new harness session; many tools discover skills only at startup.
2. Check the destination printed by the installer.
3. Confirm the harness alias with **bash installers/install.sh list**.
4. Try the harness's skill picker or explicit invocation syntax.

### macOS or Linux says “Permission denied”

Run the installer through Bash instead of executing it directly:

~~~bash
bash installers/install.sh codex swied-git-commit
~~~

### PowerShell blocks the installer script

PowerShell execution policies vary by machine. If you trust this cloned
repository, allow scripts only for the current PowerShell process and retry:

~~~powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\installers\install.ps1 -Harness codex -Skill swied-git-commit
~~~

The policy change ends when you close that PowerShell window.

### The PDF skill reports missing commands

Run its **--check** command, then install the missing requirement. The
[Markdown to PDF guide](skills/swied-markdown-to-pdf/README.md#install-the-required-tools)
has instructions for macOS, Windows, and Linux.

## Supported harnesses

The installer groups aliases by physical discovery location. One installation
serves every harness in the same row.

| Group | Accepted harness names | Discovery location |
| --- | --- | --- |
| **agents** | codex, pi, opencode, goose, copilot, github-copilot, openhands, cursor, cursor-cli, gemini, gemini-cli, kimi, kimi-code | ~/.agents/skills/ |
| **claude** | claude, claude-code | ~/.claude/skills/ |
| **antigravity** | agy, antigravity | ~/.gemini/config/skills/ |
| **amp** | amp | ~/.config/agents/skills/ |
| **qwen** | qwen, qwen-code | ~/.qwen/skills/ |
| **kilo** | kilo, kilo-cli | ~/.kilo/skills/ |
| **kiro** | kiro, kiro-cli | ~/.kiro/skills/ |
| **factory** | droid, factory, factory-droid | ~/.factory/skills/ |

### What about Aider?

Aider does not currently provide a native Agent Skills discovery interface, so
copying a SKILL.md directory into an invented location would be misleading.
Aider can consume generated prompt context through **--read**, and community
bridges exist, but this repository does not install or depend on them.
AiderDesk is a separate project with its own skill support.

## How the repository is organized

You do not need to understand the project layout to install a skill. If you
want to contribute, these are the main pieces:

~~~text
skills/                 Canonical source and documentation for each skill
installers/             macOS/Linux and Windows installation helpers
scripts/                Repository validation and audit tools
tests/                  Automated tests and reusable fixtures
config/                 Harness documentation and compatibility data
~~~

Each **skills/<skill-name>/** directory is the single source of truth for that
skill. Harness-specific copies are created only when you install it; the
repository does not maintain duplicate versions for every CLI tool.

To verify live upstream discovery paths in addition to the offline checks, run:

~~~bash
python3 scripts/audit_harness_docs.py
~~~

This network-enabled audit compares the aliases and locations in
**config/harness-docs.tsv** with their documented upstream sources.

## License

This repository is available under the [MIT License](LICENSE).
