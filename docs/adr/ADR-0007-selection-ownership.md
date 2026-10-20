# ADR-0007: Selection ownership and undo

- **ID:** ADR-0007
- **Status:** `ACCEPTED`. Selection and view state belong to the view; the kernel stores opaque undo blobs only.

## Context
Open decision OD-05: who owns selections, and how does undo restore them? The kernel owns undo history (UNDO-001) and must stay generic (KERNEL-001, KERNEL-006).

## Problem
Selections are editing-surface state (several views of one document have different selections), yet users expect undo to restore the cursor.

## Decision
- The **view** owns selections and the logical scroll anchor (ARCH-051).
- The kernel stores up to two opaque caller blobs per undo unit (*before* and *after*) and returns the right one with the result of undo or redo (UNDO-020). It never interprets them.
- Merged units keep the first edit's *before* blob and the last edit's *after* blob (UNDO-022).

## Options
- **A. View owns, kernel stores opaque blobs (accepted).** Pros: kernel stays generic; works for any number of views; no editor policy in the kernel. Cons: the caller must serialize its selection state.
- **B. Kernel owns selections.** Pros: undo restores selections directly. Cons: couples the kernel to editor concepts and to multi-view semantics.
- **C. Kernel offers markers/anchors that move with edits.** Pros: convenient. Cons: kernel keeps per-client state; kept as a separate open question ([OD-28](open-decisions.md)).

## Trade-offs
A shifts a small serialization task to the runtime in exchange for a kernel that never learns what a selection is.

## Consequences
Blob size is a creation-time limit and counts toward undo memory (UNDO-021). The runtime's view layer defines its own blob format, versioned by the runtime.

## References
[undo-redo.md](../kernel/undo-redo.md), [module-boundaries.md](../architecture/module-boundaries.md).
