# Repository Guidelines

## Project Structure & Module Organization

Canonical skill sources live in `skills/<skill-name>/`. Each skill should contain a `SKILL.md` and may include a user-facing `README.md`, executable helpers in `scripts/`, templates in `templates/`, or harness metadata in `agents/`. Keep shared installation logic in `installers/install.sh` and `installers/install.ps1`; do not duplicate skill sources for individual agent harnesses. Tests live in `tests/`, with reusable inputs in `tests/fixtures/`.

## Build, Test, and Development Commands

This repository has no separate build step. Run validation from the repository root:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_skills.py skills
python3 scripts/audit_harness_docs.py --check-config-only
python3 -m unittest discover -s tests -p 'test_*.py'
bash tests/installers-test.sh
bash tests/swied-markdown-to-pdf-test.sh
```

The skill validator enforces the portable Agent Skills specification, while the offline audit checks that every installer alias has an upstream documentation source. The unit suite exercises Python conversion, validation, and audit logic. The installer test checks copy, update, symlink, and uninstall lifecycles in a temporary home directory. The PDF integration test requires Pandoc and Typst and skips cleanly when they are absent. To try a skill during development without copying it, run `./installers/install.sh --symlink all <skill-name>`.

## Coding Style & Naming Conventions

Use lowercase kebab-case for skill directories, such as `skills/swied-markdown-to-pdf/`. Write concise, task-oriented Markdown with fenced examples. Python follows standard library conventions: four-space indentation, type hints, `snake_case` functions, and `PascalCase` test classes. Shell scripts must use Bash, quote expansions, and begin with `set -euo pipefail`. Preserve PowerShell parity when changing shared installer behavior. No formatter is configured, so match nearby code and keep patches focused.

## Testing Guidelines

Add Python tests to `tests/test_*.py` using `unittest`; name methods `test_<behavior>`. Add end-to-end shell coverage when changing installer behavior or external-tool integration. Tests must isolate filesystem changes with temporary directories and must not alter real harness installations. Include fixtures only when inline input would obscure the scenario.

## Commit & Pull Request Guidelines

Recent history favors Conventional Commit subjects, for example `feat(git-commit): require context for nontrivial commits`; use an imperative summary and add `!` for breaking changes. Keep commits scoped to one coherent change and include a body for nontrivial behavior or multi-file updates. Pull requests should explain intent, list validation commands and results, link relevant issues, and call out platform-specific effects. Screenshots are unnecessary unless documentation introduces visual output.
