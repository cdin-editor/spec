# ADR-0026: Semantic UI presentation payloads

- **ID:** ADR-0026
- **Status:** `PROPOSED`
- **Decision scope:** Additive, capability-negotiated presentation schemas for Frontend Protocol 1.0.0.

## Context

The accepted Runtime UI Model contains resolved semantic styles, declarative panels, prompts and widget state. Backend projects these values through `ui.style_table`, `ui.panel` and `ui.prompt`, while Frontend owns rendering and local geometry. The current wire contract leaves parts of those maps opaque. The GUI adapter therefore preserves their encoded values but cannot safely assign semantics to unknown fields or widget payloads. Different Frontends could otherwise interpret the same Runtime model differently.

The project needs one portable, bounded schema that does not move theme policy, command authorization, document state or pixel geometry into Frontend.

## Problem

The contract must define:

- typed style-role attributes and exact byte-based line spans;
- declarative panel, prompt and widget schemas with bounded nesting and payload sizes;
- atomic snapshot/revision and removal behavior;
- compatibility and unknown-kind fallback;
- safe widget activation without a Frontend-owned command or authorization path;
- transient input-widget editing without accidentally sending document-edit events.

## Proposed decision

Adopt the optional capability `ui-presentation/1` as an additive Protocol 1.0.0 extension, using the schemas and semantics in [UI presentation contract v1](../proposals/ui-presentation-contract-v1.md).

1. **Ownership remains explicit.** Runtime owns semantic styles, panel/widget identities and values, and command policy. Backend validates and projects the model. Frontend owns pixel layout, local focus/geometry, text shaping and drawing. Kernel owns no presentation state.
2. **Snapshot state is atomic.** Style, panel and prompt revisions equal the root `cdin.ui-model.v1` revision. Frontend stages all values and commits only with the matching `ui.flush`; stale or malformed groups preserve the previous committed state. Complete-snapshot omission removes prior panels and `prompt:null` clears the prompt.
3. **Styles are portable.** Style roles use RGBA channels and explicit emphasis attributes. Line spans use zero-based UTF-8 byte offsets into the exact returned line bytes, never glyph or code-point indices. Unknown roles fall back to the default role; invalid known attributes reject the containing atomic update.
4. **Widgets are declarative and bounded.** The v1 kinds are `label`, `text`, `list`, `tree`, `button` and `input`. Payloads have explicit item, nesting and byte limits. Unknown kinds render only as non-interactive fallback content.
5. **Commands remain Runtime-owned.** Widget activation uses the existing `core/request.command` path. Backend enforces the Driver lease; Runtime validates command existence, arguments, authorization and effects. A widget cannot bypass normal command registration.
6. **Input widgets edit locally until submission.** A focused input widget has a bounded, disposable Frontend buffer. Its keystrokes are not forwarded as document `input.key` or `input.text`; submission sends one ordinary Runtime command containing the final value. Runtime remains authoritative.
7. **Capability negotiation is mandatory.** A Frontend may rely on interactive semantics only after Backend includes `ui-presentation/1` in `hello_ack.accepted_capabilities`. Without acceptance, a peer may show compatible static text only and MUST NOT emit widget actions.

The protocol core message catalogue and existing Protocol 1.0.0 peers remain unchanged. The capability MUST NOT be advertised by a component until the shared positive/negative conformance vectors are implemented and pass in the owning repositories.

## Options considered

### Leave presentation maps opaque indefinitely

Rejected as the long-term contract. It prevents implementation-specific interpretation, but it also prevents interoperable semantic rendering and testable compatibility.

### Let each Frontend define widget and style meanings

Rejected. It creates divergent UI semantics and risks moving command policy into individual renderers.

### Add arbitrary drawing commands or toolkit-native handles

Rejected for v1. Those values are not portable, are difficult to bound and would couple Runtime to a renderer. Free-form drawing remains a separately negotiated capability.

### Let Frontend execute widget commands locally

Rejected. It bypasses Backend Driver authorization and Runtime command registration, validation and policy.

## Trade-offs

- Explicit schemas constrain future UI payload evolution; additive optional fields and capability negotiation provide a compatibility path.
- Frontend can implement input fields without changing the canonical document path, but local input is intentionally lost when the widget is removed, disabled or loses its Driver lease.
- Atomic snapshot rejection is stricter than accepting independent partial widget updates, but it prevents the renderer from displaying a state that never existed in Runtime.

## Consequences

- This ADR remains a proposal and does not amend the accepted Protocol contract until the project owner accepts it.
- [Spec #21](https://github.com/cdin-editor/spec/issues/21) tracks the schemas and vectors.
- Frontend implementation and production presentation remain tracked by [Frontend #15](https://github.com/cdin-editor/frontend/issues/15).
- CDIN must consume compatible immutable component versions and prove the live product path under [CDIN #111](https://github.com/cdin-editor/cdin/issues/111); component-only tests do not enable the capability.
- Backend and Runtime implementation checkpoints must be opened or linked after contract acceptance. The Runtime UI Model already owns the semantic source; neither component may duplicate Frontend rendering policy.

## References

- [Runtime UI Model v1](../architecture/ui-model-v1.md)
- [Frontend Protocol wire contract](../architecture/protocol-wire.md)
- [UI presentation contract v1](../proposals/ui-presentation-contract-v1.md)
- [UI presentation conformance vectors](../testing/vectors/ui-presentation-v1.json)
- [ADR-0018 — Frontend Protocol wire format and mutation authority](ADR-0018-frontend-protocol-wire.md)
- [ADR-0020 — Frontend topology and interaction](ADR-0020-frontend-topology-and-interaction.md)
