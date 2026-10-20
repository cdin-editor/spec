# ADR-0003: C ABI at binary boundaries

- **ID:** ADR-0003
- **Status:** `ACCEPTED`

## Context
Components must be replaceable independently, possibly in different languages. The owner accepted the C ABI as the direction for binary boundaries, without implying that every internal part is a separate dynamically loaded module.

## Problem
What interface style do binary boundaries between components use, and what does it require?

## Decision
- Binary boundaries use the C ABI (ABI-001).
- Components are not required to be dynamically loaded modules (ABI-013).
- The rules in [abi-and-compatibility.md](../architecture/abi-and-compatibility.md) apply: opaque handles with generations, status returns, explicit memory ownership, struct-size prefixes, additive evolution, version and feature queries, injected allocators, no exceptions or `longjmp` across the boundary.

## Options
- **A. C ABI (decision).** Pros: every language can call it; stable; mirrors the current C-to-Lua binding discipline. Cons: manual memory rules; no rich types.
- **B. A C++ interface.** Pros: richer types. Cons: ABI instability across compilers; harder for other languages.
- **C. A serialized protocol everywhere.** Pros: language-neutral. Cons: overhead for the hot path between the backend and the kernel; unnecessary in one process.
- **D. A language-specific API (for example Rust traits).** Pros: type safety. Cons: ties the architecture to one language.

## Trade-offs
Manual discipline is the price of universality. The rules reduce it to a small, checkable set (STATIC checks on headers, sanitizers, fuzzing).

## Consequences
- The exact Kernel C API, numeric constants and structure layouts are frozen for ABI 1.0.0 in the public kernel header. The Frontend Protocol serialized encoding remains a separate open decision.
- The Frontend Protocol uses the same discipline for its in-process transport and offers a serialized transport for language-neutral use ([ADR-0005](ADR-0005-frontend-protocol.md)).
- The runtime (Lua) is behind the backend's host API, not a C ABI boundary.

## References
ABI-001 to ABI-022, [abi-and-compatibility.md](../architecture/abi-and-compatibility.md).
