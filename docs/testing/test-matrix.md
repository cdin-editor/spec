# Test matrix

Maps each requirement group to its verification methods and conformance-vector families. **Nothing in this matrix has been run.** "Planned" means designed in [conformance.md](conformance.md), not written.

Methods are defined in [conventions.md](../reference/conventions.md): `INSPECT`, `STATIC`, `CONF`, `FUZZ`, `SAN`, `PERF`, `INTEG`.

## 1. Required test groups

| # | Group | Requirement IDs | Methods | Vector families | State |
|---|---|---|---|---|---|
| 1 | Multi-document lifecycle | DOC-001 to DOC-050 | CONF, SAN | `doc.lifecycle` | planned |
| 2 | Document versioning | DOC-010 to DOC-013, UNDO-002, TXN-012 | CONF | `doc.lifecycle`, `edit.version` | planned |
| 3 | Valid and invalid UTF-8 | TEXT-001, TEXT-004, TEXT-010 to TEXT-013 | CONF, FUZZ | `text.bytes` | planned |
| 4 | Exact LF, CRLF, CR preservation | TEXT-002, TEXT-003, TEXT-020 to TEXT-023 | CONF, FUZZ | `text.eol` | planned |
| 5 | Position conversion | POS-001 to POS-052 | CONF | `pos.convert` | planned |
| 6 | Transactions, rollback, undo/redo | TXN-001 to TXN-021, UNDO-001 to UNDO-040 | CONF, PERF | `txn`, `undo` | planned |
| 7 | Atomic changes and notification ordering | EDIT-010 to EDIT-020, NOTIF-001 to NOTIF-012 | CONF | `edit.replace`, `notif` | planned |
| 8 | Synchronous kernel concurrency and snapshots | CONC-001 to CONC-040 | CONF, SAN | `conc` | kernel unit/conformance checks exist; backend/protocol integration planned |
| 9 | Stale-request rejection without mutation | EDIT-003, EDIT-004, EDIT-006, ERR-002, ERR-010 | CONF | `edit.version` | planned |
| 10 | Literal and byte search; regex deferred | SEARCH-001 to SEARCH-014, SEARCH-050 to SEARCH-053 | CONF, FUZZ | `search.literal`, `search.bytes` | Kernel vectors exist for supported modes; regex unsupported/deferred |
| 11 | Multiline literal search | SEARCH-006, SEARCH-030 to SEARCH-032 | CONF | `search.literal` | Kernel vector coverage exists; regex behavior deferred |
| 12 | Unicode behaviour; `ی` versus `ي` | SEARCH-005, SEARCH-020 to SEARCH-024 | CONF | `search.literal` | planned |
| 13 | Raw-byte search | SEARCH-008, SEARCH-040 to SEARCH-042 | CONF | `search.bytes` | planned |
| 14 | Results bound to a document version | SEARCH-007, SEARCH-010 | CONF | `search.*` | planned |
| 15 | Module ABI and compatibility | ABI-001 to ABI-022 | STATIC, CONF, INTEG | `abi` | planned |

## 2. Further groups from this specification

| Group | Requirement IDs | Methods | Vector families | State |
|---|---|---|---|---|
| Kernel independence and determinism | ARCH-002, KERNEL-001, KERNEL-004, KERNEL-006 to KERNEL-009 | STATIC, INSPECT | none (static rules) | planned |
| Dependency directions | ARCH-040 to ARCH-046 | STATIC | `include-direction check` | planned |
| Error model | ERR-001 to ERR-030 | CONF, FUZZ | `abi`, `edit.*` | planned |
| Frontend Protocol | PROTO-001 to PROTO-042 | CONF, INTEG | `proto.*` | planned |
| Frontend peers and capabilities | FE-001 to FE-009, ARCH-009 | INSPECT, STATIC, INTEG | `proto.handshake` | planned |
| Notification overflow and resync | NOTIF-006, NOTIF-007, NOTIF-009 | CONF, PERF | `notif` | planned |
| Resource bounds | ARCH-021, KERNEL-013, UNDO-030, PROTO-021, BE-009 | PERF, CONF | `conc`, `undo`, `proto.updates` | planned |
| Process and module lifecycle | LIFE-001 to LIFE-030 | INTEG | none (integration) | planned |
| Extension boundary | ARCH-006, EXT-001 to EXT-056 | INSPECT, STATIC, INTEG | `ext.contract` | planned |
| Existing invariants | ARCH-020 to ARCH-028 | as stated per requirement | existing tests (`tests/`) | partly exists, not run for this specification |
| Persistence | DATA-001 to DATA-007 | STATIC, CONF, INTEG | `text.bytes` (round trip) | planned |
| Specification process | SPEC-001 to SPEC-041 | INSPECT, STATIC | none | planned |

## 3. Sanitizer and fuzz plan

| Target | Sanitizers | Fuzz input |
|---|---|---|
| kernel ABI | ASan, UBSan; TSan on `conc` | struct sizes, flags, ranges, byte strings including invalid UTF-8 |
| line-ending and region classifiers | ASan, UBSan | arbitrary bytes with CR and LF in every combination |
| regex front end | ASan, UBSan | patterns and haystacks, with step limits |
| protocol decoder | ASan, UBSan | arbitrary frames, truncated and oversized |
| notification queues | TSan | concurrent subscribe, drain, overflow |

## 4. What a verification run must report

Per requirement ID: method, vector family, implementation and version, date run, result. A requirement with no entry is reported as unverified ([conformance.md](conformance.md), TEST-030).

## 5. Honest status

- Kernel vectors and a runner exist in the separate `cdin-kernel` repository; supported ABI 1.0.0 functionality has been exercised. The remaining rows describe planned checks for backend integration, the Frontend Protocol, runtime and frontends. See [kernel implementation status](../kernel/implementation-status.md) for the boundary between executed and unverified scope.
- Existing tests in the `cdin` repository were not run as part of producing this specification.
