# Git Commit

**swied-git-commit** turns a simple request such as “Commit my changes” into a
careful, repository-aware Git commit.

You do not need to stage files or write a commit message first. The skill
reviews the work, checks for likely secrets and accidental files, runs relevant
validation, creates the commit, and confirms the result.

It uses standard Git commands, so the same workflow can run in Codex, Claude
Code, Pi, and the other harnesses supported by this repository.

## Quick start

### 1. Install the skill

Run the command from the root of this repository.

On macOS or Linux:

~~~bash
bash installers/install.sh codex swied-git-commit
~~~

On Windows PowerShell:

~~~powershell
.\installers\install.ps1 -Harness codex -Skill swied-git-commit
~~~

This example installs the skill for Codex. Replace **codex** with your own
[supported harness name](../../README.md#supported-harnesses).

### 2. Ask for a commit

Open your CLI harness in a Git repository that contains changes you are ready
to commit. In Codex:

~~~text
$swied-git-commit Commit my current changes.
~~~

The equivalent request in other common harnesses is:

| Harness | Example |
| --- | --- |
| Codex | **$swied-git-commit Commit my current changes.** |
| Claude Code | **/swied-git-commit Commit my current changes.** |
| Pi | **/skill:swied-git-commit Commit my current changes.** |
| AGY / Antigravity | Ask it to commit, or select the skill with **/skills**. |

Many harnesses can also select the skill from an ordinary request:

~~~text
Review my changes, write an appropriate commit message, and commit them.
~~~

### 3. Review the result

After a successful commit, the skill reports:

- The new commit identifier and subject.
- The validation it ran.
- Any changes that remain outside the commit.

Creating a commit does not push it to a remote repository.

## What does the skill do?

The full workflow is thorough, but the idea is simple:

1. Read the repository's instructions and commit conventions.
2. Inspect staged, unstaged, untracked, and deleted files.
3. Stop if it finds a likely secret or an unsafe repository state.
4. Stage the requested changes and review the complete patch.
5. Run relevant tests or checks.
6. Write a commit message that matches the project.
7. Create the commit and verify what Git recorded.

The skill leaves existing user work intact. It will not discard unrelated
changes merely to make the working tree clean.

## Choose what goes into the commit

The wording of your request controls the commit boundary.

### Commit everything

An unqualified request means all current changes:

~~~text
Commit my changes.
~~~

The skill uses **git add --all**, which includes modified files, new files, and
deletions.

Tip: run **git status** first if you are unsure what is currently in the working
tree.

### Commit only staged changes

Use this when you have already selected files with Git:

~~~text
Commit only the changes I have staged. Leave everything else alone.
~~~

Unstaged and untracked changes remain untouched.

### Commit a specific path or change

Name the boundary when you want a smaller commit:

~~~text
Commit only the changes under docs/.
~~~

~~~text
Commit README.md as a documentation update.
~~~

~~~text
Commit only the login validation fix. Leave the unrelated formatting changes uncommitted.
~~~

If the staged area already contains changes outside your requested boundary,
the skill asks before rearranging it.

## Safety checks

### Sensitive files and secrets

Before staging, the skill looks for files that commonly contain secrets, such
as:

- Environment files.
- Private keys and certificates.
- Credential and authentication files.
- Cloud-provider credentials.
- Tokens, passwords, and connection strings in the intended patch.

Clearly labeled examples such as **.env.example** and **.env.sample** are not
rejected just because of their names.

If the skill finds a suspicious untracked file, it stops before staging,
reports the path without printing the secret, and suggests a precise
**.gitignore** entry. It asks before editing **.gitignore**.

If the file is already tracked, adding it to **.gitignore** is not enough. The
skill explains that difference and will not remove the file from Git's staging
area (also called the index) without your approval.

This check is a useful safety net, not a replacement for a dedicated secret
scanner or repository protection.

### Repository state

The skill stops when it discovers an unfinished merge, rebase, cherry-pick, or
revert unless you explicitly asked to complete that operation. This prevents a
normal commit request from accidentally interfering with Git recovery work.

### Validation and hooks

The skill runs the narrowest relevant checks required by the repository or
justified by the patch. It also asks Git to check the staged diff for whitespace
errors.

If a meaningful test fails, the skill reports the failure instead of committing
known-broken work. It also respects normal Git hooks; it does not silently use
**--no-verify** to bypass them.

## How commit messages are chosen

The skill follows this order:

1. Documented rules in the repository.
2. Conventions visible in recent commits.
3. Conventional Commits when the project has no clear convention.

A small, self-explanatory documentation change might produce:

~~~text
docs(readme): clarify installation steps
~~~

A larger change receives a body that explains its purpose and result:

~~~text
feat(git-commit): add guarded commit workflow

Add a portable commit skill that stages the intended change set, checks for
potential secrets, validates the patch, and verifies the resulting commit.

Affected-Skills: swied-git-commit
~~~

When Conventional Commits are the fallback, the common types are:

| Type | Use it for |
| --- | --- |
| **feat** | New user-visible behavior |
| **fix** | A correction to faulty behavior |
| **docs** | Documentation-only changes |
| **refactor** | Restructuring without a behavior change |
| **perf** | Performance improvements |
| **test** | Test additions or corrections |
| **build** | Build tools or dependencies |
| **ci** | Continuous-integration configuration |
| **style** | Formatting without a behavior change |
| **chore** | Maintenance that fits no more specific type |
| **revert** | Reverting an earlier commit |

Footers are added only when there is real metadata to record, such as a known
issue relationship, a breaking change, or a repository-defined Git trailer.
The skill does not invent issue numbers or ceremonial footers.

## What the skill does not do

A normal commit request does not:

- Push the commit.
- Create a tag or pull request.
- Amend an earlier commit.
- Force an operation.
- Bypass Git hooks.
- Change remote repository state.

Ask for those operations separately when you need them. Your harness will apply
its normal permissions and safety rules.

## Test the skill without making a commit

Start a fresh harness session after installation and use a read-only prompt:

~~~text
$swied-git-commit Explain what you would inspect before committing this repository. Do not stage or commit anything.
~~~

This lets you confirm that the harness found the skill without changing the
repository.

## Troubleshooting

### The skill says there is nothing to commit

Run **git status** and confirm that the repository contains changes. If you
asked for staged-only behavior, make sure something is staged.

### The skill stops on a suspicious file

Inspect the reported path without sharing its contents. Ignore an untracked
local secret with an appropriate **.gitignore** rule. If it is already tracked,
rotate any exposed credential before deciding how to remove it from Git.

### A test or Git hook fails

Read the failure before retrying. Fix the underlying problem, or explicitly
decide how you want to handle it. The skill will not hide the failure by
bypassing checks.

### Git reports an operation in progress

Use **git status** to see whether a merge, rebase, cherry-pick, or revert needs
to be continued or aborted. Resolve that state before making an unrelated
commit.

### The harness cannot find the skill

Start a new harness session, then check the install destination and invocation
syntax in the [repository troubleshooting guide](../../README.md#troubleshooting).

## Update or uninstall

The repository installer can safely refresh or remove the skill:

- [Update an installed skill](../../README.md#update)
- [Uninstall a skill](../../README.md#uninstall-or-delete)
- [Use a development symlink](../../README.md#use-a-symlink-while-editing-a-skill)
