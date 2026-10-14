# ADR-0001: Repository topology

- **ID:** ADR-0001
- **Status:** `PROPOSED`. The following parts are `ACCEPTED`: `cdin` is the composition root; `cdin-x` is fully separate; no `cdin-common` or `cdin-shared` repository without approval (see [ADR-0014](ADR-0014-no-shared-repositories.md)).

## Context
The `cdin` repository mixes C, Lua and tooling. The owner wants it split so it is easier to manage and develop. Candidate repositories named: engine or kernel, frontend, backend, runtime, data, and `cdin-x` (already separate, top level, unrelated to `cdin`'s internals). Questions raised: whether `cdin-scripts` or `cdin-shared` are needed.

Inspected facts (see [status.md](../reference/status.md)): about 7.2 thousand lines of C, about 7.3 thousand lines of Lua core, about 6.6 thousand lines of tooling; the C API and the Lua core change together; the only coupling to `cdin-x` is the `CDINX_DIR` build input.

## Problem
Which components become separate repositories, and when?

## Decision (proposed)
Stage the split. Define contracts first (this repository), then extract:

1. `spec` now.
2. `cdin-kernel` after its ABI has a stable version and two consumers; until then a directory in `cdin`.
3. `cdin-runtime` after the runtime host API is stable.
4. The backend stays in `cdin` with the composition root.
5. Frontends are directories in `cdin` and are extractable at any time because they depend only on the protocol.
6. `data` has no repository (see [data.md](../components/data.md)).
7. No `cdin-scripts`, `cdin-shared`, `cdin-common`, `cdin-backend`, `cdin-frontend` or `cdin-data` repositories.

## Options
- **A. Split everything into five repositories now.** Pros: matches the owner's first sketch. Cons: C API and Lua core change together, so every change becomes several coordinated pull requests; contracts do not yet exist; the build rule "editor builds and starts after every step" (ARCH-026) becomes harder to hold.
- **B. Stage the split behind contracts (proposed).** Pros: repositories appear when they have an owner-visible reason; contracts get exercised first. Cons: the `cdin` repository stays larger for longer.
- **C. Keep one repository and restructure directories only.** Pros: simplest. Cons: does not provide the independent kernel the architecture wants.

## Trade-offs
Early repositories give clean boundaries on day one but multiply coordination cost; late repositories keep velocity but defer the boundary. Staging with explicit entry conditions ([repositories.md](../architecture/repositories.md), ARCH-030 to ARCH-035) gets the boundary from contracts rather than from repository walls.

## Consequences
- `cdin-scripts` is not created: the tooling depends on the Makefile and the layout of `src/`, so a separate repository would break whenever the layout changes.
- `cdin-shared` is not created: nothing is shared between two repositories today; the only shared artifact with an architectural reason is a protocol client library (ARCH-035, [OD-23](open-decisions.md)).
- Extraction rules and the migration order are in [migration.md](../architecture/migration.md).

## References
[repositories.md](../architecture/repositories.md), [migration.md](../architecture/migration.md), [ADR-0014](ADR-0014-no-shared-repositories.md).
