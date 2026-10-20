# Decisions

Two instruments record how the architecture was and will be decided.

- **[Open Decisions Register](open-decisions.md)**: every unresolved question, its importance, options, trade-offs and dependencies. `OD-01` to `OD-20` are the twenty items identified at the start of the design work; `OD-21` and later were found while writing this specification.
- **ADRs** (architecture decision records): one file per decision, with the structure in [conventions.md](../reference/conventions.md). An ADR is written when an `ACCEPTED` contract changes, when a decision is made that others depend on, or when options need to be on record.

## Index of ADRs

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-repository-topology.md) | Repository topology | `ACCEPTED` |
| [ADR-0002](ADR-0002-kernel-owns-documents.md) | The kernel owns documents; everything else is a client | `ACCEPTED` |
| [ADR-0003](ADR-0003-c-abi.md) | C ABI at binary boundaries | `ACCEPTED` |
| [ADR-0004](ADR-0004-implementation-language.md) | Implementation language: C11 | `ACCEPTED` |
| [ADR-0005](ADR-0005-frontend-protocol.md) | Frontend Protocol: backend owns state, frontends own presentation | `ACCEPTED` for semantic model; encoding open |
| [ADR-0006](ADR-0006-visual-layout-ownership.md) | Visual layout belongs to frontends | `ACCEPTED` |
| [ADR-0007](ADR-0007-selection-ownership.md) | Selection ownership and undo | `ACCEPTED` |
| [ADR-0008](ADR-0008-persistence-outside-kernel.md) | Persistence stays outside the kernel | `ACCEPTED` |
| [ADR-0009](ADR-0009-regex-engine.md) | Regular-expression engine | `OPEN` (direction `PROPOSED`) |
| [ADR-0010](ADR-0010-unicode-version.md) | Unicode version policy | `ACCEPTED` |
| [ADR-0011](ADR-0011-extension-ui.md) | Extension UI under the Frontend Protocol | `PROPOSED` |
| [ADR-0012](ADR-0012-migration-strategy.md) | Incremental migration | `ACCEPTED` |
| [ADR-0013](ADR-0013-hot-swap.md) | Hot-swap and state migration | `DEFERRED` |
| [ADR-0014](ADR-0014-no-shared-repositories.md) | No shared or common repositories | `ACCEPTED` |
| [ADR-0015](ADR-0015-spec-language-and-scope.md) | Specification language and scope | `ACCEPTED` |
| [ADR-0016](ADR-0016-arch-specific-optimizations.md) | Architecture-specific optimizations (SIMD and assembly) in the kernel | `PROPOSED` |
| [ADR-0017](ADR-0017-kernel-synchronous-concurrency.md) | Kernel call concurrency and ordering | `ACCEPTED` |

## How owner approval is recorded

Where the owner approved a proposal *in principle* during design discussion but has not yet reviewed the detailed text written here, the ADR says so and the corresponding requirements remain `PROPOSED`. They become `ACCEPTED` only after the owner reviews this text and says so (SPEC-020). The current resolved/open distinction is in [status.md](../reference/status.md) and [open-decisions.md](open-decisions.md).
