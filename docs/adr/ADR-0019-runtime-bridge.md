# ADR-0019: PUC Lua 5.4 C API as the Runtime Host bridge

- **ID:** ADR-0019
- **Status:** `ACCEPTED`
- **Date:** 2026-11-02
- **Resolves:** OD-32

## Context

The Kernel exposes a C ABI. Runtime is Lua and must not call Kernel symbols or inspect Kernel-owned structs directly. The Backend is the composition root and already contains an optional bridge built from the Lua C API. The Runtime source targets Lua 5.4 semantics, and the Host contract is a narrow capability API rather than a general FFI surface.

## Decision

Use **PUC Lua 5.4 C API** as the only supported v1 Runtime bridge:

- Backend creates and owns the `lua_State` and registers Host callbacks.
- Lua callbacks and Runtime methods execute only on the Backend's recorded owner thread.
- The Backend's private Kernel adapter is the only code that includes or calls `cdin-kernel` public C ABI functions.
- Runtime receives opaque Host objects and structured values. Extensions receive only the Runtime extension contract and Host capabilities; they never receive native pointers or Kernel handles.
- Kernel notification wakeups only signal the Backend loop. They never enter Lua from worker/callback threads.
- Lua allocation/GC and Lua callbacks do not run while a Kernel lock is held; adapter calls finish before callback dispatch.

LuaJIT FFI and MetaCall are not supported alternatives in v1. Supporting either later requires a new ADR, compatibility tests and a separate explicit Runtime target.

## Consequences

The Backend's `CDIN_WITH_LUA` build is a production release requirement, not a best-effort optional path. CI must include Lua 5.4 development headers and a live Backend -> Runtime -> Kernel round-trip. Stub builds remain available for Kernel-independent services and protocol codec tests, but they cannot satisfy Runtime integration or release gates.

## References

- [Runtime Host contract](https://github.com/cdin-editor/runtime/blob/main/docs/contracts/runtime-host-api.md)
- [Backend component](../components/backend.md)
- [Lifecycle](../architecture/lifecycle.md)
