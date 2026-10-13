# ADR-0013: Hot-swap and state migration

- **ID:** ADR-0013
- **Status:** `DEFERRED`. General hot-swap is not accepted for this phase. The items below are unconfirmed proposals recorded so they are not lost.

## Context
Open decisions OD-13 and OD-14: should modules be replaceable while running, and how would their state move?

## Problem
Is live replacement of modules required now, and if so for which modules?

## Decision
Not decided; deferred. The first phase assumes **restart** to replace any module (LIFE-013). The module lifecycle diagram carries a placeholder for a future swap path ([lifecycle.md](../architecture/lifecycle.md), LIFE-012).

## Proposals (unconfirmed)
- Only modules explicitly designed for it may be swapped live.
- Replacing the kernel needs a restart in the first phase.
- A frontend coordinates its own reload.
- The runtime has its own controlled replacement policy.
- `cdin-x` supports plugin load and unload (already part of the Lua plugin protocol: `unload`).

## Requirements any future proposal must meet
State transfer is versioned and independent of implementation internals; the incoming module validates the state before activation; there is a rollback path; restart is always available as a fallback.

## Options
- **A. No hot-swap (current).** Pros: simplest. Cons: restart on every replacement.
- **B. Selective hot-swap for designated modules.** Pros: smooth for frontends and plugins. Cons: needs state-transfer design.
- **C. General hot-swap.** Pros: maximum flexibility. Cons: very high complexity; many state shapes.

## Consequences
Contracts do not preclude B (opaque handles, versioned state, no internal layout). No component may assume swap is available.

## References
ARCH-012, LIFE-012, LIFE-013, [lifecycle.md](../architecture/lifecycle.md), [OD-13](open-decisions.md), [OD-14](open-decisions.md).
