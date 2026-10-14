# ADR-0002: The kernel owns documents; everything else is a client

- **ID:** ADR-0002
- **Status:** `ACCEPTED`

## Context
Today the document model lives in Lua (`data/core/doc/`), and the architecture overview of the `cdin` repository states the opposite principle: the C layer "knows nothing about documents, views, commands or keybindings" and the split is a *capability* argument, not a layering argument.

The new architecture introduces `cdin-kernel`, a generic text engine that owns canonical document state, undo, transactions, versions, notifications and search.

## Problem
Where does canonical document state live, and how do other components relate to it?

## Decision
- The kernel owns canonical document state (KERNEL-002).
- The kernel does not know who its clients are (KERNEL-006). The Lua document layer is one client of the ABI among any others.
- No other component keeps an independent copy of document content or undo history (KERNEL-005).
- Frontends and the runtime may keep disposable derived caches, invalidated by version.

## Options
- **A. Document model stays in Lua; the kernel is only a buffer.** Pros: no migration of the Lua document. Cons: no independent kernel, no second implementation, no way to test the document engine without Lua.
- **B. Kernel owns documents (decision).** Pros: a testable, replaceable engine with a stable ABI; the capability argument is preserved (the kernel still cannot know about GUIs, views or commands). Cons: the migration step M2 is large; the previously documented principle changes.

## Trade-offs
The earlier principle protected against document bugs in C by keeping documents out of C. The new principle protects against them by making the kernel small, deterministic (no clock, no I/O) and independently tested (conformance vectors, sanitizers, fuzzing), while keeping policy (commands, selections, highlighting) out of it.

## Consequences
- The statement in the current overview ("the C layer knows nothing about documents") becomes false for the kernel and remains true for the backend's UI and OS layers. The overview in `cdin` MUST be updated when the kernel lands (recorded as a contradiction in [status.md](../reference/status.md)).
- Migration phase M2 makes the Lua document a kernel client ([migration.md](../architecture/migration.md)).
- Syntax highlighting, text shaping and bidi stay outside the kernel (RT-009).

## References
KERNEL-001 to KERNEL-006, [kernel/overview.md](../kernel/overview.md), `docs/architecture/overview.md` in `cdin`.
