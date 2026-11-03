# Transactions

A transaction groups several edits into one logical operation with one undo unit and one change notification.

## 1. Accepted model

- **TXN-001** `ACCEPTED` An independent edit is one undo unit. — *Verify:* CONF
- **TXN-002** `ACCEPTED` An explicit transaction groups several edits into one logical operation. — *Verify:* CONF
- **TXN-003** `ACCEPTED` A committed transaction creates one undo unit. — *Verify:* CONF
- **TXN-004** `ACCEPTED` Commit publishes one logical change notification. — *Verify:* CONF
- **TXN-005** `ACCEPTED` Abort, or failure, rolls the transaction's changes back. A transaction MUST NOT require a full copy of the document per operation. — *Verify:* CONF, PERF
- **TXN-006** `ACCEPTED` Grouping of consecutive typing is controlled (see [undo-redo.md](undo-redo.md)). — *Verify:* CONF

## 2. Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Active: begin
    Active --> Active: replace, batch replace
    Active --> Committing: commit
    Committing --> Idle: version published, undo unit recorded, notification queued
    Active --> RollingBack: abort, failure, close, shutdown
    RollingBack --> Idle: tentative changes discarded
    Active --> Active: failed edit inside transaction (policy below)
```

*Caption: `PROPOSED` transaction states per document.*

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant K as Kernel
    C->>K: begin(doc, expected v7)
    K-->>C: tx handle
    C->>K: replace(tx, range A)
    C->>K: replace(tx, range B)
    Note over K: tentative state visible only to tx handle, committed version stays v7
    alt commit
        C->>K: commit(tx)
        K-->>C: new version 8, one undo unit, one notification
    else abort
        C->>K: abort(tx)
        K-->>C: unchanged, still v7
    end
```

*Caption: `PROPOSED` transaction flow.*

## 3. Proposed details

- **TXN-010** `ACCEPTED` `begin` carries an expected version (or "any"). A mismatch fails with `STALE_VERSION` and no transaction starts. — *Verify:* CONF
- **TXN-011** `ACCEPTED` Edits inside a transaction are validated against the transaction's own tentative state. A failed edit inside a transaction leaves the transaction active with the failed edit unapplied; the caller may abort. — *Verify:* CONF
- **TXN-012** `ACCEPTED` The document version does not change while a transaction is active; it increases by exactly one at commit (DOC-011). A transaction that applied no content change commits without a new version and produces no undo unit. — *Verify:* CONF
- **TXN-013** `ACCEPTED` A transaction owns a private tentative text block that initially shares the committed block and uses copy-on-write on its first mutation. Rollback discards the tentative block and its edit records; it does not replay an inverse log against the committed document. Transaction memory is bounded by the configured transaction-memory limit. — *Verify:* CONF, INSPECT
- **TXN-014** `ACCEPTED` A transaction is identified by a handle (index plus generation). Using a handle after commit or abort returns `INVALID_HANDLE`. — *Verify:* CONF
- **TXN-015** `ACCEPTED` A committed transaction produces one logical notification with its primitive edit count and ordered edit descriptions. At most `CDIN_NOTIF_MAX_EDITS` descriptions are stored; `edits_stored` and `edit_count` let clients detect truncation and choose a full resynchronization. — *Verify:* CONF, INSPECT
- **TXN-016** `ACCEPTED` Failure in the kernel during commit (for example `NO_MEMORY`) rolls the transaction back completely and reports the failure; the document remains at the last committed version. — *Verify:* CONF (with an injected failing allocator)

## 4. Interaction with other writers and readers

- **TXN-007** `ACCEPTED` While a transaction is active on a document, mutation requests on that document not belonging to the transaction fail with `BUSY`. Other documents are unaffected. Alternative (queueing) is recorded in [OD-21](../adr/open-decisions.md). — *Verify:* CONF
- **TXN-008** `ACCEPTED` Reads by other callers during an active transaction see the last committed version. Only the transaction's handle may read tentative content (CONC-012). — *Verify:* CONF
- **TXN-009** `ACCEPTED` Closing the document or shutting the kernel down aborts the active transaction and rolls it back (CONC-021, DOC-031). — *Verify:* CONF

## 5. Nesting

- **TXN-020** `ACCEPTED` Nested transactions are not supported in the first version. `begin` on a document with an active transaction fails with `INVALID_STATE` (or `BUSY` for a different caller). — *Verify:* CONF
- **TXN-021** `DEFERRED` Nested transactions with partial rollback, and savepoints. Revisit with [OD-03](../adr/open-decisions.md). — *Verify:* INSPECT

## 6. Why not queue behind a transaction

A transaction can be long-lived (a refactoring across many ranges). If other writers were silently queued behind it, one slow client could stall every other writer on the document without anyone knowing why. Rejecting with `BUSY` is explicit and makes the contention visible and testable.
