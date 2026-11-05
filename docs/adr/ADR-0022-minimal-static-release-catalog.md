# ADR-0022: Minimal static release catalog for component discovery

- **ID:** ADR-0022
- **Status:** `PROPOSED`
- **Decision scope:** Registry v1 architecture and responsibility boundaries

## Context

CDIN is assembled from independently versioned component repositories. Each component repository already owns its source, version, Git tags, release workflow and (when needed) GitHub Release assets.

A central Registry could make release discovery easier, but a full artifact registry would duplicate capabilities already provided by GitHub Releases. It would also introduce artifact hosting, retention, schemas, signing infrastructure, a resolver service and another publication pipeline.

The Registry is justified only if it reduces coordination work for CDIN. It must not become another package manager or a second source of truth for component releases.

## Decision

**Proposal: define `cdin-editor/registry` as a minimal static release catalog. It is a release-discovery directory, not an artifact host or package manager.**

The Registry answers four questions: which component releases exist; which immutable source revision belongs to each release; which independently versioned contracts the release implements; and where the authoritative source or optional release asset can be retrieved.

The Registry stores metadata and references. Component repositories remain authoritative for source code, tags, release notes, build outputs and release ownership.

### Architectural placement

The Registry belongs to the **release and discovery plane**. It sits between component publication workflows and CDIN's integration coordinator:

- Component repositories publish their own releases.
- The Registry indexes those releases in a static catalog.
- CDIN consumes the catalog, resolves a compatible component set, verifies inputs and runs integration gates.
- The Spec repository defines architecture and contract rules; it does not execute Registry operations.

The Registry is not part of the editor runtime, does not link into the product, and is not a dependency of Kernel, Runtime, Backend or Frontend. See [Registry architecture](../architecture/registry.md) for the placement diagram and end-to-end flow.

### Minimal v1 format

- One static JSON catalog, initially a single `index.json`.
- Each entry identifies a stable component ID, package version, source repository, release tag, full commit SHA, implemented contract versions and optional GitHub Release URL.
- Catalog history is the Git history of the Registry repository.
- No database, API server, custom package format, per-record schema collection or separate snapshot-versioning system.

### Source and artifact distribution

Source and optional release assets remain in the component's own repository and GitHub Release. CDIN may retrieve source at the exact recorded commit. A component may attach a prebuilt asset to its own release only when a real consumer needs it.

The Registry does not copy, mirror or retain component artifacts. Do not create platform/architecture artifact matrices for components that CDIN builds from source.

### Publication

The component's existing CI remains responsible for component build and tests, tagging and release publication. A small publication step adds the release metadata to the Registry catalog and validates the catalog update. The Registry does not rebuild or re-release components.

### Compatibility and lockfiles

Package version and contract version are independent. A Kernel package release `2.0.0` does not imply that the public Kernel ABI is `2.0.0`.

CDIN owns dependency constraints, compatibility policy, dependency graph resolution and `deps.lock`. A release is only a candidate when its declared contract versions satisfy the consuming integration profile; passing CDIN contract and integration tests is still required.

The Registry never chooses the final dependency set and never edits lockfiles.

### Automatic coordination

Automatic coordination means discovery of catalog changes, candidate resolution in CDIN, retrieval of exact pinned source and optional assets, verification and build/contract/integration tests, then opening or updating a CDIN pull request containing the proposed lockfile change and test evidence.

It does **not** mean automatic merge. Merge policy remains a separate decision and auto-merge is disabled by this proposal.

### Integrity and trust

For v1, use HTTPS, GitHub repository access controls, immutable full commit references and SHA-256 checksums for optional downloadable assets. Do not create a custom signing protocol or central root-of-trust service.

This is a practical integrity baseline, not a claim of independently verifiable publisher signatures or signed provenance. Revisit signing when external publishers or a documented threat model justify its cost.

### Withdrawal

A withdrawn release is marked unavailable in the catalog with a reason and timestamp. The Registry does not silently rewrite or delete component release assets. New CDIN resolution rejects withdrawn releases; existing lockfiles remain reproducible unless a separate security policy blocks them.

## Consequences

- Registry v1 is a discovery index, not a package manager, artifact mirror or runtime service.
- Component repositories remain independently releasable and authoritative.
- CDIN remains the sole owner of resolution, compatibility decisions, lockfiles and integration coordination.
- The first implementation can be one JSON catalog and a small validation/publication workflow.
- Signing infrastructure, external object storage, multi-platform artifact matrices, a Registry API, dependency solving inside Registry and auto-merge are out of scope until demonstrated needs exist.

## Alternatives considered

### No Registry — query component repositories directly

This is the simplest option and remains viable while CDIN has only a handful of first-party components. It avoids another repository but makes CDIN maintain discovery logic for each component source. Prefer this option if a catalog does not materially simplify coordination.

### Full artifact registry

Rejected for v1. It duplicates GitHub Release distribution and introduces storage, retention, upload, trust and schema-management responsibilities without a demonstrated need.

### Custom service and database

Rejected. Static metadata is sufficient; an always-on service would add operational cost without solving a current problem.

## References

- [Registry architecture](../architecture/registry.md)
- [ADR-0001 — Repository topology](ADR-0001-repository-topology.md)
- [ADR-0014 — No shared or common repositories](ADR-0014-no-shared-repositories.md)
- [Repository topology](../architecture/repositories.md)
- [CDIN composition root](../components/cdin.md)
