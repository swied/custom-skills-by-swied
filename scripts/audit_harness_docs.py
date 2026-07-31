#!/usr/bin/env python3
"""Audit official harness documentation for configured global skill paths."""

from __future__ import annotations

import argparse
import csv
import html
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class HarnessSource:
    product: str
    group: str
    aliases: tuple[str, ...]
    documentation_url: str


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_manifest(path: Path) -> dict[str, tuple[str, set[str]]]:
    result: dict[str, tuple[str, set[str]]] = {}
    for row in _read_tsv(path):
        group = row["group"]
        if group in result:
            raise ValueError(f"duplicate manifest group: {group}")
        result[group] = (row["path"].strip("/"), set(row["harnesses"].split(",")))
    return result


def load_sources(path: Path) -> list[HarnessSource]:
    return [
        HarnessSource(
            product=row["product"],
            group=row["group"],
            aliases=tuple(row["aliases"].split(",")),
            documentation_url=row["documentation_url"],
        )
        for row in _read_tsv(path)
    ]


def validate_source_coverage(
    manifest: dict[str, tuple[str, set[str]]], sources: list[HarnessSource]
) -> list[str]:
    errors: list[str] = []
    covered: dict[str, set[str]] = {group: set() for group in manifest}
    for source in sources:
        if source.group not in manifest:
            errors.append(f"{source.product}: unknown manifest group {source.group!r}")
            continue
        manifest_aliases = manifest[source.group][1]
        for alias in source.aliases:
            if alias not in manifest_aliases:
                errors.append(
                    f"{source.product}: alias {alias!r} is not in group {source.group!r}"
                )
            elif alias in covered[source.group]:
                errors.append(f"{source.product}: alias {alias!r} is covered more than once")
            covered[source.group].add(alias)

    for group, (_path, aliases) in manifest.items():
        missing = aliases - covered[group]
        if missing:
            errors.append(f"{group}: aliases without documentation: {', '.join(sorted(missing))}")
    return errors


def fetch_document(url: str, timeout: float) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "text/markdown, text/plain;q=0.9, text/html;q=0.8",
            "User-Agent": "custom-skills-by-swied-doc-audit/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _normalize_document(text: str) -> str:
    text = html.unescape(text).replace("\\/", "/").replace("\\", "/")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def document_contains_path(text: str, relative_path: str) -> bool:
    normalized = _normalize_document(text)
    path = relative_path.strip("/")
    candidates = (
        f"~/{path}",
        f"$HOME/{path}",
        f"${{HOME}}/{path}",
        f"%USERPROFILE%/{path}",
    )
    return any(candidate in normalized for candidate in candidates)


def audit_sources(
    manifest: dict[str, tuple[str, set[str]]],
    sources: list[HarnessSource],
    *,
    timeout: float,
    fetcher: Callable[[str, float], str] = fetch_document,
) -> list[str]:
    errors = validate_source_coverage(manifest, sources)
    if errors:
        return errors

    with ThreadPoolExecutor(max_workers=min(6, len(sources))) as executor:
        futures = {
            executor.submit(fetcher, source.documentation_url, timeout): source
            for source in sources
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                document = future.result()
            except Exception as error:  # Network failures need product-level context.
                errors.append(f"{source.product}: failed to fetch documentation: {error}")
                continue
            relative_path = manifest[source.group][0]
            if not document_contains_path(document, relative_path):
                errors.append(
                    f"{source.product}: documentation no longer contains a global "
                    f"~/{relative_path} discovery path ({source.documentation_url})"
                )
    return sorted(errors)


def _write_summary(sources: list[HarnessSource], errors: list[str]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    status = "failed" if errors else "passed"
    lines = [
        "## Harness documentation audit",
        "",
        f"Audit **{status}** for {len(sources)} upstream products.",
    ]
    if errors:
        lines.extend(["", *[f"- {error}" for error in errors]])
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("installers/harnesses.tsv"))
    parser.add_argument("--sources", type=Path, default=Path("config/harness-docs.tsv"))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--check-config-only",
        action="store_true",
        help="validate manifest/source coverage without accessing the network",
    )
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
        sources = load_sources(args.sources)
        errors = validate_source_coverage(manifest, sources)
        if not errors and not args.check_config_only:
            errors = audit_sources(manifest, sources, timeout=args.timeout)
    except (OSError, KeyError, ValueError) as error:
        print(f"Audit configuration error: {error}", file=sys.stderr)
        return 2

    _write_summary(sources, errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if args.check_config_only:
        print(f"Validated documentation coverage for {len(sources)} products.")
    else:
        print(f"Audited documentation for {len(sources)} products.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
