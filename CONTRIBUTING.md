# Contributing

This repository is design only: no implementation, no test code.

## Before you start

Read [docs/reference/conventions.md](docs/reference/conventions.md). Status labels, requirement
IDs and verification methods are the whole grammar; a change that ignores them will be sent back.

## Making a change

1. Branch from `develop` (`feature/…` or `bugfix/…`; the flow is in `.gix/config`).
2. Edit the page that owns the requirement ([where an ID lives](docs/README.md)).
3. Review relative links, requirement IDs, status transitions and diagrams affected by the change manually; this repository intentionally has no automated content-validation job.
4. Run `python3 scripts/spec_report.py` to see the current inventory and status counts. Update `docs/reference/status.md` if the release record changes.
5. Add or update the appropriate `CHANGELOG.md` entry.
6. Commit as `<type>(<scope>): <subject>` (`docs`, `fix`, `feat`, `chore`, `refactor`).

## Rules

- IDs are permanent. A withdrawn requirement keeps its ID (SPEC-012).
- Only the project owner moves a decision to `ACCEPTED` or `DEFERRED` (SPEC-020).
- A change to an `ACCEPTED` requirement needs an ADR (SPEC-021).
- An `EXISTING` statement needs an `Anchor:`; one that stops matching the code is a recorded
  contradiction, not a silent edit.
- Unresolved questions go in the [register](docs/adr/open-decisions.md), never in a requirement.
- Diagrams and prose must agree (SPEC-006).
