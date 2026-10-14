# ADR-0014: No shared or common repositories

- **ID:** ADR-0014
- **Status:** `ACCEPTED`

## Context
Repository splits tend to produce a "common" or "shared" repository for whatever does not fit elsewhere. The owner's rule is to avoid `cdin-common` and `cdin-shared` without an architectural reason and explicit approval. The owner also asked whether `cdin-scripts` or `cdin-shared` would be needed.

## Problem
Is any auxiliary repository justified now?

## Decision
No. No `cdin-common`, `cdin-shared` or `cdin-scripts` repository is created (ARCH-005). Tooling stays in `cdin` because it depends on the Makefile and the source layout. Code needed by two components is either part of a contract (the ABI, the protocol) or duplicated deliberately.

The one artifact with an architectural justification is a protocol client library for frontend authors; its location is open ([OD-23](open-decisions.md)) and needs explicit approval.

## Options
- **A. No shared repositories (decision).** Pros: every repository has one responsibility and one owner. Cons: some duplication.
- **B. A shared utilities repository.** Pros: reuse. Cons: becomes a dumping ground; ties release cycles together; blurs ownership.

## Trade-offs
A small amount of duplication is cheaper than a coupling point that every component depends on.

## Consequences
The kernel does not depend on the backend's `base/` library: it takes an allocator through its ABI (ABI-017). If a library later proves useful to two components, an ADR with the justification precedes any new repository (ARCH-030).

## References
ARCH-005, ARCH-030, ARCH-035, [ADR-0001](ADR-0001-repository-topology.md).
