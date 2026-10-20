# ADR-0012: Incremental migration

- **ID:** ADR-0012
- **Status:** `ACCEPTED`

## Context
A working editor exists (about 15 thousand lines of C and Lua core plus tooling). The target architecture moves the document model into a new kernel, introduces a protocol around the GUI and splits repositories. The project rule says the editor builds and starts after every step (ARCH-026).

## Problem
Rewrite or evolve?

## Decision
Evolve incrementally in the phases of [migration.md](../architecture/migration.md): Spec baseline; integrate the already-extracted `cdin-kernel` ABI 1.0.0 into `cdin`; migrate the Lua document layer into a kernel client; define the Frontend Protocol and integrate it in-process; add headless/serialized transport; extract `cdin-runtime` only after its host API is stable.

## Options
- **A. Big-bang rewrite.** Pros: a clean slate. Cons: long period without a working editor; no way to compare against existing behaviour.
- **B. Incremental (decision).** Pros: always a working editor; behaviour comparison against the Lua baseline at every step; reversible phases. Cons: transitional code (shims) and longer calendar time.
- **C. Fork a new editor.** Pros: freedom. Cons: duplicates all existing work.

## Trade-offs
Transitional shims are the price of never being broken; the existing tests and fuzz corpora become regression nets.

## Consequences
Each phase has an entry gate and an exit gate; each begins with a spike (SPEC-030, ARCH-062); each is reversible (ARCH-070).

## References
[migration.md](../architecture/migration.md), ARCH-026, ARCH-060 to ARCH-070.
