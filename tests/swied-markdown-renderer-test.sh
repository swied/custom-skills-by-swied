#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v pandoc >/dev/null 2>&1 || ! command -v typst >/dev/null 2>&1; then
  echo "SKIP: Pandoc and Typst are required for the Markdown renderer integration test"
  exit 0
fi

test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT

fixture="$repo_root/tests/fixtures/renderer-document.md"
renderer="$repo_root/skills/swied-markdown-renderer/scripts/render.py"

for extension in md pdf docx odt rtf html epub pptx tex typ; do
  python3 "$renderer" \
    "$fixture" \
    "$test_dir/document.$extension" \
    --no-diagrams --inspect
  test -s "$test_dir/document.$extension"
done

grep -q 'data:image/svg+xml;base64,' "$test_dir/document.md"
if grep -q '.swied-markdown-renderer-' "$test_dir/document.md"; then
  echo "Rendered Markdown contains a temporary path" >&2
  exit 1
fi

python3 "$renderer" \
  "$fixture" \
  "$test_dir/document-png.markdown" \
  --no-diagrams --render-math=png --inspect
grep -q 'data:image/png;base64,' "$test_dir/document-png.markdown"

grep -q '\\pngblip' "$test_dir/document.rtf"
grep -q '<math' "$test_dir/document.html"

if command -v unzip >/dev/null 2>&1; then
  unzip -p "$test_dir/document.docx" word/document.xml |
    grep -F '<m:oMath' >/dev/null
  unzip -p "$test_dir/document.odt" 'Formula-*/content.xml' |
    grep -F '<math ' >/dev/null
fi

if [[ "${SWIED_RUN_MERMAID_INTEGRATION:-0}" == "1" ]] &&
  command -v mmdc >/dev/null 2>&1; then
  python3 "$renderer" \
    "$fixture" \
    "$test_dir/mermaid-document.html" \
    --no-graphviz --inspect
  grep -q 'image/svg+xml' "$test_dir/mermaid-document.html"
fi

if command -v dot >/dev/null 2>&1; then
  python3 "$renderer" \
    "$fixture" \
    "$test_dir/graphviz-document.html" \
    --no-mermaid --inspect
  grep -q 'image/svg+xml' "$test_dir/graphviz-document.html"
fi
