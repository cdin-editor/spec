# Components and repositories

A **component** has one responsibility and a contract. A **repository** is a unit of version control and release. They are different things. This document says which component lives in which repository now, and the conditions under which that changes.

## 1. Today and target

### Current archive baseline

```mermaid
flowchart TB
    cdinrepo["cdin (repo)<br/>composition root, backend/UI source,<br/>build and integration"]
    kernelrepo["cdin-kernel (repo)<br/>native text engine, C ABI 1.0.0"]
    xnow["cdin-x (repo)<br/>separate extension ecosystem"]
    specnow["spec (repo)<br/>architecture and contracts"]
    specnow -. "defines contracts" .-> cdinrepo
    specnow -. "defines ABI 1.0.0 contract" .-> kernelrepo
    kernelrepo -. "to be integrated / version-checked" .-> cdinrepo
    xnow -. "extension input at build time" .-> cdinrepo
    classDef comp fill:#dbeafe,stroke:#1d4ed8,color:#0f172a
    class cdinrepo,kernelrepo,specnow,xnow comp
```

*Caption: archive snapshots inspected for the 1.0.0 synchronization. The uploads contain working trees but not Git history, so this report cannot verify commit ancestry or whether an extraction preserved history. `cdin-kernel` exists as a standalone source tree and publishes C ABI 1.0.0; its integration into `cdin` remains a separate gate.*

### Stable architecture baseline and target

```mermaid
flowchart TB
    spec["spec (repo)"]
    subgraph cdinrepo["cdin (repo): composition root + backend"]
        root["root: build, bundle, release, launcher"]
        be["backend: session, OS services, protocol server, runtime host"]
        fegui["gui-sdl frontend (directory)"]
        fetui["tui frontend (directory)"]
        fecli["cli / headless frontend (directory)"]
    end
    kernel["cdin-kernel (repo)"]
    runtime["cdin-runtime (repo)"]
    x["cdin-x (repo, separate ecosystem)"]

    root --> be
    root --> fegui
    root --> fetui
    root --> fecli
    be --> kernel
    be --> runtime
    x -. "extension contract" .-> runtime
    spec -. "defines contracts for all" .-> kernel
    spec -.-> runtime
    spec -.-> be
    spec -.-> x
    classDef comp fill:#dbeafe,stroke:#1d4ed8,color:#0f172a
    classDef group fill:#f8fafc,stroke:#cbd5e1,color:#334155
    class be,fecli,fegui,fetui,kernel,root,runtime,spec,x comp
    class cdinrepo group
```

*Caption: accepted repository boundaries and target composition. The `cdin-runtime` extraction remains gated on the runtime host API being stable. Arrows are build or link dependencies; dotted arrows are contract relationships.*

## 2. Component to repository map

| Component | Repository now | Repository target | Status |
|---|---|---|---|
| spec | `cdin-editor/spec` | same | `ACCEPTED`; Spec baseline `1.0.0` |
| kernel | standalone `cdin-kernel` archive snapshot | same; stable C ABI `1.0.0` | `ACCEPTED` |
| runtime | inside `cdin` (`data/core/`, `src/lua/`, `src/api/`) | `cdin-runtime`, created after the runtime host API is stable | `PROPOSED` |
| backend | inside `cdin` (`src/`) | stays in `cdin` | `PROPOSED` |
| frontend: gui-sdl | inside `cdin` (`src/ui/`, `src/core/window.*`, SDL parts of `src/api/system.c`) | directory in `cdin`, extractable | `PROPOSED` |
| frontend: tui, cli, headless | does not exist | directories in `cdin` first | `DEFERRED` (tui, cli), `PROPOSED` (headless reference) |
| data | not a component in code | no repository | `DEFERRED` |
| cdin (root) | `cdin` repository | same | `ACCEPTED` as composition root |
| cdin-x | its own repository | same, fully separate | `ACCEPTED` |

There is deliberately **no** `cdin-backend`, `cdin-frontend`, `cdin-data`, `cdin-scripts`, `cdin-common` or `cdin-shared` repository in the target topology. Reasons are in [ADR-0001](../adr/ADR-0001-repository-topology.md).

## 3. Rules for creating or splitting a repository

- **ARCH-030** `PROPOSED` A new repository MUST be justified by at least one of: a second consumer of the component that is not the current repository; an independent release cadence; a different implementation language or toolchain; a separation of ownership. — *Verify:* INSPECT
- **ARCH-031** `PROPOSED` A component MUST NOT be extracted into its own repository until its contract has a version number and a written compatibility policy. — *Verify:* INSPECT
- **ARCH-032** `PROPOSED` Extraction SHOULD preserve source history using a subtree/filter-repo method or an equivalent mapping; `git mv` alone does not preserve history across repositories. The editor MUST build and start before and after extraction. — *Verify:* INTEG
- **ARCH-033** `PROPOSED` Frontends MAY live outside the `cdin` repository at any time, because they depend only on the Frontend Protocol. No change to other components is required for that. — *Verify:* INSPECT
- **ARCH-034** `ACCEPTED` No `cdin-common` or `cdin-shared` repository is created without explicit approval and a stated reason (same as ARCH-005; restated here as the rule for this document). — *Verify:* INSPECT
- **ARCH-035** `PROPOSED` A protocol client library (a binding of the Frontend Protocol for frontend authors) is the one shared artifact with an architectural justification. Whether it is a separate repository is `OPEN`: see [OD-23](../adr/open-decisions.md). — *Verify:* INSPECT

## 4. What each repository is, and is not

### spec
- **Is:** architecture, contracts, decisions, verification design.
- **Is not:** an implementation, a test runner, or a place for code.

### kernel (`cdin-kernel`)
- **Is:** the document engine behind a C ABI.
- **Is not:** a UI toolkit, a file manager, a scripting host, a syntax highlighter, a text shaper.

### runtime (`cdin-runtime`)
- **Is:** the Lua policy layer and the definition of the Lua environment extensions run in.
- **Is not:** a document store; it keeps no independent copy of document content or history.

### backend (inside `cdin`)
- **Is:** the headless core that can run with no frontend attached.
- **Is not:** tied to SDL, a terminal, or any display.

### frontends (directories in `cdin`, later possibly their own repositories)
- **Are:** presentation and input for one environment.
- **Are not:** owners of documents, commands or keymaps.

### cdin (composition root)
- **Is:** build system, bundling, release workflows, installers, launcher, development tooling.
- **Is not:** a place where kernel or runtime logic is re-implemented.

### cdin-x
- **Is:** the mandatory bundled set (vim mode, extension manager, default theme, fonts) plus every optional extension.
- **Is not:** aware of the kernel, the protocol or the backend.

## 5. Why the current layout is not simply split

The current `cdin` archive still contains backend, runtime and GUI-related code together; its SDL3-dependent build/test path could not be verified in the available environment because SDL3 headers are absent and the archived test baseline is empty. The standalone `cdin-kernel` ABI is now stable, but its composition-root integration must be gated by an integration test. The next justified repository extraction is `cdin-runtime` only after its host API is stable. The supplied archives have no Git history, so migration history preservation cannot be assessed here. See [migration.md](migration.md).
