# ADR-0015: Specification language and scope

- **ID:** ADR-0015
- **Status:** `ACCEPTED`

## Context
The `spec` repository is public. The owner works in Persian and English. The current priority is architecture and system design.

## Problem
In which language is the specification written, and does it contain implementation?

## Decision
- English first for all normative text (SPEC-001). A Persian summary may be added later; it is never normative.
- Design and architecture only: no implementation and no test runner in this repository (SPEC-002). Verification is *designed* (methods, vector families, reporting) and not written.

## Options
- **A. English only for now (decision).** Pros: one source of truth; broadest audience. Cons: slower for the owner to review.
- **B. Persian primary.** Pros: owner's language. Cons: narrower audience; terminology mismatch with code and APIs.
- **C. Bilingual normative text.** Pros: both audiences. Cons: two sources of truth that drift.

## Trade-offs
One normative language avoids drift; discussion can still happen in either language.

## Consequences
Conformance vectors, when written, live with the implementation or in a dedicated place decided later; the design in [conformance.md](../testing/conformance.md) fixes their shape. The specification stays honest about this: no tests are claimed (SPEC-008).

## References
SPEC-001, SPEC-002, [spec.md](../components/spec.md).
