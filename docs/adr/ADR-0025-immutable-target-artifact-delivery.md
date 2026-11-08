# ADR-0025: Immutable target-specific artifact delivery

- **ID:** ADR-0025
- **Status:** ACCEPTED
- **Decision scope:** Generic Registry delivery of versioned prebuilt component packages.

## Context

The existing Registry contract resolves immutable component releases and collects source units. Consumers that need already-built libraries or platform-neutral modules still have to clone component repositories and build them locally. This duplicates toolchain setup, increases install time and makes consumer installation depend on component development toolchains.

A generic artifact contract is needed, but embedding product-specific package knowledge in Registry would violate ADR-0022. It must also preserve source consumption for contributors and support gradual publisher migration.

## Decision

Extend Registry Data Contracts to `1.3.0` with an additive target-specific artifact delivery model. Component Release Metadata may declare immutable package artifacts alongside its immutable source units. Product Definitions explicitly request `source`, `artifact`, or `artifact-or-source` delivery and, for artifact modes, an exact target tuple (`os`, `architecture`, `abi`).

Registry resolves component versions exactly as before, then selects one compatible artifact deterministically. It verifies size and SHA-256, safely extracts the package into a private workspace and records exact identity and provenance in the Resolved Manifest. The existing source collector remains available. Registry never builds, tests, configures or installs a component.

The only universal artifact target is the explicit `any/any/none` tuple. Exact target matches beat universal packages; partial wildcards and ambiguous matches fail. Source fallback is allowed only when explicitly selected and only if no artifact matches. A selected artifact that fails download, integrity or extraction MUST fail the operation.

Manifest replay uses the exact recorded URL and digest; it never re-resolves a floating version or silently substitutes another artifact. SHA-256 integrity is not publisher authentication. Signing, trust roots and security policy remain separate concerns.

## Consequences

- Consumers can install compact, versioned packages without cloning or compiling component repositories.
- Component repositories retain ownership of source, tests, release metadata and artifact publication.
- Registry remains reusable by unrelated consumers and does not gain CDIN, GUI, SDL or toolchain-specific branches.
- Source-only releases remain valid; migration can proceed component by component.
- Consumer Composition Roots retain final installation, linking, integration tests, packaging and launch.
- Registry must add target selection, artifact retrieval, secure extraction, immutable replay, cache and edge-case conformance tests.

## Alternatives considered

### Product-specific package downloads in each consumer

Rejected as the general solution. It duplicates resolution, integrity, caching and replay semantics in every product. A consumer may still directly pin external SDKs that are not represented as Registry-managed components.

### Source-only Registry

Rejected for consumers whose component publishers provide ready-to-use packages; it forces repeated component builds on every machine.

### Registry builds downloaded source

Rejected. Registry is a delivery plane, not a build system or package-script runner. Each component repository owns build and publication.

### Silent source fallback

Rejected. A corrupt or unavailable selected binary must not cause an unexpected compiler/toolchain build on the user's machine.

## Boundaries

- **Spec:** owns the architecture, JSON Schemas, normative requirements and conformance vectors.
- **Registry:** implements generic resolution, retrieval, verification, safe extraction, manifest/replay and cache behavior.
- **Component repositories:** build, test, version and publish their own package assets and source metadata.
- **Product Composition Root:** chooses the target and delivery policy, stages dependencies, links components, runs product-level tests and produces the final executable/installer.

## References

- [ADR-0022 — Generic Consumer-Independent Registry](ADR-0022-minimal-static-release-catalog.md)
- [Immutable artifact delivery](../architecture/immutable-artifact-delivery.md)
- [Registry data contracts](../architecture/registry-contracts.md)
