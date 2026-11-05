# Changelog

All notable changes to this specification are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

The specification version is defined in docs/reference/status.md (SPEC-010). Component package releases and public contracts are versioned independently.

## [Unreleased]

### Changed

- Replace the CDIN-specific static-catalog proposal with generic, data-driven Component Orchestration: independent Product Definitions describe requirements; Registry resolves versions, tracks updates, collects exact component sources and prepares reproducible workspaces for any consumer.
- Clarify that CDIN owns product-specific integration, build, tests, packaging and launch, while Registry owns component discovery, release/version management, update handling, resolution and source collection.
- Update Registry architecture diagrams, CDIN composition-root responsibilities, README navigation and ADR-0022 to remove consumer-specific Registry logic and resolver/lockfile ownership from CDIN.

## [1.3.0] - 2026-11-04

### Added

- Accept and document the Runtime v1 ownership boundary across Kernel, Backend, Runtime, Frontend and CDIN composition.
- Define the Backend-owned PUC Lua 5.4 bridge and Runtime Host API boundary, including ownership, execution and lifecycle constraints, in alignment with ADR-0019.
- Establish the Runtime Host API 1.0.0 as a stable, normative contract.
- Define Host API compatibility rules and independent version ownership for Runtime package, Runtime Host API, Kernel ABI, Frontend Protocol and Extension Contract.
- Document opaque handles, native resource lifetime constraints, deterministic cleanup requirements and Backend-owned Lua execution boundary.
- Record Runtime v1 verification requirements and distinguish repository extraction, Host API contract stability and production integration readiness.

### Changed

- Promote approved Runtime requirements to ACCEPTED and retain implementation conformance as a separate release gate.
- Align Runtime component specification with ADR-0019 and record open migration and extension-loader decisions.
- Preserve accepted Frontend ADR-0020 and Kernel ADR-0021 decisions and their independent compatibility/versioning boundaries.
- Clarify that Host API contract stability does not establish production integration readiness or whole-product conformance.

## [1.2.0] - 2026-11-03

### Added

- Add ADR-0021 recording owner-approved acceptance of Kernel ABI 1.1.0 implementation-backed behaviors.
- Record owner-approved Frontend decisions in ADR-0020, including TUI-first delivery, capability registry and presentation contracts.
- Define Frontend Protocol 1.0.0 as the accepted major-version schema.

### Changed

- Keep future Kernel and Unicode behaviors explicitly open or deferred.
- Distinguish accepted architecture from shipped implementation and synchronize component status documents.

