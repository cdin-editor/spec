# ADR-0005: Frontend Protocol: backend owns state, frontends own presentation

- **ID:** ADR-0005
- **Status:** `ACCEPTED` for the semantic protocol model. Wire encoding, client library and multi-frontend mutation permissions remain open.

## Context
The owner wants new frontends (a CLI, a TUI, a different GUI toolkit, anything) to be easy to add, while today the GUI is SDL and is fused with the core. An earlier recommendation, a "Display Host port" carrying a display list, was **withdrawn** in discussion: it suits swapping one GUI toolkit for another but does not make a TUI or CLI easy, because the current Lua views draw with pixels and fonts, so every new frontend would have to reimplement text rasterization and the views' pixel assumptions.

## Problem
What boundary lets any number of frontends attach without changing the kernel, runtime or backend?

## Decision
Adopt the model used by editors with attachable UIs (Neovim is the reference the owner already uses for the `cdin-x` split):

- The **backend** owns canonical editor/document state and produces a semantic UI model.
- **Frontends** own presentation and input and speak one versioned **Frontend Protocol** with a capability handshake.
- The semantic contract is transport-independent. An in-process C ABI transport and a serialized byte-stream transport are target options; exact serialized framing remains open under OD-22.
- Frontends are peers; no private channel for the first one (ARCH-009, FE-001).
- Frontends own visual layout ([ADR-0006](ADR-0006-visual-layout-ownership.md)).
- A headless frontend is the reference for protocol behaviour.

## Options
- **A. Display-list port (withdrawn).** Frontend = toolkit adapter; UI logic stays above it in Lua with pixel coordinates. Pros: cheapest from today's code. Cons: TUI and CLI are awkward; views remain pixel-bound.
- **B. Semantic UI protocol (accepted).** Pros: any frontend implements one contract; TUI, CLI, web become tractable; backend testable headless. Cons: large migration (views become declarative); plugin custom drawing needs a canvas capability ([ADR-0011](ADR-0011-extension-ui.md)); protocol design effort.
- **C. Grid/cell redraw protocol (terminal-style).** Pros: simplest messages. Cons: loses GUI richness (proportional fonts, shaping, images); cell units everywhere.

## Trade-offs
The semantic protocol asks more of the backend and migration in return for cheap independent frontends. Pixel/display-list and grid/cell alternatives were rejected because they lock frontends to GUI toolkit assumptions or cap GUI fidelity.

## Consequences
- The `renderer` and `system` Lua APIs move out of the shared runtime surface into a gui-sdl private area during transition and are retired with shims (ARCH-027, RT-020).
- The backend is headless-capable (BE-001), which also enables protocol testing.
- Open points: encoding ([OD-22](open-decisions.md)), client library ([OD-23](open-decisions.md)), multi-frontend mutation ([OD-24](open-decisions.md)), UI core language ([OD-30](open-decisions.md)).

## References
[frontend-protocol.md](../architecture/frontend-protocol.md), [frontend.md](../components/frontend.md), [backend.md](../components/backend.md).
