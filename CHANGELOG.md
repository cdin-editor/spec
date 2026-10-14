# Changelog

All notable changes to this specification are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
The specification version is defined in `docs/reference/status.md` (SPEC-010).

## [Unreleased]

### Changed

- Repository restructured to mirror `cdin`: root hygiene files, `docs/README.md` as the index,
  `docs/reference/` for conventions, glossary and status, `docs/adr/` (was `docs/decisions/`).
  Requirement IDs, ADR numbers and open-decision numbers are unchanged; all relative links rewritten.
- Diagrams share one visual vocabulary (see `docs/reference/conventions.md` §4). System context,
  module boundaries, undo/redo, text-model and migration diagrams redrawn; sequence diagrams numbered.

### Added

- `LICENSE` (GPL-3.0-or-later, as `cdin`) and `NOTICE`.
- `docs/README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `psx.yml`, issue and PR templates, check workflow.
- `scripts/check.py`: IDs, links, references, index and diagram checks, in the repository.
- A "today" diagram in `docs/architecture/repositories.md`.

### Fixed

- `DATA` page: an `EXISTING` statement lacked its `Anchor:` field.
