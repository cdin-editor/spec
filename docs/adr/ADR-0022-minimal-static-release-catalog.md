# ADR-0022: Generic Consumer-Independent Registry

- **ID:** ADR-0022
- **Status:** ACCEPTED
- **Decision scope:** Registry purpose, responsibility boundaries, public data contracts and reproducible workspace handoff

## Context

CDIN is assembled from independently developed and versioned components. Repository topology can evolve: one logical component may use several source repositories, one repository may publish several variants, and a product may require only a subset of available components and variants.

A static catalog that merely lists release URLs leaves version selection, update management, dependency resolution and source collection with every consumer. Putting those responsibilities inside CDIN couples the composition root to repository layouts and package lifecycle concerns. Hardcoding product identities or workflows inside Registry prevents reuse.

The independent `cdin-editor/registry` repository has been created. This ADR defines its architectural responsibility and data boundary; it does not claim the implementation is complete or shipped.

## Decision

**Registry is a generic, consumer-independent Component Registry and Orchestration Engine.**

Registry owns catalog ingestion, release metadata validation, version and update discovery, dependency and contract resolution, immutable source collection, workspace preparation, Resolved Manifest and Resolution Report generation, and a separate Update Discovery Report for read-only historical/current comparisons.

A declarative **Product Definition** supplies root component requirements, variants, version constraints and target-environment contracts. It is data, not executable product logic.

> **Registry must understand requirements, not consumer identity.**

The same engine serves CDIN Editor and unrelated products through different Product Definitions. A new consumer requires no product-specific code path, product-ID conditional, plug-in or custom workflow.

## Responsibilities

- **Component repositories** remain authoritative for source, package versions, release metadata, tags, release notes, component tests and publication.
- **Catalog Indexes** reference immutable Component Release Metadata and SHA-256 digests. They do not mirror source or replace component release authority.
- **Product Definitions** declare required logical components, variants, version constraints and environment contracts.
- **Registry** validates metadata, discovers eligible releases, resolves dependency and contract graphs, collects exact source revisions and prepares a deterministic workspace, Resolved Manifest and Resolution Report. It also emits a schema-validated Update Discovery Report without mutating historical Manifests or Workspaces.
- **CDIN and other consumers** use the workspace as input and own product-specific configuration, integration, builds, tests, packaging and launch.
- **Spec** defines architecture, public data contracts, requirements and decisions; it contains no Registry implementation.

## Public contract

Registry contract baseline `1.2.0` consists of six JSON Schema documents under `schemas/registry/v1/`: Product Definition, Catalog Index, Component Release Metadata, Resolved Manifest, Resolution Report and Update Discovery Report. The Resolution Report remains independently versioned at schema `1.1.0`; Update Discovery Report starts at schema `1.0.0`.

Product Definitions may be authored as YAML 1.2 or JSON. The JSON data model is canonical; other public documents and Registry outputs are JSON. The schemas use JSON Schema Draft 2020-12. Schema compatibility, identity, SemVer constraints, resolver semantics, source revision rules, workspace layout and manifest determinism are normative in [Registry data contracts](../architecture/registry-contracts.md).

A logical component is independent of repository topology. A release may declare multiple source units, and source units identify repositories by URI and commits by full immutable Git object ID. A selected release is identified by component ID, variant and Semantic Version.

## Resolution and reproducibility

Registry resolves root and transitive dependencies. Constraints for the same normalized component/variant key are intersected. A successful resolution selects exactly one active release per key and validates every required contract against exactly one compatible selected provider or environment declaration.

Prereleases are disabled unless explicitly enabled in the Product Definition. Withdrawn releases are excluded from new resolutions. Cycles, missing dependencies, constraint conflicts, metadata ambiguity and missing/ambiguous contract providers fail explicitly. Catalog ordering and publication timestamps are never tie-breakers.

A successful prepare operation materializes each source unit at its exact commit and emits a deterministic workspace, Resolved Manifest and Resolution Report. A new release creates a new resolution candidate; it never mutates an existing workspace or manifest. The manifest is the reproducibility record, not a mutable lockfile maintained by CDIN.

Update discovery verifies a historical Manifest before reading current Catalog state, resolves the current Product Definition through the same generic Resolver and emits an immutable, deterministic audit report bound to the exact historical Manifest, Product Definition bytes and Catalog Index identities. It records current withdrawal and selection evidence but never rewrites historical bytes, recollects sources or republishes a Workspace.

## Repository placement and implementation boundary

Registry belongs in the independent `cdin-editor/registry` infrastructure repository. It is not a `cdin-common`, `cdin-shared` or generic shared-utilities repository: it owns one cohesive system for component delivery and orchestration. No product component links to Registry or requires it at runtime.

The first implementation may be one local engine with a CLI entry point and version-controlled metadata. A database, microservices, permanent service, custom package format, custom artifact host or product-specific extension mechanism is not required.

## Consequences

- Component lifecycle and source collection are implemented once instead of duplicated by every consumer.
- Consumers remain independent of component repository topology and package update policy.
- Exact manifests make prepared source sets auditable and reproducible.
- Consumers retain ownership of integration and product verification.
- Registry contract 1.2.0 defines the additional Update Discovery Report data boundary; implementation language, CLI spelling, catalog distribution, cache policy, credential UX and service deployment remain repository-design choices.
- A Registry resolution is a candidate source set, not proof that the assembled product works.

## Alternatives considered

### Consumer-owned discovery and dependency resolution

Rejected. It couples each consumer to component topology, version/update management and source collection.

### Product-specific Registry rules

Rejected. Product identity conditionals and hardcoded component lists destroy consumer independence.

### Static catalog only, with consumers doing the rest

Rejected. It duplicates version selection, update tracking, dependency resolution and source collection in each consumer.

### Full package manager and artifact-hosting platform

Not required initially. Component repositories remain authoritative; Registry resolves metadata and collects exact source revisions without becoming a second source host.

### Catch-all shared repository

Rejected. Registry has its own bounded responsibility and is not a home for unrelated shared libraries or utilities. See ADR-0014.

## Deferred implementation choices

Implementation language/toolchain, internal modules, command names/flags, catalog distribution/transport, caching/garbage collection, download parallelism, authentication UX, publisher signing/trust roots, API deployment and release automation belong to Registry repository design. They do not change the accepted data contract.

## References

- [Registry architecture](../architecture/registry.md)
- [Registry data contracts](../architecture/registry-contracts.md)
- [ADR-0014 — No catch-all shared repositories](ADR-0014-no-shared-repositories.md)
- [Repository topology](../architecture/repositories.md)
- [System maps](../architecture/system-maps.md)
