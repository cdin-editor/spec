# ADR-0001: Repository topology

- **ID:** ADR-0001
- **Status:** `ACCEPTED`

## Context
The supplied working-tree archives identify four current repositories: `cdin`, `cdin-kernel`, `spec`, and `cdin-x`. The archive snapshots contain no Git history, so this ADR records the target topology, not historical commit ancestry. `cdin` still contains the composition root, backend and frontend/runtime source; `cdin-kernel` is already a standalone C11 implementation with ABI 1.0.0; `cdin-x` remains a separate extension ecosystem.

## Problem
Which components are separate repositories now, and what should be extracted next?

## Decision
1. `spec` is the authoritative architecture/contracts repository; its stable baseline is version `1.0.0`.
2. `cdin-kernel` is a separate repository now, with a stable C ABI `1.0.0`; integration into `cdin` must be verified as its own gate.
3. `cdin` remains the composition root and retains build/bundle/release/launcher tooling, backend, frontends, and the current runtime code until the next boundary is stable.
4. `cdin-runtime` is the next justified repository extraction, but only after its host API is versioned, documented, and tested through an integration spike.
5. GUI-SDL, TUI, CLI and headless reference frontends remain directories in `cdin` until independent release cadence or ownership justifies a split.
6. No `cdin-backend`, `cdin-frontend`, `cdin-data`, `cdin-scripts`, `cdin-common` or `cdin-shared` repository is created without a new explicit decision.
7. `cdin-x` remains fully separate and interacts with the runtime extension contract; the kernel remains unaware of extensions.

## Options
- **A. Split every component immediately.** Rejected: too many untested boundaries and a multi-repository coordination burden.
- **B. Extract on stable contracts and independently justified release/ownership boundaries.** Accepted: the kernel boundary is stable; the runtime boundary is next but gated.
- **C. Keep everything in `cdin`.** Rejected for the kernel, whose stable public ABI and independent tests now justify its repository.

## Trade-offs
Staged extraction puts integration tests before repository separation. It does not assert that the supplied archive preserved Git history; that requires access to the actual repositories/history.

## Consequences
- The next repo to build is `cdin-runtime`, after a small host-API integration spike confirms that the current Lua/runtime surface can be separated without duplicating canonical document state.
- The immediate integration task is wiring `cdin-kernel` into `cdin` through the published header, checking ABI major 1, and proving the editor starts/builds without reimplementing document/history logic.
- No shared/common repository is introduced without approval ([ADR-0014](ADR-0014-no-shared-repositories.md)).

## References
[repositories.md](../architecture/repositories.md), [migration.md](../architecture/migration.md), [ADR-0014](ADR-0014-no-shared-repositories.md).
