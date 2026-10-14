# ADR-0016: Architecture-specific optimizations (SIMD and assembly) in the kernel

- **ID:** ADR-0016
- **Status:** `PROPOSED`. The owner asked for assembly to improve speed; the conditions below are the proposal for doing it safely and await the owner's confirmation. It narrows, but does not remove, the accepted decision that the kernel is C11 ([ADR-0004](ADR-0004-implementation-language.md), KERNEL-011).

## Context
The owner wants performance as good as possible and asked for assembly where it helps. The kernel is C11 behind a C ABI, must build on Linux, Windows (MinGW-based) and macOS, must be deterministic (KERNEL-007), and must behave identically for every implementation (KERNEL-012). Inline assembly is not part of standard C and differs between compilers and architectures.

## Problem
How does the kernel use assembly or SIMD for speed without losing portability, correctness, testability or determinism?

## Decision (proposed)
Allow architecture-specific optimized paths, under these conditions (KERNEL-015):

1. **Correctness first.** Optimization starts only after all functional milestones pass and benchmarks exist.
2. **Algorithms before instructions.** Order of attempts: better algorithm or data structure, then tuned portable C, then SIMD intrinsics, then raw assembly only if intrinsics cannot reach the benchmark target.
3. **Portable fallback always.** Every optimized path has a portable C11 implementation of the same function, selectable at build time (a force-portable switch).
4. **Identical results.** The optimized and portable paths must give bit-identical results; this is verified by running all conformance vectors under both and by differential fuzzing.
5. **Isolated.** Optimized code lives in a dedicated directory per architecture; no optimized code touches handles, locks, queues or the public API.
6. **Measured.** An optimized path is kept only with recorded benchmark numbers showing at least a 10% improvement on the targeted benchmark and no regression elsewhere (the same threshold the current project rule uses for regressions).
7. **Runtime selection stays deterministic.** CPU feature detection happens when a kernel instance is created and its result is stored in that instance (no hidden global state, no clock, no environment).
8. **Scope of targets.** x86-64 and AArch64 only. GNU-style syntax only; other toolchains use the fallback.

Expected hot spots (to be confirmed by measurement, not assumed): UTF-8 validation and region classification, line-terminator scanning, byte and literal search, copying inside the text store.

## Options
- **A. C11 only.** Pros: maximum portability and simplicity. Cons: may leave performance on the table in byte-scanning loops.
- **B. Optional architecture-specific paths with fallback (proposed).** Pros: speed where it matters, correctness protected by the fallback and differential tests. Cons: more code, a build matrix, more to fuzz.
- **C. Assembly first or assembly required.** Pros: possible peak speed. Cons: not portable, hard to review and test, ties the kernel to specific CPUs, contradicts the rule that any implementation behaves identically.

## Trade-offs
B adds testing and maintenance cost and keeps the kernel correct and portable. Compilers' auto-vectorization and intrinsics typically reach most of the benefit of hand-written assembly for scanning loops; raw assembly is the last resort, not the first move.

## Consequences
- KERNEL-011 remains true for the portable implementation; arch paths are an addition (KERNEL-015).
- The Makefile gains a force-portable switch and `make check` runs twice.
- A perf milestone follows the functional milestones in the kernel build plan; there is no assembly before it.
- The ABI, the contracts and the conformance vectors do not change.

## References
KERNEL-007, KERNEL-011, KERNEL-012, KERNEL-015, TEST-013, [ADR-0004](ADR-0004-implementation-language.md).
