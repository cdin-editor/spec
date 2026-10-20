# Kernel implementation status — Spec 1.0.0 sync

This page records the cross-repository boundary between the stable architecture baseline and what the standalone kernel implementation actually supports. The Spec repository remains design-only; executable code and tests live in `cdin-kernel`.

## Version and evidence source

| Item | Recorded value |
|---|---|
| Spec baseline | `1.0.0` |
| Implementation repository | `cdin-kernel` (standalone archive snapshot supplied for this synchronization; archive contains no Git history) |
| Public C ABI | `1.0.0`, declared by `include/cdin/kernel.h` |
| ABI-to-Spec declaration | Header defines `CDIN_KERNEL_SPEC_VERSION_MAJOR/MINOR/PATCH = 1/0/0` |
| Language/toolchain gate | C11; warning-clean build with `-Werror` under Clang |
| Executable checks | `make check`; `make asan`; `make tsan`; fuzz-target build and bounded smoke runs as listed in the synchronization report |

## Implemented and covered by the Kernel ABI 1.0.0 surface

- Opaque kernel, document, transaction, snapshot and notification handles, with invalid/stale-handle detection.
- Length-delimited byte-preserving document content, including embedded NUL, BOM and invalid UTF-8; LF/CRLF/CR line handling; raw-byte and valid-UTF-8 region classification.
- Version-checked replace and batch edits; document/version limit guards; atomic failure semantics; clean/saved-state tracking.
- Undo/redo, edit coalescing, opaque before/after caller blobs, explicit single-level transactions and rollback.
- Immutable snapshots, text read/serialize, byte/code-point conversions, line/column helpers and extended grapheme stepping against a pinned, queryable Unicode version.
- Literal and byte search, backward/forward iteration, simple case folding, any-newline literal behavior, bounded candidate steps, cancellation and optional partial results.
- Bounded notification queues, `RESYNC` on overflow, close events and explicit unsubscribe that invalidates/frees the subscription handle.
- Caller allocator, optional caller-supplied lock/unlock pair, logging sink, ABI version and feature queries, and fixed-width 32-bit ABI enum-like fields.

## Explicitly unsupported or outside Kernel 1.0.0

- **Regex search:** `CDIN_SEARCH_REGEX` returns `CDIN_UNSUPPORTED`; no regex feature bit is advertised. Requirement `SEARCH-004` stays `DEFERRED`; engine and syntax questions remain OD-09.
- **Reload that preserves history:** `CDIN_RELOAD_KEEP_HISTORY` is unsupported; callers must use flags `0`.
- **Asynchronous executor / internal FIFO queue:** public calls execute synchronously. With a configured lock pair, the lock linearization order serializes calls; without it, the application must serialize calls. ABI 1.0.0 does not promise FIFO according to wall-clock arrival or thread scheduling.
- **Distinct graceful-drain and abort shutdown behavior:** there is no internal pending request queue; the two mode values behave identically in ABI 1.0.0.
- **Frontend Protocol wire codec, backend/runtime host API, GUI/TUI/CLI frontend behavior, plugin UI and persistence I/O:** these belong to other components and are not implemented by the kernel.
- **Kernel-owned selections, visual layout, syntax highlighting, bidi/shaping, OS file I/O or independent canonical document copies in clients:** these are explicitly outside the kernel boundary.

## Spec decision policy

The kernel is evidence for the supported ABI 1.0.0 contract, not proof that all 396 Spec requirements are implemented. Any requirement labelled `PROPOSED` remains proposed unless an owner decision promotes it. Requirements that contradict the actual kernel have been corrected, deferred or remain explicitly open rather than being described as supported. See the [Open Decisions Register](../adr/open-decisions.md) for protocol encoding, client-library, multi-frontend mutation, regex and search-normalization choices.

## Integration gate before extracting `cdin-runtime`

1. `cdin` backend creates the kernel through the public header and checks that ABI major 1 is supported.
2. One end-to-end path replaces a document, receives a notification, and observes the committed version without a second canonical document/history store.
3. The `cdin` composition root builds and starts with its documented dependencies; SDL3 availability and the currently empty test baseline must be resolved for GUI test claims.
4. Only after the runtime host API is versioned and this integration gate passes should `cdin-runtime` become the next repository.
