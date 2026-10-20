# ADR-0008: Persistence stays outside the kernel

- **ID:** ADR-0008
- **Status:** `ACCEPTED`. The kernel performs no file I/O; backend OS services own persistence and no standalone `cdin-data` repository is created at this stage.

## Context
Open decision OD-16: who owns persistence, serialization and storage? The `data` word is overloaded in this project ([glossary.md](../reference/glossary.md)).

## Problem
Where do loading, saving, atomic writes, byte-order-mark handling and session storage live?

## Decision
- The kernel never reads or writes files (KERNEL-007, DATA-001).
- The kernel exchanges bytes only: create from a byte buffer; read bytes of a snapshot; serialize to a caller-provided sink in bounded chunks (DATA-002).
- The backend's OS services perform I/O and policy; no `cdin-data` repository is created until a second consumer exists (DATA-007, [data.md](../components/data.md)).

## Options
- **A. Persistence in the backend (accepted).** Pros: no new boundary; reuses existing `fs` code; kernel stays deterministic. Cons: persistence logic is not reusable by other programs yet.
- **B. A `cdin-data` repository now.** Pros: reusable. Cons: a boundary with no second consumer; premature contract.
- **C. Persistence inside the kernel.** Pros: one place. Cons: breaks determinism and OS independence (KERNEL-001, KERNEL-007).

## Trade-offs
Reuse is deferred to the day a second consumer appears; the contract that matters (bytes in, bytes out, exact round trip) is fixed now (DATA-004).

## Consequences
BOM detection, encoding hints and line-ending choice for saving are caller policy. Saved-state tracking uses the kernel's clean marker (DOC-040).

## References
[data.md](../components/data.md), DATA-001 to DATA-007, TEXT-030, TEXT-042.
