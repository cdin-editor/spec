# PaneTree splitter resize contract v1

**Status:** `PROPOSED`. This proposal does not change the accepted Frontend Protocol 1.0.0 contract until the owner accepts the corresponding decision. Implementations MUST NOT advertise or emit the optional extension while it remains proposed.

**Related:** [Spec #20](https://github.com/cdin-editor/spec/issues/20), [Frontend #15](https://github.com/cdin-editor/frontend/issues/15), [Runtime PaneTree](../components/runtime.md), [Protocol wire contract](../architecture/protocol-wire.md).

## 1. Goals and ownership

This proposal adds an optional, revision-checked way for a Driver Frontend to commit a new ratio for an existing semantic split.

- Runtime owns the PaneTree, stable node identities and semantic split ratios.
- Frontend owns pixel geometry, divider hit targets, pointer capture, drag preview and pixel-to-ratio conversion.
- Backend authenticates the attached client, enforces Driver/capability authorization, orders the request on the Runtime owner thread and publishes the resulting semantic snapshot atomically.
- The Frontend never mutates its authoritative local copy of the PaneTree and never sends pixel rectangles to Runtime.

The existing `core/input.mouse.target` remains a Runtime **View ID** for compatibility. This extension does not reinterpret it as a pane or split ID.

## 2. Negotiation and compatibility

The exact optional capability is `pane-splitter-resize/1`. It enables the optional namespace `pane`.

A Frontend requests the capability in `hello.capabilities`; the Backend returns it in `hello_ack.accepted_capabilities` only when the complete authorization, Runtime mutation and atomic publication path is available. A request alone grants no permission.

A peer that does not accept the capability continues to use Protocol 1.0.0 unchanged. It may still hit-test or draw dividers locally, but MUST NOT send `pane` messages and MUST NOT imply that resizing was committed.

## 3. Local drag lifecycle

The gesture is local until pointer release; intermediate pointer motion does not mutate Runtime state or publish protocol traffic.

1. **Begin:** on primary-button down within the configured splitter hit band, capture the split node ID, current `ui.layout.revision`, initial ratio and pointer identity. The ID is the stable split node's `id`, not a Runtime View ID.
2. **Move:** compute a preview ratio from the divider's pixel coordinate and the split node's pixel extent. Clamp the integer result to `1000..8999` basis points. Preview geometry is disposable Frontend state; do not rewrite the committed PaneTree.
3. **Commit:** on matching pointer release, send exactly one `pane.splitter.resize` request with the captured layout revision and final ratio. The Frontend does not report success until the Backend result and corresponding snapshot are observed.
4. **Cancel:** discard the preview without sending a resize request on Escape, pointer cancellation, window/focus loss, detach/reconnect, active-view removal, loss of Driver authority, or receipt of a different committed layout revision.

Only one local splitter drag is active per window. A new drag cannot begin until the prior drag commits or cancels.

## 4. Wire request and result

All payloads use the existing deterministic CBOR envelope. The extension adds no new mandatory `core` messages.

### 4.1 Frontend to Backend — `pane.splitter.resize`

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `request_id` | uint | yes | Non-zero identifier unique among outstanding pane requests for this client connection |
| `split_id` | text | yes | Stable ID of an existing split node in the current semantic PaneTree |
| `layout_revision` | uint | yes | Exact committed `ui.layout.revision` observed when the drag began |
| `ratio_bp` | uint | yes | New first-child ratio in basis points, inclusive range `1000..8999` |

The request contains no pixel coordinate, viewport size, device scale, leaf ID or View ID. Runtime receives the semantic ratio only.

### 4.2 Backend to Frontend — `pane.splitter.result`

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `request_id` | uint | yes | Echo of the matching request |
| `status` | text | yes | `applied`, `stale_revision`, `not_found`, `invalid_ratio`, `not_driver`, `unsupported` or `busy` |
| `layout_revision` | uint | yes | Current committed revision known to the Backend after processing |

A successful result is followed by the normal complete semantic UI snapshot and `ui.flush`. The Frontend MUST keep the old committed layout until that snapshot is committed. A failure never changes the semantic tree; the Frontend discards its preview and follows the latest committed snapshot.

## 5. Validation, mutation and publication

The Backend MUST reject a request unless all of the following hold:

- the session negotiated `pane-splitter-resize/1`;
- the sender currently owns the Driver lease;
- `layout_revision` exactly equals the current Runtime UI layout revision;
- `split_id` identifies a split node in the current tree;
- `ratio_bp` is an integer in `1000..8999`;
- the request is well-formed and within the per-client queue bounds.

The Backend dispatches the operation to the Runtime owner thread. Runtime exposes an owner-thread operation equivalent to `PaneTree:set_split_ratio(split_id, ratio)`. The operation changes only the selected split's semantic ratio, preserves its children and IDs, and fails without mutation when the node is absent or is not a split.

The Runtime UI-model revision advances exactly once for a successful semantic resize. Backend builds and validates the complete snapshot, then queues the ordered projection including `ui.layout` and the matching `ui.flush` as one atomic batch. It MUST NOT publish a success result for a mutation whose semantic snapshot cannot be queued. If queueing fails, the implementation must preserve its defined retry/recovery behaviour without applying the resize twice.

A revision mismatch returns `stale_revision`; Frontend MUST NOT silently retry the same ratio against a different tree. It cancels the drag and uses the latest committed layout. A Driver lease change cancels any queued request that has not yet passed owner-thread authorization.

## 6. Coordinate and ratio rules

- Pointer coordinates and divider hit targets are in drawable pixel coordinates after the platform's high-DPI conversion.
- Horizontal splits divide the X axis; vertical splits divide the Y axis, matching the accepted PaneTree geometry contract.
- The first child occupies the leading side of the selected axis.
- The Frontend computes `ratio_bp = round(first_child_extent * 10000 / split_extent)`, then clamps to `1000..8999`.
- Pixel rectangles and hit slop are never serialized.
- Runtime stores the semantic ratio as its existing logical value; the wire carries only integer basis points.

## 7. Conformance vectors

The companion [pane-splitter-v1.json](../testing/vectors/pane-splitter-v1.json) is a proposed data-driven fixture family. It covers:

- horizontal, vertical and nested split commits;
- exact minimum and maximum ratios, plus out-of-range rejection;
- unknown split IDs and a leaf ID supplied in place of a split ID;
- stale layout revisions and a concurrent tree replacement;
- Observer rejection and missing-capability fallback;
- local cancellation on focus loss, pointer cancellation and Driver revocation;
- success ordering: result, then complete `ui.layout` snapshot, then `ui.flush`.

The fixtures are not passing test evidence. Frontend, Backend and Runtime runners must consume the same vectors after owner acceptance.

## 8. Explicit non-goals

This extension does not define new pane creation/removal, tab movement, keyboard focus navigation, arbitrary drag-and-drop, floating windows, or pixel geometry in Runtime. Those remain separate contracts.
