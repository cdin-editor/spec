# Registry data contracts

- **Status:** ACCEPTED
- **Contract baseline:** Registry data contracts `1.4.0`
- **Schema dialect:** JSON Schema Draft 2020-12
- **Implementation owner:** `cdin-editor/registry`

This page and the schemas under `schemas/registry/v1/` freeze the portable data boundary between Registry, component publishers and consumers. They do not prescribe implementation language, internal modules, hosting provider or service deployment.

## 1. Contract inventory

| Artifact | Direction | Canonical representation | Schema |
|---|---|---|---|
| Product Definition | Consumer → Registry | YAML 1.2 or JSON data model | [product-definition](../../schemas/registry/v1/product-definition.schema.json) |
| Catalog Index | Catalog source → Registry | JSON | [catalog-index](../../schemas/registry/v1/catalog-index.schema.json) |
| Component Release Metadata | Component publisher → Registry | JSON | [component-release](../../schemas/registry/v1/component-release.schema.json) |
| Resolved Manifest | Registry → consumer | JSON | [resolved-manifest](../../schemas/registry/v1/resolved-manifest.schema.json) |
| Resolution Report | Registry → caller | JSON | [resolution-report](../../schemas/registry/v1/resolution-report.schema.json) |
| Update Discovery Report | Registry → caller | JSON | [update-discovery-report](../../schemas/registry/v1/update-discovery-report.schema.json) |

The JSON data model is canonical. YAML 1.2 is an authoring convenience for Product Definitions only; it is parsed into the JSON data model before validation. Duplicate mapping keys, non-string mapping keys, custom YAML tags and non-JSON values are invalid. Catalog indexes, release metadata and Registry outputs are JSON.

Every document carries `schema_version`. The schemas in `schemas/registry/v1/` describe contract major version 1. Consumers reject unsupported major versions and ignore unknown optional fields within a supported major. Extension-specific data belongs under `extensions`; it has no Registry semantics unless a future contract explicitly assigns them.

## 2. Identity and version rules

- Component IDs are stable logical identities, not repository names, URLs, display names or consumer-specific aliases.
- Component IDs, variant IDs and source-unit IDs use lowercase ASCII letters and digits with dot and hyphen separators. Published IDs are immutable.
- An omitted variant normalizes to the literal ID `default` before lookup, dependency coalescing, conflict detection and manifest generation.
- Package and contract versions use Semantic Versioning 2.0.0. Package version, source revision and contract version are independent axes.
- Version constraints are one exact version (for example `1.2.3`, optionally prefixed by `=`) or a space-separated conjunction of comparators (for example `>=1.2.0 <2.0.0`). Supported comparators are `=`, `>`, `>=`, `<` and `<=`. OR, wildcards, partial versions, hyphen ranges, caret ranges and tilde ranges are outside contract 1.2.0.
- Build metadata does not affect SemVer precedence. Distinct candidates with equal precedence but different version strings or metadata identities are ambiguous and fail resolution; catalog order is never a tie-breaker.

### Runtime Extension Contract identity and version mapping

The Runtime Extension Contract has the canonical Registry identity
`org.cdin.runtime-extension-contract`. The Runtime component is its provider.
This ID is stable and is not a repository name, package name, display label or
consumer-defined alias. Registry treats it as an opaque contract identifier;
the semantics and compatibility policy are defined by the Runtime contract.

The Runtime Extension API currently exposes its compatibility label as
`major.minor` (the Runtime version descriptor carries `major` and `minor`).
For Registry Release Metadata, that two-field value is represented as SemVer
`major.minor.0`; therefore the existing Extension Contract label `1.0`
is published as `1.0.0`. The omitted patch field is zero, not an unspecified
version or a package version. A future non-zero patch version requires the
Runtime descriptor and the public Extension API version declaration to expose
that patch value before metadata may publish it.

Extension Contract version evolution follows SemVer 2.0.0: a major increment
is required for an incompatible change to existing extension-facing behavior;
a minor increment is for backward-compatible additions; and a patch increment
is for backward-compatible corrections that do not add or remove API
capabilities. A consumer that relies only on the baseline v1 API may require
`>=1.0.0 <2.0.0`; a consumer that relies on functionality introduced by a
later minor MUST raise its lower bound to that minor. Runtime MUST publish the
exact version it implements in `contracts.provides`, independently of its
own package version and the Backend-provided Runtime Host API version.

A Runtime Release Metadata declaration for the current Extension Contract is:

```json
{
  "contracts": {
    "provides": [
      {
        "contract_id": "org.cdin.runtime-extension-contract",
        "version": "1.0.0"
      }
    ],
    "requires": [
      {
        "contract_id": "org.cdin.runtime-host-api",
        "version_constraint": ">=1.0.0 <2.0.0"
      }
    ]
  }
}
```

This representation satisfies the metadata shape required by RT-012. It does
not by itself promote a Runtime package candidate to a stable package release
or claim that all legacy extension behavior has been migrated.

## 3. Product Definition

A Product Definition declares root component requirements and optional contracts supplied by the target environment. It is declarative data, never executable product logic.

```yaml
schema_version: "1.1.0"
product:
  id: com.example.editor
  name: Example Editor
components:
  - component_id: backend
    variant: default
    version_constraint: ">=2.0.0 <3.0.0"
  - component_id: frontend
    variant: tui
    version_constraint: "1.4.0"
environment_contracts:
  - contract_id: org.example.platform
    version: "1.0.0"
policy:
  allow_prerelease: false
resolution:
  delivery_mode: artifact
  target:
    os: linux
    architecture: x86_64
    abi: gnu-glibc-2.28
```

The optional `product.id`, `product.name` and `product.version` are provenance labels. They may be copied into outputs, but the Registry engine MUST NOT branch, select behavior, alter defaults or choose a catalog based on them. The Product Definition supplies required components, variants, constraints, external contract declarations and an optional explicit delivery policy. Omitting `resolution` preserves source delivery. Artifact modes require an exact target tuple; Registry never guesses a target or ABI.

`environment_contracts` identifies contracts supplied by the target environment rather than a Registry-managed component. A product may use this for a separately pinned platform SDK or an independently installed binary package; the Product Composition Root remains responsible for provisioning that package and ensuring the declared contract is actually present. It does not permit Registry to inspect or identify the consumer. Contract IDs are opaque namespaced strings; Registry compares declared versions and infers no semantics from their names.

## 4. Catalog Index and Component Release Metadata

A Catalog Index references immutable release-metadata documents; it does not mirror component source or become the authority for package contents. Each entry identifies a component, variant and package version, and supplies a URI plus SHA-256 digest for its Component Release Metadata. Registry verifies the digest over the exact fetched metadata bytes before parsing.

Identical entries may be deduplicated. Different metadata identities for the same `(component_id, variant, version)` are a catalog conflict.

Component Release Metadata is published and owned by the component maintainer. It declares stable component/variant IDs, package version and release status; one or more source units with repository URI and immutable full Git commit revision; optional immutable target-specific artifacts; required component dependencies; and contracts provided or required by the release. Artifact fields, target matching, package layouts, provenance and integrity semantics are normative in [Immutable target-specific artifact delivery](immutable-artifact-delivery.md).

One logical component may use multiple source units. Several variants may come from one repository. Several components may reference the same repository and revision. Registry does not assume a one-component-to-one-repository mapping.

A `withdrawn` release is ineligible for new resolution but remains identifiable for audit. Existing manifests are not silently rewritten; retrieval is blocked only by a separate explicit security policy.

### GitHub Release Sources (Registry Data Contract 1.4.0)

A Catalog Index schema 1.0.x uses `entries` (the existing static list of immutable metadata URI + SHA-256 identities). Catalog schema 1.1.x may instead use `release_sources` (stable repository-to-component/variant mappings). Component Release Metadata schema 1.2.x declares `publication`; Resolved Manifest and Resolution Report schema 1.2.x record discovered Release provenance. A Catalog Index uses exactly one of two publication models: `entries` or `release_sources`. A Catalog document MUST NOT contain both. A Release Source has a unique `source_id`, provider `github-releases-v1`, a canonical HTTPS GitHub repository URI, component ID, optional variant (default `default`) and optional tag prefix (default `v`). The same `(component_id, variant)` MUST NOT be declared more than once in the effective Catalog source set.

For every discovered Release, Registry requires the tag to equal `tag_prefix + metadata.version`. The expected metadata asset name is `<component-id>-<version>.json` for variant `default` and `<component-id>-<variant>-<version>.json` otherwise. A Release MUST contain exactly one asset with that name. The metadata document's `publication` object MUST state provider, publisher repository URI, tag, tag commit and metadata asset name. Exactly one source unit MUST identify the publisher repository, and its revision MUST equal the resolved tag commit.

Registry enumerates the complete published Release list with bounded pagination; it never calls GitHub's floating `/releases/latest` endpoint. Drafts are excluded. Prereleases are included only when the Product Definition allows them, and the GitHub prerelease flag must match SemVer. The tag reference is resolved to a commit, recursively peeling annotated tags with a finite cycle/depth guard. The API asset digest and size are mandatory and are checked against the exact downloaded bytes before JSON parsing. Missing/duplicate assets, absent digests, tag movement, source/repository mismatch, version mismatch and incomplete pagination are explicit failures.

Discovered release candidates enter the existing SemVer resolver. Highest compatible SemVer wins; publication timestamps and API ordering are not selection rules. Equal-precedence different release identities are ambiguous. The Resolved Manifest records the exact source ID, repository, Release ID/API URI, tag, tag commit and metadata asset filename/size; its existing release metadata URI/digest bind the exact asset bytes. Replay uses only that URI and digest and never re-discovers a replacement release. Offline resolution requires a verified cache snapshot for the exact Release Source identity.

The canonical generated metadata asset is a Release Asset, not a tracked source file. Component release workflows generate it after package assets and checksums exist. A per-version file under a component repository's `registry/releases/` directory is not required.

## 4.1 GitHub Release discovery failure identities

Implementations using `release_sources` MUST preserve distinct failure identities for at least:

- `RELEASE_SOURCE_INVALID`: malformed, duplicate or unsupported source declaration.
- `RELEASE_API_UNAVAILABLE`: GitHub API failure that is not a bounded retryable rate-limit response.
- `RELEASE_API_RATE_LIMITED`: the configured retry budget is exhausted for a GitHub API rate limit.
- `RELEASE_DISCOVERY_LIMIT`: pagination or response budget ended while more releases remain.
- `RELEASE_DISCOVERY_OFFLINE_MISS`: no verified discovery snapshot exists for the exact source identity.
- `RELEASE_TAG_INVALID` and `RELEASE_TAG_VERSION_MISMATCH`: tag cannot be parsed or does not equal configured prefix plus metadata SemVer.
- `RELEASE_METADATA_ASSET_MISSING` and `RELEASE_METADATA_ASSET_AMBIGUOUS`: expected metadata asset has zero or multiple matches.
- `RELEASE_METADATA_DIGEST_UNAVAILABLE`, `RELEASE_METADATA_DIGEST_MISMATCH` and `RELEASE_METADATA_SIZE_MISMATCH`: the release API does not expose a usable digest/size or downloaded bytes differ.
- `RELEASE_TAG_MOVED`, `RELEASE_SOURCE_REVISION_MISMATCH` and `RELEASE_REPOSITORY_MISMATCH`: immutable publication provenance does not match the current tag/source.
- `RELEASE_PRERELEASE_FLAG_MISMATCH`: GitHub Release prerelease state contradicts SemVer.
- `RELEASE_VERSION_AMBIGUOUS`: distinct release identities have equal SemVer precedence.

These failures are distinct from ordinary version-resolution conflicts. None may trigger source fallback or cause Registry to select from a partial candidate set.

## 5. Resolution semantics

Resolution is deterministic and independent of catalog ordering, repository names, publication timestamps and consumer identity.

1. Validate the Product Definition, every Catalog Index and all referenced release metadata before source collection.
2. Normalize omitted variants to `default`; collect root requirements and the transitive closure of required dependencies.
3. Coalesce requirements by `(component_id, variant)` and intersect every constraint imposed on that key.
4. Select exactly one active release per required key, satisfying all accumulated constraints and the prerelease policy.
5. Prereleases are excluded unless `allow_prerelease` is true. Stable candidates are ordered by SemVer precedence, highest first.
6. Missing candidates, empty constraint intersections, conflicting catalog metadata and equal-precedence ambiguity fail with structured conflicts. Registry never chooses the first catalog entry.
7. Each required contract must be satisfied by exactly one compatible provider declaration across selected releases and the declared target environment. A selected release may satisfy its own requirement when it declares a compatible provider for that contract; self-providers are not implicitly excluded.
8. Identical duplicate `(contract_id, version)` provider declarations within one selected release are coalesced. Each environment declaration is a distinct provider, and distinct compatible versions declared by one release are distinct providers. More than one compatible provider is ambiguous.
9. If no compatible provider exists, resolution fails as `CONTRACT_PROVIDER_MISSING`; the report distinguishes an absent declaration from declarations that exist but are version-incompatible.
10. The selected dependency graph must be acyclic. A cycle fails and the report identifies its exact path.
11. Output order is a deterministic topological order. Independent nodes at the same depth are ordered lexicographically by component ID, then variant ID.
12. After release selection, Registry applies the Product Definition delivery policy to each selected component/variant. Version/dependency/contract selection is unchanged. Artifact target selection follows exact OS/architecture/ABI matching, with only the explicit universal `any/any/none` target as a fallback. Ambiguous artifact matches fail; no catalog ordering or publication timestamp is a tie-breaker.
13. `artifact-or-source` falls back only when no compatible artifact is declared. A selected artifact that fails retrieval, size/digest validation, archive validation or extraction fails the operation and MUST NOT fall back to source.

Optional dependencies, feature negotiation, arbitrary solver plugins and consumer-specific compatibility callbacks are outside contract 1.3.0.

## 6. Source and artifact delivery workspace

In `source` mode, each source unit is retrieved at its declared full immutable Git commit object ID. Branch names, tags and other movable references are not valid resolved revisions. Full 40-character and 64-character hexadecimal object IDs are accepted; the retrieved commit must resolve to exactly that ID. In `artifact` mode, Registry retrieves the selected release asset by its exact URI and verifies its declared byte count and SHA-256 before safe extraction. In `artifact-or-source` mode, source collection is permitted only when no artifact matches the requested target; it is not a recovery path for a corrupt or unavailable selected artifact.

The Catalog Index digest protects static release metadata; for a discovered Release Source, the GitHub Release Asset API digest and exact asset size protect the fetched metadata bytes. Git object verification protects the declared source revision. Neither implies publisher identity or signed provenance.

The deterministic workspace layout is:

```text
prepared/
├── components/
│   └── <component-id>/
│       └── <variant-id>/
│           ├── sources/<source-unit-id>/   # source delivery only
│           └── package/                    # artifact delivery only
├── registry-manifest.json
└── resolution-report.json
```

Every source unit has its own declared path. Every selected artifact has one package path and exact artifact identity in the manifest. Physical cache deduplication is an implementation optimization and must not change manifest paths or visible contents. A declared subdirectory is a safe relative path inside the checked-out revision; absolute paths, parent traversal and escape from the source root are invalid.

The collector stages privately, verifies all revisions or artifact digests, safely materializes all selected content and validates the final layout before publishing the destination. Failure cannot leave a successful-looking partial workspace. Existing destinations are not implicitly overwritten. Registry does not run build scripts, package hooks or collected code.

Contract 1.2.0 does not automatically materialize Git submodules or Git LFS objects. Required content must be represented as separately declared source units or through a future explicit asset contract; Registry does not silently fetch unlisted content.

## 7. Resolved Manifest and Resolution Report

The Resolved Manifest records normalized roots, selected component IDs/variants/versions, release-metadata identities, effective delivery mode and target, resolved dependency edges and contract declarations. Source-delivered components record source repositories, exact revisions and workspace-relative source paths. Artifact-delivered components record the exact artifact ID, target, URI, format, byte count, SHA-256, layout, build provenance and extracted workspace-relative package path. Consumers do not rerun version or artifact selection to reproduce the selected graph.

A later catalog update creates a new resolution and manifest; it never mutates an existing manifest or prepared workspace. The manifest is the reproducibility record, not a mutable lockfile maintained by CDIN.

The Resolution Report explains success or failure. It records selected candidates and every applied version constraint. Each constraint identifies its target component/variant and whether it came from a Product Definition root or a dependency edge; dependency evidence identifies the requiring component, variant and selected release version.
Rejected candidates identify the component, variant and version, include the stable rejection reason, and preserve catalog/release-metadata provenance whenever that candidate has it. A candidate explored but abandoned because its downstream branch failed is recorded with reason code `BRANCH_CONFLICT` and the stable surfaced conflict code in `detail`. Conflict records identify involved component/variant nodes. Ambiguous-release conflicts include the full identities and provenance of the equal-precedence candidates. Contract-provider conflicts include the required contract ID and constraint plus every declared provider candidate, its contract version, origin, selected component release identity/version (when applicable) and compatibility result. An empty provider list means no declaration exists; a non-empty list with no compatible item means all declarations are incompatible.
Constraint evidence, candidate evidence and provider evidence use deterministic ordering: applied constraints sort by target component ID, variant, constraint text, source type and source identity; rejected candidates sort by component ID, variant, version, reason code and release provenance; provider candidates sort by origin, provider identity and version; involved nodes sort by component ID and variant. Duplicate entries remain duplicated where multiplicity is semantically significant. Evidence is scoped to the exact final failure branch represented by the surfaced conflict; evidence gathered only from other abandoned backtracking branches MUST NOT be aggregated into the report. The v1.1.0 schema defines closed conflict and rejected-candidate reason-code vocabularies. When a rejected candidate or a conflict's `candidate_evidence` contains `release_discovery`, the Resolution Report MUST use schema version `1.2.0`; ordinary conflicts without candidate evidence remain valid under `1.1.0`. The version gate MUST only inspect a conflict's candidate provenance when the `candidate_evidence` property is actually present.
A failed resolution produces neither a Resolved Manifest nor a published workspace.

Manifest generation is deterministic: set-like arrays are sorted by identity keys, and no timestamp, random identifier, absolute host path or catalog iteration order is embedded. JSON serialization for digesting or signing follows RFC 8785 (JSON Canonicalization Scheme). A detached digest may be calculated over canonical manifest bytes; it is not embedded in the document it hashes.

### Update Discovery Report

Update discovery is a read-only comparison operation over three independently identified inputs: a previously verified Resolved Manifest, the exact current Product Definition bytes and one or more freshly loaded Catalog Indexes with their verified SHA-256 identities. The Registry resolves the current Product Definition against the current Catalogs through the same generic Resolver used by normal resolution; it does not infer consumer identity or apply a separate update-selection algorithm.

The Update Discovery Report is a separate public JSON artifact validated against `update-discovery-report.schema.json`. It binds the exact historical Manifest SHA-256, Product Definition input SHA-256, current Catalog URI/digest identities and the complete current Resolution Report. Historical component selections and current candidates carry stable reason codes. The report is deterministic: Catalog references sort by Catalog ID, URI and digest; component decisions sort by component ID and variant; candidate decisions sort by component ID, variant, version, Catalog ID and metadata URI. It contains no timestamp or random identifier.

The operation MUST verify the historical Manifest before loading current Catalog state. It MUST NOT rewrite, replace or invalidate the historical Manifest or prepared Workspace. It MUST NOT collect Git sources or publish a Workspace. A withdrawal or identity change is reported as current evidence; it does not rewrite what the historical Manifest recorded. The report schema has its own `schema_version: "1.0.0"`; the Registry Data Contract baseline is `1.4.0`. Its `current_resolution` MUST validate as Resolution Report schema `1.1.0` for ordinary/static evidence or `1.2.0` when GitHub Release discovery provenance is present.

## 8. Security and trust boundary

Product Definitions, Catalog Indexes, release metadata and package archives are untrusted data. They are parsed and validated, never evaluated as scripts, templates or plugins. Artifact downloads require HTTPS, configured host/redirect policy, byte-count and SHA-256 verification. Extraction rejects traversal, links, special files, ambiguous/colliding paths and configured resource-limit violations. Registry stages privately and atomically publishes only a fully validated workspace; it never executes package scripts or source code.

Repository authentication, credential storage, publisher signing, trust roots, vulnerability policy and security-withdrawal overrides are deployment/security concerns. A SHA-256 match proves byte integrity relative to the pinned metadata, not publisher identity or binary safety. Registry MUST NOT claim signature verification unless an explicit trust policy validates it. These concerns must not be improvised as product-specific resolver logic.

## 9. Repository boundary

The implementation belongs in the independent `cdin-editor/registry` repository, which owns the generic engine, entry points, internal modules, executable tests, conformance fixtures and release process. This Spec owns the architecture and public data contracts only.

Registry is a build-time/delivery-plane tool. CDIN and unrelated consumers invoke it through an implementation-selected external tool or library boundary. No product component links to Registry or depends on it at runtime. Each consumer owns configuration, integration, builds, tests, packaging and launch.

## 10. Deliberately not frozen

Implementation language/toolchain, internal module boundaries, CLI command names and flags, catalog distribution/update transport, local cache and garbage collection, parallel downloads, authentication UX, signing/trust, API service deployment and release automation belong to the next repository-design phase. They can be decided without changing this data contract. Changes to public schemas, resolution behavior, source identity or workspace/manifest semantics require a Spec change. Registry Data Contract versions follow SemVer independently of the Spec repository release: additive fields and compatible delivery semantics increment the contract minor version; compatible errata that do not alter schemas or behavior increment the patch version; breaking wire-format or resolution-semantic changes increment the major version. Contract 1.3.0 adds artifact delivery while retaining the 1.x source-only behavior as the default. Contract 1.4.0 adds generic GitHub Release Sources, publication provenance and immutable discovery/replay semantics.
Resolution Reports MUST include `applied_constraints` (an empty array is valid). Reports without GitHub Release provenance MUST declare `schema_version: "1.1.0"`; reports whose rejected-candidate or conflict candidate evidence contains `release_discovery` MUST declare `schema_version: "1.2.0"`. These are additive versions within contract major version 1. Update Discovery Reports MUST declare `schema_version: "1.0.0"` and validate against the dedicated Update Discovery Report schema; its `current_resolution` uses the matching Resolution Report version.

The artifact-specific requirements REG-028 through REG-041 are normative within contract 1.3.0 and are listed in [Immutable target-specific artifact delivery](immutable-artifact-delivery.md).

## 11. Normative Registry requirements

- **REG-001** `ACCEPTED` The Registry MUST consume Product Definitions as declarative data and MUST NOT evaluate them as executable product logic. — *Verify:* STATIC
- **REG-002** `ACCEPTED` The Registry MUST NOT branch on product identity, product name or consumer-specific identifiers when resolving or collecting components. — *Verify:* CONF
- **REG-003** `ACCEPTED` Component, variant and source-unit IDs MUST use stable lowercase ASCII identifiers and MUST NOT be derived from repository names. — *Verify:* CONF
- **REG-004** `ACCEPTED` An omitted variant MUST normalize to the `default` variant before catalog lookup and dependency resolution. — *Verify:* CONF
- **REG-005** `ACCEPTED` Every public Registry document MUST declare a supported `schema_version` and be validated against its versioned JSON Schema. — *Verify:* CONF
- **REG-006** `ACCEPTED` Component package versions and contract versions MUST follow Semantic Versioning 2.0.0. — *Verify:* CONF
- **REG-007** `ACCEPTED` Version constraints MUST use only exact versions or conjunctions of the documented `=`, `>`, `>=`, `<` and `<=` comparators in contract 1.1.0. — *Verify:* CONF
- **REG-008** `ACCEPTED` Resolution MUST include the transitive closure of every selected release's required component dependencies. — *Verify:* CONF
- **REG-009** `ACCEPTED` A successful resolution MUST select exactly one release for each normalized `(component_id, variant)` key. — *Verify:* CONF
- **REG-010** `ACCEPTED` All constraints on the same normalized component key MUST be intersected; an empty intersection MUST produce a structured resolution failure. — *Verify:* CONF
- **REG-011** `ACCEPTED` Candidate selection MUST be deterministic and MUST NOT depend on catalog ordering, repository naming or publication timestamps. — *Verify:* CONF
- **REG-012** `ACCEPTED` Prerelease releases MUST be excluded unless the Product Definition explicitly enables prerelease selection. — *Verify:* CONF
- **REG-013** `ACCEPTED` Withdrawn releases MUST remain identifiable in verified Catalog candidate history for audit, MUST be rejected for new resolution, and MUST remain visible in update-discovery reports without rewriting historical Manifests. — *Verify:* CONF
- **REG-014** `ACCEPTED` A dependency cycle MUST fail resolution and the report MUST identify the cycle path. — *Verify:* CONF
- **REG-015** `ACCEPTED` Every required contract MUST be satisfied by a version-compatible declared provider in the selected component set or target environment. — *Verify:* CONF
- **REG-016** `ACCEPTED` A required contract with no compatible provider or more than one provider MUST fail resolution as missing or ambiguous. — *Verify:* CONF
- **REG-017** `ACCEPTED` A Component Release MUST support one or more declared source units and MUST NOT assume a one-component-to-one-repository mapping. — *Verify:* CONF
- **REG-018** `ACCEPTED` Every source unit MUST identify a full immutable Git commit object ID; branch and tag names MUST NOT be accepted as resolved revisions. — *Verify:* CONF
- **REG-019** `ACCEPTED` Registry MUST verify Catalog Index metadata digests before parsing the referenced release metadata. — *Verify:* CONF
- **REG-020** `ACCEPTED` Source subdirectories and workspace paths MUST be relative, normalized and confined to their declared source or workspace root. — *Verify:* CONF
- **REG-021** `ACCEPTED` The prepared workspace MUST follow the deterministic component/variant/source-unit layout defined by this contract. — *Verify:* CONF
- **REG-022** `ACCEPTED` Source collection MUST publish a workspace only after all selected sources have been retrieved and verified; failure MUST NOT publish a partial successful workspace. — *Verify:* INTEG
- **REG-023** `ACCEPTED` The Resolved Manifest MUST record exact selected releases, source revisions, dependency edges, contract declarations and workspace-relative source paths. — *Verify:* CONF
- **REG-024** `ACCEPTED` Manifest generation MUST be deterministic and MUST NOT include wall-clock timestamps, random identifiers or absolute machine paths. — *Verify:* CONF
- **REG-025** `ACCEPTED` A failed resolution MUST produce structured conflict and rejected-candidate details and MUST NOT produce a successful manifest. — *Verify:* CONF
- **REG-026** `ACCEPTED` Registry metadata MUST be treated as untrusted data and MUST NOT be executed as code, scripts, templates or plugins. — *Verify:* FUZZ
- **REG-027** `ACCEPTED` Update discovery MUST verify the historical Manifest before loading current Catalogs, resolve current state through the generic Resolver, and emit a deterministic schema-validated report bound to the exact historical Manifest SHA-256, exact Product Definition input SHA-256 and verified current Catalog Index identities. It MUST record stable historical-selection and candidate-decision reason codes, MUST NOT rewrite or invalidate the historical Manifest or prepared Workspace, and MUST NOT collect source or publish a Workspace. — *Verify:* CONF

- **REG-047** A Catalog Index MUST declare either static release-metadata entries or GitHub Release Sources; it MUST NOT mix the two models, and each Release Source MUST identify one stable component/variant-to-repository mapping. — *Verify:* CONF
- **REG-048** A GitHub Release publisher MUST generate metadata from the exact tag commit and upload one canonical variant-specific JSON Release Asset; it MUST NOT require a tracked per-version metadata file in the source repository. — *Verify:* INSPECT
- **REG-049** Registry MUST enumerate the complete eligible GitHub Release candidate set with bounded pagination and MUST fail rather than resolve from a truncated set; it MUST NOT use the floating GitHub `latest` endpoint. — *Verify:* INTEG
- **REG-050** Registry MUST verify that a discovered release tag, SemVer, GitHub prerelease flag, publisher repository, tag commit and publisher source-unit revision agree. Annotated tags MUST be resolved to their commit, and moved tags MUST fail closed. — *Verify:* CONF
- **REG-051** Registry MUST require the GitHub metadata asset's published SHA-256 digest and byte size, verify the exact downloaded bytes before parsing, and reject missing or ambiguous metadata assets. — *Verify:* INTEG
- **REG-052** Dynamic release candidates MUST use the existing deterministic SemVer resolver; GitHub publication time, API order and page order MUST NOT be tie-breakers. Equal-precedence distinct release identities MUST fail as ambiguous. — *Verify:* CONF
- **REG-053** A Resolved Manifest using GitHub discovery MUST preserve the exact Release Source ID, repository, Release ID/API URI, tag, tag commit, metadata asset name/URI/size/digest; replay MUST use only that immutable identity. — *Verify:* INTEG
- **REG-054** Release discovery caches MUST be keyed by exact source/release/tag/commit/metadata digest identity; offline discovery MUST use only a previously verified snapshot and MUST NOT silently query or substitute a newer release. — *Verify:* INTEG
- **REG-055** Release Source IDs MUST be unique within an effective Catalog source set, and each normalized `(component_id, variant)` MUST have at most one Release Source. Duplicate source IDs or component/variant mappings MUST fail semantic validation. — *Verify:* CONF
