# Immutable target-specific artifact delivery

- **Status:** ACCEPTED — [ADR-0025](../adr/ADR-0025-immutable-target-artifact-delivery.md).
- **Registry Data Contract baseline:** `1.3.0`.
- **Schema dialect:** JSON Schema Draft 2020-12.
- **Implementation owner:** `cdin-editor/registry`.
- **Consumer integration owner:** each product Composition Root.

This contract adds prebuilt package delivery to the existing source-oriented Registry. It does not turn Registry into a product build system, package script runner, installer framework or runtime dependency.

## 1. Boundary and terminology

A **release** remains the component-owned immutable identity `(component_id, variant, version, release_metadata_uri, release_metadata_sha256)`. An **artifact** is one immutable file published for that release and one target (or the explicitly universal target). A **package** is the payload represented by that artifact. The package contains no install-time scripts: Registry only verifies and stages files; the consumer decides how to link, configure, install and launch the product.

Component Release Metadata may publish both source units and artifacts. Source remains available for contributors and explicit source consumers. Artifact availability does not change component ownership, package version, contract version, or source revision identity.

Registry remains generic. It MUST NOT know CDIN, SDL, TUI, GUI, Runtime, Backend, Frontend, product IDs, package repository names, or product-specific installation sequences. A component's generic `variant` is publisher-owned data; for example, a publisher may choose `core`, `tui`, or `gui-sdl`, but Registry treats each as an opaque variant ID.

## 2. Public metadata contract

The Registry v1 Component Release Metadata schema adds optional `artifacts`. Existing source-only releases remain valid and retain their current behavior. Every release that publishes artifacts MUST continue to declare its immutable source units, because source provenance and an explicit source fallback remain part of the release identity.

Each artifact declares:

| Field | Meaning |
|---|---|
| `artifact_id` | Stable ID unique within this exact component release metadata document. |
| `kind` | `native-development-package`, `runtime-module-archive`, or `sdk-package`. |
| `target` | Exact OS, architecture and ABI tuple, or the one universal tuple. |
| `format` | `tar.gz`, `tar.xz`, or `zip`. |
| `file_name` | Safe basename used for cache and diagnostics; never used as identity. |
| `uri` | Absolute HTTPS asset URI. |
| `sha256` | SHA-256 of the exact downloaded bytes. |
| `size_bytes` | Exact published byte count. |
| `layout` | `cmake-prefix-v1` or `lua-module-tree-v1`. |
| `source_unit_ids` | One or more source-unit IDs that produced this artifact. |
| `build` | Immutable recipe source path and toolchain identity. |
| `attestations` | Optional digest-addressed provenance statements; references are not automatically trusted. |

The artifact ID is unique within the metadata document. There MUST NOT be more than one artifact with the same target and layout role. A producer that needs several libraries or headers publishes one coherent package archive, not several ambiguous matches for the same target.

### Target vocabulary and matching

OS identifiers are `linux`, `darwin`, `windows`, `freebsd`, and `openbsd`. Architecture identifiers are `x86_64` and `arm64`. Publishers and consumers MUST normalize platform aliases before metadata validation: for example, `AMD64` or `x64` becomes `x86_64`, and `aarch64` becomes `arm64`.

The `abi` value is a lower-case, publisher-defined, stable identifier for the binary compatibility family, including relevant C runtime and deployment baseline. It is compared exactly; Registry MUST NOT guess ABI compatibility from compiler names, host names, libc version strings or substring matches. A consumer needing a different ABI must request a different target tuple. Changing an artifact's ABI is a new artifact identity and normally requires a new release or a new immutable metadata document/version.

The only platform-independent target is exactly `{ "os": "any", "architecture": "any", "abi": "none" }`. Partial wildcards are invalid. Registry first looks for one exact OS/architecture/ABI match. If there is none, it may select one explicitly universal artifact. If both exact and universal artifacts exist, exact wins. More than one candidate at the winning specificity is an ambiguity error; catalog order is never a tie-breaker. A universal artifact is an explicit publisher declaration, not an implicit host fallback.

### Package layouts

- `cmake-prefix-v1`: archive root is an install prefix. It may contain `include/`, `lib/`, `bin/`, `share/`, `lib/cmake/` and `lib/pkgconfig/`. Files are already built and install-ready; Registry does not run CMake or a package script.
- `lua-module-tree-v1`: archive root contains the platform-neutral Lua module tree under `lua/`. It contains source modules and package metadata, not VM-specific bytecode. Lua host version constraints remain ordinary component or environment requirements and are not inferred by Registry.

A package layout describes files, not a product's final installation prefix. Consumers may stage packages in a private prefix and link them from there. Package archives MUST NOT require an install hook, shell script, CMake configure step, or network activity to become usable.

## 3. Product Definition delivery policy

Product Definition adds an optional `resolution` object:

```json
{
  "resolution": {
    "delivery_mode": "artifact",
    "target": {
      "os": "linux",
      "architecture": "x86_64",
      "abi": "gnu-glibc-2.28"
    }
  }
}
```

The modes are:

- `source`: collect source units exactly as contract 1.2.0 does.
- `artifact`: require exactly one compatible artifact for every selected component/variant; fail when one is missing.
- `artifact-or-source`: prefer a compatible artifact and use source units only when no compatible artifact is declared for that selected release.

Omitting `resolution` preserves legacy behavior and means `source`. Artifact modes require an explicit target tuple. The product owns target selection; Registry MUST NOT silently substitute the detected host for an explicit target or infer a different ABI. A product may generate a target-specific Product Definition for each native build target.

Fallback is deliberately narrow. `artifact-or-source` may fall back only when metadata contains no matching artifact. It MUST NOT fall back after an artifact was selected but its download, size, digest, archive format, extraction, path validation or staging failed. Such a failure is an integrity or delivery failure and MUST fail the operation.

## 4. Resolution and workspace semantics

Version/dependency/contract resolution remains unchanged. Once a component release is selected, Registry applies the Product Definition delivery policy to that exact release:

1. `source` collects the exact source-unit revisions.
2. `artifact` selects an exact target match, else an explicitly universal artifact, or fails with `ARTIFACT_NOT_FOUND`.
3. `artifact-or-source` applies the same selection and uses source only if no artifact matches.
4. Multiple candidates at the winning specificity fail with `ARTIFACT_AMBIGUOUS`. A target/ABI mismatch is not a compatible match.
5. Artifact download, size, digest, package-format, extraction or publication errors fail with their own stable error code; source fallback is forbidden.

The Resolved Manifest records top-level effective `delivery_mode` and `target`, and, for every selected component/variant, a `delivery` value of `artifact` or `source`. Artifact-delivered components record the exact artifact ID, kind, target, format, filename, URI, SHA-256, size, layout, source-unit provenance IDs, build recipe/toolchain identity and workspace-relative extracted path. Source-delivered components retain the source-unit repository, revision and workspace path fields.

Manifest replay MUST NOT run version selection again. It MUST fetch the exact recorded URI, verify the exact recorded size and SHA-256, and materialize the same artifact identity. A missing, withdrawn, replaced or inaccessible historical asset causes replay to fail; Registry MUST NOT substitute another artifact, a newer release, a different mirror or `latest`. A cache hit is valid only after its bytes are rechecked against the recorded digest.

Suggested workspace handoff:

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

The workspace is published atomically only after every selected source or artifact has been completely retrieved, verified, validated and staged. Partial component packages MUST NOT be exposed as a successful workspace.

## 5. Download, integrity and archive security

Artifact URIs MUST use HTTPS, contain no embedded credentials and be checked against the consumer's configured host allow-list. Redirects MUST remain HTTPS and pass the same host policy; HTTPS-to-HTTP downgrade, unapproved redirect hosts, loopback/private/link-local destinations and non-HTTP schemes MUST be rejected. Registry MUST NOT forward credentials to a different host.

The declared `size_bytes` is checked while streaming; implementation limits for compressed bytes, expanded bytes, entry count and nesting depth MUST be configurable and enforced before workspace publication. A package exceeding any configured limit fails closed. The expected SHA-256 is checked before extraction; neither a filename nor a checksum text file discovered inside the archive overrides metadata's digest.

Portable archive extraction MUST reject:

- absolute POSIX paths, UNC paths, drive-letter paths and NUL bytes;
- `.` or `..` traversal, backslash-based traversal and paths that escape the staging root after normalization;
- symbolic links, hard links, device nodes, sockets, FIFOs and other special file types;
- duplicate entries, case-fold collisions, Unicode-normalization collisions, trailing-dot/space collisions and file-versus-directory prefix conflicts;
- Windows reserved device names and alternate data stream syntax;
- unsupported compression/format and entries exceeding configured limits.

Implementations MUST use a fresh private temporary directory, validate every entry before creating it, refuse to follow pre-existing symlinks/reparse points in the destination path, and publish the completed directory with an atomic rename. A failed extraction removes its temporary tree and MUST NOT modify an existing successful workspace or cache entry.

The content hash proves byte integrity relative to the pinned metadata. It does not by itself authenticate the publisher, prove a trustworthy builder, or establish that the binary is safe. Optional attestations are immutable references; Registry may verify their digest but MUST NOT claim signature or identity verification without an explicitly configured trust policy.

## 6. Cache, offline and withdrawal behavior

The artifact cache key is the immutable artifact identity, including component release metadata digest, artifact ID, target and SHA-256. It MUST NOT be keyed only by version or filename. Cache reuse requires revalidation of the cached bytes or a locally protected verification record with equivalent tamper resistance. Offline mode uses only a fully verified cache entry and fails clearly when it is absent or corrupt; it never resolves a newer version.

A withdrawn release is excluded from new resolutions as before. Historical manifests remain immutable and replay the exact selected identity. If the asset has been deleted or its bytes no longer match the recorded digest, replay fails rather than rewriting historical evidence. A security policy may deny use of a known-compromised artifact, but such a denial is explicit and must not mutate the manifest.

## 7. Migration and compatibility

The extension is additive under Registry Data Contract `1.3.0`:

- Source-only metadata, Product Definitions and manifests from 1.2.0 remain valid. Missing `resolution` means `source`.
- Existing source collection remains supported and unchanged.
- A new Registry can process old source-only metadata. An old Registry that does not understand `artifacts` cannot provide artifact delivery; consumers requiring artifacts must fail with an unsupported-contract/version error, not silently build source.
- Component publishers may publish artifacts incrementally. Until a component release contains compatible assets, an `artifact` consumer fails and an explicit `artifact-or-source` consumer may use source.
- Registry does not build artifacts and does not run component test suites. Component CI builds/tests/publishes; product CI verifies the assembled product and its target matrix.

## 8. Normative requirements

- **REG-028** Registry MUST validate artifact descriptors against the versioned Component Release Metadata schema. — *Verify:* CONF
- **REG-029** Artifact identity MUST include the exact release metadata digest, artifact ID, target, URI and SHA-256. — *Verify:* CONF
- **REG-030** Target matching MUST be deterministic and use exact OS, architecture and ABI identity; partial wildcards MUST be rejected. — *Verify:* CONF
- **REG-031** The universal target MUST be the explicit `any/any/none` tuple; exact target matches MUST take precedence over it. — *Verify:* CONF
- **REG-032** Artifact selection ambiguity MUST fail; catalog order and publication time MUST NOT be tie-breakers. — *Verify:* CONF
- **REG-033** Source fallback MUST occur only in explicit `artifact-or-source` mode when no artifact matches. Integrity, network, archive or extraction failures MUST NOT trigger fallback. — *Verify:* CONF
- **REG-034** The Resolved Manifest MUST record effective delivery policy, target and exact selected artifact identity and workspace path. — *Verify:* CONF
- **REG-035** Manifest replay MUST reproduce the recorded artifact identity and MUST NOT select a newer or floating artifact. — *Verify:* INTEG
- **REG-036** Registry MUST verify artifact size and SHA-256 before extraction and MUST NOT publish partially staged workspaces. — *Verify:* INTEG
- **REG-037** Artifact extraction MUST reject traversal, links, special files, duplicate/colliding paths and configured resource-limit violations. — *Verify:* FUZZ
- **REG-038** Artifact retrieval MUST enforce HTTPS, configured host policy, redirect policy and protection against private/local destinations. — *Verify:* INTEG
- **REG-039** Registry MUST treat checksum verification and publisher authentication as separate claims. — *Verify:* INSPECT
- **REG-040** Artifact cache reuse MUST be bound to immutable metadata and digest identity; offline mode MUST NOT substitute a newer artifact. — *Verify:* INTEG
- **REG-041** Registry MUST remain consumer-independent and MUST NOT run package scripts, component build systems or product installation logic. — *Verify:* STATIC

## 9. References

- [Registry data contracts](registry-contracts.md)
- [Registry architecture](registry.md)
- [ADR-0022 — Generic Consumer-Independent Registry](../adr/ADR-0022-minimal-static-release-catalog.md)
- [ADR-0025 — Immutable target-specific artifact delivery](../adr/ADR-0025-immutable-target-artifact-delivery.md)
- [Conformance edge-case vectors](../../tests/registry/artifact-delivery-v1.json)
