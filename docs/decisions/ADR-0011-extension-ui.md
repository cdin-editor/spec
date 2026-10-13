# ADR-0011: Extension UI under the Frontend Protocol

- **ID:** ADR-0011
- **Status:** `PROPOSED`. Changes the extension contract; requires the owner's explicit approval (ARCH-027).

## Context
The extension contract lets plugins add side panels, a prompt, providers and views, and plugins can subclass views and draw directly (`View:extend()`, the panels section of the contract). The Frontend Protocol sends semantic UI, not pixels, and frontends include terminals.

## Problem
How do plugins express UI so that every frontend can show it, without breaking existing plugins abruptly?

## Decision (proposed)
1. **Declarative widgets** for ordinary plugin UI: lists, trees, styled text, inputs, buttons. Every frontend implements them (EXT-030).
2. An **optional `canvas` capability** for free-form drawing. Only frontends that declare it receive canvas messages; plugins must degrade gracefully or report unavailability (EXT-031).
3. Existing drawing APIs remain as **shims** with one deprecation log per process (ARCH-027, EXT-032), working through an in-process canvas path in the GUI during migration.

## Options
- **A. Keep arbitrary drawing for everything.** Pros: no plugin changes. Cons: TUI and any non-pixel frontend cannot show plugin UI at all.
- **B. Declarative only.** Pros: uniform across frontends. Cons: removes drawing plugins (graphs, minimaps).
- **C. Declarative widgets plus optional canvas (proposed).** Pros: uniform for the common case, power for the rest. Cons: two paths; canvas plugins are GUI-only in practice.

## Trade-offs
C costs a larger contract and two code paths, and keeps both reach and power. A would make the protocol pointless for non-GUI frontends.

## Consequences
- The extension contract gains a UI section and a version bump (EXT-040); a transitional shim layer is required (RT-020).
- `cdin-x` plugins that draw must declare the `canvas` need.
- Needs a prototype before acceptance (SPEC-030): one real panel plugin ported to widgets.

## References
[extension-model.md](../architecture/extension-model.md), [frontend-protocol.md](../architecture/frontend-protocol.md), `docs/architecture/extension-contract.md` in `cdin` ("Side panels", "The prompt").
