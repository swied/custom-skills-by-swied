---
name: swied-git-commit
description: Stage and commit the current Git working tree, using all changes by default or a narrower scope when requested. Use when the user asks to commit changes, create a commit, write a commit message and commit it, or invokes the swied-git-commit skill. Before staging, detect potentially sensitive files that are not ignored; then validate the patch, follow repository commit conventions, and verify the resulting commit.
---

# Git Commit

Stage and commit the full working tree by default. Use a narrower commit boundary
only when the user specifies one. Use Git commands directly so the workflow
remains independent of any agent harness.

## Workflow

1. Locate the repository root and read applicable repository instructions and
   contribution guidance.
2. Inspect `git status --short`, the staged diff, and the unstaged diff. If a
   merge, rebase, cherry-pick, or revert is in progress, stop and explain the
   state unless the user explicitly asked to complete that operation.
3. Run a sensitive-file preflight before changing the index:
   - Enumerate untracked, non-ignored files with
     `git ls-files --others --exclude-standard`, and combine them with modified
     or already-staged paths from Git status.
   - Treat `.env` and environment variants, private keys and certificates,
     credential or secret files, authentication configs, and cloud-provider
     credentials as suspicious. Do not flag clearly labeled examples such as
     `.env.example`, `.env.sample`, or templates solely because of their names.
   - Use `git check-ignore -v --no-index -- <path>` when ignore status needs
     confirmation.
   - Inspect suspicious candidates and intended diff content for likely
     passwords, tokens, private keys, or connection strings without printing
     secret values. Use a repository-configured secret scanner when available;
     do not install one as part of committing.
   - If an untracked suspicious file is not ignored, stop before staging,
     report only its path and reason, and recommend a precise `.gitignore`
     entry. Ask before editing `.gitignore`.
   - If a suspicious file is already tracked, stop and explain that
     `.gitignore` does not affect tracked files. Do not run `git rm --cached`
     without explicit user approval.
4. Stage the intended commit boundary:
   - When the user simply asks to commit, run `git add --all` so tracked,
     untracked, and deleted files are included without requiring the user to
     stage them first.
   - When the user asks to commit only staged changes, leave unstaged changes
     untouched.
   - When the user names paths or a narrower change, stage only that scope. If
     the index already contains changes outside it, ask before modifying the
     staged set.
5. Review the complete staged patch with `git diff --cached`, including
   `--stat` and `--name-status`. Look for debug artifacts, generated files,
   credentials, private keys, tokens, large binaries, accidental deletions,
   and unrelated edits. Do not commit suspected secrets.
6. Run the narrowest relevant validation required by repository instructions
   or justified by the staged change. Do not modify unrelated files merely to
   make validation pass. Report failures and do not commit when they indicate
   the staged change is broken.
7. Check the staged patch with `git diff --cached --check`. Stop if the index is
   empty.
8. Derive the message from the staged diff:
   - Follow documented repository-specific conventions. Use recent commit
     history to infer type, scope, tone, and trailer names, but do not copy
     subject-only messages when the rules below require a body or footer.
   - Otherwise use Conventional Commits:
     `<type>[(scope)][!]: <imperative summary>`.
   - Use a specific scope only when it adds useful context.
   - Keep the subject concise, omit its trailing period, and describe the
     outcome rather than the editing activity.
   - For every nontrivial commit, add a body separated from the subject by a
     blank line. Treat a commit as nontrivial when it changes multiple files or
     concerns, introduces or changes behavior, alters a workflow or policy, or
     has motivation or tradeoffs that the subject cannot fully convey. Omit the
     body only for a truly atomic, self-explanatory change.
   - Use the body to explain the purpose, resulting behavior, and important
     related changes. Prefer cohesive prose over a file-by-file inventory, and
     wrap lines at roughly 72 characters.
   - Add a footer separated from the body by a blank line when factual,
     useful metadata is available. Use `BREAKING CHANGE: ...` for breaking
     behavior; `Fixes`, `Closes`, or `Refs` for known issue relationships; and
     repository-defined Git trailers for relevant metadata. For example, a
     skills repository may use `Affected-Skills: swied-git-commit, swied-markdown-to-pdf`.
     Never invent an issue, breaking change, contributor, or ceremonial footer
     merely to fill the section.
9. Create the commit without bypassing hooks. Do not amend, force, disable
   signing, or use `--no-verify` unless the user explicitly requests it.
10. Verify the result with `git status --short` and
   `git show -s --format=%B HEAD`, then inspect the summary with
   `git show --stat --oneline --decorate --no-renames HEAD`. Confirm that the
   subject, required body, and applicable footer were preserved. Report the
   commit identifier, subject, validation performed, and any remaining changes.

## Conventional commit types

Use the smallest accurate type:

- `feat`: introduce user-visible functionality
- `fix`: correct faulty behavior
- `docs`: change documentation only
- `refactor`: restructure code without changing behavior
- `perf`: improve performance
- `test`: add or correct tests
- `build`: change build tooling or dependencies
- `ci`: change continuous-integration configuration
- `style`: change formatting without changing behavior
- `chore`: perform maintenance that fits no more specific type
- `revert`: revert an earlier commit

## Boundaries

- Treat all pre-existing changes as user work; never discard or overwrite them.
- Treat an unqualified request to commit as authorization to stage all current
  changes with `git add --all`.
- Honor explicit requests for staged-only, path-specific, or otherwise narrower
  commits.
- Treat the sensitive-file check as a heuristic, not proof that a patch is
  secret-free. Stop on credible findings instead of exposing or committing them.
- Do not push, create tags, open pull requests, or modify remote state.
- Do not claim success unless Git reports that the commit was created and the
  resulting commit has been inspected.
