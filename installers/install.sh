#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: install.sh {codex|claude|pi|agy|all} SKILL_NAME" >&2
}

if [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

harness="$1"
skill_name="$2"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
source_dir="$repo_root/skills/$skill_name"

if [ ! -f "$source_dir/SKILL.md" ]; then
  echo "Skill not found: $source_dir" >&2
  exit 1
fi

install_link() {
  local destination_root="$1"
  local destination="$destination_root/$skill_name"

  mkdir -p "$destination_root"

  if [ -L "$destination" ]; then
    current_target="$(readlink "$destination")"
    if [ "$current_target" = "$source_dir" ]; then
      echo "Already installed: $destination"
      return
    fi
    echo "Refusing to replace existing symlink: $destination" >&2
    exit 1
  fi

  if [ -e "$destination" ]; then
    echo "Refusing to replace existing path: $destination" >&2
    exit 1
  fi

  ln -s "$source_dir" "$destination"
  echo "Installed: $destination -> $source_dir"
}

install_codex_or_pi() {
  install_link "$HOME/.agents/skills"
}

install_claude() {
  install_link "$HOME/.claude/skills"
}

install_agy() {
  install_link "$HOME/.gemini/config/skills"
}

case "$harness" in
  codex|pi)
    install_codex_or_pi
    ;;
  claude|claude-code)
    install_claude
    ;;
  agy|antigravity)
    install_agy
    ;;
  all)
    install_codex_or_pi
    install_claude
    install_agy
    ;;
  *)
    usage
    exit 2
    ;;
esac

