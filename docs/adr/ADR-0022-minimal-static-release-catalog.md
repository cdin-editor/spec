# ADR-0022: Minimal static release catalog for component discovery

- **ID:** ADR-0022
- **Status:** `PROPOSED`

## Context

CDIN components already have independent Git repositories, tags, release workflows and versioned contracts. A separate registry could duplicate GitHub Releases by introducing artifact hosting, schemas, signing infrastructure, a resolver service and a second publication pipeline.

The registry is useful only if it removes coordination work from CDIN. It must not become another package manager or a second source of truth for component releases.

## Decision

**Proposal: keep `cdin-editor/registry` as a small, static release catalog. Do not make it an artifact host in v1.**

The catalog answers only:

1. Which component releases exist?
2. Which immutable source revision does each release identify?
3. Which independently versioned contracts does that release implement?
4. Where can CDIN retrieve the source or an explicitly published release asset?

The component repository remains authoritative for source code, tags, release notes, build outputs and release ownership. The registry stores references and discovery metadata only.

### Minimal catalog record

A record contains only:

- stable component identifier;
- package version;
- source repository URL;
- release tag and full commit SHA;
- contract identifiers and versions;
- optional GitHub Release URL and asset references when the component actually publishes assets.

The initial catalog is one static JSON document (for example, `index.json`). Do not introduce per-entity schema files, a database, an API server, a custom package format or a separate snapshot-versioning system in v1.

### Artifact and source distribution

The component's own Git repository and GitHub Release remain the distribution location. CDIN may retrieve source at the recorded immutable commit. A component may attach a binary or other artifact to its own GitHub Release when a real consumer requires it. The registry does not copy or mirror those files.

Do not create platform-specific artifact matrices for components that CDIN builds from source. Add target-specific assets only when a component has a concrete prebuilt-distribution requirement.

### Publication and discovery

The component's existing release workflow remains responsible for tests, tagging and publishing its release. Registry metadata is updated automatically from that release metadata; the registry does not rebuild or re-release the component.

CDIN periodically or on an explicit sync trigger reads the catalog, checks for newer eligible releases, resolves the component set against the declared contract requirements, and runs integration gates.

### Compatibility and lockfiles

Package version and contract version are independent. A package release such as Kernel `2.0.0` does not imply that its public ABI is also `2.0.0`.

A release is eligible only when its declared contract versions satisfy the consumer's requirements and the CDIN integration tests pass. A publisher's compatibility declaration alone is not proof of compatibility.

The resolver and dependency policy remain in CDIN. `deps.lock` records the exact selected source revision (and any required artifact digest); the registry never edits lockfiles.

### Automatic coordination

Automatic coordination means:

1. discover a catalog change;
2. resolve a candidate dependency set;
3. retrieve and verify the pinned source/artifacts;
4. run build, contract and integration tests;
5. open or update a CDIN pull request containing the lockfile change and test evidence.

It does **not** mean automatic merge. Merging remains a separate repository policy and is disabled by this proposal.

### Trust and integrity for v1

Use HTTPS, GitHub repository access controls, immutable release tags/revisions and SHA-256 checksums for explicitly published release assets. Do not invent a signing protocol or operate a custom root-of-trust service in v1.

This is an integrity baseline, not a claim of independently verifiable publisher signatures. Revisit signed provenance only when the threat model or external publishers justify the operational cost.

### Withdrawal

A withdrawn release is marked unavailable in the catalog with a reason and timestamp. Existing GitHub assets are not silently rewritten or deleted by the registry. CDIN must reject withdrawn releases during new resolution; existing lockfiles remain reproducible unless a security policy explicitly blocks them.

## Consequences

- The registry is a discovery index, not a package manager or binary mirror.
- Component repositories remain independently releasable and authoritative.
- CDIN owns dependency resolution, compatibility policy, lockfiles and integration decisions.
- The first implementation can be one JSON catalog plus a small validation/publication workflow.
- Signing, external object storage, multi-platform artifact matrices, a registry API, dependency solving in the registry and auto-merge are out of scope until a demonstrated need exists.

## Alternatives

- **Full artifact registry:** rejected for v1 because it duplicates GitHub Release storage and adds retention, upload, signing and schema-management responsibilities.
- **No registry; query every GitHub repository directly:** viable for a very small fixed set of first-party components. Keep this as the fallback if the static catalog does not materially simplify CDIN coordination.
- **Custom registry service/database:** rejected because static metadata is sufficient and does not justify an always-on service.

## References

[ADR-0001](ADR-0001-repository-topology.md), [ADR-0014](ADR-0014-no-shared-repositories.md), [repository topology](../architecture/repositories.md), [CDIN composition root](../components/cdin.md).
