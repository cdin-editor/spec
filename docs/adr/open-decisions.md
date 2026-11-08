# Open Decisions Register

Every unresolved or not-yet-confirmed question, with importance, options, trade-offs and dependencies.

**Columns.** *Importance*: how much else depends on it (High / Medium / Low). *Disposition*: `OPEN`, `PROPOSED`, `DEFERRED`, or `RESOLVED` (the contract decision is recorded; implementation gaps may still exist). A resolved high-level decision does not close separate lower-level decisions.

## Summary

| ID | Question | Importance | Disposition |
|---|---|---|---|
| [OD-01](#od-01) | Piece Table or Piece Tree; internal structure | Medium | `RESOLVED` |
| [OD-02](#od-02) | Final position representation and byte-to-code-point conversion contract | High | `RESOLVED` |
| [OD-03](#od-03) | Nested transactions and rollback details | Low | `RESOLVED` |
| [OD-04](#od-04) | Grouping consecutive typing for undo | Medium | `RESOLVED` |
| [OD-05](#od-05) | Selection ownership and interaction with undo | High | `RESOLVED` by ADR-0007 |
| [OD-06](#od-06) | Document id reuse and stale handles | High | `RESOLVED` |
| [OD-07](#od-07) | Reads during an active transaction | Medium | `RESOLVED` |
| [OD-08](#od-08) | Subscriber recovery after lost notifications | Medium | `RESOLVED` |
| [OD-09](#od-09) | Regex engine and guaranteed syntax | High | `OPEN` (direction proposed) |
| [OD-10](#od-10) | Unicode version policy | Medium | `RESOLVED` by ADR-0010 |
| [OD-11](#od-11) | Search at the boundary of valid and invalid UTF-8 | Medium | `PROPOSED` |
| [OD-12](#od-12) | Frontend repository structure; GUI and TUI separation | Medium | `RESOLVED` |
| [OD-13](#od-13) | General hot-swap policy | Low | `DEFERRED` |
| [OD-14](#od-14) | State transfer on module swap | Low | `DEFERRED` |
| [OD-15](#od-15) | Backend/host responsibilities from source review | High | `RESOLVED` |
| [OD-16](#od-16) | Persistence, serialization and storage responsibility | Medium | `RESOLVED` |
| [OD-17](#od-17) | Final API names and public C ABI layout | High | `RESOLVED` by Kernel ABI 1.0.0 |
| [OD-18](#od-18) | Shutdown with operations in flight | Medium | `RESOLVED` |
| [OD-19](#od-19) | Resource limits, cancellation, expensive regex | High | `RESOLVED` |
| [OD-20](#od-20) | Identifier behaviour in a close-versus-new-request race | High | `RESOLVED` |
| [OD-21](#od-21) | Other writers during an active transaction: reject or queue | Medium | `RESOLVED` |
| [OD-22](#od-22) | Encoding of the serialized protocol | Medium | `RESOLVED` by ADR-0018 |
| [OD-23](#od-23) | Protocol client library and where it lives | Medium | `RESOLVED` by ADR-0018 |
| [OD-24](#od-24) | Several frontends attached: who may mutate | Medium | `RESOLVED` by ADR-0018 |
| [OD-25](#od-25) | Plugin UI: declarative widgets and canvas | High | `RESOLVED` |
| [OD-26](#od-26) | Visual layout ownership confirmation | High | `RESOLVED` by ADR-0006 |
| [OD-27](#od-27) | Parallel mutation of different documents | Low | `DEFERRED` |
| [OD-28](#od-28) | Position-mapping helper (anchors, markers) in the kernel | Medium | `OPEN` |
| [OD-29](#od-29) | Search normalization and folding options in the first version | Medium | `OPEN` |
| [OD-30](#od-30) | UI core stays in Lua or becomes native | Medium | `RESOLVED` |
| [OD-31](#od-31) | Name of the specification repository | Low | `OPEN` |
| [OD-32](#od-32) | Lua-to-native bridge behind the Runtime Host API | Medium | `RESOLVED` by ADR-0019 |
| [OD-33](#od-33) | Native IME composition lifecycle and commit authority | High | `RESOLVED` by ADR-0023 |
| [OD-34](#od-34) | Semantic PaneTree splitter resize protocol | High | `RESOLVED` by ADR-0024 |

---

## OD-01

**Resolution:** `RESOLVED`. Internal storage is not a public contract. The Kernel 1.2.1 copy-on-write block and cached line index are implementation details; a future release may replace them without changing the ABI, provided observable byte/version semantics remain stable.
**Piece Table or Piece Tree; internal structure.**
Importance: Medium. Depends on: KERNEL-012 (the structure is invisible in contracts).
- *Piece table (array/list):* simplest; edits are O(pieces); good for modest edit counts; poor for very long edit histories without compaction.
- *Piece tree (balanced tree over pieces):* O(log n) edits and offset lookup; more complex; the choice for the 1 GB case.
- *Rope or gap buffer:* not preferred by the owner's direction.
Trade-off: complexity against worst-case behaviour. Because the structure is hidden, the choice does not block contracts. Resolve with a spike measuring the 1 GB case (SPEC-033).

## OD-02

**Resolution:** `RESOLVED`. The canonical position is a 64-bit byte offset; ranges are half-open. Code-point, line and grapheme values are derived through the published conversion APIs.
**Final position representation and conversion contract.**
Importance: High. Depends on: POS-001 to POS-052.
Proposal: byte offset is canonical; code point, line and grapheme are derived (POS-010, POS-030). Alternatives: code-point-canonical (breaks raw regions), line/column-canonical (ambiguous across line endings). Trade-off: byte offsets are exact and storage-independent but require callers to convert for user-facing behaviour.

## OD-03

**Resolution:** `RESOLVED`. ABI 1.1.0 supports one active transaction per document. A nested `begin` returns `INVALID_STATE`. Nested transactions and savepoints remain future work and are not part of this accepted contract.
**Nested transactions and rollback details.**
Importance: Low. Proposal: not supported in the first version (TXN-020); revisit with savepoints (TXN-021). Option: nested with partial rollback. Trade-off: simplicity and predictable rollback cost against composability of commands.

## OD-04

**Resolution:** `RESOLVED`. Undo coalescing uses a caller-supplied non-zero key. The Runtime decides when the key changes (pause, cursor movement, word boundary); the Kernel does not infer timing policy.
**Grouping consecutive typing for undo.**
Importance: Medium. Proposal: caller supplies a coalesce key; the kernel merges adjacent units with equal non-zero key (UNDO-010). Options: kernel-side time window (breaks determinism), kernel-side word-boundary heuristics (embeds editor policy). Trade-off: policy stays in the runtime, mechanism in the kernel.

## OD-05
**Selection ownership and interaction with undo.**
Importance: High. `RESOLVED` by [ADR-0007](ADR-0007-selection-ownership.md): the view owns selections; the kernel stores opaque before/after blobs per undo unit (UNDO-020). Kernel-managed markers remain a separate question (OD-28). Options considered: kernel-owned selections (couples the kernel to editor behaviour and multi-view semantics); kernel-managed markers. Trade-off: kernel stays generic against slightly more caller work.

## OD-06

**Resolution:** `RESOLVED`. Public handles are 64-bit slot/generation values. Generation changes on release; exhausted slots are retired rather than wrapped. Stale and never-issued handles return `INVALID_HANDLE`.
**Document id reuse and stale handles.**
Importance: High. Proposal: index plus generation, generations never reused in a process (DOC-005). Option: monotonically increasing ids with a lookup table. Trade-off: constant-time detection against a 64-bit budget split.

## OD-07

**Resolution:** `RESOLVED`. Ordinary document reads observe the last committed content while a transaction is active. Only the transaction handle reads tentative content.
**Reads during an active transaction.**
Importance: Medium. Proposal: other readers see the last committed version; only the transaction handle sees tentative state (CONC-012). Option: readers block until commit (stall risk); readers see tentative state (breaks snapshot isolation).

## OD-08

**Resolution:** `RESOLVED`. Each subscriber has a bounded queue. Overflow drops pending event details and produces one `RESYNC` marker carrying the current version; clients must obtain a fresh snapshot.
**Subscriber recovery after lost notifications.**
Importance: Medium. Proposal: bounded queues; overflow collapses to one `RESYNC` marker (NOTIF-007). Option: unbounded queues (violates ARCH-021); sequence numbers with a replay buffer (more memory, more state).

## OD-09
**Regex engine and guaranteed syntax.**
Importance: High. `OPEN` for a future version and explicitly outside Runtime v1. Kernel ABI 1.1.0 does not provide a supported Regex engine; the Regex search mode returns `CDIN_UNSUPPORTED` and no enabled feature capability is advertised. Runtime MUST NOT create a second canonical document store or silently substitute a different Regex engine. Any later adoption needs a portable engine decision, a syntax contract, resource-limit/cancellation vectors and an owner-approved ADR. See [ADR-0009](ADR-0009-regex-engine.md).

## OD-10
**Unicode version policy.**
Importance: Medium. `RESOLVED` by [ADR-0010](ADR-0010-unicode-version.md): each kernel release pins a queryable Unicode data version (POS-032). Tracking latest at build time and runtime-selectable versions were rejected for reproducibility/complexity reasons.

## OD-11
**Search at the boundary of valid and invalid UTF-8.**
Importance: Medium. `PROPOSED`; do not promote until normative Kernel conformance vectors define malformed-sequence classification, including maximal-subpart boundaries and matches adjacent to raw bytes. Runtime MUST preserve document bytes and MUST NOT normalize, repair or independently reinterpret malformed UTF-8. Display decoding policy belongs to Frontend; canonical byte offsets and search classification belong to Kernel. Unicode-aware modes and `bytes` mode retain the distinctions specified by SEARCH-040 to SEARCH-042.

## OD-12

**Resolution:** `RESOLVED`. One Frontend repository contains peer `core`, `gui-sdl`, `tui` and `headless` adapters. Shared protocol abstractions do not imply a shared renderer; see ADR-0020.
**Frontend repository structure; GUI and TUI separation.**
Importance: Medium. Proposal: one repository with a directory per frontend until a frontend needs its own release cadence (ARCH-030, ARCH-033). Options: repository per frontend now; GUI/TUI sharing a UI core (rejected for now: the protocol is the shared layer, see [ADR-0005](ADR-0005-frontend-protocol.md)).

## OD-13
**General hot-swap policy.** Importance: Low. `DEFERRED`; see [ADR-0013](ADR-0013-hot-swap.md).

## OD-14
**State transfer on module swap.** Importance: Low. `DEFERRED`; see [ADR-0013](ADR-0013-hot-swap.md).

## OD-15
**Backend/host responsibilities from source review.**
Importance: High. `RESOLVED` by the ownership matrix below. This resolves design ownership, not implementation completeness.

| Responsibility | Owner |
|---|---|
| Canonical document bytes, versions, transactions, snapshots, undo/redo, notifications and search | Kernel |
| Kernel lifecycle, public ABI adapter, ABI/feature validation | Backend |
| `lua_State`, PUC Lua 5.4 callbacks/userdata and Runtime owner-thread enforcement | Backend |
| Host API descriptor, document services, status translation, OS services and save/load I/O | Backend |
| Commands, keymaps, editor policy, document clients, selections, semantic UI model and plugin lifecycle | Runtime |
| Protocol codec/server, transport/session roles, per-client projection queues, ACK/backpressure/resync | Backend / shared Protocol contract |
| Geometry, grapheme visual movement, wrapping, shaping, bidi, rendering and terminal/pixel I/O | Frontend |
| Extension bundle/index, remote install and discovery catalog | CDIN composition / `cdin-x` |

## OD-16
**Persistence, serialization and storage responsibility.**
Importance: Medium. `RESOLVED` in line with [ADR-0008](ADR-0008-persistence-outside-kernel.md): Kernel accepts/returns bytes and owns document state; it performs no filesystem I/O. Runtime owns editor save policy (when, which path, clean-state policy and user-facing command semantics). Backend owns filesystem access, atomic read/write, path/platform services and failure mapping. Runtime requests a version-pinned snapshot; the document is marked clean only if that saved version is still current (for example, through a version-conditional clean-state operation). No separate `cdin-data` repository is created unless a second consumer justifies it.

## OD-17
**Final API names and public C ABI layout.**
Importance: High. `RESOLVED` for the Kernel by its published ABI major 1 public header. The current header declares ABI `1.1.0`; additive v1.1 logging API details are recorded in [ABI compatibility](../architecture/abi-and-compatibility.md). Existing function names, field widths, numeric identities, layouts and prototypes remain compatible. Frontend Protocol wire decisions are resolved by ADR-0018 and the Lua bridge by ADR-0019; Runtime Host API compatibility remains a separate implementation gate.

## OD-18

**Resolution:** `RESOLVED`. Kernel calls are synchronous. Graceful and abort shutdown mode values have equivalent behavior in ABI 1.1.0: reject new mutations, abort active transactions and tear down deterministically. There is no queued work to drain.
**Shutdown with operations in flight.**
Importance: Medium. Proposal: two modes, graceful and abort (CONC-020, CONC-021). Option: single mode (always graceful) is simpler but can hang on a long search; mitigated by cancellation.

## OD-19

**Resolution:** `RESOLVED`. Current literal/byte search supports bounded candidate steps, cancellation and optional partial results; resource limits are configured and surfaced as typed limit details. Expensive future engines such as Regex remain outside this resolution (OD-09).
**Resource limits, cancellation, expensive regex.**
Importance: High. Proposal: limits at creation, step-counted bounds, cancellation tokens (KERNEL-013, SEARCH-013, SEARCH-052). Option: wall-clock timeouts (violates determinism, KERNEL-007).

## OD-20

**Resolution:** `RESOLVED`. Close and ordinary calls serialize at the configured caller lock (or caller-managed serialization point). A call that resolves the handle after close receives `INVALID_HANDLE`; ABI 1.1.0 makes no wall-clock FIFO claim and has no asynchronous request queue.
**Identifier behaviour in a close-versus-new-request race.**
Importance: High. Proposal: `close` is an ordered request; later requests see `INVALID_HANDLE` (DOC-030). Option: reference-counted documents keeping closed documents alive for in-flight requests (more state, more races).

## OD-21

**Resolution:** `RESOLVED`. A mutation on a document with an active transaction, when not issued through that transaction, returns `BUSY`. The Kernel does not queue or retry that writer; retry policy belongs to the caller/Backend.
**Other writers during an active transaction: reject or queue.**
Importance: Medium. Proposal: reject with `BUSY` (CONC-013, TXN-007). Option: queue behind the transaction (hides contention, can stall all writers on one document). Trade-off: explicitness against caller retry logic.

## OD-22
**Encoding of the serialized protocol.**
Importance: Medium. **RESOLVED** by [ADR-0018](ADR-0018-frontend-protocol-wire.md): deterministic CBOR (RFC 8949 deterministic profile) inside a four-byte unsigned big-endian length prefix. Definite-length values only; document and paste data uses CBOR byte strings, never UTF-8 coercion. Default frame body cap is 1 MiB. The decoder rejects duplicate map keys, non-shortest integer/length encodings, invalid UTF-8 text, indefinite-length values, all CBOR floating-point values, truncated frames and trailing bytes. `proto.codec.binary_roundtrip` verifies the binary-safe round trip.

## OD-23
**Protocol client library and where it lives.**
Importance: Medium. **RESOLVED** by [ADR-0018](ADR-0018-frontend-protocol-wire.md): the C reference codec is the standalone `cdin_protocol` target inside `cdin-editor/backend`, exposed through installed `include/cdin/protocol.h` and independent of Kernel, Lua, GUI and OS services. This preserves the design-only scope of `spec` and avoids a new repository. Other language clients implement the published wire contract and consume the shared conformance vectors; they do not link `cdin_backend` or `cdin-kernel` merely to encode/decode a protocol frame.

## OD-24
**Several frontends attached: who may mutate.**
Importance: Medium. **RESOLVED** by [ADR-0018](ADR-0018-frontend-protocol-wire.md): one attached driver lease and zero or more observers. The first attached client receives the lease; observers cannot send editor-mutating events or commands. On driver detach/close, the oldest still-attached client is promoted in connection order. ACKs and read-only line-range requests are allowed for observers. Protocol v0.2.0 has no last-writer-wins mode.

## OD-25

**Resolution:** `RESOLVED`. Declarative widgets are the default plugin UI contract; free-form drawing is an optional `canvas` capability and must degrade gracefully when absent. See accepted ADR-0011 and ADR-0020.
**Plugin UI: declarative widgets and canvas.**
Importance: High. See [ADR-0011](ADR-0011-extension-ui.md). Changes the extension contract; needs owner approval (ARCH-027).

## OD-26
**Visual layout ownership confirmation.**
Importance: High. `RESOLVED` by [ADR-0006](ADR-0006-visual-layout-ownership.md): frontends own visual layout, shaping, bidi, wrapping and scroll state; kernel positions remain logical/byte-based.

## OD-27
**Parallel mutation of different documents.**
Importance: Low. `DEFERRED` (DOC-050). Option: a future API may allow different documents to execute in parallel, but it would need an explicit order contract. ABI 1.0.0 serializes entry through the configured lock or caller-side serialization; there is no internal executor or FIFO queue. Trade-off: throughput against a weaker global order.

## OD-28
**Position-mapping helper in the kernel.**
Importance: Medium. Options: clients transform positions from change events (POS-050; no kernel state per client); kernel-managed anchors with a bias (convenient; kernel stores per-client state, bounded and counted against limits). Decide after the first runtime port shows how much transformation code is needed.

## OD-29
**Search normalization and folding options in the first version.**
Importance: Medium. Which of NFC/NFD normalization, mark-insensitive matching, and named fold profiles ship first (SEARCH-023). Persian-specific equivalences (for example the Persian/Arabic letter pairs) MUST stay explicit and off by default (SEARCH-021, SEARCH-022). Options: ship none in v1; ship normalization and mark-insensitivity; ship profiles.

## OD-30

**Resolution:** `RESOLVED`. Runtime UI policy remains in PUC Lua 5.4; native C owns protocol, platform event/input integration and rendering adapters. Backend owns the bridge and is the only component allowed to call the Kernel ABI; see ADR-0019 and ADR-0020.
**UI core stays in Lua or becomes native.**
Importance: Medium. Proposal: stays in Lua (it is about 7.3 thousand lines of policy today). Option: native UI core later if performance or portability requires it. Recorded because the owner has not yet answered it.

## OD-31
**Name of the specification repository.**
Importance: Low. The repository is `cdin-editor/spec`; the owner has also called it "cdin-spec" in conversation. Proposal: keep `spec` (the organization already scopes it).

## OD-32
**Lua-to-native bridge behind the Runtime Host API.**
Importance: Medium. **RESOLVED** by [ADR-0019](ADR-0019-runtime-bridge.md): PUC Lua 5.4 C API is the only supported v1 bridge. Backend owns the Lua state and native callbacks; all calls occur on the Runtime owner thread. Kernel pointers and handles remain private to the Backend adapter and are never exposed to Runtime extensions. LuaJIT FFI and MetaCall are not v1 targets. This does not add a dependency to `cdin-kernel`. A production release still requires the live bridge, Lua/Kernel round-trip tests and the complete platform matrix.


## OD-33

**Resolution:** `RESOLVED` by [ADR-0023](ADR-0023-ime-composition-contract.md). The optional `ime-composition/1` lifecycle is accepted as a Protocol 1.0.0 extension. Native preedit remains local to the originating Frontend; Backend validates capability, Driver role, lifecycle and exactly-once admission; Runtime validates the captured view/version/selection and owns committed text; Kernel sees only the committed edit. Capability advertisement remains disabled until the complete Frontend/Backend/Runtime implementation and CDIN live conformance path pass.

**Native IME composition lifecycle and commit authority.**
Importance: High. A committed-only `input.text` path cannot represent preedit cancellation or safely bind a composition to a view/version. The accepted optional capability preserves Protocol 1.0 peers and the component ownership boundaries. Implementation remains tracked separately.

## OD-34

**Resolution:** `RESOLVED` by [ADR-0024](ADR-0024-pane-tree-splitter-resize.md). Splitter manipulation is an optional `pane-splitter-resize/1` capability. Frontend owns geometry, pointer lifecycle and local preview; Backend owns authorization, revision validation and ordered atomic publication; Runtime owns the semantic split ratio and layout revision. `input.mouse.target` remains a Runtime View ID. Pixel rectangles are never protocol or Runtime state. Capability advertisement remains disabled until all owning implementations and CDIN live conformance tests pass.

**Semantic PaneTree splitter resize protocol.**
Importance: High. The GUI has hit-testing/geometry but cannot mutate authoritative PaneTree state before a protocol and owner-thread operation exists. The accepted contract prevents Frontend-only mutation and keeps the existing Protocol 1.0 behavior as the fallback.
