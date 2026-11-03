# ADR-0011: Extension UI under the Frontend Protocol

- **ID:** ADR-0011
- **Status:** `ACCEPTED` by explicit owner approval on 2026-11-03; integrated with the Frontend decisions in [ADR-0020](ADR-0020-frontend-topology-and-interaction.md).

## Context
The extension contract lets plugins add side panels, a prompt, providers and views, and plugins can subclass views and draw directly (`View:extend()`, the panels section of the contract). The Frontend Protocol sends semantic UI, not pixels, and frontends include terminals.

## Problem
How do plugins express UI so that every frontend can show it, without breaking existing plugins abruptly?

## Decision (accepted scope)
1. **Declarative widgets** for ordinary plugin UI: lists, trees, styled text, inputs, buttons. Every frontend implements them (EXT-030).
2. An **optional `canvas` capability** for free-form drawing. Only frontends that declare it receive canvas messages; plugins must degrade gracefully or report unavailability (EXT-031).
3. Migration mechanics for legacy direct-drawing APIs (including whether and how long to retain shims and the deprecation-log policy) are not settled by this decision; they remain governed by EXT-032 and require a separate owner-approved compatibility plan.

## Options
- **A. Keep arbitrary drawing for everything.** Pros: no plugin changes. Cons: TUI and any non-pixel frontend cannot show plugin UI at all.
- **B. Declarative only.** Pros: uniform across frontends. Cons: removes drawing plugins (graphs, minimaps).
- **C. Declarative widgets plus optional canvas (proposed).** Pros: uniform for the common case, power for the rest. Cons: two paths; canvas plugins are GUI-only in practice.

## Trade-offs
C costs a larger contract and two code paths, and keeps both reach and power. A would make the protocol pointless for non-GUI frontends.

## Consequences
- The extension contract gains the accepted declarative-widget and optional-canvas rules. Versioning migration and any legacy API shims remain separate implementation work.
- `cdin-x` plugins that draw must declare the `canvas` need.
- Implementation follow-up: port one real panel plugin to widgets and verify graceful degradation when `canvas` is not available. This follow-up is an implementation gate, not a condition on the owner's architectural decision.

## References
[extension-model.md](../architecture/extension-model.md), [frontend-protocol.md](../architecture/frontend-protocol.md), `docs/architecture/extension-contract.md` in `cdin` ("Side panels", "The prompt").


The owner-approved Frontend topology and graceful-degradation rules are integrated with [ADR-0020](ADR-0020-frontend-topology-and-interaction.md).
