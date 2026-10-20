# Kernel implementation status — cdin-kernel package 1.1.0 / ABI 1.0.0

This page records the cross-repository boundary between the stable CDIN Spec baseline, the `cdin-kernel` 1.1.0 package release, and the public C ABI. The Spec repository remains design-only; executable code and tests live in `cdin-kernel`. The package number, ABI number and Spec baseline are independent labels.

## Version and evidence source

| Item | Recorded value |
|---|---|
| Spec baseline | `1.0.0` |
| Kernel package release | `1.1.0` (release notes dated 2026-10-20 in the supplied source snapshot) |
| Implementation repository | `cdin-kernel` (standalone source archive; archive contains no Git history) |
| Public C ABI | `1.0.0`, declared by `include/cdin/kernel.h` |
| ABI-to-Spec declaration | Header defines `CDIN_KERNEL_SPEC_VERSION_MAJOR/MINOR/PATCH = 1/0/0` |
| Distribution | Release workflow builds OS packages and is configured to publish a multi-architecture Docker Hub SDK image when the required secrets are available; a successful public push is not independently verified by this Spec snapshot. |
| Language/toolchain gate | C11; warning-clean build with `-Werror` under Clang |
| Executable checks | `make check`; `make asan`; `make tsan`; fuzz-target build and bounded smoke runs as listed in the synchronization report |

## Implemented and covered by the Kernel ABI 1.0.0 surface (package 1.1.0)

- Opaque kernel, document, transaction, snapshot and notification handles, with invalid/stale-handle detection.
- Length-delimited byte-preserving document content, including embedded NUL, BOM and invalid UTF-8; LF/CRLF/CR line handling; raw-byte and valid-UTF-8 region classification.
- Version-checked replace and batch edits; document/version limit guards; atomic failure semantics; clean/saved-state tracking.
- Undo/redo, edit coalescing, opaque before/after caller blobs, explicit single-level transactions and rollback.
- Immutable snapshots, text read/serialize, byte/code-point conversions, line/column helpers and extended grapheme stepping against a pinned, queryable Unicode version.
- Literal and byte search, backward/forward iteration, simple case folding, any-newline literal behavior, bounded candidate steps, cancellation and optional partial results.
- Bounded notification queues, `RESYNC` on overflow, close events and explicit unsubscribe that invalidates/frees the subscription handle.
- Caller allocator, optional caller-supplied lock/unlock pair, logging sink, ABI version and feature queries, and fixed-width 32-bit ABI enum-like fields.

## Package 1.1.0 changes that do not alter the public contract

- Release archives include documentation, installation instructions and examples; install paths and `pkg-config` metadata are documented for supported native toolchains.
- A Docker SDK image recipe and tag-based GitHub Actions publishing workflow target `linux/amd64` and `linux/arm64`. Publishing uses `DOCKER_USERNAME` and `DOCKER_TOKEN`; the repository snapshot alone does not prove that a particular namespace has been pushed successfully.
- Forward literal search has internal fast paths: Linux may use `memmem` for byte-exact searches that are uncancellable and have a full candidate-window budget; other platforms use a selective-byte anchor before full comparisons. Cancellable and step-limited searches retain their incremental path. These choices are implementation details, not ABI promises, and they do not change match ranges or status semantics.
- Public-header comments, the C quickstart, README, binding examples and installation docs have been clarified. The optional FFI example is sample integration code, not an additional stable ABI.

## Explicitly unsupported or outside Kernel ABI 1.0.0

- **Regex search:** `CDIN_SEARCH_REGEX` returns `CDIN_UNSUPPORTED`; no regex feature bit is advertised. Requirement `SEARCH-004` stays `DEFERRED`; engine and syntax questions remain OD-09.
- **Reload that preserves history:** `CDIN_RELOAD_KEEP_HISTORY` is unsupported; callers must use flags `0`.
- **Asynchronous executor / internal FIFO queue:** public calls execute synchronously. With a configured lock pair, the lock linearization order serializes calls; without it, the application must serialize calls. ABI 1.0.0 does not promise FIFO according to wall-clock arrival or thread scheduling.
- **Distinct graceful-drain and abort shutdown behavior:** there is no internal pending request queue; the two mode values behave identically in ABI 1.0.0.
- **Frontend Protocol wire codec, backend/runtime host API, GUI/TUI/CLI frontend behavior, plugin UI and persistence I/O:** these belong to other components and are not implemented by the kernel.
- **Kernel-owned selections, visual layout, syntax highlighting, bidi/shaping, OS file I/O or independent canonical document copies in clients:** these are explicitly outside the kernel boundary.

## Spec decision policy

The package version `1.1.0` is not the ABI version: the supported public C ABI remains `1.0.0`, which declares conformance to Spec baseline `1.0.0`. Kernel evidence does not prove that all Spec requirements are implemented. Any requirement labelled `PROPOSED` remains proposed unless an owner decision promotes it. Requirements that contradict the actual kernel have been corrected, deferred or remain explicitly open rather than being described as supported. See the [Open Decisions Register](../adr/open-decisions.md) for protocol encoding, client-library, multi-frontend mutation, regex and search-normalization choices.

## Integration gate before extracting `cdin-runtime`

1. `cdin` backend creates the kernel through the public header and checks that ABI major 1 is supported.
2. One end-to-end path replaces a document, receives a notification, and observes the committed version without a second canonical document/history store.
3. The `cdin` composition root builds and starts with its documented dependencies; SDL3 availability and the currently empty test baseline must be resolved for GUI test claims.
4. Only after the runtime host API is versioned and this integration gate passes should `cdin-runtime` become the next repository.
