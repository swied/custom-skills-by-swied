#!/usr/bin/env python3
"""Validate SKILL.md packages against the Agent Skills specification."""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml


SPEC_FIELD_TYPES = {
    "name": ("string",),
    "description": ("string",),
    "license": ("string",),
    "compatibility": ("string",),
    "metadata": ("string-map",),
    "allowed-tools": ("string",),
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_profiles(path: Path) -> dict[str, dict[str, tuple[str, ...]]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        raise ValueError("compatibility config 'profiles' must be a mapping")

    result: dict[str, dict[str, tuple[str, ...]]] = {}
    for profile_name, profile in profiles.items():
        if not isinstance(profile, dict):
            raise ValueError(f"profile {profile_name!r} must be a mapping")
        fields = profile.get("field-types", {})
        if not isinstance(fields, dict):
            raise ValueError(f"profile {profile_name!r} field-types must be a mapping")
        result[str(profile_name)] = {
            str(field): tuple(str(value) for value in values)
            for field, values in fields.items()
        }
    return result


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )
    if expected == "string-list":
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    if expected == "string-map":
        return isinstance(value, dict) and all(
            isinstance(key, str) and isinstance(item, str) for key, item in value.items()
        )
    raise ValueError(f"unknown configured field type: {expected}")


def parse_frontmatter(skill_file: Path) -> tuple[dict[str, Any], str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("must start with a YAML frontmatter delimiter ('---')")
    try:
        closing_index = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("is missing the closing YAML frontmatter delimiter ('---')") from error

    try:
        metadata = yaml.safe_load("\n".join(lines[1:closing_index]))
    except yaml.YAMLError as error:
        raise ValueError(f"contains invalid YAML frontmatter: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return metadata, "\n".join(lines[closing_index + 1 :])


def validate_skill(
    skill_dir: Path,
    *,
    compatibility: str | None = None,
    profiles: dict[str, dict[str, tuple[str, ...]]] | None = None,
) -> list[str]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill_dir}: missing SKILL.md"]

    try:
        metadata, _body = parse_frontmatter(skill_file)
    except (OSError, UnicodeError, ValueError) as error:
        return [f"{skill_file}: {error}"]

    allowed_types = dict(SPEC_FIELD_TYPES)
    if compatibility:
        if profiles is None or compatibility not in profiles:
            return [f"{skill_file}: unknown compatibility profile {compatibility!r}"]
        allowed_types.update(profiles[compatibility])

    errors: list[str] = []
    for field in ("name", "description"):
        if field not in metadata:
            errors.append(f"{skill_file}: missing required frontmatter field {field!r}")

    for field, value in metadata.items():
        if field not in allowed_types:
            errors.append(f"{skill_file}: unsupported frontmatter field {field!r}")
            continue
        expected_types = allowed_types[field]
        if not any(_matches_type(value, expected) for expected in expected_types):
            errors.append(
                f"{skill_file}: field {field!r} must be one of: {', '.join(expected_types)}"
            )

    name = metadata.get("name")
    if isinstance(name, str):
        if not 1 <= len(name) <= 64:
            errors.append(f"{skill_file}: 'name' must contain 1-64 characters")
        if not NAME_PATTERN.fullmatch(name):
            errors.append(
                f"{skill_file}: 'name' must use lowercase letters, numbers, and single hyphens"
            )
        if name != skill_dir.name:
            errors.append(
                f"{skill_file}: 'name' {name!r} must match parent directory {skill_dir.name!r}"
            )

    description = metadata.get("description")
    if isinstance(description, str) and not 1 <= len(description.strip()) <= 1024:
        errors.append(f"{skill_file}: 'description' must contain 1-1024 characters")

    compatibility_value = metadata.get("compatibility")
    if isinstance(compatibility_value, str) and not 1 <= len(compatibility_value.strip()) <= 500:
        errors.append(f"{skill_file}: 'compatibility' must contain 1-500 characters")

    allowed_tools = metadata.get("allowed-tools")
    if isinstance(allowed_tools, str) and not allowed_tools.strip():
        errors.append(f"{skill_file}: 'allowed-tools' must not be empty")
    return errors


def discover_skill_dirs(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        if (path / "SKILL.md").is_file():
            result.append(path)
        elif path.is_dir():
            result.extend(sorted(item.parent for item in path.glob("*/SKILL.md")))
        else:
            result.append(path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--compatibility")
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path("config/frontmatter-compatibility.yml"),
    )
    args = parser.parse_args(argv)

    try:
        profiles = load_profiles(args.profiles)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Compatibility configuration error: {error}", file=sys.stderr)
        return 2

    skill_dirs = discover_skill_dirs(args.paths)
    if not skill_dirs:
        print("No skills found.", file=sys.stderr)
        return 2

    errors = [
        error
        for skill_dir in skill_dirs
        for error in validate_skill(
            skill_dir,
            compatibility=args.compatibility,
            profiles=profiles,
        )
    ]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
