#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage:
  install.sh [install] [--symlink] {codex|claude|pi|agy|all} SKILL_NAME
  install.sh update [--symlink] {codex|claude|pi|agy|all} SKILL_NAME
  install.sh uninstall {codex|claude|pi|agy|all} SKILL_NAME
USAGE
}

action="install"
use_symlink=false

if [ "$#" -gt 0 ]; then
  case "$1" in
    install|update|uninstall)
      action="$1"
      shift
      ;;
  esac
fi

if [ "$#" -gt 0 ] && [ "$1" = "--symlink" ]; then
  use_symlink=true
  shift
fi

if [ "$action" = "uninstall" ] && [ "$use_symlink" = true ]; then
  usage
  exit 2
fi

if [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

harness="$1"
skill_name="$2"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
source_dir="$repo_root/skills/$skill_name"
marker_name=".portable-agent-skill-install"
marker_value="custom-skills-by-swied:$skill_name"

if [ "$action" != "uninstall" ] && [ ! -f "$source_dir/SKILL.md" ]; then
  echo "Skill not found: $source_dir" >&2
  exit 1
fi

is_owned_installation() {
  local destination="$1"

  if [ -L "$destination" ]; then
    [ "$(readlink "$destination")" = "$source_dir" ]
    return
  fi

  [ -f "$destination/$marker_name" ] &&
    [ "$(cat "$destination/$marker_name")" = "$marker_value" ]
}

install_copy() {
  local destination_root="$1"
  local destination="$destination_root/$skill_name"
  local staging_root
  local staged_copy

  staging_root="$(mktemp -d "$destination_root/.${skill_name}.install.XXXXXX")"
  staged_copy="$staging_root/$skill_name"
  cp -R "$source_dir" "$staged_copy"
  printf '%s\n' "$marker_value" >"$staged_copy/$marker_name"

  if [ "$action" = "update" ]; then
    mv "$destination" "$staging_root/previous"
    if ! mv "$staged_copy" "$destination"; then
      mv "$staging_root/previous" "$destination"
      rm -rf "$staging_root"
      echo "Update failed; restored previous installation: $destination" >&2
      exit 1
    fi
  else
    mv "$staged_copy" "$destination"
  fi

  rm -rf "$staging_root"
}

manage_at() {
  local destination_root="$1"
  local destination="$destination_root/$skill_name"

  mkdir -p "$destination_root"

  case "$action" in
    install)
      if [ -e "$destination" ] || [ -L "$destination" ]; then
        echo "Refusing to replace existing path: $destination" >&2
        echo "Use 'update' to refresh an installation created by this installer." >&2
        exit 1
      fi

      if [ "$use_symlink" = true ]; then
        ln -s "$source_dir" "$destination"
        echo "Installed symlink: $destination -> $source_dir"
      else
        install_copy "$destination_root"
        echo "Installed copy: $destination"
      fi
      ;;
    update)
      if [ ! -e "$destination" ] && [ ! -L "$destination" ]; then
        echo "Cannot update missing installation: $destination" >&2
        echo "Use 'install' first." >&2
        exit 1
      fi
      if ! is_owned_installation "$destination"; then
        echo "Refusing to update path not owned by this installer: $destination" >&2
        exit 1
      fi

      if [ "$use_symlink" = true ]; then
        if [ -L "$destination" ]; then
          echo "Already current (symlink): $destination -> $source_dir"
        else
          rm -rf "$destination"
          ln -s "$source_dir" "$destination"
          echo "Updated as symlink: $destination -> $source_dir"
        fi
      else
        install_copy "$destination_root"
        echo "Updated copy: $destination"
      fi
      ;;
    uninstall)
      if [ ! -e "$destination" ] && [ ! -L "$destination" ]; then
        echo "Not installed: $destination"
        return
      fi
      if ! is_owned_installation "$destination"; then
        echo "Refusing to uninstall path not owned by this installer: $destination" >&2
        exit 1
      fi

      if [ -L "$destination" ]; then
        rm "$destination"
      else
        rm -rf "$destination"
      fi
      echo "Uninstalled: $destination"
      ;;
  esac
}

manage_codex_or_pi() {
  manage_at "$HOME/.agents/skills"
}

manage_claude() {
  manage_at "$HOME/.claude/skills"
}

manage_agy() {
  manage_at "$HOME/.gemini/config/skills"
}

case "$harness" in
  codex|pi)
    manage_codex_or_pi
    ;;
  claude|claude-code)
    manage_claude
    ;;
  agy|antigravity)
    manage_agy
    ;;
  all)
    manage_codex_or_pi
    manage_claude
    manage_agy
    ;;
  *)
    usage
    exit 2
    ;;
esac
