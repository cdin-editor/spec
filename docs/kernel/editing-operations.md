# Editing operations

The mutation surface of the kernel and its rules for validity, versions and atomicity.

## 1. Client access

- **EDIT-001** `ACCEPTED` Clients request edits through a direct API and receive changes through ordered change notifications. — *Verify:* CONF, INSPECT
- **EDIT-002** `PROPOSED` The single primitive is **replace**: replace the bytes of range `[start, end)` with a byte string. Insertion is replace with an empty range; deletion is replace with empty bytes. All higher-level operations (indent, join lines, transpose) are composed by the caller from replaces inside a transaction. — *Verify:* CONF
- **EDIT-005** `PROPOSED` A **batch replace** applies several non-overlapping ranges, all expressed against the same version, as one atomic edit and one undo unit (for multiple cursors). Overlapping or unordered ranges fail with `INVALID_ARGUMENT` and nothing is applied. — *Verify:* CONF, FUZZ

## 2. Version-checked requests

- **EDIT-003** `PROPOSED` Every mutation request carries an expected document version or an explicit "any version" marker. — *Verify:* CONF
- **EDIT-004** `ACCEPTED` When a request carries an expected version and it does not match the document's current version: the request is rejected; the document is unchanged; the response reports the expected version; the response reports the current version; the kernel MUST NOT transform stale positions automatically and MUST NOT silently re-apply the request against the new state. — *Verify:* CONF
- **EDIT-006** `ACCEPTED` The version check MUST be atomic with the mutation, so no race can turn a stale request into a valid change. — *Verify:* CONF, SAN

```mermaid
sequenceDiagram
    autonumber
    participant C1 as Client 1
    participant C2 as Client 2
    participant K as Kernel
    C1->>K: replace(range A, expected v7)
    C2->>K: replace(range B, expected v7)
    K->>K: serialize calls; validate expected version
    K->>K: first serialized call matches v7; apply, now v8
    K-->>C1: ok, new version 8
    K->>K: next call sees v8; expected v7 mismatches
    K-->>C2: STALE_VERSION (expected 7, current 8), no change
    Note over C2: client re-reads, recomputes, retries with expected v8
```

*Caption: two clients race on the same version. Kernel serialization/linearization decides which call applies first; the stale caller changes nothing and is told why. ABI 1.0.0 makes no wall-clock FIFO promise.*

## 3. Atomicity and validity

- **EDIT-010** `PROPOSED` An edit is atomic: after any outcome the document is either entirely unchanged or entirely changed. — *Verify:* CONF, FUZZ
- **EDIT-011** `PROPOSED` Validation (handle, flags, struct size, ranges, positions per POS-020 and POS-021, limits) happens before any change. A failed validation changes nothing and does not consume a version (ERR-002). — *Verify:* CONF
- **EDIT-012** `PROPOSED` The result of a successful edit includes: the new version; a description of the edit as `{start, removed length, inserted length}` in coordinates of the previous version; and the new document length. — *Verify:* CONF
- **EDIT-013** `PROPOSED` An edit that would exceed the document-size or single-edit limit fails with `LIMIT_EXCEEDED` and changes nothing. — *Verify:* CONF
- **EDIT-014** `PROPOSED` Edits do not copy the whole document (TXN-005); cost is proportional to the size of the edit and to the structure's own overhead, not to document size. — *Verify:* PERF

## 4. Result and notification relationship

- **EDIT-020** `PROPOSED` For every successful edit exactly one logical change notification is eventually produced for each subscriber, in version order (NOTIF-005). The submit result and the notification describe the same edit. — *Verify:* CONF

## 5. What editing does not include

- Selections and cursors (owned by the view; ARCH-051).
- Indentation, auto-pairing, completion and every other editor behaviour (policy, in the runtime).
- Saving (persistence, caller).

## 6. Existing behaviour

- **EXISTING** The current Lua document performs edits against its own buffer with undo and three hooks (`docs/architecture/internals.md`, "The document"). Those semantics are the starting point for the conformance vectors; where they differ from this specification, the difference is recorded in [status.md](../reference/status.md) and resolved by ADR. — *Anchor:* `data/core/doc/init.lua`, `docs/architecture/internals.md`
