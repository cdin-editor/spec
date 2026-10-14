# Status

State of the specification and of what it was drawn from. Written to be honest: it separates what was inspected from what was assumed, what is decided from what is proposed, and what was run from what was only designed.

**Specification version:** `0.1.0` (draft, first complete pass). See SPEC-010.

## 1. What was inspected

| Source | What was examined | What was **not** examined |
|---|---|---|
| `cdin` repository, as a **working-tree snapshot** supplied as an archive (no git history; 669 files) | Directory structure of `src/`, `data/`, `scripts/`, `mk/`, `docs/`, `tests/`; `Makefile`, `mk/bundle.mk`; the head of `mk/build.mk` and `scripts/assemble_data.py`; `AGENTS.md` (sections 1 to 3 and 8 read; the rest only partly); `docs/architecture/overview.md`; the introduction and the "plugin protocol" section of `docs/architecture/extension-contract.md` and the section headings of it and of `docs/architecture/internals.md`; the function list of `src/ui/renderer.h`; the Lua function tables in `src/api/*.c`; the includes of `src/main.c`; line counts per directory; searches for SDL and for `cdin-x` across `src/`, `data/`, `scripts/`, `mk/`; `.gix/config` and `psx.yml` presence | The bodies of the C sources and of the Lua sources; `docs/guides/`; the tests' contents; CI workflow contents; `CHANGELOG.md`. Test suites were **not** run. |
| `cdin-editor/spec` (this repository) | Cloned; at that time it contained one commit and only `.gix/config` | |
| Owner's architecture context document and the design discussion | Used as the source of every `ACCEPTED` decision | |
| `cdin-x` | **Not inspected.** Statements about it come from `cdin`'s documents and build scripts, and from the owner's stated requirements | everything inside it |
| `cdin-kernel`, `cdin-runtime`, any other repository | **Do not exist** (as far as the owner has said); nothing to inspect | |

A first attempt to unpack the archive with one tool produced empty files; it was re-extracted with another tool and the contents were then verified to be non-empty before use.

## 2. Contents of this specification

| Measure | Count |
|---|---|
| Markdown files | 58 |
| Normative requirements | 396 |
| ... `ACCEPTED` | 72 |
| ... `EXISTING` (each with a code anchor) | 31 |
| ... `PROPOSED` | 288 |
| ... `DEFERRED` | 5 |
| ADRs | 16 |
| Open decisions in the register | 31 (9 `OPEN`, 19 `PROPOSED`, 3 `DEFERRED`) |
| Mermaid diagrams | 35 |

## 3. Decisions

### `ACCEPTED` (stated by the owner)

- `cdin` is the composition root and must not reimplement kernel, runtime or other logic.
- The kernel is a generic text engine, independent of GUI, TUI, runtime and OS; it owns canonical document state; it does not know who its clients are; the Lua document layer is just a client.
- Multiple independent documents with identity, version and own undo/redo; explicit create and close; invalid handles give a specific error.
- Preservation of valid UTF-8 and the original bytes of invalid UTF-8; LF, CRLF, CR and mixtures; no implicit normalization.
- Position model: code points, byte offsets, raw bytes, graphemes as distinct concepts.
- Direct API from frontends to the kernel plus ordered change notifications identifying versions and describing logical change.
- Transactions: independent edit is one undo unit; explicit transactions group edits; rollback without per-operation full copy.
- Concurrency: multi-thread callers, serial mutations, FIFO; stale `expected version` rejected without change and without auto-transforming positions; the version check is atomic with mutation.
- C ABI at binary boundaries; not every component must be a dynamic module.
- Search is part of the kernel with the listed capabilities; Persian and Arabic letters are not treated as equivalent automatically.
- Hot-swap is not accepted generally.
- Extensions have no direct kernel access; `cdin-x` is fully separate; the vim plugin is mandatory in a standalone build and its source stays in `cdin-x`; installing a plugin downloads only that plugin.
- No `cdin-common` or `cdin-shared` repository without approval.
- Specification is English first and design-only; migration is incremental; implementation language is C11.

### Approved in principle (written here as `PROPOSED`, awaiting the owner's review of the text)

- Byte offset as the canonical position; selections owned by the view with opaque blobs in undo units; syntax highlighting, shaping and bidi outside the kernel; persistence outside the kernel with no `cdin-data` repository for now; snapshot reads and the FIFO acceptance-point definition; a pinned Unicode version per release; ABI semantic versioning with a struct-size prefix; an existing regex library chosen by ADR; step-counted resource limits and cancellation.

### `PROPOSED` and **not yet confirmed**

- The Frontend Protocol model ([ADR-0005](../adr/ADR-0005-frontend-protocol.md)) and frontend ownership of visual layout ([ADR-0006](../adr/ADR-0006-visual-layout-ownership.md)).
- Extension UI via declarative widgets and an optional canvas ([ADR-0011](../adr/ADR-0011-extension-ui.md)), which changes the extension contract.
- The staged repository topology and the definition of "backend" as the headless core ([ADR-0001](../adr/ADR-0001-repository-topology.md), [OD-15](../adr/open-decisions.md)).
- Optional architecture-specific optimized paths (SIMD, assembly) in the kernel, as requested by the owner ([ADR-0016](../adr/ADR-0016-arch-specific-optimizations.md)); it narrows the accepted "kernel is C11" decision and needs the owner's confirmation of its conditions.
- Rejecting other writers during a transaction ([OD-21](../adr/open-decisions.md)); the UI core staying in Lua ([OD-30](../adr/open-decisions.md)); the repository name ([OD-31](../adr/open-decisions.md)).

### Open

See the [Open Decisions Register](../adr/open-decisions.md): internal text structure, regex engine, final ABI names, protocol encoding, client library, multi-frontend mutation, position-mapping helper, search normalization scope.

## 4. Contradictions and divergences found

| # | Finding | Where | Handling |
|---|---|---|---|
| C-1 | `cdin`'s overview says the C layer "knows nothing about documents"; the new architecture gives the kernel (C) the documents | `docs/architecture/overview.md` in `cdin` | Resolved by [ADR-0002](../adr/ADR-0002-kernel-owns-documents.md); `cdin`'s overview must be updated when the kernel lands |
| C-2 | `cdin`'s overview and the extension contract describe "two repositories"; the target topology has more | same, and `extension-contract.md` | [ADR-0001](../adr/ADR-0001-repository-topology.md); update with the topology |
| C-3 | The rule "never break the extension contract" versus the proposal to change plugin UI | `AGENTS.md §2.2` | [ADR-0011](../adr/ADR-0011-extension-ui.md) requires owner approval and shims |
| C-4 | `AGENTS.md` names a master prompt file (`PROMPT_CDIN_MASTER.md`) that is not in the supplied archive | `AGENTS.md §1` | Recorded; not needed by this specification |
| C-5 | The Lua-visible `system` table mixes window, clipboard, filesystem, process, time and debug hooks | `src/api/system.c` | Divergence from the boundaries; split planned in [backend.md](../components/backend.md), BE-010 |
| C-6 | SDL is referenced in `src/loop/` and `src/platform/`, which are OS-services code | those directories | Must be removed per BE-002 and BE-006 |
| C-7 | The extension contract and `AGENTS.md` link `cdin-x` under a personal GitHub account; the owner referred to it under the `cdin-editor` organization | `docs/architecture/extension-contract.md` | Not resolved; owner to confirm where `cdin-x` lives |
| C-8 | Source files mention `cdin-x` only in comments, so the "nothing depends on `cdin-x`" claim holds for code but not for comments | `src/lua/error.h`, `src/api/system.c`, `src/main.c`, `data/core/config.lua`, `data/core/keymaps/default.lua` | Recorded as ARCH-011 with its precise wording |

## 5. Verification status

- **No conformance vector, runner or test exists, and none was run.** No requirement is verified. See [test-matrix.md](../testing/test-matrix.md).
- The existing tests of `cdin` were not run for this specification.
- Structural checks **were** run on this specification by `scripts/check.py` in this repository: every requirement ID is unique and well-formed; every status and verification method is in the allowed set; every `EXISTING` requirement has an anchor; every relative link resolves; every referenced requirement, ADR and open decision exists; and all 34 Mermaid diagrams rendered with the Mermaid command-line tool (one was fixed after a first failure). This checks form and internal consistency, not correctness against code.

## 6. Next step

1. The owner reviews the `PROPOSED` and "not yet confirmed" items above and answers the open decisions that block the first spikes: at least [OD-17](../adr/open-decisions.md) (API names, resolved by the first spike), [OD-22](../adr/open-decisions.md), [OD-26](../adr/open-decisions.md), [OD-30](../adr/open-decisions.md).
2. Spikes in the order of SPEC-033 (handles and FIFO acceptance point; replace with undo and version check; region classification; notification overflow; handshake and one `view.lines` round trip; regex step limits). Findings are written back before any `PROPOSED` item is promoted.
3. Phase M1 of [migration.md](../architecture/migration.md): the kernel as a directory in `cdin`, behind its ABI header.
