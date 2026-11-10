# Changelog

All notable changes to this specification are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

The specification version is defined in `docs/reference/status.md`
(SPEC-010). The Kernel package release version is tracked independently
from the public Kernel ABI and the Spec release or compatibility target.

## [1.5.0] - 2026-11-10

### Accepted contracts

- Accept ADR-0028: GitHub Release metadata discovery. Component Release Metadata is generated from the exact tag commit and published as a Release Asset; a tracked per-version JSON file is no longer required.
- Extend Registry Data Contract to 1.4.0 with one-time GitHub Release Source declarations, complete paginated discovery, exact tag/commit/metadata-asset verification, deterministic SemVer selection and immutable Manifest replay.
- Preserve the existing static Catalog entries model as a backward-compatible alternative to dynamic GitHub Release Sources.

### Added

- Add Catalog Index schema support for stable component/variant Release Sources and generated metadata asset discovery.
- Add Component Release Metadata publication provenance and Resolved Manifest Release ID/tag/commit/asset evidence.
- Add positive and negative GitHub Release discovery conformance cases for tag mismatch/movement, duplicate/missing assets, digest failures, prerelease policy, pagination limits, SemVer ambiguity, offline cache and exact replay.

### Changed

- Advance the Registry Data Contract baseline from 1.3.0 to 1.4.0 and the Spec release from 1.4.0 to 1.5.0.
- Keep GitHub publication time and API order as provenance only; SemVer precedence remains the deterministic selection rule.



### Accepted contracts

- Accept ADR-0023, IME Composition v1: capability-gated, client-local preedit state and exact-once committed-text semantics, with cancellation and stale-context rules.
- Accept ADR-0024, PaneTree Splitter Resize v1: stable semantic split identity, Driver-authorized ratio changes, revision checks and atomic UI projection requirements.
- Add shared positive/negative conformance fixtures for IME lifecycle and nested PaneTree splitter resizing; component implementations remain separately release-gated.
- Accept ADR-0026, Semantic UI Presentation: revision-pinned, capability-negotiated presentation payloads with bounded styles, panels and prompts.
- Accept ADR-0027, Byte-Anchored Visible Line Windows: byte-offset anchors, exact document revision checks and negotiated line-window semantics.

### Added

- Extend Registry Data Contracts to baseline 1.3.0 with immutable target-specific package artifacts, explicit source/artifact delivery modes, ABI-aware deterministic target selection, verified download and safe extraction, replay and cache identity, and positive/negative security conformance vectors.
- Add ADR-0025 accepting generic artifact delivery while preserving Registry's consumer-independent boundary and source-only compatibility.
- Extend Product Definition, Component Release Metadata, Resolved Manifest and Resolution Report JSON Schemas for explicit target/delivery identities and stable artifact-selection conflict codes.
- Extend Registry Data Contracts to baseline 1.1.0 with fully sourced applied constraints, candidate provenance, structured contract-provider evidence, closed conflict/rejection reason codes and explicit self-provider semantics.
- Extend Registry Data Contracts to baseline 1.2.0 with a dedicated, deterministic Update Discovery Report schema bound to historical Manifest, Product Definition and current Catalog identities; define immutable withdrawal/update audit semantics without changing historical manifests or workspaces.
- Accept ADR-0022 as the generic, consumer-independent Registry architecture and align ADR-0014 so a cohesive infrastructure system is distinguished from a catch-all shared-utilities repository.
- Maintain the versioned Registry v1 JSON Schemas for Product Definitions, Catalog Indexes, Component Release Metadata, Resolved Manifests, Resolution Reports and Update Discovery Reports; the Resolution Report schema remains at 1.1.0 while Update Discovery Report is introduced at 1.0.0.
- Define deterministic SemVer/dependency/contract resolution, immutable source identity, staged workspace publication and manifest reproducibility requirements.
- Record `cdin-editor/registry` as the independent implementation repository; keep implementation language, internal modules, CLI syntax, catalog distribution, cache policy and service deployment for its repository-design phase.

### Changed

- Align `cdin.ui-model.v1` split-ratio constraints with accepted ADR-0024: inclusive Runtime range `[0.1,0.8999]`, exact basis-point projection and rejection instead of silent clamping.

- Refresh Backend requirement evidence anchors to the standalone repository layout and synchronize the ABI compatibility table with the current Spec release version (`1.4.0`).

- Reconcile the repository inventory with the extracted standalone Backend repository and distinguish repository existence from completion of the CDIN Composition Root migration.

- Align Registry architecture, repository topology, system maps, overview, ADR index, documentation navigation and conventions with the accepted responsibility boundaries.
- Preserve the core invariant: Registry understands requirements, not consumer identity; a new consumer supplies data and does not require product-specific Registry code.
- Clarify that Registry is a build-time/delivery-plane tool. Consumers retain integration, build, product tests, packaging and launch.

## [1.3.0] - 2026-11-04

### Added

- Accept and document the Runtime v1 ownership boundary across Kernel,
  Backend, Runtime, Frontend and CDIN composition.

- Define the Backend-owned PUC Lua 5.4 bridge and Runtime Host API
  boundary, including ownership, execution and lifecycle constraints,
  in alignment with ADR-0019.

- Establish the Runtime Host API 1.0.0 as a stable, normative contract.
  Define descriptor negotiation, required services, document operations,
  snapshots, transactions, notifications, search, UI publication, logging,
  error identities, ownership rules and owner-thread constraints.

- Define Host API compatibility rules: compatible implementations share
  the same major version and satisfy the consumer's minimum minor-version
  requirement. Compatible additive changes may be introduced within the
  same major version; breaking changes require a major-version increment.

- Define Runtime v1 responsibilities for document clients, commands,
  keymaps, logical views, syntax policy, semantic UI state and extension
  lifecycle management.

- Establish independent version ownership for the Runtime package,
  Runtime Host API, Kernel ABI, Frontend Protocol and Extension Contract.

- Document opaque handles, native resource lifetime constraints,
  deterministic cleanup requirements and the Backend-owned Lua execution
  boundary.

- Record Runtime v1 verification requirements and distinguish repository
  extraction, Host API contract stability and production integration
  readiness as separate concerns.

### Changed

- Promote the approved Runtime requirements RT-001, RT-003, RT-004,
  RT-006 through RT-010, RT-012, RT-015 and RT-016 to `ACCEPTED`.

- Accept the Host API 1.0.0 contract freeze under RT-010 and align its
  normative definitions with the Backend and Runtime specifications.

- Retain RT-011 as pending implementation conformance. The Host API
  contract defines stable Kernel-status identity and typed Lua error
  details, but production adapter conformance still requires verification
  against the required error-mapping vectors.

- Retain RT-020 and RT-021 as `PROPOSED` pending completion of the exact
  legacy API inventory and corresponding migration parity tests.

- Align the Runtime component specification with ADR-0019 and mark
  OD-32 as resolved without reopening the approved Lua bridge design.

- Accept extension document isolation and contract-change governance
  (EXT-004 and EXT-032), together with independent Extension Contract
  versioning (EXT-040).

- Keep extension manifest compatibility details and default-field
  behavior as pre-release loader decisions rather than silently treating
  them as finalized requirements.

- Resolve OD-15 and OD-16 by specifying explicit ownership and
  persistence responsibilities across Kernel, Backend and Runtime.

- Keep Regex support, malformed UTF-8 conformance vectors, Kernel anchors,
  search normalization, hot-swap behavior and parallel mutation explicitly
  open or deferred as recorded in the relevant specification sections.

- Update migration phases to reflect the extracted Runtime repository
  while retaining the remaining Host API, integration and migration gates.

- Align system maps, repository inventory, component descriptions and
  glossary terminology with the accepted Runtime v1 architecture and
  independent version boundaries.

- Preserve accepted Frontend ADR-0020 and Kernel ADR-0021 decisions and
  their independent compatibility and versioning boundaries.

- Record the Runtime package as `1.0.0-rc.1`, independently of the stable
  Runtime Host API contract version `1.0.0`.

- Keep production Lua C bridge verification, native lifecycle behavior,
  complete error-mapping conformance, RT-013 extension-loader semantics
  and RT-020/RT-021 migration parity as outstanding evidence or scope
  decisions before declaring the Runtime package stable.

- Clarify that Host API contract stability does not establish production
  integration readiness or whole-product conformance.

## [1.2.0] - 2026-11-03

### Added

- Add ADR-0021 recording the owner-approved acceptance of Kernel ABI 1.1.0 implementation-backed behaviors.
- Accept the Kernel ABI 1.1.0 behaviors that are implemented and covered by the public header, source and conformance vectors in Kernel package 1.2.1.
- Record the owner-approved Frontend decisions F-01..F-13 in ADR-0020, including one Frontend repository, TUI-first delivery, capability registry, Lua/native ownership, typed UI options, text presentation and terminal lifecycle.
- Define Frontend Protocol 1.0.0 as the accepted major-version schema with nullable `active_view` and typed `ui.options`.

### Changed

- Keep Regex, nested transactions, Kernel anchors/markers, parallel mutation, Unicode normalization profiles and non-interactive CLI in their future/open/deferred states.
- Distinguish accepted architecture from shipped implementation: the Backend checkout still validates Protocol 0.2.0 and requires an upgrade before claiming 1.0.0 conformance.
- Synchronize the Kernel requirements, Open Decisions Register, Frontend component and release inventory.


## [1.1.0] - 2026-10-20

### Added

- Add layered system maps covering the target system topology, dependency ownership, the end-to-end edit path, application startup/shutdown, and independent version labels.
- Clarify the roles and boundaries of `cdin`, `cdin-x`, frontend, Frontend Protocol, backend, Lua runtime, Runtime Host API, kernel host adapter, C ABI, `cdin-kernel`, and the Spec repository.
- Document the Runtime Host API and Lua-to-native bridge as open integration decisions; Lua C API, LuaJIT FFI, and MetaCall remain options rather than mandatory dependencies.
- Add a cross-repository synchronization report for `cdin-kernel` package `1.1.0`.
- Add `scripts/spec_report.py` to summarize unique requirement statuses, ADRs, open decisions, document inventory, diagrams and version labels.
- Add a tag-triggered GitHub Release workflow that combines the generated Spec summary with the exact version's Changelog entry.

### Changed

- Record Spec release `1.1.0` while explicitly retaining the kernel's declared Spec compatibility target `1.0.0` and public C ABI `1.0.0`. The Spec release number does not imply that the kernel implements the proposed runtime, backend, or frontend integration.
- Align architecture, status, and release documentation with the current kernel package: its internal literal-search fast paths do not introduce a new public complexity guarantee or change the ABI contract.
- Distinguish the current implementation from target architecture throughout the diagrams and component descriptions.
- Keep GitHub Actions release-only: publish on a pushed `vX.Y.Z` tag, without per-push or pull-request validation jobs. Treat generated counts as release metadata, not as a pass/fail quality gate.

### Removed

- Remove `scripts/check.py` and its structural-checking CI workflow. The Spec repository no longer runs automated link, index, reference or Mermaid validation.

### Fixed

- Fix the startup/compatibility/shutdown Mermaid sequence diagram by removing semicolons from message labels and making each shutdown action a separate, parser-safe message.
- Clarify that the kernel's graceful and abort shutdown mode values have the behavior documented for ABI `1.0.0`; the diagram's full application lifecycle remains a target requirement.
- Keep `docs/adr/` as the canonical decision directory and remove stale references to the former `docs/decisions/` path where present.

## [1.0.0] - 2026-10-14

First release.

### Added

#### Specification content (requirement/ADR/diagram counts are generated by `python3 scripts/check.py --stats`)

- **Architecture** (`docs/architecture/`): overview, repositories, module boundaries, the C ABI
  rules, the Frontend Protocol, concurrency, lifecycles, the error model, the extension model and
  the migration plan from today's `cdin`.
- **Components** (`docs/components/`): one page each for the `cdin` composition root, backend,
  runtime, frontends, data, `cdin-x` and the specification itself.
- **Kernel** (`docs/kernel/`): the generic text engine in full: document model, text model (bytes
  first, regions of valid and raw UTF-8, line endings), positions and ranges, editing operations,
  transactions, undo and redo, change notifications and the search engine.
- **Testing** (`docs/testing/`): the conformance-suite design and the test matrix. The Spec repository remains design-only; separate `cdin-kernel` ABI 1.0.0 tests and their actual results are recorded in `docs/kernel/implementation-status.md`.
- **Decisions** (`docs/adr/`): ADRs and the Open Decisions Register (31 entries).
- **Reference** (`docs/reference/`): conventions (status labels, requirement IDs, verification
  methods, diagram vocabulary), the glossary, and the status report.

#### Structure and tooling

- `docs/README.md`: the index, with reader paths and a map from requirement-ID prefix to page.
- `scripts/check.py`: checks requirement IDs, relative links and anchors, ID/ADR/OD references,
  index completeness and diagram types; `--stats` prints the counts quoted in the status report;
  `--render` renders every diagram with the Mermaid CLI.
- `psx.yml`: repository-structure rules for a design-only repository. `src`, `tests`, package
  manager, lockfile, Makefile and Dockerfile are deliberately not checked; the `docs/` tree is
  declared under `custom`.
- GitHub: a CI workflow (`ci.yml`) running `scripts/check.py`; issue templates for specification
  defects and proposals; Dependabot for GitHub Actions; `CODEOWNERS`.
- A detailed pull-request template (`.github/PULL_REQUEST_TEMPLATE.md`): type of change and
  semantic-version impact, a requirement table (ID, change, status before and after, verification
  method), status-transition rules (owner approval, ADR, prototype spike), ADR and register
  checks, `EXISTING` anchors and contradictions with `cdin`, diagram rules, version and
  changelog, the checks that were and were not run, impact on implementers, and signed commits.
- Project files: `CONTRIBUTING.md`, `AGENTS.md`, `SECURITY.md` (scoped to design flaws in the
  contracts), `CODE_OF_CONDUCT.md`, `.editorconfig`, `.gitattributes`, a `.gitignore` for this
  repository, and the git-flow configuration in `.gix/config`.
- `LICENSE` (GPL-3.0-or-later, the same as `cdin`) and a `NOTICE` stating that no third-party
  source is bundled.

#### Diagrams

- One visual vocabulary for every diagram: components, contracts, external systems, `DEFERRED`
  items and outcomes (documented in `docs/reference/conventions.md`).
- Redrawn: system context, module boundaries (with the `ARCH-04x` rule on each dependency),
  undo and redo, the text-model example with byte offsets, and the migration phases with their
  gates. A "today" diagram was added beside the target topology.
- Sequence diagrams are numbered.

### Changed

- Documents moved to the layout above: `CONVENTIONS.md`, `GLOSSARY.md` and `STATUS.md` are now
  under `docs/reference/`; `docs/decisions/` is now `docs/adr/`. Requirement IDs, ADR numbers and
  open-decision numbers are unchanged, and every relative link was rewritten.
- The Spec baseline is `1.0.0`. The synchronized kernel implementation advertises ABI `1.0.0`; unimplemented components and unresolved lower-level decisions remain explicitly marked.
- Paths changed, so external links to `CONVENTIONS.md`, `GLOSSARY.md`, `STATUS.md` and
  `docs/decisions/` no longer resolve; documents in `cdin` and `cdin-x` that link here need updating.
- `docs/reference/status.md` documented the release-era `scripts/check.py` structural check; that historical tooling was removed in Spec 1.1.0 in favour of a report-only script.
