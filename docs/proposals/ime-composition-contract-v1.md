# IME composition and preedit contract v1

**Status:** `ACCEPTED` by [ADR-0023](../adr/ADR-0023-ime-composition-contract.md). This optional capability is part of the accepted Protocol 1.0.0 extension surface; implementations MUST still withhold capability advertisement until their complete negotiated lifecycle is implemented and conformance-tested.

**Related:** [Spec #14](https://github.com/cdin-editor/spec/issues/14), [Frontend #15](https://github.com/cdin-editor/frontend/issues/15), [CDIN #111](https://github.com/cdin-editor/cdin/issues/111), [Protocol wire contract](../architecture/protocol-wire.md), [Runtime UI Model](../architecture/ui-model-v1.md).

## 1. Goals and non-goals

This proposal defines a bounded, versioned, capability-gated lifecycle for native input-method composition. It distinguishes transient preedit from committed text, binds a composition to one Runtime view and document version, and makes cancellation deterministic across focus, view, role and session changes.

It preserves the accepted ownership boundaries:

- The Frontend captures native IME events and renders preedit.
- The Backend owns protocol validation, per-client composition lifecycle, capability enforcement, stale-state cancellation and exactly-once admission of a committed text event.
- Runtime owns the logical view selection, text-input semantics and committed editor state.
- Kernel owns canonical document bytes and document versions.

This proposal does not add IME state to `cdin.ui-model.v1`, does not expose preedit to extensions or observer Frontends, does not move keymap policy into Frontend, and does not change Kernel byte/position semantics. It does not prescribe SDL-specific API calls or a particular IME toolkit.

## 2. Versioning and capability negotiation

The proposed capability identifier is exactly `ime-composition/1`. It enables the optional Protocol namespace `ime` and the messages defined below. The existing general `ime` capability remains a legacy declaration that a Frontend can accept native input-method text and submit its committed result through `input.text`; by itself it does not authorize the lifecycle messages in this proposal.

A Frontend requests `ime-composition/1` in `hello.capabilities`. The Backend returns it in `hello_ack.accepted_capabilities` only when the complete validation, cancellation and commit path is available for that session. Neither side may infer acceptance from a request. The `ime` namespace is valid only for a session that accepted this exact capability.

The extension is additive to Protocol 1.0.0:

- The mandatory `core` namespace and existing `input.text` semantics remain compatible.
- A peer that does not accept `ime-composition/1` receives no `ime` namespace messages.
- The optional `composition_id` field on `input.text` is used only when the capability was accepted and must be ignored/omitted by a peer that did not negotiate it.
- No Protocol major/minor change is proposed. This is a separately versioned optional capability, following the existing `driver-role-events/1` pattern.

## 3. Wire schemas

All payloads are definite-length CBOR maps in the existing five-field envelope. Namespace and message type strings are exact and case-sensitive. The normal envelope sequence, UTF-8 text, deterministic CBOR, frame-size and per-client ordering rules continue to apply.

### 3.1 Frontend to Backend: start

Namespace: `ime`  
Type: `composition.start`

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `id` | uint | yes | Non-zero composition identifier, strictly greater than every earlier identifier used by this client connection. |
| `view_id` | text | yes | Stable Runtime view ID being composed into. |
| `document_version` | uint | yes | Exact document version observed by the Frontend when composition begins. |

The Backend accepts start only from the current Driver, for a visible and focused Runtime view, when the supplied document version equals the current version. A start from an Observer is rejected with `INVALID_STATE`. The Backend captures the Runtime-owned selection (`anchor`, `caret`) at that same version; the Frontend does not supply or own the replacement range. A client may have at most one active composition. Starting another while one is active is an `INVALID_STATE` error; the current composition must first be cancelled.

Composition identifiers are scoped to one attached client connection. They MUST be non-zero, strictly increasing and never reused within that connection. A reconnect starts a new identifier sequence because it starts a new client connection and never resumes an old composition.

### 3.2 Frontend to Backend: update / preedit

Namespace: `ime`  
Type: `composition.update`

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `id` | uint | yes | The identifier of the active composition. |
| `preedit` | text | yes | Current transient preedit string; valid UTF-8, at most 4096 encoded bytes. Empty text is allowed to represent an empty preedit update. |
| `cursor_byte` | uint | yes | Cursor offset from the beginning of `preedit`, in UTF-8 bytes. |
| `selection_start_byte` | uint | yes | Lower bound of the IME-selected range in `preedit`, in UTF-8 bytes. |
| `selection_end_byte` | uint | yes | Exclusive upper bound of the IME-selected range in `preedit`, in UTF-8 bytes. |

The three offsets MUST be in `0..utf8_length(preedit)`, and each MUST lie on a UTF-8 code-point boundary (never inside a multibyte encoding). The selection range MUST satisfy `selection_start_byte <= selection_end_byte`. Offsets are byte offsets, not code-point, UTF-16 code-unit, grapheme or pixel offsets. The Frontend converts native platform units to this wire representation. A combining sequence may contain multiple code points; the byte boundaries remain unambiguous, and the Frontend's shaping/grapheme layer maps them to visual positions.

The update MUST refer to the currently active identifier. It is a transient presentation update only. It MUST NOT mutate canonical document bytes, advance the document version, enter undo history, invoke keymaps or be dispatched to Runtime as committed text.

### 3.3 Frontend to Backend: commit

A composition is committed using the existing mandatory message:

Namespace: `core`  
Type: `input.text`

The existing required field `text:text` remains the committed UTF-8 text. When and only when `ime-composition/1` was accepted and an active composition exists, the Frontend adds:

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `composition_id` | uint | conditional | The active composition identifier being committed. |

For a composition commit, `composition_id` MUST equal the active composition identifier. It MUST NOT be present on ordinary keyboard text input or on a peer that did not negotiate the capability. The Backend uses the view ID, document version and selection captured at `composition.start`; the Frontend cannot redirect a commit by changing those values.

The Backend admits the commit to the Runtime owner-thread input queue atomically. If the bounded queue reports `QUEUE_FULL`, the composition remains active and the Frontend may retry the same commit identifier. Once the commit has been successfully admitted, the Backend consumes the identifier and clears the active composition before another message can commit it. A duplicate or late commit for a consumed/cancelled identifier is rejected and MUST NOT be dispatched again. While a composition is active, a bare `input.text` without the matching `composition_id` is rejected with `INVALID_STATE`; the Frontend must cancel first rather than accidentally committing outside the captured view context.

An empty final string is represented by `composition.cancel`, not by a commit.

### 3.4 Cancel

Namespace: `ime`  
Type: `composition.cancel`

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `id` | uint | yes | Active composition identifier. |
| `reason` | text | yes | One of the reason values below. |

The message is bidirectional. A Frontend sends it when the native IME cancels or the local composition is replaced. The Backend sends it to the originating Frontend when it must cancel an active composition. The Frontend clears only the matching active identifier; an old cancellation for another identifier is ignored.

Reason values sent by Frontend:

- `ime_cancelled`
- `focus_lost`
- `view_changed`

Reason values sent by Backend:

- `focus_lost`
- `stale_document`
- `view_changed`
- `selection_changed`
- `view_removed`
- `driver_revoked`
- `session_reset`

A detached connection has no cancellation delivery guarantee; both sides discard its transient state as part of detach/close. A new connection MUST NOT restore a previous composition.

## 4. Lifecycle, ordering and cancellation

1. **Start:** the Backend verifies Driver role, negotiated capability, active/focused/visible view and document version. It captures the authoritative Runtime selection and records only bounded composition metadata (client, identifier, view, version and selection).
2. **Update:** the Backend validates the identifier, UTF-8, byte cap and offsets, then discards the preedit payload after validation. The Frontend retains and renders the local preedit. The Backend does not retain a second preedit string.
3. **Commit:** the Frontend sends one `core/input.text` message with `composition_id`. The Backend verifies the active record and queues one committed text event for Runtime. Runtime revalidates the captured view, document version and selection before applying text through its normal committed-text path. A stale context returns `STALE_VERSION` or `INVALID_STATE` without document mutation.
4. **Cancel:** either side may cancel the active identifier. Cancellation clears only transient composition state; it is not a document edit and does not advance the document version.
5. **No active composition:** update, commit or cancel for an unknown, consumed, older or mismatched identifier is rejected and cannot mutate a document.

The Backend MUST cancel and send `ime.composition.cancel` to the originating Frontend when any of the following occurs while a composition is active:

- the client sends `focus{focused:false}`;
- the view is removed, becomes hidden/unfocused, or another view becomes the active text-input target (reason `view_changed`);
- the Runtime selection for that view changes from the captured selection (reason `selection_changed`);
- the document version advances from the captured version;
- the client's Driver lease is revoked or the client becomes an Observer;
- the Backend resets the session's semantic state.

On Driver revocation, the cancellation MUST be queued before the corresponding negotiated `driver.role_changed` event in that client's ordered outbound stream. Subsequent update/commit messages are rejected because the client is no longer Driver. On detach, connection loss or Backend session reset, the active composition is discarded and is never replayed after reconnect.

## 5. Ownership and presentation isolation

- **Frontend:** captures platform IME events, converts platform offsets to UTF-8 byte offsets, retains the preedit string and draws the preedit/caret/IME-selected range as a local overlay for the bound view. It sends start/update/cancel and the final committed `input.text` event.
- **Backend:** negotiates the capability, validates and bounds the extension, maintains at most one active composition record per client, cancels it on lifecycle changes, enforces Driver permission, prevents duplicate commits and forwards only the final committed text to Runtime.
- **Runtime:** remains authoritative for the view selection, keymap/command policy and committed text insertion. It receives no preedit update. For a commit it verifies the captured view/version/selection still match, then processes the committed text through its ordinary text-input semantics. Runtime MUST NOT treat preedit as a key event or command.
- **Kernel:** receives only the committed edit through the existing document API; it never sees preedit state.

Preedit is intentionally **client-local**. It is not added to `cdin.ui-model.v1`, is not published by `ui.flush`, and is not broadcast to Observer Frontends or extensions. The Backend sends only forced cancellation control messages to the originating Frontend. This avoids turning a device-local transient state into shared editor state and prevents observers from seeing text that the user has not committed.

The Runtime Host API 1.0.0 is not changed by this proposal. Composition metadata is an internal Backend-to-Runtime input-dispatch context, not a new Lua Host service or extension API. If the Runtime candidate lacks an input-dispatch entrypoint with the required context, that implementation work must be added and versioned by its owning repository without changing Host API 1.0.0 semantics.

## 6. Compatibility and fallback

- The Backend MUST advertise `ime-composition/1` only when it implements namespace validation, active-composition state, forced cancellation, Driver checks, duplicate-commit suppression and Runtime stale-context validation.
- The Frontend MUST send `ime` namespace messages and `input.text.composition_id` only after the capability is present in `hello_ack.accepted_capabilities`.
- If the capability is absent, the Frontend uses the existing committed-only `input.text` path and sends no composition lifecycle messages or `composition_id`. It clears its local preedit on locally observable focus loss and detach. The Backend continues to enforce Driver role on the ordinary `input.text` message.
- A peer that does not implement the optional namespace remains compatible with Protocol 1.0.0. The Backend MUST NOT send new core message types to it.
- Capability acceptance is per connection. It is not inherited by another Frontend attached to the same Backend session.

## 7. Bounds and errors

- At most one active composition per attached client.
- `id` is a non-zero unsigned 64-bit integer, strictly increasing per connection and never wrapping.
- `preedit` is valid UTF-8 and at most 4096 bytes. The ordinary Protocol frame cap continues to apply to the whole envelope.
- All preedit offsets are unsigned byte offsets at UTF-8 code-point boundaries.
- A malformed field is rejected before dispatch. Oversized preedit returns `LIMIT_EXCEEDED`; a stale document returns `STALE_VERSION`; an invalid lifecycle transition or reused identifier returns `INVALID_STATE`; an unsupported namespace/capability returns `UNSUPPORTED`; an input queue at capacity returns `QUEUE_FULL`.
- Rejection, cancellation and malformed update MUST leave canonical document bytes, document version and undo history unchanged.

## 8. Proposed implementation ownership

| Repository | Work after owner acceptance |
|---|---|
| `spec` | Accept ADR-0023; maintain the schema and shared vectors. |
| `frontend` | Add the negotiated capability, SDL/native event conversion, local preedit rendering, byte-offset mapping, forced-cancel handling and adapter conformance tests. |
| `backend` | Register capability/namespace, validate events, track active composition metadata, trigger cancellations, atomically admit/deduplicate commits and supply captured context to Runtime. |
| `runtime` | Revalidate target view/version/selection and apply committed text through the existing input policy on the owner thread; never accept preedit as document input. |
| `cdin` | Pin compatible component revisions and add live end-to-end composition tests after the owning components publish support. |

## 9. Conformance coverage

The proposed shared data-driven vectors are in [ime-composition-v1.json](../testing/vectors/ime-composition-v1.json). They cover capability absence/acceptance, multibyte and combining-mark offsets, cancellation, duplicate commits, queue-full retry, stale versions, invalid UTF-8, oversized preedit, non-boundary offsets, Observer rejection, focus loss and view removal.

The Spec repository has no executable Protocol runner. The vector file is a proposed contract fixture, not a test result. Backend, Frontend and Runtime owners must add runners/tests and report the exact implementation version and result before claiming conformance.

## 10. Acceptance checklist for this proposal

- [x] Define a versioned optional capability and namespace boundary.
- [x] Specify start, update/preedit, commit-through-input.text and cancel schemas.
- [x] Define UTF-8 byte-offset units and bounds for cursor/selection mapping.
- [x] Define local-only preedit presentation and Runtime/Kernel commit ownership.
- [x] Define duplicate-commit, queue-full retry and stale-version semantics.
- [x] Define cancellation on focus, view, document, Driver-role and session changes.
- [x] Add shared positive and negative conformance cases.
- [x] Assign implementation work to Frontend, Backend, Runtime and CDIN.
- [x] Owner accepts ADR-0023. Capability advertisement remains gated on complete component and CDIN integration conformance.
