# Kernel implementation status — cdin-kernel package 1.2.1 / ABI 1.1.0

This page records the cross-repository boundary between CDIN Spec 1.2.0, the `cdin-editor/kernel` 1.2.1 package release, and public C ABI 1.1.0. The Spec repository remains design-only; executable Kernel code and tests live in `cdin-editor/kernel`. Package, ABI and Spec versions are independent labels.

## Version and evidence source

| Item | Recorded value |
|---|---|
| Spec baseline | `1.2.0` |
| Kernel package release | `1.2.1` (package version inspected in the Kernel repository) |
| Implementation repository | `cdin-editor/kernel` (Git repository inspected read-only) |
| Public C ABI | `1.1.0`, declared by `include/cdin/kernel.h` |
| ABI-to-Spec declaration | Header defines `CDIN_KERNEL_SPEC_VERSION_MAJOR/MINOR/PATCH = 1/1/0` |
| Distribution | Release workflow builds OS packages and is configured to publish a multi-architecture Docker Hub SDK image when the required secrets are available; a successful public push is not independently verified by this Spec snapshot. |
| Language/toolchain gate | C11; warning-clean build with `-Werror` under Clang |
| Executable checks | `make check`; `make asan`; `make tsan`; fuzz-target build and bounded smoke runs as listed in the synchronization report |

## ABI 1.1.0 additive surface

The current public header reports ABI `1.1.0`. Relative to the earlier `1.0.0` baseline described by the historical requirements below, the additive v1.1 surface includes the Kernel-owned logging configuration and `cdin_kernel_log` entry point. The Backend consumes it through the existing public header and must not bind the private logger implementation.

## Implemented and covered by the Kernel ABI 1.1.0 surface (package 1.2.1)

- Opaque kernel, document, transaction, snapshot and notification handles, with invalid/stale-handle detection.
- Length-delimited byte-preserving document content, including embedded NUL, BOM and invalid UTF-8; LF/CRLF/CR line handling; raw-byte and valid-UTF-8 region classification.
- Version-checked replace and batch edits; document/version limit guards; atomic failure semantics; clean/saved-state tracking.
- Undo/redo, edit coalescing, opaque before/after caller blobs, explicit single-level transactions and rollback.
- Immutable snapshots, text read/serialize, byte/code-point conversions, line/column helpers and extended grapheme stepping against a pinned, queryable Unicode version.
- Literal and byte search, backward/forward iteration, simple case folding, any-newline literal behavior, bounded candidate steps, cancellation and optional partial results.
- Bounded notification queues, `RESYNC` on overflow, close events and explicit unsubscribe that invalidates/frees the subscription handle.
- Caller allocator, optional caller-supplied lock/unlock pair, logging sink, ABI version and feature queries, and fixed-width 32-bit ABI enum-like fields.

## Package 1.2.1 / Kernel ABI 1.1.0 synchronization

- Release archives include documentation, installation instructions and examples; install paths and `pkg-config` metadata are documented for supported native toolchains.
- A Docker SDK image recipe and tag-based GitHub Actions publishing workflow target `linux/amd64` and `linux/arm64`. Publishing uses `DOCKER_USERNAME` and `DOCKER_TOKEN`; the repository snapshot alone does not prove that a particular namespace has been pushed successfully.
- Forward literal search has internal fast paths: Linux may use `memmem` for byte-exact searches that are uncancellable and have a full candidate-window budget; other platforms use a selective-byte anchor before full comparisons. Cancellable and step-limited searches retain their incremental path. These choices are implementation details, not ABI promises, and they do not change match ranges or status semantics.
- Public-header comments, the C quickstart, README, binding examples and installation docs have been clarified. The optional FFI example is sample integration code, not an additional stable ABI.

## Explicitly unsupported or outside Kernel ABI 1.1.0

- **Regex search:** `CDIN_SEARCH_REGEX` returns `CDIN_UNSUPPORTED`; no regex feature bit is advertised. Requirement `SEARCH-004` stays `DEFERRED`; engine and syntax questions remain OD-09.
- **Reload that preserves history:** `CDIN_RELOAD_KEEP_HISTORY` is unsupported; callers must use flags `0`.
- **Asynchronous executor / internal FIFO queue:** public calls execute synchronously. With a configured lock pair, the lock linearization order serializes calls; without it, the application must serialize calls. ABI 1.0.0 does not promise FIFO according to wall-clock arrival or thread scheduling.
- **Distinct graceful-drain and abort shutdown behavior:** there is no internal pending request queue; the two mode values behave identically in ABI 1.0.0.
- **Frontend Protocol wire codec, backend/runtime host API, GUI/TUI/CLI frontend behavior, plugin UI and persistence I/O:** these belong to other components and are not implemented by the kernel.
- **Kernel-owned selections, visual layout, syntax highlighting, bidi/shaping, OS file I/O or independent canonical document copies in clients:** these are explicitly outside the kernel boundary.

## Spec decision policy

The package version `1.2.1` is not the ABI version: the current public C ABI is `1.1.0`, with ABI major `1` preserving existing field layouts and numeric identities while adding the Kernel logger API. The current header declares Spec target `1.1.0`. Kernel evidence does not prove that all Spec requirements are implemented. Any requirement labelled `PROPOSED` remains proposed unless an owner decision promotes it. Requirements that contradict the actual Kernel have been corrected, deferred or remain explicitly open rather than being described as supported. Frontend wire, client-library and driver-policy decisions are resolved by ADR-0018; other entries remain in the [Open Decisions Register](../adr/open-decisions.md).

## Integration gate before extracting `cdin-runtime`

1. `cdin` backend creates the kernel through the public header and checks that ABI major 1 is supported.
2. One end-to-end path replaces a document, receives a notification, and observes the committed version without a second canonical document/history store.
3. The `cdin` composition root builds and starts with its documented dependencies; SDL3 availability and the currently empty test baseline must be resolved for GUI test claims.
4. Only after the runtime host API is versioned and this integration gate passes should `cdin-runtime` become the next repository.


## Owner-approved synchronization — Spec 1.2.0

The Kernel requirements promoted to `ACCEPTED` in Spec 1.2.0 are recorded by [ADR-0021](../adr/ADR-0021-kernel-implementation-backed-contracts.md) and are limited to behavior present in the Kernel 1.2.1 / ABI 1.1.0 public surface. The review inspected (read-only) the following anchors:

| Area | Implementation anchors | Conformance/test anchors |
|---|---|---|
| ABI, handles, limits, logging | `include/cdin/kernel.h`; `src/kernel.c`; `src/core/handle_table.c` | `tests/test_p1.c`; `tests/test_logging.c`; `conformance/vec/abi.*.vec` |
| Document lifecycle, versions, edits and reload | `src/doc/doc.c`; `src/doc/edit.c` | `conformance/vec/doc/doc.lifecycle.vec`; `conformance/vec/edit/edit.replace.vec`; `conformance/vec/edit/edit.version.vec` |
| Transactions and rollback | `src/txn/txn.c` | `conformance/vec/txn/txn.basic.vec` |
| Undo, coalescing, blobs and saved marker | `src/history/undo.c`; `src/doc/edit.c` | `conformance/vec/undo/undo.basic.vec` |
| Notifications, overflow and resync | `src/notif/notif.c`; `src/doc/edit.c` | `conformance/vec/notif/notif.basic.vec` |
| UTF-8 regions, bytes and line endings | `src/util/utf8.c`; `src/core/block.c`; `src/text/lines.c` | `conformance/vec/text/text.bytes.vec`; `conformance/vec/text/text.eol.vec` |
| Positions and graphemes | `src/text/positions.c`; `src/text/graphemes.c` | `conformance/vec/pos/pos.convert.vec`; `conformance/vec/unicode/unicode.fold.vec` |
| Search and cancellation | `src/search/literal.c`; `src/search/fold.c` | `conformance/vec/search/search.literal.vec`; `search.bytes.vec`; `search.unicode.vec` |
| Concurrency and shutdown | `src/kernel.c`; `src/doc/edit.c`; `src/txn/txn.c` | `tests/test_p3_conc.c`; `conformance/vec/conc/conc.basic.vec` |

This synchronization was a source/header/test-definition review. The tests and conformance vectors were inspected but were **not executed in this review session**. The pre-existing report of `make check`, sanitizer and fuzz runs remains attributable to the Kernel repository's own recorded evidence, not to this Spec review.

The following remain intentionally outside current acceptance: strict no-clock/no-I/O determinism (`KERNEL-007`), universal process-termination guarantees (`KERNEL-009`), Regex (`KERNEL-010`, `SEARCH-004`, OD-09), architecture-specific optimizations (`KERNEL-015`), formal maximal-subpart invalid-UTF-8 partition rules (`TEXT-012`, OD-11), Kernel position anchors (`POS-051`, OD-28), Unicode normalization/profile choices (OD-29), and internal parallel mutation (OD-27).
