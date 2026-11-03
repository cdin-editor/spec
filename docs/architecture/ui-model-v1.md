# Runtime UI Model `cdin.ui-model.v1`

**Status:** `ACCEPTED` as the Runtime-to-Backend semantic snapshot contract. This document does not transfer rendering, pixel geometry, wrapping, bidi or scroll-in-pixels ownership to Runtime.

## 1. Root object

The root is a map with the following required fields:

| Field | Type | Constraints |
|---|---|---|
| `schema` | text | Exactly `cdin.ui-model.v1` |
| `revision` | uint | Monotonically increases for every published semantic mutation; never wraps |
| `views` | map<text, view> | Keys are stable view IDs; empty map is valid |
| `layout` | map | Logical pane tree snapshot; no rectangles or pixels |
| `panels` | map<text, map> | Declarative panel states keyed by stable panel ID |
| `focus` | text|null | Active view ID or null |
| `prompt` | map|null | Declarative prompt description or null |
| `status` | map | Semantic status fields |
| `theme` | text | Registered theme identifier |
| `options` | map | Required typed options map; it may be empty. Individual keys are optional and defaulted by the frontend. Defined keys: `title:text`, `tab_width:uint` (1..64), `wrap:bool`, `line_numbers:bool`, `relative_line_numbers:bool`, `cursor_shape:text` (`block`, `bar` or `underline`), `cursor_blink:bool`. |
| `styles` | map<text, map> | Resolved semantic role styles for the active theme; no pixel geometry or platform handles |

The root and every nested map MUST contain unique text keys. Values MUST be serializable scalars, arrays or maps; functions, userdata, threads, metatables with executable semantics, cyclic tables and Host/Kernel handles are forbidden. Byte strings are preserved as bytes. Runtime must never place document contents or document handles in this model.

## 2. View object

Every entry in `views` is a map with required fields:

| Field | Type | Constraints |
|---|---|---|
| `id` | text | Equals its containing map key |
| `document_id` | text | Opaque Runtime-side identifier; not a Kernel handle |
| `document_version` | uint | Current Kernel document version observed by Runtime when this snapshot is built |
| `document_length` | uint | Current document length in bytes at `document_version` |
| `selection` | map | Required `anchor:uint`, `caret:uint`; byte offsets |
| `scroll_anchor` | uint | Zero-based byte offset in the document at `document_version`; it is transformed with edits and is never pixels or a visual-line index |
| `focused` | bool | At most one view is true and agrees with root `focus` |
| `visible` | bool | Visibility in the logical pane tree |
| `revision` | uint | View-local revision, nondecreasing |

## 3. Layout tree

The `layout` map has `root:map|null` and `active_leaf:text|null`.

- A leaf has `kind="leaf"`, stable `id:text`, `views:array<text>` and `active_view:text|null`. Every referenced view exists; a non-null `active_view` belongs to `views`.
- A split has `kind="split"`, stable `id:text`, `axis` equal to `horizontal` or `vertical`, `ratio:number` in `(0.1,0.9)`, and `first:map`, `second:map` children. `ratio` is a Runtime-only floating-point value; it is never emitted as a CBOR float.
- IDs are unique within a tree; the tree is acyclic; every view appears exactly once.
- `active_leaf` identifies an existing leaf or is null when the tree is empty.

The Frontend maps the abstract ratio to local geometry. Runtime does not calculate rectangles, font metrics, wrapping or visual-line positions.

## 4. Protocol projection

Backend validates the entire model snapshot before publishing. A valid snapshot is projected into the ordered semantic messages below, followed by one `ui.flush` for each attached client:

1. `ui.options` (`revision`, `theme` and the required typed `options` map, which may be empty).
2. `ui.style_table` (theme style-role registry).
3. `ui.layout` (`revision`, logical layout).
4. `ui.statusline` and `ui.prompt` (`revision`).
5. `view.cursor`, `view.selection` and `view.invalidate` for each visible view. The initial invalidation covers `[0, document_length)` at `document_version`; the frontend requests only the visible line windows.
6. One `ui.panel` message per panel currently present. Omitted panels are removed when the complete snapshot is applied.
7. `ui.flush` with `scope="snapshot"`, the exact model `revision`, and a per-client flush-group `sequence`.

A projection MUST preserve the model revision and document versions. The backend must not synthesize line content from a stale Runtime cache. A model validation or queueing failure leaves the last successfully published revision unchanged for that client and emits a structured diagnostic through the Kernel logger. The snapshot is queued as one atomic batch; partial model groups MUST NOT be visible. The Backend may retain the newest semantic snapshot for a later attach/resynchronization, but it MUST NOT acknowledge a snapshot group until the client ACKs its `ui.flush.sequence`.

## 5. Limits and ownership

The current Runtime projection contract bounds one semantic snapshot to at most 32 views and 16 panels. These limits align with the Backend's atomic queue batch capacity and must be negotiated or raised together with that capacity; a model that exceeds either limit is rejected before publication. The default serialized model size is bounded by the negotiated protocol frame limit. Limits apply before allocation and include nested keys, arrays and byte strings. Backend copies queued payloads; Lua table references are not retained as the only source of a message. Runtime remains the source of semantic editor state; Frontend owns disposable presentation caches.

## 6. Protocol projection rules (Frontend Protocol 0.2.0)

`cdin.ui-model.v1` is a Runtime-owned semantic snapshot, not a wire frame. The Backend projection MUST preserve its monotonic `revision` and map the current snapshot into the Protocol message catalogue rather than forward a Lua table representation. Split ratios are converted from Runtime floating-point ratios to integer basis points (`ratio_bp = clamp(floor(ratio * 10000 + 0.5), 1000, 8999)`), then validated in `1000..8999`; floating-point CBOR values are forbidden. Clamping reflects the Runtime's strict `(0.1,0.9)` invariant while keeping the wire value representable as an integer. The view model carries identity, version/length metadata, selection and scroll metadata only. `view.cursor.scroll_anchor`, when emitted, is the view's zero-based byte anchor at the same document version. `view.lines.total_lines`, when emitted, gives the Kernel-reported logical line count for the matching document version; the Frontend uses it for viewport/scrollbar bounds and must discard it with any other stale line result. It MUST NOT contain document bytes or a second copy of document history. Visible line content is a version-pinned pull response to `view.request_lines`, using byte strings in `view.lines`.

The semantic nullable fields `focus`, `prompt`, `layout.root`, `layout.active_leaf` and each leaf's `active_view` are encoded as CBOR `null` by the Backend where Lua's table representation omits a `nil` value. The Backend must not silently omit these nullable fields from their wire payloads.

The Backend source snapshot now includes a bounded projection in `src/runtime/lua_host_protocol.c`, atomic snapshot publication in `src/protocol/server.c`, and owner-thread inbound dispatch in `src/runtime/lua_host_protocol.c`. The Runtime companion integration patch is supplied separately under `runtime-patch/`; the public Runtime repository has not yet been updated or live-tested as part of this delivery.


**Implementation gap:** the inspected Backend projector currently emits only `revision` and `theme` for `ui.options`, and its wire validator requires `active_view` to be non-empty text. The semantic v1 model and Protocol 1.0.0 target therefore require a Backend conformance update before this projection is considered complete.
