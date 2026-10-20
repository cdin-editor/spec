# Release-reporting script

This directory contains one standard-library Python script: `spec_report.py`.
It reports the Spec inventory and status counts. It is not a linter, content validator, test runner, link checker, or Mermaid renderer.

## Commands

```sh
python3 scripts/spec_report.py
python3 scripts/spec_report.py --release-version 1.1.0 --output release-notes.md
```

The first command prints current metrics. The second builds GitHub Release notes by combining the metrics with the matching `CHANGELOG.md` section. It fails if that exact version has no Changelog entry, so a release tag cannot silently publish notes from another version.

The release workflow runs only for pushed semantic-version tags matching `vX.Y.Z`; there is no branch-push or pull-request validation workflow.
