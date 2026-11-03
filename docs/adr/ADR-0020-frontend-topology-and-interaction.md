# ADR-0020: Frontend topology, TUI-first delivery and presentation contracts

- **ID:** ADR-0020
- **Status:** `ACCEPTED` by explicit owner approval on 2026-11-03.
- **Resolves:** OD-12, OD-25, OD-30

## Context

CDIN has an accepted semantic Frontend Protocol and an emerging Backend/Runtime split. The remaining Frontend proposals need one consistent ownership model before the standalone frontend repository and the first interactive adapter are built. This ADR records the owner's accepted F-01..F-13 decisions. It does not claim that the target Frontend repository or TUI has already shipped.

## Decision

1. **Repository topology.** Use one `cdin-editor/frontend` repository with peer `core`, `gui-sdl`, `tui` and `headless` adapters. `core` contains shared protocol/client abstractions and non-rendering utilities. The GUI and TUI retain independent renderers and layout implementations.
2. **Delivery order.** `headless` is the protocol reference adapter. The TUI is the first interactive frontend and is a full-screen, Neovim-like terminal editor. A non-interactive command runner is a distinct `cli` target and remains `DEFERRED`.
3. **Plugin UI.** Ordinary extension surfaces use declarative widgets. Free-form drawing is an optional `canvas` capability; a frontend without it degrades gracefully or reports the surface unavailable. This supersedes the requirement for arbitrary plugin drawing in every frontend and accepts ADR-0011.
4. **Policy and native boundaries.** Runtime UI policy, keymaps, commands and semantic UI state remain in PUC Lua 5.4. Native C owns protocol encoding/decoding, platform event integration, input adapters and rendering backends. Frontends and Runtime never call the Kernel ABI or inspect Kernel handles.
5. **Capabilities.** A central registry defines capability names and semantics. Requested capabilities are not active capabilities. Only capabilities implemented by both peers and accepted for that session may be advertised or used.
6. **Keyboard.** `input.key` carries key identity, action and modifiers; `input.text` carries committed text and IME output separately. The frontend adapts devices but does not resolve editor keymaps; Runtime owns that policy.
7. **Semantic model and wire.** A layout leaf's `active_view` is `text|null`. `ui.options` is a typed map with the initial keys and types defined in `ui-model-v1.md` and `protocol-wire.md`. The accepted wire target is Protocol 1.0.0. This is a major bump from 0.2.0 because changing the value domain of an existing required field is not an additive minor evolution under PROTO-040/ADR-0018.
8. **Text presentation.** Frontends own UTF-8 decoding for display, grapheme-aware visual navigation, shaping, bidi reordering, wrapping, tab expansion and scrolling. The Kernel and protocol continue to use logical byte offsets. The TUI maps terminal-cell operations back to logical byte positions.
9. **Terminal lifecycle.** The interactive TUI event loop multiplexes input, Backend readiness, resize and termination; it does not busy-wait. It restores raw mode, cursor and screen state on normal exit, handled errors and catchable termination signals routed through cleanup. Uncatchable termination and power loss are outside this guarantee; teardown remains deterministic.

## Consequences

- The owner-approved Frontend requirements are `FE-001..FE-007`, `FE-009`, `FE-010..FE-020` and `FE-023`; `FE-008` (non-interactive CLI) remains deferred. `FE-021` and `FE-022` are historical migration evidence from the pre-extraction `cdin` tree, not a claim about a standalone Frontend implementation.
- Protocol 1.0.0 adds a nullable `active_view` and a required typed options map whose individual keys are optional. It is an accepted major-version contract target; Backend 0.2.0 code must be updated and its validator/projector/conformance tests must pass before 1.0.0 support is advertised.
- The TUI, the Frontend repository and capability implementations remain implementation work. `ACCEPTED` here records the owner's design decision, not implementation status.
- The headless adapter remains the reference for protocol behavior. No common GUI/TUI rendering pipeline is mandated.
- The peer/dependency boundary and the restriction of display-toolkit dependencies to the frontend are accepted through `ARCH-042` and `ARCH-043`.

## References

- [Frontend component](../components/frontend.md)
- [Frontend Protocol](../architecture/frontend-protocol.md)
- [Protocol wire contract](../architecture/protocol-wire.md)
- [Runtime UI Model](../architecture/ui-model-v1.md)
- [ADR-0011: Extension UI](ADR-0011-extension-ui.md)
- [ADR-0018: Frontend Protocol wire](ADR-0018-frontend-protocol-wire.md)
- [ADR-0019: Runtime bridge](ADR-0019-runtime-bridge.md)
