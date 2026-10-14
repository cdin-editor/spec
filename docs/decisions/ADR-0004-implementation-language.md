# ADR-0004: Implementation language: C11

- **ID:** ADR-0004
- **Status:** `ACCEPTED` for the kernel and the backend. Frontends and other consumers are free to use any language (they use the protocol or the ABI).

## Context
The existing `cdin` core is C11 with Lua 5.4, libuv and SDL. The kernel's boundary is a C ABI. The project is maintained by one person, with a three-platform build and release pipeline already in place.

## Problem
In which language are the kernel and the backend written?

## Decision
C11 for both (KERNEL-011). The specification does not require C: a different implementation of the kernel, in another language, is valid if it passes the conformance vectors.

## Options
- **A. C11 (decision).** Pros: existing code, build, CI and Lua binding; no new toolchain; natural fit for the C ABI and the Lua C API. Cons: no memory safety by construction.
- **B. Rust.** Pros: memory safety, strong concurrency model; good fit for a multithreaded kernel. Cons: rewrite cost of existing C; unsafe bridges to the Lua C API; new toolchain on the three-platform pipeline (including a MinGW-based Windows build).
- **C. Zig or C++.** Pros: improved ergonomics. Cons: new toolchain, and for C++ an unstable ABI at the boundary.

## Trade-offs
Safety is bought back by discipline instead of by the language: strict warnings as errors, sanitizers on every run, thread sanitizer on concurrency vectors, fuzzing at every input boundary, an injected failing allocator, and the existing memory-accounting rules (TEST-010 to TEST-013).

## Consequences
- A second kernel implementation in Rust remains possible behind the same contract; the contract makes that a replacement, not a rewrite of the system.
- Requirements in this specification that depend on the language (none are normative) are limited to the sketches in the ABI document, which are labelled non-normative.

- The owner later asked for assembly where it improves speed. That is handled as an addition, not a change of language: optional architecture-specific paths with a portable C11 fallback ([ADR-0016](ADR-0016-arch-specific-optimizations.md), `PROPOSED`).

## References
KERNEL-011, ABI-001, [conformance.md](../testing/conformance.md).
