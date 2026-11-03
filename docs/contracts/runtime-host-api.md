# Runtime Host API 1.0.0

> Normative contract owned by the CDIN Spec. Backend provides it; Runtime consumes it. The companion Backend and Runtime repositories may add implementation notes but MUST NOT redefine this contract.

**Status:** stable public Backend-to-Runtime contract, version 1.0.0.

This API is the only route from `cdin-runtime` to the Backend. The Backend owns
the native Kernel adapter, OS services and frontend transport. Runtime must not
load the Kernel shared library, call C ABI symbols, inspect Kernel structs or
keep a shadow copy of document bytes/history.

The contract is aligned with CDIN Kernel C ABI `1.1.0` (Kernel package `1.2.1`)
and CDIN Spec `1.4.0`. ABI `1.1.0` is the first release with the Kernel logging
API that section 5 depends on. The companion Backend source implements the C
adapter; live Lua 5.4 + Kernel integration remains a separate verification gate.

## 1. Host descriptor and version negotiation

`host:info()` returns data equivalent to:

```lua
{
  host_api = { major = 1, minor = 0, patch = 0 },
  kernel_abi = { major = 1, minor = 1, patch = 0 },
  extension_contract = { major = 1, minor = 0 },
  frontend_protocol = { major = 1, minor = 0, patch = 0 },
  features = {
    documents = true, notifications = true, snapshots = true,
    transactions = true, batch_edits = true, literal_search = true,
    ui_model = true, document_lines = true, frontend_events = true, logging = true,
  },
  kernel_features = {
    transactions = true, snapshots = true, notifications = true,
    batch = true, search_literal = true, search_bytes = true,
    search_regex = false,
  },
  logging = {
    provider = "cdin-kernel",
    levels = { "error", "warn", "info", "debug", "trace", "fatal" },
    max_message_bytes = 16384,
  },
}
```

Host API `1.x` follows stable semantic-version compatibility: the provided
major must equal `1` and the provided minor must be at least the required minor
(`1.0`). Additive minor versions are compatible; a different major or an older
minor is rejected. Patch versions do not change the contract shape. Kernel ABI
requires major `1`, minor `>= 1`; the extension contract requires major `1`.
Frontend Protocol follows the accepted wire compatibility rule: the major must be `1` and the provided minor must be
at least the required minor (`1.0`). Additive `1.x` minor versions are
compatible; a different major is rejected. Protocol `0.2.x` is intentionally
rejected because its wire schema is incompatible. Backend owns optional
capability negotiation.

Host API 1.0.0 freezes the method names, argument/result shapes, byte-offset
conventions, ownership/lifetime rules, owner-thread rule, required capability
set, stable error-code vocabulary, and the Kernel ABI 1.1.0 minimum described
in this document. A compatible 1.x minor may add optional methods, fields, or
capabilities; it must not change existing meanings or make an optional item
required. A breaking change requires Host API 2.0.0. Unknown additive descriptor
fields must be ignored; unknown required capabilities must fail closed. See [ADR-0018](https://github.com/cdin-editor/spec/blob/main/docs/adr/ADR-0018-frontend-protocol-wire.md)
and [Protocol version evolution](https://github.com/cdin-editor/spec/blob/main/docs/architecture/protocol-wire.md#version-evolution).

The Backend must query `cdin_abi_version()` and `cdin_features()` before
creating the Lua Runtime and report the negotiated result accurately. For
Kernel ABI 1.1.0, `search_regex` must be `false`; advertising unsupported regex
is a contract violation. Runtime never performs native version queries itself.

## 2. Calling conventions and error mapping

Services are Lua objects called with `:`. Success values are documented below.
Failures throw a structured table:

```lua
{
  domain = "cdin.runtime",
  code = "STALE_VERSION",
  message = "document version changed",
  details = { expected = 4, current = 5 },
}
```

`code` is stable and machine-readable; `message` is diagnostic text. The
Backend must preserve Kernel status identities and details, including:

| Kernel status | Lua `code` |
|---|---|
| `CDIN_OK` | success; no exception |
| `CDIN_INVALID_ARGUMENT` | `INVALID_ARGUMENT` |
| `CDIN_INVALID_HANDLE` | `INVALID_HANDLE` |
| `CDIN_STALE_VERSION` | `STALE_VERSION` |
| `CDIN_OUT_OF_RANGE` | `OUT_OF_RANGE` |
| `CDIN_INVALID_POSITION` | `INVALID_POSITION` |
| `CDIN_INVALID_STATE` | `INVALID_STATE` |
| `CDIN_BUSY` | `BUSY` |
| `CDIN_LIMIT_EXCEEDED` | `LIMIT_EXCEEDED` |
| `CDIN_NO_MEMORY` | `NO_MEMORY` |
| `CDIN_PATTERN_INVALID` | `PATTERN_INVALID` |
| `CDIN_CANCELLED` | `CANCELLED` |
| `CDIN_SHUTDOWN` | `SHUTDOWN` |
| `CDIN_UNSUPPORTED` | `UNSUPPORTED` |
| `CDIN_BUFFER_TOO_SMALL` | `BUFFER_TOO_SMALL` |
| `CDIN_VERSION_MISMATCH` | `VERSION_MISMATCH` |
| `CDIN_INTERNAL` | `INTERNAL` |

The Backend must preserve `expected/current`, `requested/length`, `required`,
`limit_id` and other relevant details. Numeric `CDIN_LIMIT_*` values pass
through unchanged: `0` none, `1` documents, `2` document size, `3` edit size,
`4` undo memory, `5` blob size, `6` snapshots, `7` subscribers, `8` search
steps, `9` transaction memory, `10` batch edits, `11` version, `12` sequence.

No C pointer or Kernel handle is exposed to extensions. Host handles are opaque
Backend-created Lua values and may be userdata.

## 3. Required `host.documents` service

The service must implement these methods. The runtime assumes Kernel mutations
are synchronous for ABI 1.1.0.

### Document lifecycle and reads

- `create(initial_bytes, metadata?) -> { handle, version, length }`
- `close(handle) -> true`
- `read(handle, { start, length, expected_version? }) -> { bytes, version, total_length, flags? }`
- `read_lines(handle, { first_line, line_count, expected_version, max_bytes? }) -> { version, first_line, total_lines, lines: array<byte-string> }`
- `acquire_snapshot(handle) -> { handle, version, length }`
- `read_snapshot(snapshot_handle, { start, length }) -> { bytes, version }`
- `release_snapshot(snapshot_handle) -> true`

When `expected_version` is omitted or `nil`, `read` returns metadata for the
latest version; `start = 0, length = 0` is the metadata-only resync path. Reads return caller-owned transient strings. `read_lines` returns a bounded, version-pinned
window; each line is an exact byte string including its original EOL bytes. The Backend
may return a complete prefix when `max_bytes` is reached; it never splits a line.
`DocumentClient` must not store read results on itself. Snapshot handles are pinned
leases and must be released.

### Mutations and history

- `replace(handle, request) -> edit_result`
- `replace_batch(handle, request) -> edit_result`
- `undo(handle, { expected_version, blob_capacity }) -> edit_result`
- `redo(handle, { expected_version, blob_capacity }) -> edit_result`
- `begin_transaction(handle, { expected_version }) -> { handle, base_version }`
- `transaction_replace(transaction_handle, edit) -> result`
- `transaction_read(transaction_handle, { start, length }) -> { bytes, total_length }`
- `commit_transaction(transaction_handle, { undo_blob_before, undo_blob_after }) -> edit_result`
- `abort_transaction(transaction_handle) -> true`
- `mark_clean(handle) -> true`
- `mark_clean_if_version(handle, saved_version) -> boolean`
- `is_clean(handle) -> boolean`

`replace` requests use zero-based half-open byte ranges `[start, finish)`, the
expected current version, optional `coalesce_key`, and opaque selection blobs
before/after the edit. Batch edits are ascending, non-overlapping ranges in the
same pre-edit version and form one undo unit. Returned `accepted_seq` indicates
the Kernel accepted the operation; it does not promise later notifications
cannot report an issue.

For transactions, tentative content is owned by Kernel. Runtime retains only the
opaque transaction handle and offset metadata needed for view transformation.
It must explicitly commit or abort. On close, outstanding transactions are
aborted best-effort before the document is closed.

The Kernel ABI's `mark_clean` has no expected-version argument. Backend must
implement `mark_clean_if_version` as a serialized version comparison plus
`cdin_doc_mark_clean` in one critical section. It returns `false` if the
current document version differs from `saved_version`.

### Notifications

- `subscribe(handle) -> { handle, version }`
- `unsubscribe(subscription_handle) -> true`
- `drain(subscription_handle, max_events) -> array of normalized notifications`

Notifications are scoped to their subscribed document and use Kernel event
kinds: `EDIT`, `BATCH`, `TRANSACTION`, `UNDO`, `REDO`, `RELOAD`, `CLOSED`,
`HISTORY_EVICTED`, `RESYNC`, and `SAVED_STATE_CHANGED` where applicable. Preserve
`from_version`, `to_version`, `current_version`, `edit_count`, `edits_stored`,
`edits_truncated` and `edits`. Each edit is `{ start, removed, inserted }`; for
sequential operations, each `start` refers to the content state immediately
before that edit. If edit data is truncated, or the version chain has a gap,
Runtime refreshes metadata and discards incremental assumptions. It never
replays a partial edit list.

Kernel wakeup callbacks may signal the Backend event loop only. They must never
call Lua from a non-owner thread. Backend calls `runtime:pump_notifications()`
on the Lua owner thread.

### Search

`search(handle, { pattern, mode, direction, from, bound, limit, expected_version, case_insensitive, any_newline, step_limit }) -> result`

Supported modes are `literal` and `bytes`. `regex` must return `UNSUPPORTED`
for Kernel ABI 1.1.0. Kernel resource-limit failures are recoverable outcomes,
not internal Runtime crashes.

## 4. Required `host.ui` service

`host.ui:publish(model_snapshot) -> true`

The model is serializable semantic state. Backend validates it and projects it to
Frontend Protocol 1.0.0 messages on the Lua owner thread. Every publication is a
complete snapshot ending in one `ui.flush`; Frontends replace projected model state
atomically at that boundary. Runtime does not know which frontends are attached and
does not draw. `view.request_lines` is answered from the Kernel through `read_lines`.

## 5. Required logging service

CDIN has one logger: the Kernel's (`m-mdy-m/log.c`, owned by the Kernel and
reached through the C ABI). Runtime does not bind `log.c`, create a logger, or
choose an output. The Backend, Frontend and `cdin` write to the same Kernel
logger and Runtime reaches it through this service.

`host:log(level, message, fields?) -> boolean`

- `level` is one of `error`, `warn`, `info`, `debug`, `trace`, `fatal`. The
  Backend maps each name to the Kernel value (`CDIN_LOG_ERROR` 0, `WARN` 1,
  `INFO` 2, `DEBUG` 3, `TRACE` 4, `FATAL` 5). The numeric values are not ordered
  by severity, so any threshold comparison must use severity order, not the
  numbers.
- `message` is a UTF-8 string no longer than `info.logging.max_message_bytes`.
  Runtime truncates longer messages itself on a character boundary.
- `fields` is a flat table of strings, numbers and booleans (at most 16 entries;
  string values at most 256 bytes). The reserved field `component` names the
  record's source and is always set by Runtime.
- The Backend forwards the record to `cdin_kernel_log(kernel, level, component,
  message)`. It may append the remaining fields to the message text; the Kernel
  API has no structured fields. It must not create another logger.
- Return `true` when the Kernel accepted the record and `false` when it was not
  recorded (below the Kernel threshold, or `CDIN_UNSUPPORTED` because logging is
  disabled). Dropping a record is not an error and must not raise. Raising is
  reserved for an invalid call (unknown level, non-string message).
- `info.logging.provider` must equal `"cdin-kernel"`. A Host that names another
  provider, omits the descriptor, lacks a level, or reports a
  `max_message_bytes` outside `1..1048576` is rejected at startup with
  `HOST_API_MISMATCH`, as is any Kernel ABI below `1.1.0`.

Components are how layers are told apart in the shared logger:

| Source | Component |
|---|---|
| Kernel | `cdin-kernel` (default) |
| Runtime | `cdin-runtime`, `cdin-runtime.documents`, `cdin-runtime.saver`, `cdin-runtime.extension`, `cdin-runtime.extension.<name>` |
| Backend / Frontend / `cdin` | `cdin-backend`, `cdin-frontend`, `cdin` (convention; owned by those projects) |

Known limitation: `cdin_kernel_log` always stamps the layer `kernel` and the
`[KERNEL]` prefix, so records from Runtime are distinguished by component only.
A per-layer prefix would need an additive Kernel ABI change.

Runtime never writes to stdout/stderr. A logging failure never changes the
result of the operation being logged: the Runtime logger catches Host errors and
counts them (`runtime:log_stats()`). Records contain ids, versions, sizes and
error codes, never document bytes or file paths.

## 6. Optional atomic-save service

`host.fs` may provide:

- `begin_atomic_write(path, options) -> writer_handle`
- `write_chunk(writer_handle, bytes) -> true`
- `commit_atomic_write(writer_handle) -> true`
- `abort_atomic_write(writer_handle) -> true`

The runtime writes a version-pinned snapshot in bounded chunks, commits the
atomic replacement, then calls `mark_clean_if_version`. This service is optional
at startup but required for the built-in `document.save` command.

## 7. Kernel ABI mapping

| Runtime operation | Kernel ABI 1.1.0 symbol family |
|---|---|
| `create` / `close` | `cdin_doc_create` / `cdin_doc_close` |
| `read` | `cdin_text_version`, `cdin_text_len`, `cdin_text_read` |
| snapshot lease | `cdin_snapshot_acquire`, `cdin_snapshot_release`, `cdin_text_*` via `cdin_src_snap` |
| replace / batch | `cdin_doc_replace`, `cdin_doc_replace_batch` |
| transaction | `cdin_txn_begin`, `cdin_txn_replace`, `cdin_txn_len`, `cdin_txn_read`, `cdin_txn_commit`, `cdin_txn_abort` |
| undo / redo | `cdin_doc_undo`, `cdin_doc_redo` |
| dirty state | `cdin_doc_mark_clean`, `cdin_doc_is_clean` plus Backend-side conditional operation |
| notification | `cdin_notif_subscribe`, `cdin_notif_unsubscribe`, `cdin_notif_drain` |
| search | `cdin_search`; literal/bytes only |
| logging | `cdin_kernel_log` (the Backend configures the logger with `cdin_log_options_init`, `cdin_kernel_set_log_options`, `cdin_kernel_set_log_level`) |

The Backend adapter must use only the public `include/cdin/kernel.h` header and
must run the Kernel's conformance vectors through the adapter before declaring
this integration complete.

## 8. Stable compatibility and evolution policy

- Runtime requires Host API `1.0.0` or newer `1.x` minor; it rejects Host API
  `0.x`, `2.x`, and any `1.x` version with a minor below `0` (the latter is
  structurally impossible but remains a validation failure).
- Patch releases correct documentation or implementation defects without
  changing observable contract behavior.
- Minor releases may add optional methods, descriptor fields, error detail
  fields, or capability flags. Additions are capability-gated and must preserve
  behavior for a 1.0 consumer.
- Major releases may remove or change methods, argument/result shapes, error
  identity, ownership, threading, or required capabilities.
- Backend is the provider and source of truth for the descriptor. Runtime is a
  consumer and validates the negotiated descriptor at startup. Runtime does not
  negotiate Kernel ABI or Frontend Protocol independently.
- Kernel ABI `1.1.0` and Frontend Protocol `1.0.0` remain separate version axes.
  Their compatibility rules are not inherited from the Host API version.
