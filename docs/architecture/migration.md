# Migration from the current code

How the supplied `cdin` snapshot is integrated with the already-existing standalone `cdin-kernel` repository, then evolved toward the target architecture without breaking the editor. Strategy: **incremental** (`ACCEPTED`). Every integration phase must preserve a build/start gate (ARCH-026).

## 1. What exists today (inspected)

The inspected tree is a working-tree snapshot of the `cdin` repository (not git history). Measured on it:

| Part | Size | Content |
|---|---|---|
| `src/` | about 7.2 thousand lines of C | `base` (alloc, arena, error), `core` (config, logger, window), `fs`, `loop` (libuv jobs), `lua` (binding), `api` (Lua-visible tables), `platform`, `search`, `ui` (renderer, cache) |
| `data/core/` | about 7.3 thousand lines of Lua | documents, views, commands, keymaps, syntax, text pipeline, themes, plugin loader |
| `scripts/` | about 6.6 thousand lines | build, install, bench, measure, Lua tests |
| `mk/` | 8 make includes | `bundle.mk` is the only place that knows `cdin-x` exists |
| `tests/` | 484 files, mostly fuzz corpus | C tests, Lua unit and integration tests, benchmarks |

## 2. Where each piece goes (`PROPOSED`)

This mapping is a **plan to be verified during migration review**, not a statement of fact about the code. Files not analysed in detail are marked.

| Current location | Target | Notes |
|---|---|---|
| `src/base/*` | backend (internal); kernel uses injected allocator/lock/log services | `cdin-kernel` is already a separate repository and MUST NOT depend on `cdin/src/base` (ARCH-040). Candidate sharing requires a new ADR. |
| `src/loop/*` | backend OS services (jobs) | libuv-based; stays |
| `src/fs/*`, `src/platform/*` | backend OS services | SDL appears in `platform.*`; see the next section |
| `src/search/find.c` | migrate callers to supported kernel search modes | about 155 lines; regex is not supported by Kernel ABI 1.1.0 and must remain explicitly deferred rather than silently emulated |
| `src/lua/*`, `src/api/*` | runtime host API (backend side) | `api/system.c` is split by owner |
| `src/api/system.c` | split: OS services, frontend requests, debug hooks | grab-bag today |
| `src/api/renderer_*.c`, `src/ui/*` | gui-sdl frontend | renderer already behaves as a cached command list |
| `src/core/window.*`, SDL in `src/main.c` | gui-sdl frontend | |
| `src/core/config.*`, `logger.*` | backend | |
| `data/core/doc/*` | runtime; document layer becomes a client of the kernel | `highlighter` moves to the runtime/frontend side; `translate.lua` and `search.lua` not analysed |
| `data/core/text/{bidi,shaper,utf8}.lua` | frontend side (shaping, bidi), `utf8` stays for runtime use | confirms "shaping and bidi are outside the kernel" |
| `data/core/views/*`, `rootview/*` | runtime UI model; drawing code moves to frontend or becomes declarative | largest step (see below) |
| `data/core/commands/*`, `input/*`, `keymaps/*`, `config.lua`, `themes.lua`, `style.lua` | runtime | |
| `data/core/plugins.lua`, `project.lua` | runtime | |
| `mk/*`, `scripts/*`, `Makefile`, `Dockerfile`, `.github/` | composition root (`cdin`) | |
| `docs/architecture/extension-contract.md` | stays with `cdin` until `cdin-runtime` exists, then moves there | contract text is shared with `cdin-x` by reference |

## 3. Phases

```mermaid
flowchart LR
    M0["M0<br/>Spec 1.3.0 baseline"]
    M1["M1<br/>Backend integrates<br/>Kernel ABI 1.1.0"]
    M2["M2<br/>Lua document layer<br/>becomes a kernel client"]
    M3["M3<br/>in-process Frontend Protocol<br/>around the GUI"]
    M4["M4<br/>headless frontend<br/>and serialized transport"]
    M5["M5<br/>Runtime repository<br/>already extracted"]
    M6["M6<br/>stable Host API 1.0.0<br/>live native integration"]
    M0 -- "ABI and ownership gates clear" --> M1
    M1 -- "integrated create/edit/notify vectors pass" --> M2
    M2 -- "one canonical document/history store" --> M3
    M3 -- "no private backend calls" --> M4
    M4 -- "second frontend attaches" --> M5
    M5 -- "Host API and live bridge gates" --> M6
```

*Caption: `PROPOSED` order. Kernel and Runtime repositories already exist; M5 records the completed Runtime repository extraction, while stable Host API and live integration are tracked separately.*

| Phase | Outcome | Entry gate | Exit gate |
|---|---|---|---|
| M0 | Stable Spec baseline and frozen Kernel public C ABI | Spec baseline reviewed; ABI header and compatibility target reviewed | ownership and version boundaries documented |
| M1 | Backend integrates `cdin-kernel` through its public header and validates ABI/features | M0 | create/edit/read/notification path passes integrated tests; no private Kernel header is included |
| M2 | Runtime document layer is a thin Host-backed client; Kernel is the sole canonical document/history store | M1; Host API contract and ownership rules reviewed | no canonical document bytes/history duplicated outside Kernel; stale-handle and resync behavior tested |
| M3 | Frontend uses the semantic Frontend Protocol through Backend projection | M2; Protocol contract accepted | atomic projection and protocol conformance tests pass; no private Backend calls from Frontend |
| M4 | Headless and additional Frontend adapters attach through the same Protocol contract | M3 | second adapter attaches and role/capability/resync behavior is verified |
| M5 | Runtime repository extraction and provisional package versioning | Historical milestone; already completed | standalone Runtime repository/package exists; this does not imply stable Host API or production integration |
| M6 | Stable Runtime Host API and live Backend→Lua Runtime→Kernel integration | M1–M5 contracts aligned; Host API compatibility freeze prepared | Host API 1.0.0 frozen; native bridge, owner-thread, lifecycle, failure-injection and end-to-end conformance gates pass |

- **ARCH-060** `ACCEPTED` Migration tracking MUST distinguish repository extraction, contract acceptance, implementation completion and production verification. Runtime repository extraction and provisional package versioning are complete; stable Host API 1.0.0 and live Backend→Lua Runtime→Kernel integration remain gates. A phase MUST NOT be declared complete solely because its repository exists. Dependencies and exit gates remain mandatory. — *Verify:* INSPECT
- **ARCH-061** `ACCEPTED` The kernel is a standalone `cdin-kernel` repository, not a directory duplicated under `cdin`. Consumers include only `include/cdin/kernel.h`; ABI-specific internals stay private. — *Verify:* STATIC
- **ARCH-062** `ACCEPTED` A prototype spike MUST be used only when a material design uncertainty cannot be resolved by existing contracts or implementation evidence. It MUST produce reproducible evidence and a recommendation; any change to a normative contract requires owner approval before implementation. Accepted ADR-0018, ADR-0019 and ADR-0020 decisions MUST NOT be reopened by repetitive spikes without new material evidence. — *Verify:* INSPECT
## 4. The hardest steps

**The document layer (M2).** The current document model lives in Lua (`data/core/doc/`). Moving it to the kernel reverses a documented principle: today's overview states that the C layer "knows nothing about documents". That statement is recorded as a contradiction in [status.md](../reference/status.md) and resolved by [ADR-0002](../adr/ADR-0002-kernel-owns-documents.md).

**The views (M3).** Views draw directly through the renderer API today. Making them produce a semantic UI model is the largest change, and the extension contract lets plugins subclass views. The transitional plan: keep the existing drawing path working through an in-process `canvas`-style capability while the declarative path is built, then retire it with shims (ARCH-027).

## 5. Rollback

- **ARCH-070** `ACCEPTED` Each migration phase MUST preserve the last passing component boundary/build/start path and MUST NOT merge a state in which previously accepted conformance tests fail. Where state-level reversal is not technically possible, the phase MUST document a tested rollback or recovery procedure before merge; trivial reversibility of every data/state transition is not required. — *Verify:* INTEG


## Accepted Frontend delivery order — ADR-0020

The standalone Frontend repository has one accepted family: `core`, `gui-sdl`, `tui` and `headless`. The `headless` adapter is the protocol reference and verification harness. The TUI is the first new interactive frontend target and uses a full-screen, Neovim-like interaction model. The legacy SDL GUI may remain the migration bridge while its source is extracted into `gui-sdl`; it does not change the TUI-first decision for the new interactive adapter. The non-interactive `cli` target remains deferred. These are target decisions, not claims that the repository or TUI has shipped.
