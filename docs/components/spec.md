# The specification (this repository)

How this repository works, so that it stays correct against real code instead of becoming paper.

## 1. Purpose

- Hold the architecture and contracts of CDIN in one authoritative place.
- Record decisions and open questions explicitly (ADRs and the Open Decisions Register).
- Describe how every requirement will be verified.
- Report honestly what was inspected, what is decided and what is not.

It is **design only**: no implementation, no test runner, no code beyond non-normative sketches.

## 2. Requirements on the specification itself

- **SPEC-001** `ACCEPTED` The specification MUST be written in English first. — *Verify:* INSPECT
- **SPEC-002** `ACCEPTED` This repository contains design and architecture only; no implementation. — *Verify:* INSPECT
- **SPEC-003** `PROPOSED` Every normative requirement has a stable ID and a named verification method ([conventions.md](../reference/conventions.md)). — *Verify:* STATIC
- **SPEC-004** `PROPOSED` Every `EXISTING` statement carries a code anchor; a statement whose anchor no longer matches is a recorded contradiction. — *Verify:* INSPECT
- **SPEC-005** `PROPOSED` Unresolved items appear only in the Open Decisions Register, never as requirements. — *Verify:* STATIC
- **SPEC-006** `PROPOSED` Diagrams and prose agree; a diagram never shows `OPEN` behaviour as settled. — *Verify:* INSPECT
- **SPEC-007** `PROPOSED` No history or date is invented. A claim about the state of any repository names the snapshot it was drawn from ([status.md](../reference/status.md)). — *Verify:* INSPECT
- **SPEC-008** `ACCEPTED` No test is reported as passing unless it was run. Spec-only checks and cross-repository implementation tests MUST be reported separately, with command, implementation version, date and result. — *Verify:* INSPECT

## 3. Versioning of the specification

- **SPEC-010** `ACCEPTED` This specification has a semantic version recorded in [status.md](../reference/status.md). MAJOR increments when a stable contract changes incompatibly; MINOR adds compatible contract content or promotes decisions; PATCH contains corrections that do not change normative meaning. — *Verify:* INSPECT
- **SPEC-011** `PROPOSED` A component states the specification version it claims to conform to (ARCH-014). A conformance claim is meaningful only for requirements that were `ACCEPTED` at that version. — *Verify:* INSPECT
- **SPEC-012** `PROPOSED` Requirement IDs are permanent. A withdrawn requirement keeps its ID, with a note, and is never reused. — *Verify:* STATIC

## 4. Change process

```mermaid
flowchart LR
    Q["question or idea"] --> OD["OPEN in the register"]
    OD --> P["PROPOSED with options and trade-offs (ADR)"]
    P --> SP["prototype spike exercises it"]
    SP --> D{"owner decides"}
    D -- "accept" --> A["ACCEPTED"]
    D -- "postpone" --> DF["DEFERRED"]
    D -- "revise" --> P
    SP -- "contradicts spec" --> P
```

*Caption: the life of a decision.*

- **SPEC-020** `PROPOSED` Only the project owner moves a decision to `ACCEPTED` or `DEFERRED`. — *Verify:* INSPECT
- **SPEC-021** `PROPOSED` A change to an `ACCEPTED` requirement requires an ADR describing the change, its reason and its consequences. — *Verify:* INSPECT
- **SPEC-022** `PROPOSED` A spec change MUST be committed before or together with the code change that depends on it, never after. — *Verify:* INSPECT

## 5. Implementation feedback gates

This is how the specification stays honest against real code while keeping implementation code in its own repositories.

- **SPEC-030** `PROPOSED` Before a component's `PROPOSED` requirements are promoted, a **prototype or production implementation** MUST exercise the relevant contract against conformance checks. A production implementation with public-API tests may satisfy this gate; the project MUST record where the implementation does not match the proposal. — *Verify:* INSPECT
- **SPEC-031** `PROPOSED` The spike's findings are written back: either the specification is confirmed, or the contradicting requirement returns to `PROPOSED` with a note and an ADR. — *Verify:* INSPECT
- **SPEC-032** `PROPOSED` Each phase of [migration.md](../architecture/migration.md) begins with a spike and ends with a gate; the gates are listed there. — *Verify:* INSPECT
- **SPEC-033** `PROPOSED` The remaining implementation spikes, in order, are: integrate `cdin-kernel` into the backend; validate its ABI-1 compatibility in the composition root; define the serialized Frontend Protocol and one `view.lines` round trip; stabilize the runtime host API; then decide whether and how regex search is added. The Kernel ABI, versioned handles, replace/version check, text-region classification, transactions and notification overflow already have implementation-backed checks. — *Verify:* INSPECT

## 6. Traceability

- **SPEC-040** `PROPOSED` [status.md](../reference/status.md) lists requirement counts by status and identifies verification that was actually executed, separating Spec structure checks from implementation tests. — *Verify:* INSPECT
- **SPEC-041** `PROPOSED` The matrix in [test-matrix.md](../testing/test-matrix.md) maps each requirement group to its verification methods and to the planned conformance-vector families. — *Verify:* INSPECT

## 7. Repository layout and flow

The repository carries a git-flow configuration (`.gix/config`) with `main`, `develop`, `feature/`, `bugfix/`, `release/` and `hotfix/` branches. This specification follows it: day-to-day edits on `feature/` or `bugfix/` branches into `develop`; releases tag `main`. (`EXISTING`, anchor: `.gix/config` in this repository.)
