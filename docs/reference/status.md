# Status and verification record

This file is the authoritative status report for Spec release `1.1.0` and the `cdin-kernel` package `1.1.0` synchronization. It distinguishes archive facts, accepted architectural decisions, unresolved choices and commands that were actually executed. All inspected input was a working-tree archive snapshot; none of the supplied RAR files contains Git history.

**Specification release: `1.1.0` (compatible architecture and documentation release).** The previous `1.0.0` baseline remains the specification compatibility target declared by `cdin-kernel` in its public header. This release clarifies system maps, component boundaries, and current-versus-target status; it does not claim that backend integration, the Runtime Host API, Frontend Protocol wire encoding or every proposed requirement is implemented. The kernel's C ABI remains `1.0.0`.

## 1. Source snapshots inspected

| Snapshot | What was examined | Limits of the evidence |
|---|---|---|
| `cdin` archive | Source/build/test directory structure; README and architecture notes; Makefile and build includes; public UI/API headers; Lua API tables; SDL3 references; test baseline and test invocation | This is an archive snapshot, not a checkout with history. The full test/build gate could not pass in the current environment: SDL3 development headers are missing and the archived test baseline is empty/unusable. This is an environment/baseline blocker, not evidence that every source file fails to compile. |
| `cdin-kernel` archive | Public C header, implementation modules, ABI/limits docs, conformance runner and vectors, C regression tests, fuzz targets, Makefile/release workflow, package 1.1.0 docs and Docker SDK recipe | Working tree only; no Git commit ancestry or upstream CI results available. The source release notes report the project checks; the Docker workflow is configured, but a successful push to a specific Docker Hub namespace is not established by the archive. |
| `spec` archive | Full Markdown requirement set, ADRs, open-decision register, status/conventions pages, structural checker, CI/build configuration | Spec is intentionally design-only; implementation tests live in the `cdin-kernel` repository. |
| `cdin-x` | Only references from supplied `cdin`/Spec material | The `cdin-x` archive/source itself was not supplied, so no claim is made about its current implementation. |

A previous status report said `cdin-kernel` did not exist and the kernel API names were open. That is now superseded by the standalone kernel snapshot and its public ABI header `include/cdin/kernel.h` declaring C ABI `1.0.0`.

## 2. Current Spec structure counts

The final structural-checker output for this release is: 65 Markdown files; 396 normative requirements (96 ACCEPTED, 31 EXISTING, 262 PROPOSED, 7 DEFERRED); 17 ADRs; and 41 Mermaid diagrams. Re-run `python3 scripts/check.py --stats` to recompute these counts after any status or document change.

## 3. Stable decisions inherited from the 1.0.0 compatibility baseline

- `cdin` remains the composition root: build, bundle, release, launcher and integration stay here; domain logic is not reimplemented there.
- `cdin-kernel` is a standalone repository with stable C ABI `1.0.0`; its header is the authority for exact ABI names, fixed-width enum-like types, field order, constants and function signatures.
- The kernel owns canonical document bytes, versioning, editing/history, transactions, snapshots, text/position primitives, supported search and bounded notifications. It has no GUI, frontend, runtime, plugin or filesystem policy.
- Kernel calls are synchronous. A caller-provided lock pair serializes multi-threaded access; without it, the caller must serialize calls. No internal FIFO executor or queue is promised. The lock/linearization order is not a wall-clock FIFO guarantee.
- Frontends own rendering, shaping, bidi, visual layout, wrapping and selection/view state. The kernel stores opaque application blobs only when callers attach them to undo units.
- The backend/OS-services layer owns persistence and file I/O. No `cdin-data`, `cdin-common` or `cdin-shared` repository is created without a new explicit decision.
- The Frontend Protocol is one semantic, versioned interface shared by GUI/TUI/CLI/headless frontends. Its serialized framing, client library, multi-frontend mutation permissions and plugin UI protocol remain separate open decisions.
- The kernel supports literal and raw-byte search in ABI 1.0.0. Regex is explicitly deferred/unsupported, not part of the stable 1.0.0 conformance claim. Unicode data is pinned/queryable per kernel release.
- The next candidate repository is `cdin-runtime`, but extraction is gated on a versioned/tested runtime host API and an integration path through the kernel.

## 4. Kernel package 1.1.0 / ABI 1.0.0 implementation boundary

Implemented kernel features, package-only changes, and deliberately unsupported items are recorded in [kernel/implementation-status.md](../kernel/implementation-status.md). Kernel package `1.1.0` adds distribution/documentation improvements and an internal literal-search fast path without changing public C ABI `1.0.0`; its header continues to declare the Spec `1.0.0` compatibility target. This repository's Spec release `1.1.0` is a compatible clarification and documentation release; it does not retroactively claim that the kernel implements application-level architecture. Do not infer full Spec implementation from green kernel tests: backend/frontend protocol/runtime/plugin integration is not covered by the kernel repository.

## 5. Remaining open or proposed work

- **Frontend Protocol serialization** and codec/client library: [OD-22](../adr/open-decisions.md), [OD-23](../adr/open-decisions.md).
- **Multi-frontend mutation/control ownership:** [OD-24](../adr/open-decisions.md).
- **Regex engine and syntax for a future ABI:** [OD-09](../adr/open-decisions.md); Kernel ABI 1.0.0 (also in package 1.1.0) returns `CDIN_UNSUPPORTED`.
- **Search normalization and named fold profiles:** [OD-29](../adr/open-decisions.md); Persian/Arabic letter equivalence remains explicit and off by default.
- **Runtime host API / Lua-core boundary:** [OD-30](../adr/open-decisions.md) and the runtime integration gate in [repositories.md](../architecture/repositories.md).
- **Extension UI and canvas capabilities:** [ADR-0011](../adr/ADR-0011-extension-ui.md).
- **Internal text data structure, position mapping and architecture-specific optimization:** [OD-01](../adr/open-decisions.md), [OD-28](../adr/open-decisions.md), [ADR-0016](../adr/ADR-0016-arch-specific-optimizations.md).

## 6. Contradictions found and resolutions

| Finding | Resolution in this release |
|---|---|
| Earlier docs described a FIFO mutation executor and queued shutdown semantics, but Kernel ABI 1.0.0 executes API calls synchronously (now shipped in package 1.1.0). | Corrected concurrency and editing diagrams/requirements; recorded [ADR-0017](../adr/ADR-0017-kernel-synchronous-concurrency.md). |
| Kernel API names and exact layouts were called open despite a concrete published header. | Resolved OD-17 against the v1.0.0 header; Frontend Protocol encoding remains separate. |
| Regex was labelled accepted/provided in parts of the Spec, but the kernel explicitly returns `CDIN_UNSUPPORTED`. | SEARCH-004 is retained and marked `DEFERRED`; no regex support claim is made. |
| Notification unsubscribe documentation claimed subscriptions remained allocated until kernel destruction. | Kernel code/docs and regression vector now specify invalidation/free on unsubscribe and `CDIN_INVALID_HANDLE` on subsequent use. |
| The kernel Makefile passed the P3 executable as an argument to P1 instead of running P1 and P3 separately, and a few P1 assertions reflected pre-1.0 assumptions. | Fixed separate build/run rules; made failure injection honor `details` and `accepted_seq` semantics; corrected transaction reads and history blob setup; added 2,000-cycle unsubscribe churn coverage. |
| The kernel feature mask omitted locking support despite implementing a caller lock vtable. | ABI 1.0.0 advertises `CDIN_FEAT_LOCKING`; documentation states the caller still owns the mutex and must serialize when not configured. |
| `docs/decisions/` duplicated and drifted from `docs/adr/`. | Removed duplicate ADR copies; `docs/adr/` is the only canonical record. Root legacy reference pages are compatibility pointers. |

## 7. Verification record

### Spec repository

- `python3 scripts/check.py`: **PASS** — requirement IDs, links, references, index completeness and diagram types. Final local stats: 65 Markdown files, 396 normative requirements, 17 ADRs and 41 Mermaid diagrams.
- `python3 scripts/check.py --render`: structural checks **PASS**; diagram rendering was **skipped** because `mmdc` (Mermaid CLI) is not installed in this environment. Mermaid source has not been rendered in a browser here.
- The Spec repository contains no executable product test runner by design. Its structural check does not verify implementation behaviour.

### Kernel repository

Against the supplied `cdin-kernel` package 1.1.0 source snapshot, `make clean && make all shared ffi-shared quickstart check` **PASS** on this Linux workspace; this includes the normal conformance vectors and P1/P3 regression/concurrency tests. `bash scripts/check-public-header.sh` **PASS** (C11/C++17 header compile). These are local results only; they do not establish macOS/Windows CI, sanitizer/fuzzer smoke coverage, a Docker image build, or a Docker Hub push in this run.

### CDIN composition repository

The `cdin` integration gate remains open in this environment because SDL3 development headers are not installed and the supplied test baseline is empty/unusable. The exact failure is an integration/build-environment blocker, not proof that the editor source is otherwise broken or fully correct. Before extracting `cdin-runtime`, the composition root must build/start with documented dependencies, create a document through the public kernel ABI, edit it, observe a change notification, and prove that no second canonical document/history store exists.

## 8. Next step

Do not create the runtime repository blindly. First land the kernel integration spike in `cdin`: consume the public ABI 1.0.0 header, validate the ABI major at startup, run one create/edit/notify/read path, then document the runtime host surface. Once that gate is green, create `cdin-runtime` as the next repository.
