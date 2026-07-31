# Portable Agent Skills

A collection of focused, reusable skills built on the open Agent Skills
`SKILL.md` format. Canonical skill sources live under `skills/`; portable
installers copy or link them into discovery locations used by more than twenty
popular CLI harness names.

## Skills

| Skill | Purpose | Documentation |
| --- | --- | --- |
| `swied-git-commit` | Safely stage, validate, and commit a Git working tree with repository-aware messages. | [Usage and behavior](skills/swied-git-commit/README.md) |
| `swied-markdown-to-pdf` | Convert Markdown into polished PDF documents with Pandoc and Typst. | [Prerequisites and usage](skills/swied-markdown-to-pdf/README.md) |

Each skill README contains its prerequisites, invocation examples, and
skill-specific behavior. The sections below cover installation and repository
management shared by every skill.

## Quick start

Install all skills for every supported harness.

On macOS or Linux:

```bash
for skill in swied-git-commit swied-markdown-to-pdf; do
  ./installers/install.sh all "$skill"
done
```

On Windows PowerShell:

```powershell
"swied-git-commit", "swied-markdown-to-pdf" | ForEach-Object {
    .\installers\install.ps1 -Harness all -Skill $_
}
```

These commands install every skill currently listed in this repository for
every supported harness.

### Install a single skill for one harness

Replace `all` with a harness name or destination group when a skill is needed
in only one discovery location. List accepted values with
`./installers/install.sh list`.

```bash
./installers/install.sh agents SKILL_NAME  # shared cross-harness location
./installers/install.sh claude SKILL_NAME
./installers/install.sh amp SKILL_NAME
./installers/install.sh qwen SKILL_NAME
./installers/install.sh kiro SKILL_NAME
./installers/install.sh factory SKILL_NAME
./installers/install.sh agy SKILL_NAME
```

The optional POSIX `install` action is equivalent to the shorter form:

```bash
./installers/install.sh install HARNESS SKILL_NAME
```

## Manage installations

Installers create independent copies by default, so installed skills keep
working if this repository is moved or deleted.

### Update

After pulling repository changes, update an installed copy:

```bash
./installers/install.sh update all SKILL_NAME
```

```powershell
.\installers\install.ps1 -Harness all -Skill SKILL_NAME -Update
```

An update replaces only an installation created by these installers and refuses
to overwrite an unrelated directory or symbolic link. It replaces local edits
inside an installed copy, so make source changes under `skills/`.

### Uninstall

```bash
./installers/install.sh uninstall all SKILL_NAME
```

```powershell
.\installers\install.ps1 -Harness all -Skill SKILL_NAME -Uninstall
```

Use a single harness instead of `all` to remove only its destination. Harnesses
in the same group share a destination, so uninstalling through one alias removes
the skill for every harness in that group. Uninstall is idempotent and refuses
to delete paths not owned by the installer.

### Development symlinks

Contributors can link installations to the working tree so source edits appear
immediately:

```bash
./installers/install.sh --symlink all SKILL_NAME
```

```powershell
.\installers\install.ps1 -Harness all -Skill SKILL_NAME -UseSymlink
```

Pass `--symlink` with a POSIX update, or `-UseSymlink` with PowerShell
`-Update`, to convert an installer-owned copy to a symlink. Windows may require
Developer Mode or elevated permissions.

## Supported harnesses

Harness aliases are grouped by physical discovery location. Installing once for a
group makes the skill available to every harness in that row.

| Group | Harness arguments | Discovery location |
| --- | --- | --- |
| `agents` | `codex`, `pi`, `opencode`, `goose`, `copilot`, `github-copilot`, `openhands`, `cursor`, `cursor-cli`, `gemini`, `gemini-cli`, `kimi`, `kimi-code` | `~/.agents/skills/` |
| `claude` | `claude`, `claude-code` | `~/.claude/skills/` |
| `antigravity` | `agy`, `antigravity` | `~/.gemini/config/skills/` |
| `amp` | `amp` | `~/.config/agents/skills/` |
| `qwen` | `qwen`, `qwen-code` | `~/.qwen/skills/` |
| `kilo` | `kilo`, `kilo-cli` | `~/.kilo/skills/` |
| `kiro` | `kiro`, `kiro-cli` | `~/.kiro/skills/` |
| `factory` | `droid`, `factory`, `factory-droid` | `~/.factory/skills/` |

Harnesses may select a skill automatically from its description. Their manual
invocation syntax varies; consult the harness documentation or its skill picker.

### Aider and non-native harnesses

Aider does not currently provide a native Agent Skills discovery interface.
Installing a `SKILL.md` directory alone would therefore be misleading. Aider can
consume generated prompt context through `--read`, and community bridges exist,
but this repository does not install or depend on them. AiderDesk is a separate
project with its own skills directory and should not be treated as Aider.

## Validation and upstream audits

Install the development-only YAML dependency, then run the portable validator:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_skills.py skills
```

The validator enforces the required [Agent Skills specification](https://agentskills.io/specification) fields, types, length limits,
naming rules, and directory-name match. Vendor extensions are rejected in
portable mode. Documented extensions have isolated profiles in
`config/frontmatter-compatibility.yml` and fixtures under
`tests/fixtures/harness-frontmatter/`.

Check that every installer alias has an official documentation source without
using the network:

```bash
python3 scripts/audit_harness_docs.py --check-config-only
```

Run the complete upstream discovery-path audit with:

```bash
python3 scripts/audit_harness_docs.py
```

The audit sources live in `config/harness-docs.tsv`. The scheduled GitHub
Actions workflow runs every Monday at 16:17 UTC and can also be started through
`workflow_dispatch`. A missing path, unreachable page, duplicate alias, or
undocumented alias fails with product-specific diagnostics.

## Repository design

Keep each skill under `skills/<skill-name>/` as its single source of truth.
Skill-specific documentation belongs beside that skill; shared installation
and repository guidance belongs in this README. Add or regroup harnesses in
`installers/harnesses.tsv` instead of duplicating dispatch logic or skill copies.
