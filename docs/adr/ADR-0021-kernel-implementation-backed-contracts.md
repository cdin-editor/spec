# ADR-0021: Kernel ABI 1.1.0 implementation-backed contracts

- **ID:** ADR-0021
- **Status:** `ACCEPTED` by explicit owner approval on 2026-11-03.
- **Scope:** Kernel package 1.2.1, public C ABI 1.1.0

## Context

The Spec previously described many behaviors as `PROPOSED` even though they are present in the current Kernel public ABI, implementation and conformance vectors. The owner requested a strict synchronization: accept only observable behavior supported by the current implementation and leave future mechanisms proposed, open or deferred.

## Decision

1. Promote only the Kernel requirements listed in the Spec 1.2.0 synchronization report whose semantics match the public ABI 1.1.0, inspected source and existing conformance vectors.
2. Where the earlier proposal overstated behavior, replace it with the narrower observable contract. In particular, bounded notifications expose at most eight edit descriptions; transactions use a copy-on-write tentative block; the newest undo unit may exceed the configured cap; reload-preserved history, Regex, nested transactions and Kernel anchors are not supported.
3. Keep internal data structures such as the copy-on-write block, cached line index, search index and handle-table layout out of the public contract.
4. Do not infer that inspected conformance vectors, unit tests, sanitizer targets or fuzz targets passed during this review. They were inspected, not run in this review session.
5. Keep the Kernel-declared Spec compatibility target at `1.1.0`. Spec release `1.2.0` records application-level owner decisions and implementation synchronization; it does not change the Kernel header or claim that the Kernel implements Frontend/Backend features.

## Consequences

- Kernel requirements promoted to `ACCEPTED` are recorded in `docs/kernel/implementation-status.md` and their topic pages.
- Decisions OD-01, OD-02, OD-03, OD-04, OD-06, OD-07, OD-08, OD-18, OD-19, OD-20 and OD-21 are resolved only to the current ABI 1.1.0 behavior.
- Regex (OD-09), invalid-UTF-8 partition details (OD-11), Kernel-managed anchors (OD-28), Unicode normalization profiles (OD-29), parallel mutation (OD-27), and other unimplemented proposals remain outside acceptance.

## References

- [Kernel implementation status](../kernel/implementation-status.md)
- [Kernel ABI and compatibility](../architecture/abi-and-compatibility.md)
- [Kernel concurrency](../architecture/concurrency.md)
- [Open Decisions Register](open-decisions.md)
- [ADR-0017: Kernel call concurrency and ordering](ADR-0017-kernel-synchronous-concurrency.md)
