# Registry architecture

- **Status:** ACCEPTED — [ADR-0022](../adr/ADR-0022-minimal-static-release-catalog.md).
- **Implementation status:** NOT IMPLEMENTED in this Spec repository; implementation belongs to [`cdin-editor/registry`](https://github.com/cdin-editor/registry).
- **Architecture:** Generic Consumer-Independent Component Registry.
- **Contract baseline:** `1.3.0`; see [Registry data contracts](registry-contracts.md).

## 1. Purpose

Registry is an independent delivery-plane system that discovers component releases, resolves declared requirements and target-compatible package artifacts, collects exact source revisions or verified package bytes, and prepares reproducible workspaces. It serves unrelated products through the same generic engine and public data contracts.

> **Registry must understand requirements, not consumer identity.**

A new consumer supplies a Product Definition and applicable target-environment contracts. It does not require a product-specific Registry code path, plugin, identifier conditional or workflow.

## 2. Ownership and boundaries

| Owner | Owns | Does not own |
|---|---|---|
| Component repository | Component source, package version, release metadata, tags, component tests and publication | Product-wide version selection |
| Catalog publisher | Catalog Index entries referencing immutable release metadata | Component source or package contents |
| Product Definition | Root component requirements, variants, constraints and environment contracts | Resolver algorithm or source retrieval |
| Registry | Catalog ingestion, metadata validation, version/dependency/contract resolution, update discovery, source collection, verification, workspace and manifest production | Product-specific integration or product builds |
| Consumer (CDIN or another product) | Product policy, configuration, integration, builds, tests, packaging and launch | Catalog, dependency solving or source collection |
| Spec | Architecture, schemas, normative requirements and ADRs | Registry implementation or runtime execution |

Component repositories remain authoritative for source and releases. A Catalog Index references immutable Component Release Metadata; it is not a second source of truth for component code.

Registry is an independent infrastructure repository, not a catch-all shared-code repository. It owns one responsibility: component delivery and orchestration. No component links to Registry or depends on it at runtime.

## 3. Public inputs and outputs

The public data boundary consists of six versioned artifacts:

1. **Product Definition:** requested components and target-environment contracts.
2. **Catalog Index:** references to release metadata and SHA-256 digests.
3. **Component Release Metadata:** component/variant/version, source units, optional target-specific artifacts, dependencies and contract declarations.
4. **Resolved Manifest:** selected graph, metadata identities, source revisions and workspace paths.
5. **Resolution Report:** selected/rejected candidates, warnings and conflicts.
6. **Update Discovery Report:** a deterministic, schema-validated comparison of a verified historical Manifest with current Product Definition and Catalog state.

Their canonical schemas and validation rules are in [Registry data contracts](registry-contracts.md) and `schemas/registry/v1/`. These contracts do not prescribe a hosting provider, implementation language or CLI syntax.

## 4. Resolution model

The resolver expands Product Definition roots into the transitive closure of required dependencies and normalizes omitted variants to `default`. After selecting exact component releases, it applies the Product Definition's explicit `source`, `artifact`, or `artifact-or-source` delivery mode and exact target tuple. It intersects version constraints for each component/variant key, filters withdrawn and disallowed prerelease releases, and selects the highest compatible Semantic Version.

Compatibility includes component dependencies and explicit contract declarations. Each required contract has exactly one compatible provider in the selected component set or declared target environment. Missing, incompatible or ambiguous providers fail.

Resolution is deterministic. Catalog order and publication timestamps are not selection rules. Cycles, empty constraint intersections, conflicting metadata and equal-precedence ambiguous releases are explicit errors.

## 5. Source collection and handoff

Registry either collects each selected source unit at its immutable full Git commit revision or retrieves and safely extracts one exact target-compatible artifact for each selected component/variant. A component may map to multiple repositories, and a repository may contribute source to multiple components or variants. Workspace paths derive from stable component, variant and source-unit IDs, not repository names.

A successful prepare operation publishes a complete workspace, Resolved Manifest and Resolution Report. Artifact manifests bind the exact asset URL, digest, target, provenance and extracted package path; source fallback is explicit and never hides an integrity failure. The manifest records enough information to reproduce the exact selected graph without re-running version selection. A new release creates a new resolution; existing manifests and workspaces are not silently changed. Update discovery is a separate read-only report operation: it verifies the historical Manifest first, resolves current state through the generic Resolver, and records historical/current selection decisions without collecting sources or publishing a Workspace.

Registry does not run component build scripts or perform product integration. CDIN consumes the prepared input and performs configuration, build, product tests, packaging and launch.

## 6. Operating model

The accepted architecture is a locally invocable engine with entry points chosen by implementation. It does not require a permanently running service, database, microservices, custom artifact host or custom package format.

The implementation repository owns its engine, CLI or API entry point, internal modules, executable tests, conformance fixtures, cache policy and release process. Language/toolchain, CLI command surface, catalog distribution, cache lifecycle and service deployment remain repository-design choices.

## 7. Security and reproducibility

Registry treats declarative inputs as untrusted data, validates them before collection and never evaluates metadata as code. It retrieves only declared source units and exact commit revisions, verifies release-metadata digests, and stages workspace publication so failed collection cannot look successful.

Manifest output is deterministic and uses workspace-relative paths. Update Discovery Reports bind the exact historical Manifest and Product Definition input digests plus current Catalog identities; they contain stable reason codes and never mutate historical artifacts. Immutable Git revisions and SHA-256 metadata digests do not by themselves establish signed publisher provenance, vulnerability scanning or security-policy overrides.

## 8. Non-goals

Registry is not a product build system, package script runner, Runtime dependency, source-hosting service, component release authority, consumer-specific plugin system or generic shared-utilities repository. It does not replace component tests or consumer-side integration tests.

## References

- [ADR-0022 — Generic Consumer-Independent Registry](../adr/ADR-0022-minimal-static-release-catalog.md)
- [ADR-0014 — No catch-all shared repositories](../adr/ADR-0014-no-shared-repositories.md)
- [Registry data contracts](registry-contracts.md)
- [Repository topology](repositories.md)
- [System maps](system-maps.md)
