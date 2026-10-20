# ADR-0017: Synchronous kernel calls and linearization order

- **ID:** ADR-0017
- **Status:** `ACCEPTED`

## Context
The initial design described a FIFO mutation executor, queued requests, and two shutdown modes that drain or abort pending work. Inspection and execution of the standalone `cdin-kernel` implementation show a different, simpler model: public calls execute synchronously on the caller thread; a caller-provided lock vtable serializes calls when multi-thread access is needed; without it, the application must serialize access. No internal request queue or mutation executor exists in ABI 1.0.0.

## Decision
- Kernel API calls execute synchronously.
- When a lock vtable is provided, kernel calls serialize in the order established by lock acquisition / linearization. Otherwise the caller is responsible for preventing overlapping calls.
- The accepted mutation sequence is ordering metadata, not a promise of FIFO by wall-clock arrival, thread creation time or scheduler order. A request rejected as stale does not mutate the document; failures after acceptance may leave sequence gaps.
- Snapshots pin immutable content; long search scans can work against pinned content without seeing partial edits.
- Shutdown does not drain a queue. ABI 1.0.0 graceful/abort mode values are behaviorally equivalent: mutation is stopped, active transactions are aborted, and teardown remains caller-controlled.

## Options
- **A. Add an internal FIFO executor now.** Rejected: it would fundamentally change the current synchronous call and wakeup model, add queue lifecycle/backpressure semantics, and duplicate the serializing lock.
- **B. Specify synchronous calls and truthful lock-order semantics.** Accepted: it matches the current public ABI and implementation, with a caller-owned serialization contract.

## Consequences
- Requirements and diagrams no longer claim wall-clock FIFO, a queue lock, or a pending-work drain.
- A future asynchronous executor requires a new ADR and explicit API/ABI changes.
- Backend job systems must configure a lock or enforce single-thread ownership before calling the kernel.

## References
[concurrency.md](../architecture/concurrency.md), [kernel/overview.md](../kernel/overview.md), `cdin-kernel/include/cdin/kernel.h` in the sibling repository.
