# ADR-0023: Versioned Frontend IME composition contract

- **ID:** ADR-0023
- **Status:** `ACCEPTED`
- **Resolves:** Spec issue [#14](https://github.com/cdin-editor/spec/issues/14)

## Context

The accepted Frontend Protocol 1.0.0 transports committed text through `input.text`, while the capability catalogue mentions IME support without defining a normative preedit lifecycle. An SDL or other native frontend cannot safely treat preedit as committed text: doing so would mutate canonical document bytes before the user commits and make cancellation ambiguous.

The design must preserve the accepted rules that Runtime owns editor policy and view selection, Frontend owns native input and presentation, Backend owns session/permission/queue enforcement, and Kernel owns canonical document bytes.

## Problem

A composition contract needs to answer all of the following without breaking existing Protocol 1.0 peers:

- how start/update/preedit/cancel are represented and negotiated;
- how preedit cursor/selection positions map across UTF-8 and combining sequences;
- how the eventual text commit is tied to the intended view/version/selection and delivered once;
- how focus, view, document, Driver-role and connection lifecycle changes cancel a pending composition;
- whether preedit becomes shared semantic UI state or remains local to the originating Frontend.

## Decision

1. Add the separately versioned optional capability `ime-composition/1`, which enables the optional `ime` namespace. A request alone never enables the extension; only `hello_ack.accepted_capabilities` does.
2. Define `ime.composition.start`, `ime.composition.update` and bidirectional `ime.composition.cancel` messages in that namespace. One active composition is allowed per attached client connection; its non-zero 64-bit identifier increases strictly and never wraps/reuses.
3. Keep commit on the already accepted `core/input.text` message. When the capability is accepted, its optional `composition_id` field identifies the active composition. The Backend consumes that ID only after successful admission to the bounded Runtime input queue, so queue-full retry is safe and a second successful dispatch is impossible.
4. Bind start to a focused visible Runtime view and exact document version. The Backend captures the authoritative Runtime selection; Runtime rechecks the view, version and selection before applying committed text. Stale context is rejected without mutation.
5. Define preedit offsets as UTF-8 byte offsets that must lie on code-point boundaries. The preedit text is valid UTF-8 and bounded to 4096 bytes. This is independent of visual grapheme segmentation and shaping.
6. Keep preedit client-local. The Backend validates updates but does not send them to Runtime, the semantic UI model, extensions or Observer Frontends. The originating Frontend renders the local overlay. Only committed text reaches Runtime/Kernel.
7. Cancel an active composition on focus loss, view/selection change, document version change, view removal, Driver revocation or session reset. A forced Backend cancellation is delivered to the originating Frontend in the ordered outbound stream. Detach/reconnect drops the state and never restores it.
8. If the capability is absent, existing Protocol 1.0 committed-only `input.text` behavior remains; no `ime` namespace message or `composition_id` is sent.

The complete proposed wire schema, lifecycle rules, bounds, ownership and conformance vectors are in [IME composition and preedit contract v1](../proposals/ime-composition-contract-v1.md).

## Options considered

### A. Send preedit as ordinary `input.text`

Rejected. It treats transient text as committed document input, causing premature edits and making cancel/replace behavior impossible to express safely.

### B. Put preedit in `cdin.ui-model.v1` and broadcast it to all Frontends

Rejected. IME preedit originates from one native input device and is transient to one Driver/view. Broadcasting it would turn device-local state into shared Runtime UI state and expose uncommitted text to observers.

### C. Add mandatory core messages for all peers

Rejected. That would force every Protocol 1.0 peer to implement IME and would break the existing optional-capability compatibility model.

### D. Keep preedit entirely local and send only a bare committed `input.text`

Retained as the fallback when the capability is not accepted, but insufficient for negotiated sessions: the Backend cannot cancel stale composition after view/document/role transitions or bind a commit to the captured view/version/selection.

## Trade-offs

- The Backend sees bounded preedit payloads transiently for validation, but does not retain or broadcast them.
- A versioned optional namespace adds a small state machine to Backend; in return, stale commits, duplicate commits and Driver-role changes become deterministic.
- Byte offsets are unambiguous and compatible with canonical document positions, but each platform adapter must translate its native cursor/selection units at the boundary.
- The local-only presentation avoids observer leakage and keeps `cdin.ui-model.v1` free of device-local transient state.

## Consequences

- This ADR accepts the wire and ownership contract. Acceptance does not claim that any component currently implements the extension. No implementation may advertise `ime-composition/1` until the owning Frontend, Backend and Runtime work and CDIN end-to-end conformance pass. Follow-on implementation work is tracked in [Frontend #37](https://github.com/cdin-editor/frontend/issues/37), [Backend #22](https://github.com/cdin-editor/backend/issues/22), [Runtime #13](https://github.com/cdin-editor/runtime/issues/13) and [CDIN #118](https://github.com/cdin-editor/cdin/issues/118).
- The Runtime Host API 1.0.0 is unchanged. The composition context is an internal Backend-to-Runtime input-dispatch detail, not a new Host service or extension API.
- After acceptance, Frontend, Backend and Runtime implementation work is required in the owning repositories; CDIN must add a live integration test and pin compatible revisions.
- The existing unversioned `ime` capability remains a generic committed-text input declaration; it does not by itself enable the new namespace.

## References

- [Spec issue #14](https://github.com/cdin-editor/spec/issues/14)
- [Frontend Protocol wire contract](../architecture/protocol-wire.md)
- [Frontend Protocol architecture](../architecture/frontend-protocol.md)
- [Runtime UI Model](../architecture/ui-model-v1.md)
- [Runtime Host API 1.0.0](../contracts/runtime-host-api.md)
- [ADR-0018: Protocol wire format and mutation authority](ADR-0018-frontend-protocol-wire.md)
- [ADR-0020: Frontend topology and interaction](ADR-0020-frontend-topology-and-interaction.md)
