# AGENTS.md: rules for working on the CDIN specification

## What this repository is

The design-only specification of CDIN. It contains Markdown/Mermaid documentation and one small Python script used to report Spec metadata for GitHub Releases. It has no product implementation or automated CI test suite.

## Hard rules

1. Never promote a status. Only the owner sets `ACCEPTED` or `DEFERRED`.
2. Never reuse or renumber a requirement ID.
3. Never invent history, dates or test results. Describe verification only when it was actually performed.
4. Every `EXISTING` statement carries an `Anchor:` into the relevant implementation snapshot.
5. Diagrams use the vocabulary in `docs/reference/conventions.md` §4; caption any `PROPOSED` flow.
6. The `PROPOSED`, `OPEN`, and `DEFERRED` states must not be presented as accepted implementation facts.

## When counts change

Run `python3 scripts/spec_report.py` to report the current number of unique requirements by status, ADRs, Open Decisions Register dispositions, Markdown documents and Mermaid diagrams. Update the version/status documentation when preparing a release. The report is informational: it does not check links, references, index coverage, Mermaid syntax, or implementation conformance.

## Release flow

1. Add a dated/versioned entry to `CHANGELOG.md`.
2. Update the Spec release version in `docs/reference/status.md` and related version tables.
3. Preview the notes with `python3 scripts/spec_report.py --release-version X.Y.Z --output release-notes.md`.
4. Push tag `vX.Y.Z`. `.github/workflows/release.yml` creates the GitHub Release and puts the report and matching Changelog entry in its body.

## When to ask

An ambiguity whose wrong guess changes an `ACCEPTED` item. Otherwise decide, and say what you decided.
