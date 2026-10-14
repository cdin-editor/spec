# Data

Status: **`DEFERRED` as a repository.** This document records the responsibilities that "data" might cover, where they live now, and the condition for ever creating a `cdin-data` repository.

## 1. Two different things called "data"

The word means two unrelated things in this project (see [glossary.md](../reference/glossary.md)):

| Meaning | What it is |
|---|---|
| `data/` the directory (`EXISTING`) | The Lua runtime source (`data/core/`) in the source tree; in a *build output*, the assembled directory of core, plugins, themes and fonts. |
| the `DATA` component (this document) | Persistence and serialization responsibilities: loading and saving files, atomic writes, session and settings storage. |

The directory is covered by [runtime.md](runtime.md) and [cdin.md](cdin.md). The rest of this document is about the component.

## 2. Responsibilities in scope for the component

| Responsibility | Where it lives |
|---|---|
| Load a file's bytes into a kernel document | caller (backend OS services) reads in chunks and passes bytes to the kernel |
| Serialize a kernel document to a file | caller reads bytes from a snapshot in chunks and writes them |
| Atomic save, backup, permissions | backend OS services |
| Detect and handle byte-order mark | caller (the kernel never removes one: TEXT-030) |
| Choose encoding or line-ending style for saving | caller policy (runtime) |
| Remember recent files, session state, settings storage | backend or runtime configuration, `PROPOSED` |
| File watching and external-change detection | backend OS services (jobs) |

## 3. Requirements

- **DATA-001** `ACCEPTED` The kernel MUST NOT perform file I/O or serialization to files. (KERNEL-007; the owner's decision that persistence stays outside the kernel.) — *Verify:* STATIC
- **DATA-002** `PROPOSED` The kernel exposes only byte-oriented exchange: create from a byte buffer, read bytes of a snapshot, serialize a snapshot to a caller-provided sink in bounded chunks. — *Verify:* CONF
- **DATA-003** `PROPOSED` Load and save MUST be streamed in bounded chunks and MUST NOT block the main thread (ARCH-023). — *Verify:* PERF, INSPECT
- **DATA-004** `PROPOSED` A load followed by a save without edits MUST reproduce the original bytes exactly (TEXT-042). — *Verify:* CONF, FUZZ
- **DATA-005** `PROPOSED` Saving is atomic where the platform allows (write to a temporary file in the same directory, then replace). A failure leaves the original file unchanged and reports a status. — *Verify:* INTEG
- **DATA-006** `PROPOSED` After a successful save the caller marks the saved state in the kernel (DOC-040). — *Verify:* INTEG
- **DATA-007** `PROPOSED` These responsibilities live inside the backend's OS services until a second consumer exists. — *Verify:* INSPECT

## 4. Condition for a `cdin-data` repository

A `cdin-data` repository is created only if all hold (an application of ARCH-030):

1. At least one consumer other than the `cdin` backend needs the same persistence code (for example a command-line converter or a second implementation of the backend).
2. Its contract can be stated without referring to the kernel's internals.
3. The owner approves it in an ADR (ARCH-005).

Until then, no repository, no component boundary and no ABI exist for it. Recorded in [OD-16](../adr/open-decisions.md).

## 5. Existing code

- **EXISTING** File and path primitives already exist in the backend layer (`src/fs/ops.c`, `src/fs/path.c`) and the Lua tables `fs` and `path` expose them. — *Anchor:* `src/fs/`, `src/api/api.c`
- **EXISTING** The current buffer stores bytes and does not rewrite content on load. That behaviour is the baseline for DATA-004. — *Anchor:* `AGENTS.md §2.6`
