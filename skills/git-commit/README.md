# Git Commit

`git-commit` helps an agent stage and commit the current working tree. A simple
request commits all current changes, while an explicitly named path or narrower
scope limits the commit. The skill inspects repository guidance, validates the
staged patch, follows local commit conventions, and verifies the result.

## Highlights

- Works from standard Git commands rather than harness-specific tools.
- Runs `git add --all` by default, so manual staging is not required.
- Supports staged-only or path-specific commits when explicitly requested.
- Checks before staging for sensitive files that are not covered by Git ignore
  rules.
- Checks the patch for unrelated edits, accidental deletions, generated
  artifacts, and suspected secrets before committing.
- Uses repository-specific commit conventions when available, with
  Conventional Commits as the fallback.
- Runs relevant validation and Git's whitespace/error check before committing.
- Does not push, amend, bypass hooks, or change remote state without an explicit
  request.

## Install

From the repository root, install the skill for every supported harness:

```bash
./installers/install.sh all git-commit
```

Install it for a single harness by replacing `all` with `codex`, `claude`,
`pi`, or `agy`. On Windows PowerShell:

```powershell
.\installers\install.ps1 -Harness all -Skill git-commit
```

For update, uninstall, symlink, and discovery-location details, see the
[repository README](../../README.md#install).

## Invoke

Explicit invocation differs by harness:

```text
Codex:       $git-commit Commit the changes for the login fix.
Claude Code: /git-commit Commit the changes for the login fix.
Pi:          /skill:git-commit Commit the changes for the login fix.
AGY:         Ask it to commit the intended changes or select the skill with /skills.
```

The skill can also be selected automatically for requests such as:

- “Commit the staged changes.”
- “Create a commit for the documentation updates.”
- “Review my changes, write an appropriate commit message, and commit them.”

No manual staging or extended prompt is needed for the normal case. An
unqualified request such as “Commit my changes” stages the entire working tree
with `git add --all`. State paths or a narrower change boundary only when you do
not want every current change included.

## Sensitive-file preflight

Before running `git add --all`, the skill examines untracked files that are not
excluded by the repository ignore rules, along with modified and staged paths.
It looks for likely environment files, private keys, credential files,
authentication configuration, and cloud-provider credentials. Clearly labeled
examples and templates are not rejected solely because of their names.

If a suspicious untracked file is not ignored, the skill stops before staging,
identifies the path without displaying secret values, and recommends a precise
`.gitignore` entry. It asks before changing `.gitignore`.

If the file is already tracked, adding it to `.gitignore` is insufficient. The
skill reports that distinction and does not remove it from the Git index without
explicit approval. This is a heuristic safety check, not a replacement for a
dedicated secret scanner or server-side repository protection.

## Commit-message behavior

The skill first follows documented repository rules and established history. If
the repository has no clear convention, it uses:

```text
<type>[(scope)][!]: <imperative summary>

[optional body]

[optional footer]
```

Examples:

```text
docs(git-commit): clarify staged-change handling
```

```text
fix(parser): preserve escaped delimiters

Keep escaped delimiters intact during tokenization so downstream validation
receives the original value.

Fixes #42
```

Supported fallback types are `feat`, `fix`, `docs`, `refactor`, `perf`, `test`,
`build`, `ci`, `style`, `chore`, and `revert`.
