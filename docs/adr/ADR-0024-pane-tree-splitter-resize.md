# ADR-0024: PaneTree splitter resize protocol contract

- **ID:** ADR-0024
- **Status:** `ACCEPTED`
- **Resolves:** Spec issue [#20](https://github.com/cdin-editor/spec/issues/20)

## Context

The accepted PaneTree model gives Runtime ownership of stable leaf/split identities and semantic split ratios. Frontend owns drawable-pixel geometry and hit-testing. The existing `core/input.mouse.target` remains a Runtime View ID and must not be overloaded with internal PaneTree IDs. GUI-SDL now has deterministic multi-pane geometry and splitter hit-testing, but the protocol does not yet define a committed resize operation.

## Decision

Accept the optional capability `pane-splitter-resize/1` and its `pane` namespace as specified in [PaneTree splitter resize contract v1](../proposals/panetree-splitter-resize-v1.md).

1. A Frontend may request the capability, but may send resize requests only when the Backend explicitly accepts it for that connection.
2. The Frontend owns divider hit-testing, pointer capture, drag preview and conversion from drawable pixels to integer basis points. The preview is local and disposable; no mutation is sent during pointer motion.
3. A commit identifies the stable split-node ID, exact committed layout revision and first-child ratio in basis points (1000..8999). It contains no pixels, viewport dimensions, View IDs or toolkit objects.
4. Backend enforces capability, Driver lease, request bounds and revision, and dispatches the semantic operation to the Runtime owner thread.
5. Runtime owns the PaneTree mutation and advances its semantic model revision exactly once for a successful change. It preserves the selected split's children, stable IDs and focus.
6. Backend publishes a successful result followed by the complete semantic layout snapshot and its matching `ui.flush` as one ordered bounded batch. A failed request never changes the tree.
7. Missing capability remains a Protocol 1.0.0-compatible no-resize fallback. Stale revisions cancel the local drag; the Frontend never silently retries against another layout.

## Ownership

- **Frontend:** pixel geometry, hit targets, drag lifecycle and local preview.
- **Backend:** capability negotiation, authentication/Driver enforcement, protocol validation, owner-thread dispatch and ordered atomic publication.
- **Runtime:** authoritative PaneTree and semantic ratio/revision mutation.
- **Kernel:** no role; PaneTree is editor presentation state, not document storage.
- **CDIN:** pins compatible component releases and tests the live product path; it does not implement component logic.

## Consequences

Acceptance defines the protocol; it does not claim the optional capability is implemented. No Backend may advertise it and no Frontend may emit `pane` messages until Frontend drag/commit, Backend dispatch/publication and Runtime owner-thread routing pass the shared conformance vectors and CDIN's live product test.

Implementation work is tracked in [Frontend #38](https://github.com/cdin-editor/frontend/issues/38), [Backend #23](https://github.com/cdin-editor/backend/issues/23), [Runtime #14](https://github.com/cdin-editor/runtime/issues/14) and [CDIN #118](https://github.com/cdin-editor/cdin/issues/118).

## References

- [Spec issue #20](https://github.com/cdin-editor/spec/issues/20)
- [PaneTree splitter resize contract v1](../proposals/panetree-splitter-resize-v1.md)
- [Shared conformance vectors](../testing/vectors/pane-splitter-v1.json)
- [ADR-0018: Frontend Protocol wire format and mutation authority](ADR-0018-frontend-protocol-wire.md)
- [ADR-0020: Frontend topology and interaction](ADR-0020-frontend-topology-and-interaction.md)
