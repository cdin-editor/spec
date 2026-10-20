<!--
Thanks for improving the CDIN specification.
This repository is design only: no implementation, no test code. A good pull request here
changes words, requirements, decisions or diagrams, and says exactly which.
Delete any section that does not apply, but do not delete the checklist.
Rules referenced below live in docs/components/spec.md and docs/reference/conventions.md.
-->

## Summary

<!-- One or two sentences: what changes and why. Describe the effect on the specification,
     not the editing you did. -->

## Motivation

<!-- What is wrong or missing today? Link the evidence: an issue, an open decision,
     a spike finding, a contradiction with the `cdin` code. -->

Closes # (issue)
Related open decisions: <!-- e.g. OD-17, OD-22 -->
Related ADRs: <!-- e.g. ADR-0005 -->

## Type of change

<!-- Tick every box that applies. -->

- [ ] **Editorial**: wording, typos, links, formatting. No requirement changes meaning (PATCH)
- [ ] **New requirement(s)**: new IDs added (MINOR)
- [ ] **Changed requirement(s)**: an existing requirement's text or verification changes
- [ ] **Status change**: a requirement or decision moves between `OPEN`, `PROPOSED`, `ACCEPTED`, `DEFERRED` (needs the owner)
- [ ] **Changed `ACCEPTED` requirement**: its meaning changes (MAJOR, needs an ADR and the owner)
- [ ] **New or changed ADR**
- [ ] **Open Decisions Register**: entry added, updated or resolved
- [ ] **Diagram**: added, redrawn or restyled
- [ ] **Contradiction with `cdin` found**: recorded in `docs/reference/status.md`
- [ ] **Anchor update**: an `EXISTING` statement re-verified against a newer `cdin` snapshot
- [ ] **Repository, tooling or CI**: `scripts/`, `.github/`, `psx.yml`, project files
- [ ] **Release**: version bump and changelog

## Areas touched

<!-- Tick every area with a changed file. -->

- [ ] `docs/architecture/`
- [ ] `docs/components/`
- [ ] `docs/kernel/`
- [ ] `docs/testing/`
- [ ] `docs/adr/`
- [ ] `docs/reference/` (conventions, glossary, status)
- [ ] `docs/README.md` or `README.md`
- [ ] `scripts/`
- [ ] `.github/`, `psx.yml`, project files

## What changed

<!-- File by file, or area by area. Be specific enough that a reviewer can find each change. -->

| File | Change |
| --- | --- |
|  |  |

## Requirements

<!-- Fill in for every requirement added, changed, promoted or withdrawn.
     IDs are permanent: never reuse or renumber (SPEC-012). A withdrawn requirement keeps its
     ID with status DEFERRED or a note. Write "none" if no requirement is touched. -->

| ID | Change | Status before | Status after | Verify |
| --- | --- | --- | --- | --- |
|  | added / reworded / promoted / withdrawn |  |  | INSPECT, STATIC, CONF, FUZZ, SAN, PERF, INTEG |

- [ ] Each requirement line has the exact shape: `- **PREFIX-NNN** \`STATUS\` text. — *Verify:* METHOD`
- [ ] The prefix is registered in `docs/reference/conventions.md`
- [ ] MUST, MUST NOT, SHOULD, SHOULD NOT, MAY appear only in requirement lines
- [ ] Every requirement names how it will be verified, even though nothing is run here
- [ ] The requirement states one thing; a second thing is a second requirement

## Status transitions

<!-- Allowed: OPEN → PROPOSED → ACCEPTED; any → DEFERRED; DEFERRED → PROPOSED.
     Only the project owner sets ACCEPTED or DEFERRED (SPEC-020). -->

- [ ] No `PROPOSED` item was promoted to `ACCEPTED` by this PR, **or** the owner approved it in: <!-- link -->
- [ ] A change to an `ACCEPTED` requirement has an ADR describing the change, its reason and its consequences (SPEC-021)
- [ ] A component section was not declared settled without a prototype spike having exercised it (SPEC-030, SPEC-031)
- [ ] Unresolved questions are in the Open Decisions Register, not written as requirements (SPEC-005)

## Decisions and ADRs

<!-- Skip if no ADR or register entry changes. -->

- [ ] ADR has: ID, title, status, context, problem, decision (or the question), options, trade-offs, consequences, references
- [ ] ADR carries no invented dates or histories (SPEC-007)
- [ ] `docs/adr/README.md` index updated
- [ ] `docs/adr/open-decisions.md` summary table and entry updated

## Existing code (`EXISTING` statements)

<!-- Skip if no EXISTING statement is added or changed. -->

- [ ] Every `EXISTING` statement has `*Anchor:*` naming a path relative to the `cdin` root, and a section or symbol where useful (SPEC-004)
- [ ] The anchor was verified against the snapshot recorded in `docs/reference/status.md`: <!-- snapshot / commit -->
- [ ] A statement that stopped matching the code is recorded as a contradiction in `status.md`, not silently edited

Contradictions found:

| # | Finding | Where in `cdin` | Handling |
| --- | --- | --- | --- |
|  |  |  |  |

## Diagrams

<!-- Skip if no diagram changes. -->

- [ ] Uses the vocabulary in `docs/reference/conventions.md` §4 (component, contract, external, deferred, outcome)
- [ ] A `PROPOSED` flow says so in its caption; an `OPEN` behaviour is not drawn as settled (SPEC-006)
- [ ] The diagram and the surrounding prose agree
- [ ] Mermaid source reviewed manually; rendered locally if a Mermaid renderer is available

## Documentation hygiene

- [ ] Relative links resolve; moved or renamed pages are updated everywhere
- [ ] New pages are linked from `docs/README.md` (or their directory index)
- [ ] New terms are in `docs/reference/glossary.md`, with exactly one meaning
- [ ] The written spec change is committed before or together with any code that depends on it (SPEC-022)
- [ ] Do not claim an implementation test passed unless it was actually run (SPEC-008)
- [ ] No component named in a way that contradicts `docs/architecture/repositories.md`

## Version and changelog

- [ ] `CHANGELOG.md` has an entry under `[Unreleased]`
- [ ] If this is a release: version bumped in `docs/reference/status.md` (SPEC-010), changelog dated, tag `vX.Y.Z` planned
- [ ] Current inventory reviewed with `python3 scripts/spec_report.py`

## How was this checked?

<!-- Describe any manual review or external tests actually performed. No automated Spec validation workflow runs. -->

```text
$ python3 scripts/spec_report.py
```

- [ ] Manual review of affected links, requirement IDs, status transitions and diagram/prose alignment completed
- [ ] `scripts/spec_report.py` output reviewed (informational only; it is not a validation gate)

Not run, and why:

## Impact

- [ ] No requirement changes meaning
- [ ] Changes an `ACCEPTED` requirement (breaking for implementers)
- [ ] Changes a contract (ABI, Frontend Protocol, extension contract): who is affected?

<!-- If breaking: which components, which repositories (`cdin`, `cdin-x`), what must change. -->

## Reviewer notes

<!-- Where should the reviewer look hardest? What are you unsure about?
     Which alternatives did you reject, and why? -->

## Before merging

- [ ] Commits follow `<type>(<scope>): <subject>` (`docs`, `fix`, `feat`, `chore`, `refactor`, `build`, `ci`)
- [ ] Commits are signed (`git commit -S`)
- [ ] Branch is `feature/…` or `bugfix/…` into `develop` (releases tag `main`)
- [ ] I have read the pull request myself, top to bottom