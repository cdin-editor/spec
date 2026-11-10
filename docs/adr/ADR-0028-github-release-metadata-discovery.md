# ADR-0028: GitHub Release metadata discovery

- **ID:** ADR-0028
- **Status:** ACCEPTED
- **Decision scope:** Component Release Metadata publication, discovery and immutable Registry resolution.

## Context

Component publishers currently commit a new JSON document for every package version under repository-local paths such as `registry/releases/backend-1.2.1.json`. A new component release therefore requires a source-tree change solely to add release metadata, followed by a separate Catalog edit that pins the new metadata URI and digest.

This duplicates the immutable GitHub Release identity, scatters generated release data through source repositories, and makes consumers maintain a per-version list even though the component's release already contains the authoritative tag, commit and assets. It also encourages treating a checked-in metadata file as current when the source tree and published release have moved on.

## Decision

GitHub Releases become a first-class, generic discovery source for Component Release Metadata. Component source repositories remain authoritative for code, tags, package versions and publication; the Release Asset is the generated, immutable metadata document for that exact published release.

### Publisher contract

1. The component release workflow MUST generate Component Release Metadata from the exact tag commit after all package artifacts and their checksums have been produced.
2. The generated metadata document MUST be uploaded to the GitHub Release as a Release Asset. It MUST NOT be committed to the source repository and MUST NOT require a tracked per-version file under a registry directory.
3. The canonical asset name is `<component-id>-<version>.json` for variant `default`, and `<component-id>-<variant>-<version>.json` for every non-default variant. Example assets include `backend-1.2.1.json`, `frontend-tui-1.1.0.json` and `frontend-gui-sdl-1.1.0.json`.
4. The metadata document MUST include a `publication` declaration containing provider `github-releases-v1`, the exact repository URI, the exact release tag and the full commit SHA resolved by that tag, plus the exact metadata asset filename. It MUST NOT include its own digest or URI because those values are supplied by the GitHub Release API after upload.
5. The metadata's source-unit list MUST contain exactly one publisher source unit whose repository URI equals the declared release repository and whose immutable revision equals the release tag commit. Additional source units may identify other repositories.
6. A release tag MUST be a version tag: the exact tag name is the Catalog source's configured tag prefix followed by the metadata SemVer. The GitHub Release prerelease flag MUST agree with the SemVer prerelease component.

### Catalog and Registry contract

1. A Catalog Index may use either the existing static `entries` model or the new `release_sources` model. A document MUST NOT mix both models. Existing static catalogs remain valid and retain their current semantics.
2. A Release Source identifies a stable source ID, provider, GitHub repository URI, component ID, variant and optional tag prefix (default `v`). This is one declaration per discoverable component/variant, not one declaration per package version.
3. Registry MUST enumerate all eligible published releases through the paginated GitHub Releases list API. It MUST NOT use the floating `/releases/latest` endpoint and MUST NOT treat API page order or `published_at` as a version-selection rule.
4. Registry derives the expected metadata asset filename from the source's component/variant and the release SemVer, then requires exactly one matching asset. Draft releases are ignored; prereleases are candidates only when Product Definition policy permits them. A verified `withdrawn` Release Metadata document remains in the Catalog's auditable candidate history, but the Resolver MUST reject it for new selection; update discovery reports the withdrawal without rewriting historical Manifests.
5. Registry MUST resolve the tag reference to a commit, including annotated tag objects, and verify that it equals both `publication.tag_commit` and the publisher source-unit revision. A moved tag, a tag/version mismatch, a prerelease-flag mismatch, or a repository/source-unit mismatch is invalid release metadata.
6. Registry MUST require the GitHub Release Asset API's SHA-256 digest and byte size for the metadata asset. It MUST verify the exact downloaded bytes before parsing. A missing digest, missing asset, duplicate asset, digest mismatch or size mismatch is a discovery failure, not permission to fall back to source.
7. Registry feeds validated discovered metadata into the existing SemVer/dependency/contract resolver. It selects the highest compatible SemVer under the existing stable/prerelease policy. Equal-precedence candidates with different release identities are ambiguous and MUST fail; publication time and list order MUST NOT break ties.
8. Registry MUST record the exact release-source ID, repository URI, GitHub Release ID/API URI, tag, resolved tag commit, metadata asset name/URI/size/digest and publication timestamp (when supplied) in the Resolved Manifest. Replay MUST use the recorded metadata URI and digest and MUST NOT query for a newer release or substitute another asset.
9. Release discovery MUST be bounded and complete. Pagination limits, response-size limits, timeouts and retry budgets MUST be finite. If the configured limit is reached before all candidate pages are examined, Registry MUST fail with an explicit discovery-limit error rather than resolve from a partial release list.
10. Online discovery may use conditional requests and verified caches. Offline discovery may use only a previously verified cache snapshot for the exact Catalog Release Source identity; otherwise it fails clearly. A historical Manifest remains replayable only from its exact recorded asset identity.

### Compatibility

The Registry Data Contract baseline advances additively to `1.4.0`. Catalog Index documents using `release_sources` use schema version `1.1.x`; Component Release Metadata declaring `publication` uses schema version `1.2.x`; Resolved Manifests recording GitHub discovery provenance use schema version `1.2.x`. Existing static Catalog entries, existing checked-in metadata documents and older manifests remain valid under their existing schema versions.

## Consequences

- A component release no longer needs a source commit just to add a versioned metadata JSON file.
- A component publisher adds one release workflow step that generates and uploads metadata after the package assets are ready.
- A Catalog needs one stable declaration per component/variant/repository instead of a new URI and digest for every release.
- Registry remains consumer-independent. GitHub is a generic provider adapter, not a CDIN-specific workflow.
- Discovery is dynamic, while each successful resolution and replay remains immutable and deterministic.
- GitHub asset SHA-256 verifies byte integrity relative to the API response; it does not independently authenticate the publisher or prove a trusted build.

## Alternatives considered

### Continue committing one JSON file per version

Rejected. It creates source-tree churn and duplicate publication records for data that is already attached to an immutable release.

### Use the GitHub `/releases/latest` endpoint

Rejected. It excludes prereleases, returns one mutable selection rather than the complete candidate set, and cannot preserve the existing deterministic SemVer resolver or complete candidate evidence.

### Select by `published_at`

Rejected. Release publication time is provenance, not package-version precedence; delayed or backfilled releases would change selection semantics.

### Remove Catalog configuration entirely

Rejected for this contract. Registry remains generic and must know which repositories provide requested logical component/variant identities. A small Release Source declaration supplies that mapping once; versions are discovered automatically from the repository's Release inventory.

## Boundaries

- **Spec:** owns this decision, Registry schemas, normative requirements and conformance vectors.
- **Registry:** implements generic GitHub Release enumeration, metadata verification, candidate construction, caching and exact replay.
- **Component repositories:** generate and upload their own release metadata assets and package artifacts.
- **Catalog publisher / consumer:** declares which logical component/variant is discoverable from which repository; it does not add each version manually.

## References

- [ADR-0022 — Generic Consumer-Independent Registry](ADR-0022-minimal-static-release-catalog.md)
- [ADR-0025 — Immutable target-specific artifact delivery](ADR-0025-immutable-target-artifact-delivery.md)
- [Immutable artifact delivery](../architecture/immutable-artifact-delivery.md)
- [Registry data contracts](../architecture/registry-contracts.md)
- [Spec issue #37](https://github.com/cdin-editor/spec/issues/37)