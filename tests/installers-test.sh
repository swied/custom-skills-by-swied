#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_file() {
  [ -f "$1" ] || fail "expected file: $1"
}

assert_missing() {
  [ ! -e "$1" ] && [ ! -L "$1" ] || fail "expected missing path: $1"
}

test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT
repo="$test_root/repo"
test_home="$test_root/home"
mkdir -p "$repo/installers" "$repo/skills" "$test_home"
cp -R installers/. "$repo/installers/"
cp -R skills/. "$repo/skills/"
installer="$repo/installers/install.sh"
skill="swied-markdown-to-pdf"
agent_destination="$test_home/.agents/skills/$skill"
claude_destination="$test_home/.claude/skills/$skill"
agy_destination="$test_home/.gemini/config/skills/$skill"

HOME="$test_home" "$installer" codex "$skill"
[ -d "$agent_destination" ] || fail "default install did not create a directory"
[ ! -L "$agent_destination" ] || fail "default install created a symlink"
assert_file "$agent_destination/SKILL.md"
assert_file "$agent_destination/.portable-agent-skill-install"

if HOME="$test_home" "$installer" codex "$skill" >/dev/null 2>&1; then
  fail "install replaced an existing installation"
fi

printf 'new version\n' >"$repo/skills/$skill/UPDATED"
printf 'local edit\n' >"$agent_destination/LOCAL_EDIT"
HOME="$test_home" "$installer" update codex "$skill"
assert_file "$agent_destination/UPDATED"
assert_missing "$agent_destination/LOCAL_EDIT"

mkdir -p "$claude_destination"
printf 'unrelated\n' >"$claude_destination/KEEP"
if HOME="$test_home" "$installer" update claude "$skill" >/dev/null 2>&1; then
  fail "update replaced an unrelated directory"
fi
assert_file "$claude_destination/KEEP"
if HOME="$test_home" "$installer" uninstall claude "$skill" >/dev/null 2>&1; then
  fail "uninstall removed an unrelated directory"
fi
assert_file "$claude_destination/KEEP"

HOME="$test_home" "$installer" uninstall codex "$skill"
assert_missing "$agent_destination"
HOME="$test_home" "$installer" uninstall codex "$skill"

HOME="$test_home" "$installer" --symlink agy "$skill"
[ -L "$agy_destination" ] || fail "--symlink did not create a symlink"
HOME="$test_home" "$installer" update agy "$skill"
[ -d "$agy_destination" ] || fail "update did not preserve the installation"
[ ! -L "$agy_destination" ] || fail "default update did not migrate symlink to copy"
assert_file "$agy_destination/.portable-agent-skill-install"
HOME="$test_home" "$installer" uninstall agy "$skill"
assert_missing "$agy_destination"

echo "Installer lifecycle tests passed."
