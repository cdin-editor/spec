#!/usr/bin/env python3
"""Report CDIN Spec inventory/status counts and generate versioned release notes.

This script reports metadata from the documentation. It deliberately does not
act as a content linter, link checker, conformance checker, or CI test suite.
It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = ROOT / "docs/reference/status.md"
README_FILE = ROOT / "README.md"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"

REQUIREMENT_RE = re.compile(
    r"^\s*-\s+\*\*([A-Z][A-Z0-9]*-\d{3})\*\*\s+`(ACCEPTED|PROPOSED|EXISTING|DEFERRED)`",
    re.IGNORECASE,
)
REQUIREMENT_STATUSES = ("ACCEPTED", "PROPOSED", "EXISTING", "DEFERRED")
OTHER_STATUSES = ("OPEN", "RESOLVED")
SEMVER_RE = re.compile(r"\d+\.\d+\.\d+")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Could not read {path.relative_to(ROOT)}: {exc}") from exc


def markdown_files() -> list[Path]:
    excluded = {".git", ".gix", ".psx", "node_modules"}
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in excluded for part in path.relative_to(ROOT).parts)
    )


def count_requirements(files: list[Path]) -> Counter[str]:
    counts: Counter[str] = Counter()
    seen_ids: set[str] = set()
    for path in files:
        for line in read_text(path).splitlines():
            match = REQUIREMENT_RE.match(line)
            if match:
                requirement_id = match.group(1).upper()
                if requirement_id in seen_ids:
                    # Counts should reflect published requirement IDs, not duplicate copies.
                    continue
                seen_ids.add(requirement_id)
                counts[match.group(2).upper()] += 1
    return counts


def count_adrs() -> tuple[int, Counter[str]]:
    adr_dir = ROOT / "docs/adr"
    statuses: Counter[str] = Counter()
    files = sorted(adr_dir.glob("ADR-[0-9][0-9][0-9][0-9]-*.md"))
    status_re = re.compile(
        r"^\s*-\s+\*\*Status:\*\*\s+`?(ACCEPTED|PROPOSED|EXISTING|DEFERRED|OPEN|RESOLVED)\b",
        re.IGNORECASE | re.MULTILINE,
    )
    for path in files:
        match = status_re.search(read_text(path))
        statuses[match.group(1).upper() if match else "UNLABELLED"] += 1
    return len(files), statuses


def count_open_decisions() -> tuple[int, Counter[str]]:
    path = ROOT / "docs/adr/open-decisions.md"
    summary = read_text(path).split("## OD-01", 1)[0]
    counts: Counter[str] = Counter()
    for line in summary.splitlines():
        if not re.match(r"^\s*\|\s*\[OD-\d+\]", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells:
            continue
        match = re.search(r"\b(OPEN|PROPOSED|DEFERRED|RESOLVED)\b", cells[-1], re.IGNORECASE)
        if match:
            counts[match.group(1).upper()] += 1
        else:
            counts["UNLABELLED"] += 1
    return sum(counts.values()), counts


def count_diagrams(files: list[Path]) -> int:
    return sum(
        len(re.findall(r"^\s*```mermaid\s*$", read_text(path), re.IGNORECASE | re.MULTILINE))
        for path in files
    )


def spec_version() -> str:
    status = read_text(STATUS_FILE)
    match = re.search(r"Specification release:\s*`([^`]+)`", status, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "unversioned"


def version_labels() -> tuple[str, str, str]:
    """Return kernel package version, public ABI version and declared Spec target."""
    readme = read_text(README_FILE)
    package = "not recorded"
    abi = "not recorded"
    target = "not recorded"
    for line in readme.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = re.sub(r"`", "", cells[0]).strip().lower()
        value_match = re.search(r"`([^`]+)`", cells[1])
        value = value_match.group(1) if value_match else cells[1]
        if "cdin-kernel" in label and "package" in label:
            package = value
        elif label == "public c abi":
            abi = value
        elif "kernel-declared spec target" in label:
            target = value
    return package, abi, target


def open_decision_totals(counts: Counter[str]) -> str:
    order = ("OPEN", "PROPOSED", "DEFERRED", "RESOLVED", "UNLABELLED")
    return ", ".join(f"{status}: {counts[status]}" for status in order if counts[status]) or "None recorded"


def format_status_table(title: str, counts: Counter[str], order: tuple[str, ...]) -> list[str]:
    rows = [f"### {title}", "", "| Status | Count |", "| --- | ---: |"]
    for status in order:
        rows.append(f"| `{status}` | {counts[status]} |")
    return rows + [""]


def render_report(release_version: str | None = None) -> str:
    files = markdown_files()
    requirements = count_requirements(files)
    requirement_total = sum(requirements.values())
    adr_total, adr_statuses = count_adrs()
    decision_total, decision_statuses = count_open_decisions()
    diagrams = count_diagrams(files)
    kernel_package, kernel_abi, kernel_spec_target = version_labels()
    displayed_version = release_version or spec_version()

    metrics = [
        ("Markdown documents", len(files)),
        ("Normative requirements", requirement_total),
        ("Architecture Decision Records (ADRs)", adr_total),
        ("Open Decisions Register entries", decision_total),
        ("Mermaid diagrams", diagrams),
        ("Architecture pages", len(list((ROOT / "docs/architecture").glob("*.md")))),
        ("Component pages", len(list((ROOT / "docs/components").glob("*.md")))),
        ("Kernel topic pages", len(list((ROOT / "docs/kernel").glob("*.md")))),
        ("Testing/design pages", len(list((ROOT / "docs/testing").glob("*.md")))),
    ]

    lines = [
        f"# CDIN Specification v{displayed_version}",
        "",
        "> Automatically generated from this tagged source tree. Counts are an inventory summary, not a documentation-quality or implementation-conformance check.",
        "",
        "## Specification overview",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {name} | {count} |" for name, count in metrics)
    lines += [
        "",
        "## Version labels",
        "",
        "| Contract / package | Version |",
        "| --- | --- |",
        f"| Spec release | `{displayed_version}` |",
        f"| `cdin-kernel` package | `{kernel_package}` |",
        f"| Public C ABI | `{kernel_abi}` |",
        f"| Kernel-declared Spec target | `{kernel_spec_target}` |",
        "",
        "## Status counts",
        "",
        "The categories below are counted independently: requirement status, ADR status and Open Decisions Register disposition are not the same thing.",
        "",
    ]
    lines.extend(format_status_table("Normative requirements", requirements, REQUIREMENT_STATUSES))
    lines.extend(format_status_table("Architecture Decision Records", adr_statuses, (*REQUIREMENT_STATUSES, *OTHER_STATUSES, "UNLABELLED")))
    lines.extend(format_status_table("Open Decisions Register", decision_statuses, ("OPEN", "PROPOSED", "DEFERRED", "RESOLVED", "UNLABELLED")))

    if release_version is not None:
        changelog_section = extract_changelog_section(release_version)
        lines += ["## Changelog", ""]
        if changelog_section.strip():
            # Keep the release entry's Added/Changed/Fixed sections, omitting only the top-level version heading.
            lines.extend(changelog_section.rstrip().splitlines())
        else:
            lines.append("No details were listed under this version in `CHANGELOG.md`.")
        lines.append("")

    lines += [
        "---",
        "Generated by `scripts/spec_report.py`. This script reports counts and assembles release notes only; it does not lint links, enforce indexes, render Mermaid, or run implementation tests.",
        "",
    ]
    return "\n".join(lines)


def extract_changelog_section(version: str) -> str:
    changelog = read_text(CHANGELOG_FILE)
    heading_re = re.compile(rf"^## \[{re.escape(version)}\](?:\s|$).*$", re.MULTILINE)
    match = heading_re.search(changelog)
    if not match:
        raise RuntimeError(
            f"CHANGELOG.md has no '## [{version}]' entry. Add the release's Changelog entry before pushing tag v{version}."
        )
    next_heading = re.search(r"^## \[", changelog[match.end():], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(changelog)
    section = changelog[match.end():end].strip()
    return section


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print CDIN Spec inventory/status counts or generate version-specific GitHub Release notes."
    )
    parser.add_argument(
        "--release-version",
        help="Generate release notes for this exact x.y.z version, including its CHANGELOG.md section.",
    )
    parser.add_argument("--output", type=Path, help="Write output to this path instead of standard output.")
    args = parser.parse_args()

    try:
        version = args.release_version
        if version is not None and not SEMVER_RE.fullmatch(version):
            raise RuntimeError(f"Invalid release version '{version}'; expected numeric MAJOR.MINOR.PATCH (for example 1.2.0).")
        output = render_report(version)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
            print(f"Wrote release report to {args.output}")
        else:
            print(output, end="")
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
