# ADR-0015: Specification language and scope

- **ID:** ADR-0015
- **Status:** `ACCEPTED`

## Context
The `spec` repository is public. The owner works in Persian and English. The current priority is architecture and system design.

## Problem
In which language is the specification written, and does it contain implementation?

## Decision
- English first for all normative text (SPEC-001). A Persian summary may be added later; it is never normative.
- Design and architecture only: no product implementation or test runner in this repository (SPEC-002). Verification methods and vectors are designed here; separate implementation repositories own executable runners and report actual results.

## Options
- **A. English only for now (decision).** Pros: one source of truth; broadest audience. Cons: slower for the owner to review.
- **B. Persian primary.** Pros: owner's language. Cons: narrower audience; terminology mismatch with code and APIs.
- **C. Bilingual normative text.** Pros: both audiences. Cons: two sources of truth that drift.

## Trade-offs
One normative language avoids drift; discussion can still happen in either language.

## Consequences
Conformance vectors live with the relevant implementation when that is the practical owner. `cdin-kernel` includes vectors and a runner for ABI 1.0.0; the Spec only claims results recorded with exact commands and versions (SPEC-008).

## References
SPEC-001, SPEC-002, [spec.md](../components/spec.md).
