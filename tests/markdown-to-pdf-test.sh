#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v pandoc >/dev/null 2>&1 || ! command -v typst >/dev/null 2>&1; then
  echo "SKIP: pandoc and typst are required for the Markdown-to-PDF integration test"
  exit 0
fi

test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT

python3 "$repo_root/skills/markdown-to-pdf/scripts/convert.py" \
  "$repo_root/tests/fixtures/sample-document.md" \
  "$test_dir/sample-document.pdf" \
  --inspect --no-mermaid

test -s "$test_dir/sample-document.pdf"
