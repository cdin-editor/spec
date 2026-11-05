# ADR-0022: Data-driven Component Orchestration

- **ID:** ADR-0022
- **Status:** PROPOSED
- **Decision scope:** Generic Registry architecture, Product Definition input and product/Registry responsibility boundaries

## Context

CDIN is assembled from independently developed and versioned components. Repository topology may evolve: one logical component may split across multiple repositories, a repository may publish multiple variants, and a product may need only a subset of available variants.

A static catalog that merely lists release URLs leaves version selection, update management, dependency resolution and source collection with each consumer. Putting those responsibilities inside CDIN couples its build system to repository layouts and package lifecycle concerns. Hardcoding CDIN-specific product identities or rules inside Registry makes Registry non-reusable.

## Decision

**Proposal: define Registry as a consumer-independent, data-driven Component Orchestration system.**

Registry owns component discovery, release/version metadata, update tracking, dependency and compatibility resolution, source collection, immutable revision verification, and preparation of a reproducible workspace plus resolved manifest.

A separate declarative **Product Definition** supplies component IDs, variants, version constraints and other generic requirements. It is data, not executable product logic. Its storage location is independent and remains open; this ADR does not require a new repository.

> **Registry must understand requirements, not consumer identity.**

The same Registry must serve CDIN Editor and a future unrelated product by consuming different Product Definitions. Supporting a new consumer must not require consumer-specific code, product-ID conditionals or custom workflows in the Registry engine.

### Responsibilities

- **Component repositories:** own source, package versions, tags, release notes, component tests and publication workflows.
- **Product Definition:** declares logical components, variants, version constraints and product composition requirements.
- **Registry:** manages catalog, release/version lifecycle, update discovery, dependency resolution, compatibility metadata evaluation, source collection and workspace preparation.
- **CDIN:** consumes the prepared workspace and manifest, performs product-specific configuration and integration, builds, runs product/integration tests, packages and launches the editor.
- **Spec:** defines normative contracts and architecture; it does not execute Registry operations or contain component source.

### Product Definition and generic resolution

A Product Definition is declarative data. It may request Frontend variants cli and gui-sdl without selecting other available variants. Registry resolves those requirements against component metadata and release records.

A logical component need not map one-to-one to a repository. Metadata may describe multiple source units for a component or multiple variants published from one repository. Repository splits and variant growth must not require product-specific Registry logic.

Registry may evaluate declared version constraints, dependencies and contract metadata. It cannot prove that a set works as an integrated product; CDIN owns those tests.

### Workspace handoff

Registry returns:
- a deterministic prepared workspace containing the exact source trees required by the resolved Product Definition;
- a resolved manifest recording component IDs, variants, package versions, source repositories, immutable full commit revisions and available integrity metadata;
- a resolution report describing selected candidates, applied constraints and warnings.

A list of URLs and SHAs alone is not the handoff contract: Registry performs source collection before returning the prepared workspace. CDIN does not fetch component sources or resolve versions.

The workspace layout and manifest schema are implementation contracts to be specified before Registry implementation; examples are not finalized schemas.

### Versioning and updates

Registry owns release discovery, version selection and update tracking. Product Definitions supply constraints or update policy as data. A new release creates a new resolution candidate; it never mutates an existing workspace or manifest. Previous manifests retain exact revisions for reproducibility, subject to source availability and explicit security withdrawal policy.

CDIN does not maintain component versions, an updater, a dependency solver or a component lockfile. The Registry-produced resolved manifest is the reproducibility record for a prepared set.

### Product integration and verification

Registry checks metadata consistency, declared dependency constraints and compatibility declarations. CDIN remains responsible for product-specific configuration, integration, build, contract/integration tests, packaging and launch. A Registry resolution is a candidate input, not proof that the assembled product works.

### Architectural placement and complexity limits

Registry belongs to the component delivery and orchestration plane, outside product runtime and product build implementation. No component links to Registry at runtime. Product-specific needs enter only through Product Definitions and generic component metadata; Registry must not contain product-ID conditionals.

The proposal does not require microservices, a database, a permanently running API, a custom artifact host, a custom package format or a separate repository for every Registry responsibility. The first implementation may be one generic CLI/engine with version-controlled metadata, declarative definitions and deterministic workspace/manifest output.

## Consequences

- Component lifecycle and source collection are centralized rather than reimplemented by every consumer.
- CDIN is limited to product composition, integration, build, tests, packaging and launch.
- Registry can serve unrelated products without knowing their identities.
- Component repository splits and additional variants are represented through metadata rather than consumer-specific code.
- Exact resolved manifests make prepared workspaces auditable and reproducible.
- Generic metadata, Product Definition and workspace/manifest contracts must be defined before implementation.
- End-to-end compatibility remains the responsibility of each consuming product's integration tests.

## Alternatives considered

### CDIN-owned discovery and dependency resolution

Rejected. It couples CDIN to component repository topology, version/update management and source collection.

### CDIN-specific Registry rules

Rejected. Product identity conditionals and hardcoded component lists prevent reuse by unrelated consumers.

### Static catalog only, with each consumer doing the rest

Not selected. It leaves version selection, updates, dependency resolution and source collection duplicated in consumers.

### Full artifact-hosting package manager

Rejected for the initial architecture. Component repositories remain authoritative for source and releases; Registry collects source when preparing a workspace rather than becoming a second artifact store.

## Open implementation questions

- Exact Product Definition schema and ownership/location.
- Generic component metadata schema, including multiple source units and variants.
- Dependency constraint syntax and resolution policy.
- Workspace layout, lifecycle, caching and cleanup.
- Resolved manifest schema and integrity fields.
- How Registry update candidates are requested or scheduled.

These are implementation contracts to resolve before implementation; they do not change the responsibility boundaries above.

## References

- [Registry architecture](../architecture/registry.md)
- [System maps](../architecture/system-maps.md)
- [Architecture overview](../architecture/overview.md)
- [CDIN composition root](../components/cdin.md)
- [ADR-0014 — No shared or common repositories](ADR-0014-no-shared-repositories.md)
