# Portable Agent Skills

A collection of focused, reusable skills built on the open Agent Skills
`SKILL.md` format. Canonical skill files live under `skills/`; the installers
copy or link them into the discovery locations used by Codex, Claude Code, Pi,
and Google Antigravity CLI.

## Included skills

- [`markdown-to-pdf`](skills/markdown-to-pdf/README.md): Convert Markdown files
  into polished PDF documents with Pandoc and Typst.
- [`git-commit`](skills/git-commit/README.md): Stage, review, and commit Git
  changes with commit-message and sensitive-file checks.

## Install

The installers copy skills by default. An installed copy remains usable if this
repository is later moved or deleted. Replace `SKILL_NAME` below with a name
from the included-skills list.

### macOS or Linux

Install a skill for every supported harness:

```bash
./installers/install.sh all SKILL_NAME
```

Install it for one harness:

```bash
./installers/install.sh codex SKILL_NAME
./installers/install.sh claude SKILL_NAME
./installers/install.sh pi SKILL_NAME
./installers/install.sh agy SKILL_NAME
```

The optional `install` action is equivalent to the shorter form:

```bash
./installers/install.sh install codex SKILL_NAME
```

### Windows PowerShell

```powershell
.\installers\install.ps1 -Harness all -Skill SKILL_NAME
```

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

### Discovery locations

| Harness | Personal/global skill directory |
| --- | --- |
| Codex | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| Pi | `~/.agents/skills/` |
| Antigravity/AGY | `~/.gemini/config/skills/` |

Codex and Pi intentionally share the same installation.

## Invoke a skill

Harnesses use different explicit-invocation syntax:

```text
Codex:       $SKILL_NAME <request>
Claude Code: /SKILL_NAME <request>
Pi:          /skill:SKILL_NAME <request>
AGY:         Describe the task or select the skill with /skills.
```

Harnesses may also select a skill automatically from its description. Each
skill README contains concrete invocation examples.

## Repository design

Keep each skill under `skills/<skill-name>/` as the single source of truth.
Add harness-specific installation or packaging logic under `installers/`
instead of maintaining multiple copies of a skill.
