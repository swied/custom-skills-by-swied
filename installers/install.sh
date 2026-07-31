#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage:
  install.sh [install] [--symlink] {HARNESS|GROUP|all} SKILL_NAME
  install.sh update [--symlink] {HARNESS|GROUP|all} SKILL_NAME
  install.sh uninstall {HARNESS|GROUP|all} SKILL_NAME
  install.sh list
USAGE
}

action="install"
use_symlink=false

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
harness_config="$script_dir/harnesses.tsv"

list_harnesses() {
  echo "GROUP          DISCOVERY LOCATION                  HARNESS ARGUMENTS"
  tail -n +2 "$harness_config" | while IFS=$'\t' read -r group relative_path aliases; do
    printf '%-14s %-35s %s\n' "$group" "~/$relative_path" "$aliases"
  done
}

if [ "${1:-}" = "list" ]; then
  if [ "$#" -ne 1 ]; then
    usage
    exit 2
  fi
  list_harnesses
  exit 0
fi

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

manage_harness() {
  local requested_harness="$1"
  local matched=false
  local group
  local relative_path
  local aliases
  local alias
  local -a alias_list

  while IFS=$'\t' read -r group relative_path aliases; do
    if [ "$requested_harness" = "all" ] || [ "$requested_harness" = "$group" ]; then
      manage_at "$HOME/$relative_path"
      matched=true
      continue
    fi

    IFS=',' read -ra alias_list <<<"$aliases"
    for alias in "${alias_list[@]}"; do
      if [ "$requested_harness" = "$alias" ]; then
        manage_at "$HOME/$relative_path"
        matched=true
        break
      fi
    done
  done < <(tail -n +2 "$harness_config")

  if [ "$matched" = false ]; then
    echo "Unknown harness or group: $requested_harness" >&2
    echo "Run '$0 list' to see supported values." >&2
    exit 2
  fi
}

manage_harness "$harness"
