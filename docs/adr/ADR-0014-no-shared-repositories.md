# ADR-0014: No catch-all shared repositories

- **ID:** ADR-0014
- **Status:** ACCEPTED

## Context

Repository splits can produce a `common` or `shared` repository for code that does not fit elsewhere. Such repositories tend to become dumping grounds, couple unrelated release cycles and blur ownership. The project avoids `cdin-common`, `cdin-shared` and `cdin-scripts` without a concrete architectural responsibility and explicit approval.

The accepted Registry architecture in [ADR-0022](ADR-0022-minimal-static-release-catalog.md) introduces an independent repository. This must be distinguished from a catch-all shared-code repository.

## Decision

No catch-all `cdin-common`, `cdin-shared` or `cdin-scripts` repository is created (ARCH-005). Tooling specific to the CDIN composition root stays in `cdin`. Code shared by components belongs in a versioned public contract or is duplicated deliberately unless a separately justified system boundary is approved.

A standalone repository is acceptable when it owns one cohesive system with its own purpose, public boundary, implementation, tests and release lifecycle. It is not a shared-utilities repository merely because multiple products may use it.

**Registry is a valid independent infrastructure repository** because it owns component delivery and orchestration: catalog ingestion, version/dependency/contract resolution, source collection and reproducible workspace production. It owns its implementation and conformance tests. It does not host generic libraries for components, replace component source ownership or link into a product at runtime.

The protocol reference codec remains the independently linkable `cdin_protocol` target inside Backend. [ADR-0018](ADR-0018-frontend-protocol-wire.md) accepts that placement and avoids a separate shared/client-library repository.

## Options

- **A. No catch-all shared repositories (decision).** Each repository has one responsibility and one owner; some deliberate duplication may remain.
- **B. A shared utilities repository.** Rejected because it becomes a coupling point and blurs ownership.
- **C. A separately justified infrastructure system.** Accepted when the system owns a cohesive capability, public contracts, tests and independent lifecycle; Registry is the concrete case.

## Trade-offs

A small amount of duplication is cheaper than an unbounded shared-code coupling point. A genuinely independent system can serve multiple consumers without becoming a common library repository.

## Consequences

- No repository may be created only to collect miscellaneous shared helpers.
- A new infrastructure repository requires an explicit responsibility, public boundary, owner and independent verification/release story.
- `cdin-editor/registry` is permitted as the implementation repository for the accepted Registry architecture in ADR-0022.
- ARCH-030 remains the repository-creation justification rule; Registry satisfies it through its distinct capability, public contracts, owner and lifecycle. ARCH-031 governs extraction of product components.

## References

ARCH-005, ARCH-030, ARCH-034, [ADR-0018](ADR-0018-frontend-protocol-wire.md), [ADR-0022](ADR-0022-minimal-static-release-catalog.md).
