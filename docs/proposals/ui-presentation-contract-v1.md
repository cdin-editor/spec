# UI presentation contract v1

**Status:** `ACCEPTED` by ADR-0026. The field schemas below are the normative optional `ui-presentation/1` capability contract for the existing Protocol 1.0.0 presentation messages. The capability remains disabled unless explicitly negotiated; older peers retain static-only compatibility.

**Related:** [Spec #21](https://github.com/cdin-editor/spec/issues/21), [Frontend #15](https://github.com/cdin-editor/frontend/issues/15), [ADR-0011](../adr/ADR-0011-extension-ui.md), [Runtime UI Model](../architecture/ui-model-v1.md), [Protocol wire contract](../architecture/protocol-wire.md).

## 1. Goals and ownership

The proposal defines portable text styles and bounded declarative panels/prompts without prescribing pixels or SDL/TUI drawing APIs.

- Runtime owns semantic roles, panel/widget identity, widget values, enabled/visible state and command policy.
- Backend validates and projects the complete semantic snapshot; it does not invent renderer-specific fields.
- Frontend owns local font metrics, pixel geometry, shaping, clipping, scrolling and native control drawing.
- User activation is submitted through existing `core/request.command`; Frontend does not implement command policy or directly mutate Runtime state.

No arbitrary drawing or platform-native handles are embedded in these payloads. Free-form drawing remains a separately negotiated optional canvas capability.

## 2. Versioning and atomicity

The proposed capability is `ui-presentation/1`. It signals that the Frontend understands the role/panel/widget schema in this document. The Backend may still send the existing Protocol 1.0.0 messages to older peers, but MUST NOT rely on an older peer interpreting these fields.

All style, panel and prompt values belong to the same root `cdin.ui-model.v1` revision. Their `revision` fields MUST equal that root revision; they are not independent counters. The Backend publishes one complete ordered snapshot group and its existing `ui.flush` with the same revision. The Frontend stages the group and replaces the committed presentation state only at the matching flush sequence and revision. A complete snapshot replaces the full style table and panel set; omission removes old entries. A null prompt clears the previous prompt. A revision not greater than the last committed revision is stale and the entire group is discarded; a malformed or over-limit presentation payload also rejects the entire pending group and preserves the last committed state. Repeated `panel_id` values in one group are invalid rather than last-writer-wins.

The following byte and item limits are proposed for v1. They are deliberately bounded before allocation:

| Resource | Proposed limit |
|---|---:|
| Style-table encoded CBOR | 32 KiB |
| Style roles | 256 |
| Role ID | 64 UTF-8 bytes |
| Panels | 16 |
| Panel ID | 128 UTF-8 bytes |
| Widgets per panel | 128 |
| Widget nesting depth | 16 |
| Total widgets per snapshot | 1024 |
| One label/text value | 16 KiB UTF-8 |
| Aggregate presentation payload | 128 KiB |

Implementations may use smaller local limits only if they reject the complete snapshot with a defined limit error; silent truncation is forbidden.

## 3. Style roles and line spans

### 3.1 Style table

The existing `ui.style_table` payload remains `{revision:uint, styles:map}`. Each key is a stable role ID matching `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`. Each value is a map with these optional fields:

| Field | Type | Constraints |
|---|---|---|
| `foreground` | RGBA map | `r`, `g`, `b`, `a` are uints in `0..255` |
| `background` | RGBA map | Same as foreground |
| `bold` | bool | Default false |
| `italic` | bool | Default false |
| `underline` | bool | Default false |
| `strikethrough` | bool | Default false |
| `dim` | bool | Default false |
| `inverse` | bool | Default false |

RGBA alpha is source-over opacity. A missing color inherits the Frontend's base foreground/background; it does not inherit from another role. Roles are resolved semantic styles, not theme tokens or palette references. Unknown style fields are ignored when their values are bounded valid CBOR. A malformed known field rejects the complete style table. A missing or unknown role resolves to the Frontend's default text role; it never makes the line undisplayable.

A complete style table replaces the previous table at snapshot commit. Role IDs are case-sensitive and unique under normal CBOR duplicate-key rejection.

### 3.2 Line spans

Each optional `view.lines[].spans[]` entry is `{start:uint, end:uint, role:text}`. Offsets are zero-based UTF-8 byte offsets in the exact line byte string; the underlying document bytes remain unchanged.

For v1:

- spans are ordered by ascending `start`;
- spans are non-overlapping and non-empty (`start < end`);
- `end` MUST be at most the line byte length;
- boundaries MUST be valid UTF-8 code-point boundaries when the line is valid UTF-8; raw/invalid byte ranges may only be styled when both endpoints are byte boundaries in the original byte stream;
- a missing or unknown role uses the default role;
- unknown span fields are ignored, malformed known fields reject the containing line response.

Frontends map byte spans to visual glyph clusters after shaping. They MUST NOT interpret byte offsets as glyph indices or code-point counts.

## 4. Common widget object

Each widget is a CBOR map with required `id:text` and `kind:text`. IDs are unique within a panel or prompt, stable while the semantic widget is the same, and bounded to 128 UTF-8 bytes. Common optional fields are `enabled:bool` (default true), `visible:bool` (default true) and `accessible_label:text`. An omitted optional label may be derived from the visible label text; accessibility text does not replace visible content.

Widgets are declarative. Child order is array order. Every array/map is definite-length and is validated against the limits above. A widget with `visible=false` is omitted from visual layout but remains part of the semantic snapshot. A widget with `enabled=false` is rendered disabled and MUST NOT emit activation.

## 5. Supported v1 widget kinds

### 5.1 `label`

Required: `text:text`. Optional: `role:text`. Renders non-interactive styled text.

### 5.2 `text`

Required: `runs:array`. Each run is `{text:text, role:text|null}`. Runs are concatenated in order; null or unknown roles use the default style. This is not a document view and has no editing semantics.

### 5.3 `list`

Required: `items:array`. Optional: `selected_id:text|null`. Each item has required `id:text`, `label:text`, optional `detail:text`, `enabled:bool`, and optional `activate:map`. Item IDs are unique within the list. A selected ID not present in items is treated as no selection. Empty lists are valid.

### 5.4 `tree`

Required: `nodes:array`. Each node has required `id:text`, `label:text`, optional `expanded:bool` (default false), `enabled:bool` (default true), optional `activate:map`, and optional recursive `children:array`. Node IDs are unique within the tree. The maximum nested depth is 16.

### 5.5 `button`

Required: `label:text`, `activate:map`. A button is focusable unless disabled. The action map has required `command:text` and optional `arguments:map`.

### 5.6 `input`

Required: `value:text`, `submit:map`. Optional: `placeholder:text`, `max_bytes:uint` (default 4096, maximum 16384), `multiline:bool` (default false). The submit map has required `command:text` and optional `arguments:map`. `value` is the Runtime-provided initial value. While this widget owns local focus, the Frontend edits a bounded, disposable local buffer and consumes its text/editing keys locally; it MUST NOT forward those keystrokes as document `input.text` or `input.key` events. The buffer does not mutate the Runtime UI model or document before submission. Submission sends one ordinary `core/request.command` with the declared arguments plus the final `value`; the Runtime validates and applies it. For the same stable widget ID and kind, an unrelated snapshot preserves the local buffer while the Runtime-provided initial `value` remains unchanged; a changed Runtime value replaces the buffer and its base value. When the widget is hidden, removed, disabled, or the client loses the Driver lease, local editing stops and no submission is sent.

### 5.7 Action map

An action map is `{command:text, arguments:map}`. `command` is non-empty and at most 128 UTF-8 bytes; the encoded action and arguments are included in the aggregate presentation-payload limit. On activation or input submission, the Frontend sends existing `core/request.command` with that exact command name and a copy of the declared arguments. For an input widget, the Frontend adds the current `value:text` to the arguments under the reserved key `value`; if the action already defines that key, the payload is invalid and no command is sent. The Frontend does not execute commands or treat a widget action as an alternate authorization path.

Runtime remains authoritative for command existence, validation, authorization and side effects. A widget may not name a command that bypasses normal Runtime command registration.

## 6. Panel and prompt schemas

### 6.1 `ui.panel`

The existing message is `{revision:uint, panel_id:text, panel:map|null}`. A non-null panel requires:

| Field | Type | Constraints |
|---|---|---|
| `kind` | text | One of `list`, `tree`, `content`, `form` |
| `title` | text | May be empty |
| `widgets` | array | Ordered array of supported v1 widgets |
| `visible` | bool | Default true |
| `focusable` | bool | Default true |
| `scrollable` | bool | Default true |
| `selected_widget_id` | text|null | Must refer to a focusable widget or is treated as no selection |

The outer `panel_id` is authoritative and MUST equal the panel map's `id` when that optional field is provided. Null removes the panel. Complete-snapshot omission also removes prior panels.

### 6.2 `ui.prompt`

The existing message is `{revision:uint, prompt:map|null}`. A non-null prompt requires `id:text`, `title:text`, `widgets:array`; optional fields are `message:text`, `visible:bool` (default true), and `cancel:map|null`. Prompt IDs are stable while the prompt remains open. The `cancel` action uses the same action map and is sent only through `core/request.command`. Null clears the prompt.

## 7. Unknown kinds, fields and capabilities

- Unknown optional fields are ignored if their encoded values are valid and bounded.
- Unknown role IDs fall back to the default style.
- Unknown widget kinds are rendered as a non-interactive fallback label using their optional `label` or `text` field, if present; otherwise they are omitted. The rest of the panel remains usable.
- Unknown panel kinds fall back to `content` layout and apply the same widget-kind rules.
- A peer without `ui-presentation/1` MUST NOT receive reliance-critical interaction. A compatible Frontend may render plain text labels only and must not emit widget actions.
- An interactive widget action is ignored if the widget is hidden/disabled or if the sender lacks the Driver lease.

### 6.3 Revision and replacement rules

Every `ui.style_table`, `ui.panel` and `ui.prompt` message in one snapshot carries the same root model revision. The Backend MUST validate that equality before publication. The Frontend MUST stage these messages with the rest of the snapshot; it MUST NOT expose a subset before the matching `ui.flush`. A complete snapshot replaces the entire style table and panel set. A panel omitted from the snapshot is removed, `panel:null` removes that panel, and `prompt:null` clears the prompt. A stale, duplicate or non-monotonic snapshot revision is discarded without changing committed presentation state. A panel ID may occur at most once per snapshot group.

## 8. Conformance vectors

The companion [ui-presentation-v1.json](../testing/vectors/ui-presentation-v1.json) is a proposed language-neutral fixture family covering valid roles and spans, unknown-role fallback, malformed colors, overlap and range errors, complete snapshot replacement, panel removal, null prompt, nested tree bounds, duplicate IDs, unknown widgets, disabled activation, Observer rejection, unknown commands and missing-capability fallback.

These fixtures are not executable evidence. Frontend, Backend and Runtime runners must consume the same cases after owner acceptance.

## 9. Explicit non-goals

This contract does not define pixel sizing, font fallback, text shaping, bidi, glyph cluster mapping, cursor/selection drawing, arbitrary canvas drawing, or a native toolkit control. Those belong to Frontend's local renderer or separate capabilities.
