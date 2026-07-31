# Portable Agent Skills

A collection of focused, reusable skills built on the open Agent Skills
`SKILL.md` format. Canonical skill sources live under `skills/`; portable
installers copy or link them into the discovery locations used by Codex,
Claude Code, Pi, and Google Antigravity CLI.

## Skills

| Skill | Purpose | Documentation |
| --- | --- | --- |
| `swied-git-commit` | Safely stage, validate, and commit a Git working tree with repository-aware messages. | [Usage and behavior](skills/swied-git-commit/README.md) |
| `swied-markdown-to-pdf` | Convert Markdown into polished PDF documents with Pandoc and Typst. | [Prerequisites and usage](skills/swied-markdown-to-pdf/README.md) |

Each skill README contains its prerequisites, invocation examples, and
skill-specific behavior. The sections below cover installation and repository
management shared by every skill.

## Quick start

Install one skill for every supported harness on macOS or Linux:

```bash
./installers/install.sh all SKILL_NAME
```

On Windows PowerShell:

```powershell
.\installers\install.ps1 -Harness all -Skill SKILL_NAME
```

Replace `SKILL_NAME` with `swied-git-commit` or `swied-markdown-to-pdf`. The `all` argument
means all supported harnesses; it does not mean all skills.

### Install every included skill

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

### Install for one harness

Replace `all` with a harness name when a skill is needed in only one tool:

```bash
./installers/install.sh codex SKILL_NAME
./installers/install.sh claude SKILL_NAME
./installers/install.sh pi SKILL_NAME
./installers/install.sh agy SKILL_NAME
```

The optional POSIX `install` action is equivalent to the shorter form:

```bash
./installers/install.sh install codex SKILL_NAME
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

Use a single harness instead of `all` to remove only that installation.
Uninstall is idempotent and refuses to delete paths not owned by the installer.

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

| Harness | Installer argument | Explicit invocation | Discovery location |
| --- | --- | --- | --- |
| Codex | `codex` | `$SKILL_NAME <request>` | `~/.agents/skills/` |
| Claude Code | `claude` | `/SKILL_NAME <request>` | `~/.claude/skills/` |
| Pi | `pi` | `/skill:SKILL_NAME <request>` | `~/.agents/skills/` |
| Antigravity/AGY | `agy` | Describe the task or use `/skills` | `~/.gemini/config/skills/` |

Codex and Pi intentionally share the same installation directory. Harnesses
may also select a skill automatically from its description.

## Repository design

Keep each skill under `skills/<skill-name>/` as its single source of truth.
Skill-specific documentation belongs beside that skill; shared installation
and repository guidance belongs in this README. Add harness-specific packaging
logic under `installers/` instead of maintaining duplicate skill copies.
