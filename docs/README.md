# Documentation

The authoritative CDIN architecture and contract index. Most readers need three pages to begin.

This is the index of the CDIN specification. The repository-level picture is in the
[README](../README.md); this page tells you which of the pages below to open for what
you are about to do.

## Start here

**[reference/conventions.md](reference/conventions.md)** — the status labels
(`EXISTING`, `ACCEPTED`, `PROPOSED`, `OPEN`, `DEFERRED`), the requirement-ID format, the
verification methods and the diagram vocabulary. Every other page assumes you have read
it. It is short.

**[reference/glossary.md](reference/glossary.md)** — the exact meaning of every term.
`data`, `backend`, `view` and `position` each mean one specific thing here, and not
always the obvious one.

**[architecture/overview.md](architecture/overview.md)** — goals, principles and the
system context. Read this before touching anything.

**[reference/status.md](reference/status.md)** — what was inspected, what is decided,
what is open, and what contradicts what. Read it before trusting any claim about the
current `cdin` code.

## What are you doing?

| You are | Read, in this order |
| --- | --- |
| **building the kernel** | [kernel/overview](kernel/overview.md), [text-model](kernel/text-model.md), [positions-and-ranges](kernel/positions-and-ranges.md), [editing-operations](kernel/editing-operations.md), [transactions](kernel/transactions.md), [undo-redo](kernel/undo-redo.md), then [abi-and-compatibility](architecture/abi-and-compatibility.md) |
| **writing a frontend** | [components/frontend](components/frontend.md), [frontend-protocol](architecture/frontend-protocol.md), [concurrency](architecture/concurrency.md), [error-model](architecture/error-model.md) |
| **writing an extension** | [extension-model](architecture/extension-model.md), [components/runtime](components/runtime.md), [components/cdin-x](components/cdin-x.md) |
| **migrating today's `cdin`** | [repositories](architecture/repositories.md), [migration](architecture/migration.md), [module-boundaries](architecture/module-boundaries.md), [reference/status](reference/status.md) |
| **designing the tests** | [testing/conformance](testing/conformance.md), [testing/test-matrix](testing/test-matrix.md) |
| **reviewing decisions** | [adr/open-decisions](adr/open-decisions.md), then [adr/](adr/README.md) |

## Architecture

System-level design: who owns what, how components talk, how they start and stop.

| Page | What it settles |
| --- | --- |
| [overview](architecture/overview.md) | goals, principles, system context, the component list |
| [repositories](architecture/repositories.md) | which component lives in which repository, today and at the target |
| [module-boundaries](architecture/module-boundaries.md) | who may depend on whom; who owns which state |
| [abi-and-compatibility](architecture/abi-and-compatibility.md) | the C ABI rules every binary boundary follows |
| [frontend-protocol](architecture/frontend-protocol.md) | how GUI, TUI, CLI and future frontends attach |
| [concurrency](architecture/concurrency.md) | synchronous kernel calls, lock-order semantics, snapshots, shutdown |
| [lifecycle](architecture/lifecycle.md) | process, module, plugin and document lifecycles |
| [error-model](architecture/error-model.md) | status codes and error structure |
| [extension-model](architecture/extension-model.md) | how `cdin-x` and plugins relate to the core |
| [migration](architecture/migration.md) | how today's code becomes this architecture without breaking the editor |

## Components

One page per component: what it is, what it is not, what it owns.

[cdin](components/cdin.md) (the composition root) · [backend](components/backend.md) ·
[runtime](components/runtime.md) · [frontend](components/frontend.md) ·
[data](components/data.md) · [cdin-x](components/cdin-x.md) ·
[spec](components/spec.md) (how this repository itself works)

## Kernel

The text engine in full, from the document down to a byte.

| Page | Topic |
| --- | --- |
| [overview](kernel/overview.md) | scope, properties, the request path |
| [document-model](kernel/document-model.md) | identity, version, lifecycle |
| [text-model](kernel/text-model.md) | bytes first, Unicode second; regions; line endings |
| [positions-and-ranges](kernel/positions-and-ranges.md) | byte offsets, code points, graphemes |
| [editing-operations](kernel/editing-operations.md) | replace, batch, the version check |
| [transactions](kernel/transactions.md) | grouping, commit, rollback |
| [undo-redo](kernel/undo-redo.md) | linear history, coalescing, bounds |
| [change-notifications](kernel/change-notifications.md) | ordered events, queues, resync |
| [search-engine](kernel/search-engine.md) | literal and byte search, limits; regex deferred |

## Testing

Verification plan and external test evidence. This repository contains no executable test suite.
[conformance](testing/conformance.md) describes the data-driven contract;
[test-matrix](testing/test-matrix.md) maps requirement groups;
[kernel implementation status](kernel/implementation-status.md) records actual `cdin-kernel` checks.

## Decisions

[adr/README.md](adr/README.md) indexes the seventeen ADRs and says how owner approval is
recorded. [adr/open-decisions.md](adr/open-decisions.md) is the register of every
unresolved question, with options and trade-offs. Unresolved questions are never
requirements.

## Where a requirement ID lives

An ID's prefix tells you which page owns it.

| Prefix | Page | Prefix | Page |
| --- | --- | --- | --- |
| `ARCH` | [overview](architecture/overview.md), [repositories](architecture/repositories.md), [module-boundaries](architecture/module-boundaries.md), [migration](architecture/migration.md) | `KERNEL` | [kernel/overview](kernel/overview.md) |
| `ABI` | [abi-and-compatibility](architecture/abi-and-compatibility.md) | `DOC` | [document-model](kernel/document-model.md) |
| `PROTO` | [frontend-protocol](architecture/frontend-protocol.md) | `TEXT` | [text-model](kernel/text-model.md) |
| `CONC` | [concurrency](architecture/concurrency.md) | `POS` | [positions-and-ranges](kernel/positions-and-ranges.md) |
| `LIFE` | [lifecycle](architecture/lifecycle.md) | `EDIT` | [editing-operations](kernel/editing-operations.md) |
| `ERR` | [error-model](architecture/error-model.md) | `TXN` | [transactions](kernel/transactions.md) |
| `EXT` | [extension-model](architecture/extension-model.md), [cdin-x](components/cdin-x.md) | `UNDO` | [undo-redo](kernel/undo-redo.md) |
| `BE` | [backend](components/backend.md) | `NOTIF` | [change-notifications](kernel/change-notifications.md) |
| `RT` | [runtime](components/runtime.md) | `SEARCH` | [search-engine](kernel/search-engine.md) |
| `FE` | [frontend](components/frontend.md) | `TEST` | [conformance](testing/conformance.md) |
| `DATA` | [data](components/data.md) | `SPEC` | [spec](components/spec.md) |
| `ROOT` | [cdin](components/cdin.md) | | |

## Working on the specification

**[../CONTRIBUTING.md](../CONTRIBUTING.md)** — how a change is made, and the checklist.
**[../AGENTS.md](../AGENTS.md)** — the same, for agents: what to run after touching what.
**[../scripts/README.md](../scripts/README.md)** — `scripts/check.py`, the structural
checks every change has to pass.

## The short version

```sh
python3 scripts/check.py            # IDs, links, references, index, diagram types
python3 scripts/check.py --stats    # the counts reference/status.md quotes
python3 scripts/check.py --render   # also render every diagram (needs mmdc)
psx check                           # repository structure, against psx.yml
```
