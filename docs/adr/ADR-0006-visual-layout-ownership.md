# ADR-0006: Visual layout belongs to frontends

- **ID:** ADR-0006
- **Status:** `ACCEPTED`. The owner-approved architecture keeps shaping, bidi and visual layout outside the kernel.

## Context
Under the Frontend Protocol, somebody must decide where a line breaks, how tabs expand, how Persian text is shaped and bidi-reordered, and how far the view is scrolled. The kernel excludes layout and rendering (KERNEL-004). Shaping and bidi were declared outside the kernel by the owner.

## Problem
Who owns visual layout: the backend (so every frontend receives ready-made rows and columns) or the frontend?

## Decision
The frontend owns visual layout: wrapping, tab expansion, shaping, bidi reordering and scroll position in its own units. The protocol carries logical positions (byte offsets, lines) only. Visual motion (move up or down by visual line) is computed by the frontend and sent as a logical position request (PROTO-002, PROTO-003).

## Options
- **A. Frontend owns layout (accepted).** Pros: proportional fonts and shaping work correctly in a GUI; terminals use cells; the backend never needs font metrics. Cons: visual-line commands cannot be implemented purely in the backend; each frontend implements wrapping.
- **B. Backend owns layout in abstract cells.** Pros: uniform behaviour. Cons: wrong for proportional fonts and for Persian shaping; forces cell semantics onto GUIs.
- **C. Both with negotiation.** Pros: flexibility. Cons: two code paths and a complex protocol.

## Trade-offs
A pushes a modest amount of work (wrapping, scrolling) into each frontend and keeps the backend and kernel free of presentation. The existing Persian-aware Lua text pipeline (`data/core/text/`) is the starting point for the GUI frontend's implementation.

## Consequences
- `text/shaper.lua` and `bidi.lua` belong to the frontend side (FE-006).
- Commands that depend on visual lines are expressed as protocol requests handled by the frontend (PROTO-003).
- Headless and CLI frontends have trivial layout.

## References
PROTO-002, PROTO-003, ARCH-052, FE-006, [frontend-protocol.md](../architecture/frontend-protocol.md).
