# Frontend Protocol wire contract 1.0.0

**Status:** `ACCEPTED` by [ADR-0018](../adr/ADR-0018-frontend-protocol-wire.md) and [ADR-0020](../adr/ADR-0020-frontend-topology-and-interaction.md). The pinned Backend 1.0.0 source declares Protocol 1.0.0 and implements the accepted nullable `active_view`, typed `ui.options` map and fixed-point `ratio_bp` schema. Concrete OS transport creation remains a separate integration responsibility.

## 1. Frame and envelope

A stream frame is `uint32_be body_length` followed by exactly `body_length` bytes of deterministic CBOR. The default body limit is 1 MiB. `body_length` excludes the four-byte prefix, must be non-zero, and MUST be checked before allocation. One frame contains one CBOR envelope. No delimiter or NUL terminator follows a frame.

The envelope is a definite-length CBOR map with exactly five text keys. The `seq` field is the per-connection message sequence; it is distinct from the flush-group sequence carried in `ui.flush.payload.sequence` and acknowledged by `ack.payload.sequence`:

| Key | Type | Meaning |
|---|---|---|
| `v` | array `[uint, uint]` | Protocol major and minor (`[1, 0]` for this version) |
| `ns` | text | Namespace; `core` is mandatory |
| `seq` | uint | Per-connection monotonically increasing message sequence, starting at 1 |
| `type` | text | Exact message name from §3 |
| `payload` | map | Payload matching the schema in §3 |

The deterministic profile uses shortest-width integer and length encodings, definite-length containers and text map keys. Duplicate keys, trailing bytes, malformed UTF-8 text, indefinite-length values and unsupported CBOR simple values are invalid. Protocol v1.0.0 does not admit floating-point values. Ratios and other fractional UI values MUST be converted to explicitly named fixed-point unsigned integers by the model adapter (for split ratios, `ratio_bp` is an unsigned integer basis-point value in `1000..8999`; it is derived from the Runtime ratio and never emitted as a float). Document and paste data is represented only as CBOR byte strings. Implementations MUST NOT infer text encoding for byte-string values.

Unknown fields in a known message are ignored when their CBOR value is valid and bounded. Unknown messages in mandatory namespace `core` return `UNSUPPORTED`. The `core` namespace is mandatory. An optional namespace is accepted only when negotiated through a registered capability; an unknown optional namespace may be ignored, while an unknown message in `core` returns `UNSUPPORTED`. Invalid known fields reject the entire message without dispatch.

## 2. Protocol flow and permissions

Every connection performs `hello`, `hello_ack`, `attach`, then steady-state messages. The first frame MUST be `hello`; `attach` is accepted only after successful negotiation. A client is not considered attached until `attach` succeeds. Messages are sequence-checked independently per connection.

The session has one driver and zero or more observers. The first attached client gets the driver lease. Driver-only messages are `input.key`, `input.text`, `input.mouse`, `input.paste`, `window.resize`, `focus`, `view.set_position` and `request.command`. Observers may send `ack`, `view.request_lines`, and responses for requests addressed to them. A driver is promoted only when the current driver detaches or closes; the oldest still-attached observer is promoted. When a Frontend negotiates the optional `driver-role-events/1` capability, the Backend sends `driver.role_changed` after a live lease transition. The event carries `epoch:uint` and the new `driver` boolean. `epoch` MUST equal the event frame's envelope `seq`; it is therefore monotonic on that client's ordered outbound stream. The initial `driver_role_epoch` in `hello_ack` MUST equal the `hello_ack` envelope `seq`. The Frontend's normal inbound sequence validation rejects duplicate, stale or out-of-order frames, and the role handler rejects a payload epoch that does not match its envelope sequence. The Backend remains authoritative for every driver-only request. A client that does not negotiate this capability receives no role event and must reconnect to obtain a refreshed `driver` value in `hello_ack`.

All accepted input is copied into a bounded inbound queue and dispatched on the Runtime owner thread. A full queue returns `QUEUE_FULL`; it MUST NOT silently discard input. Kernel wakeup callbacks may signal the owner loop but MUST NOT invoke Lua.

## 3. Message schemas

The terms below mean: `uint` = unsigned CBOR integer; `bool` = CBOR false/true; `text` = valid UTF-8 CBOR text; `bytes` = CBOR byte string; `map` = definite CBOR map with text keys; `array<T>` = definite array; `null` = CBOR null. All payloads are maps. Fields marked `required` MUST appear exactly once. Unlisted fields are optional extension fields.

The reference Backend registers the optional `driver-role-events/1` capability. A Frontend requests it by including that exact identifier in `hello.capabilities`; the Backend returns it in `hello_ack.accepted_capabilities` only when the role lifecycle event path is enabled. Clipboard, dialog and other optional services remain independently negotiated and MUST NOT be assumed available merely because they were requested.

### 3.1 Frontend to Backend

| Message | Required fields | Optional fields / semantics |
|---|---|---|
| `hello` | `minimum_major:uint`, `minimum_minor:uint`, `maximum_major:uint`, `maximum_minor:uint`, `frontend_name:text`, `capabilities:array<text>` | `metadata:map`; first frame only |
| `attach` | `session_id:uint`, `units:text`, `width:uint`, `height:uint` | `view_id:text`; `units` is `pixels` or `cells` and never changes text coordinates |
| `detach` | — | `reason:text` |
| `input.key` | `key:text`, `action:text`, `modifiers:array<text>` | `scancode:uint`; action is `press`, `release` or `repeat` |
| `input.text` | `text:text` | Committed IME text; not a key event |
| `input.mouse` | `action:text`, `button:text`, `modifiers:array<text>` | `target:text`, `position:map`; logical positions only |
| `input.paste` | `bytes:bytes` | Raw pasted bytes; invalid UTF-8 is preserved |
| `window.resize` | `width:uint`, `height:uint`, `units:text` | Dimensions are display units, not document offsets |
| `focus` | `focused:bool` | — |
| `view.request_lines` | `view_id:text`, `first_line:uint`, `line_count:uint`, `version:uint` | Pull request; version must match the source version requested |
| `view.set_position` | `view_id:text`, `anchor:uint`, `caret:uint`, `version:uint` | Zero-based byte offsets; half-open selection is `[min,max)` |
| `request.command` | `name:text`, `arguments:map` | Driver only; command policy remains in Runtime |
| `response.clipboard` | `request_id:uint`, `bytes:bytes` | Only for a clipboard request issued to this client |
| `response.dialog` | `request_id:uint`, `accepted:bool` | `selected:text`; only for a dialog request issued to this client |
| `ack` | `sequence:uint` | Acknowledges a previously published `ui.flush`; observers may ACK |

### 3.2 Backend to Frontend

| Message | Required fields | Optional fields / semantics |
|---|---|---|
| `hello_ack` | `major:uint`, `minor:uint`, `session_id:uint`, `client_id:uint`, `driver:bool`, `accepted_capabilities:array<text>` | `driver_role_epoch:uint`; MUST equal the `hello_ack` envelope `seq` when present |
| `ui.options` | `revision:uint`, `theme:text`, `options:map` | The map may be empty; its only defined keys are `title:text`, `tab_width:uint` (1..64), `wrap:bool`, `line_numbers:bool`, `relative_line_numbers:bool`, `cursor_shape:text` (`block`, `bar` or `underline`), and `cursor_blink:bool`. Unknown optional keys follow the version-evolution rules. |
| `ui.style_table` | `revision:uint`, `styles:map` | Role IDs map to attributes; no palette-specific pixel values required |
| `ui.layout` | `revision:uint`, `layout:map` | `layout` contains `root:map|null` and `active_leaf:text|null`. `root` is a recursive PaneTree node: a leaf is `{kind:"leaf",id:text,views:array<text>,active_view:text|null}`; `active_view` is either null or an ID contained in `views`. a split is `{kind:"split",id:text,axis:"vertical"|"horizontal",ratio_bp:uint,first:node,second:node}`. `ratio_bp` is fixed-point in `[1000,8999]`; it is not a float. |
| `view.lines` | `view_id:text`, `version:uint`, `first_line:uint`, `lines:array<map>` | `total_lines:uint` is optional and, when present, is the total logical line count at the same `version`; receivers require `first_line < total_lines` and `first_line + len(lines) <= total_lines`. Each line map requires `bytes:bytes` and may contain `spans:array<map>`. Each span requires `start:uint`, `end:uint`, `role:text`; offsets are zero-based byte offsets within that line and must satisfy `start <= end <= len(bytes)`. A response may contain at most 4096 lines and at most 4096 spans per line. |
| `view.invalidate` | `view_id:text`, `version:uint`, `ranges:array<map>` | Each range has `start:uint`, `end:uint` and must satisfy `start <= end`; stale versions are discarded. At most 4096 ranges are accepted. |
| `view.cursor` | `view_id:text`, `version:uint`, `position:uint` | Position is a zero-based byte offset; optional `scroll_anchor:uint` is a logical zero-based document byte offset, never pixel or visual-line geometry |
| `view.selection` | `view_id:text`, `version:uint`, `anchor:uint`, `caret:uint` | — |
| `ui.statusline` | `revision:uint`, `status:map` | Structured, declarative status fields |
| `ui.prompt` | `revision:uint`, `prompt:map|null` | Null clears the prompt |
| `ui.panel` | `revision:uint`, `panel_id:text`, `panel:map|null` | Null removes the panel |
| `ui.notify` | `level:text`, `text:text` | `notification_id:uint` |
| `request.clipboard_get` | `request_id:uint` | Requires negotiated `clipboard` capability |
| `request.clipboard_set` | `request_id:uint`, `bytes:bytes` | Requires negotiated `clipboard` capability |
| `request.dialog` | `request_id:uint`, `kind:text`, `options:map` | Requires negotiated `dialogs` capability |
| `ui.flush` | `scope:text`, `sequence:uint` | Ends one atomic update. `scope` is `snapshot` or `response`. `sequence` is the monotonically increasing flush-group ID used by `ack`; the envelope `seq` remains the ordinary per-message sequence. `revision:uint` is required only for `snapshot` and forbidden for `response`. |
| `detach_ack` | — | — |
| `driver.role_changed` | `epoch:uint`, `driver:bool` | Optional; sent only when `driver-role-events/1` was accepted. `epoch` MUST equal this frame's envelope `seq` (strictly increasing per client); `driver` is the new lease state for this client. It is not an authorization token. |
| `error` | `code:text`, `message:text` | `request_id:uint` |

## 4. Atomic updates, versions and flow control

All messages queued before `ui.flush` form one atomic UI update. A frontend MUST stage the messages and apply them together only after the corresponding `ui.flush` is received. Every flush payload has a strictly increasing per-client flush-group sequence. A `scope="snapshot"` group is a complete replacement of the projected semantic UI state: after validating its `revision`, the frontend MUST atomically replace options, styles, layout, view state, status, prompt and panels, removing any previously projected view or panel omitted from the snapshot. Its `revision` is required and MUST be newer than the last applied snapshot revision. A `scope="response"` group carries a request result or diagnostic and MUST NOT clear or replace the existing UI model; `view.lines` and `error` responses use this scope. A receiver MUST reject a flush with an unknown scope, a snapshot without `revision`, or a response that includes `revision`. The flush-group `sequence` remains independent from both the model `revision` and the envelope message `seq`. The envelope sequence independently increases for every message. ACKs at or below the latest acknowledged flush-group sequence, or above the last published flush-group sequence, are invalid. The Backend bounds both queue capacity and unacknowledged flush count. When the queue is full, state-like outbound updates may be coalesced only by an explicit key; input events are never silently coalesced.

`view.lines` and `view.invalidate` always carry a document version. A frontend MUST discard line data older than the newest version it has observed. A snapshot projection emits a full-document invalidation range for each visible view; the frontend then requests only the visible line windows it needs. Line delivery is pull-based: the Backend sends only explicitly requested line ranges unless a negotiated push capability says otherwise. A line payload carries original bytes; spans are byte ranges and do not carry presentation colours.

## 5. Transport API

The same semantic messages and CBOR payload maps are used by in-process C calls and serialized streams. The reference `cdin_protocol` C target provides payload validation, frame encode/decode and partial stream read/write helpers. The transport supplies read/write callbacks for sockets, named pipes or in-memory test streams. It owns connection establishment, authentication, encryption, socket lifetime, event-loop readiness and OS error translation. The protocol library does not open a network port.

## 6. Version evolution

Protocol version is `[major, minor]`. While major is unchanged, new optional fields and optional message types may be added. Existing field types, requiredness and semantics do not change in a minor release. New mandatory core operations require a major bump or an explicit capability. A receiver ignores unknown optional fields and rejects malformed required fields. A receiver returns `UNSUPPORTED` for an unknown message in `core`.

## 7. Validation profile implemented by the reference codec

The v1.0.0 reference C codec validates every message type listed in §3, including recursive PaneTree layout nodes, active-leaf membership and the optional `driver.role_changed` schema. It additionally enforces these semantic bounds: frontend and view identifiers are non-empty and bounded; dimensions are in `1..32768`; key names are at most 64 bytes; modifiers are unique members of `ctrl`, `alt`, `altgr`, `shift`; key actions are `press`, `release`, or `repeat`; mouse actions are `press`, `release`, `move`, or `scroll`; line requests ask for `1..4096` lines; notification text is at most 4096 bytes; and all byte spans are bounded by their line byte-string length. Unknown optional payload fields are skipped only after the CBOR value has passed structural/depth/canonical validation. The reference server continues to accept the mandatory `core` namespace and negotiates the optional `driver-role-events/1` capability; other optional services remain independently gated.

The C codec exposes frame encode/decode and callback-based partial read/write helpers. The Backend server adds per-client sequence checking, role enforcement, bounded input/output queues, keyed outbound coalescing, flush markers and ACK release. The Backend Lua Host bridge projects `cdin.ui-model.v1` to atomic message groups, queues inbound events and dispatches them on the Lua owner thread. Concrete socket and named-pipe creation remains a separate transport integration gate; see the Backend's `docs/spec-traceability.md`.


## 8. Implementation conformance note for v1.0.0

The pinned Backend 1.0.0 implementation declares `CDIN_BACKEND_PROTOCOL_MAJOR/MINOR` as `1.0` and `src/protocol/codec.c` validates the Protocol 1.0.0 schemas, including nullable `active_view`, the typed `ui.options` map and bounded `ratio_bp`. `src/runtime/lua_host_protocol.c` projects the typed options map and fixed-point layout values. The Backend protocol codec tests cover these schema rules. This confirms the Backend's in-process protocol implementation; it does not prove that CDIN has connected a real Frontend transport or launched an interactive TUI.


## 9. Driver role lifecycle extension

`driver-role-events/1` is an optional capability. It is included in `hello.capabilities` only by Frontends that implement the `driver.role_changed` state transition. The Backend MUST send the initial `driver` role and `driver_role_epoch` in `hello_ack`; after a negotiated client's role changes while attached, it MUST enqueue one `driver.role_changed` message in that client's ordered outbound stream. `epoch` MUST equal the outbound envelope `seq` of that message. The `hello_ack` role epoch follows the same rule. This makes the epoch monotonic per client and avoids adding mutable role counters or fields to public Frontend session structs. A receiver MUST reject epoch zero and any payload/envelope mismatch; the protocol client's normal receive sequence check rejects duplicate, older and skipped frames. The event is state synchronization only: the Backend MUST continue validating the current lease for every inbound driver-only message, regardless of what a client reports locally. When the capability is not accepted, no new core message is sent to that client, preserving compatibility with v1.0 consumers; that client refreshes its local role by reconnecting and negotiating again.
