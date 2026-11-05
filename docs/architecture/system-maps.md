# System maps

This page collects architecture views at different levels of abstraction. Read them in order: landscape, dependency boundaries, request flow, then startup and release. These diagrams describe the target architecture unless marked `EXISTING`; they do not promote `PROPOSED` or `OPEN` work to implemented status.

## 1. Landscape view — who plays which role?

```mermaid
flowchart TB
    USER(["User / automation"])

    subgraph PRESENTATION["Frontends — presentation and input"]
        GUI["gui-sdl"]
        TUI["tui — first interactive target"]
        HL["headless — protocol reference"]
        CLI["cli — DEFERRED"]
    end
    FP{{"Frontend Protocol<br/>versioned semantic contract"}}

    subgraph CORE["CDIN core — headless-capable"]
        BE["Backend<br/>session and orchestration"]
        RT["Runtime · Lua<br/>policy and UI model"]
        RHA{{"Runtime Host API<br/>1.0.0 · STABLE"}}
        KH["Kernel host"]
        ABI{{"C ABI 1.1.0"}}
        K["cdin-kernel<br/>package 1.2.1"]
        OS[("OS services")]
    end
    EXTC{{"Lua Extension Contract"}}
    X["cdin-x<br/>extension ecosystem"]
    ROOT["cdin<br/>composition and delivery"]
    SPEC["spec<br/>architecture governance"]

    USER --> GUI
    USER --> TUI
    USER --> HL
    USER --> CLI
    GUI <--> FP
    TUI <--> FP
    HL <--> FP
    CLI <--> FP
    FP <--> BE
    BE --- RHA
    RT --> RHA
    BE --> KH --> ABI --> K
    BE --> OS
    X --> EXTC --> RT
    ROOT -. "build, bundle, launch" .-> PRESENTATION
    ROOT -.-> CORE
    ROOT -. "bundle assets" .-> X
    SPEC -. "defines contracts" .-> CORE
    SPEC -.-> PRESENTATION

    classDef comp fill:#dbeafe,stroke:#1d4ed8,color:#0f172a
    classDef contract fill:#ede9fe,stroke:#6d28d9,color:#0f172a
    classDef external fill:#f1f5f9,stroke:#64748b,color:#0f172a
    classDef deferred fill:#f8fafc,stroke:#94a3b8,color:#475569,stroke-dasharray:4 3
    classDef group fill:#f8fafc,stroke:#cbd5e1,color:#334155
    class GUI,TUI,HL,BE,RT,KH,K,X,ROOT,SPEC comp
    class FP,RHA,ABI,EXTC contract
    class OS,USER external
    class TUI comp
    class CLI deferred
    class PRESENTATION,CORE group
```

This is the quickest mental model: frontends present, the runtime decides editor policy, the backend coordinates, the kernel owns canonical document state, `cdin-x` supplies extensions, and `cdin` assembles the product. `spec` describes and governs contracts; it is not linked into the executable.

## 2. Dependency and ownership view

In this diagram, arrows mean **depends on or calls**. Dashed arrows mean **build-time composition or contract definition**. A dependency must not be inferred merely because two boxes appear next to each other.

```mermaid
flowchart TB
    ROOT["cdin composition root"]
    SPEC["spec repository"]

    subgraph CONSUMERS["Consumers"]
        FE["Frontend implementations"]
        X["cdin-x extensions"]
    end

    FP{{"Frontend Protocol"}}
    EXT{{"Lua Extension Contract"}}
    RHA{{"Runtime Host API"}}
    ABI{{"Kernel C ABI 1.1.0"}}

    subgraph CORE["Core components"]
        BE["Backend"]
        RT["Runtime · Lua"]
        KH["Kernel host / adapter<br/>inside backend"]
        K["cdin-kernel"]
        OS["Backend OS-services adapters"]
    end
    EXTAPI["Runtime extension loader"]

    FE --> FP
    BE --> FP
    X --> EXT
    RT --> EXT
    RT --> EXTAPI
    RT --> RHA
    BE --> RHA
    BE --> KH
    KH -->|"uses"| ABI
    K -->|"implements"| ABI
    BE --> OS
    OS --> SYS[("Operating system")]
    ROOT -. "assembles and launches" .-> CONSUMERS
    ROOT -.-> CORE
    ROOT -.-> K
    SPEC -. "defines" .-> FP
    SPEC -.-> EXT
    SPEC -.-> RHA
    SPEC -.-> ABI

    classDef comp fill:#dbeafe,stroke:#1d4ed8,color:#0f172a
    classDef contract fill:#ede9fe,stroke:#6d28d9,color:#0f172a
    classDef external fill:#f1f5f9,stroke:#64748b,color:#0f172a
    classDef group fill:#f8fafc,stroke:#cbd5e1,color:#334155
    class BE,FE,K,KH,OS,RT,ROOT,SPEC,X,EXTAPI comp
    class FP,EXT,RHA,ABI contract
    class SYS external
    class CORE,CONSUMERS group
```

### Boundary rules

- **The backend is the only direct kernel client in the target topology.** Lua uses the Runtime Host API; frontends use the Frontend Protocol; extensions use the Lua Extension Contract.
- **No second canonical document store exists.** The kernel owns document bytes, document versions and undo/redo history. Runtime views may own selections and logical scroll anchors; frontends may own disposable visual caches.
- **The kernel is presentation-neutral.** It does not know about SDL, terminals, Lua, `cdin-x`, the filesystem or release tooling.
- **The root is not a runtime service.** `cdin` can know about components to assemble them but no component depends on the composition root.
- **The language bridge is decided.** PUC Lua 5.4 C API is the only supported v1 bridge under [ADR-0019](../adr/ADR-0019-runtime-bridge.md); Backend owns the Lua state and callbacks. LuaJIT FFI and MetaCall are not v1 alternatives. The Runtime Host API is a separate stable `1.0.0` compatibility contract.

## 3. Detailed request path — one edit from input to pixels

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant FE as Frontend
    participant FP as Frontend Protocol
    participant BE as Backend
    participant RT as Runtime (Lua)
    participant RHA as Runtime Host API
    participant KH as Kernel host
    participant ABI as Kernel C ABI
    participant K as cdin-kernel

    U->>FE: key / text input
    FE->>FP: input event (raw key/text)
    FP->>BE: protocol message
    BE->>RT: dispatch event on Lua owner thread
    RT->>RT: keymap → command / edit intent
    RT->>RHA: document replace request
    RHA->>KH: validated host call
    KH->>ABI: cdin_doc_replace(...)
    ABI->>K: synchronous C call
    K->>K: validate handle, range, expected version
    K->>K: commit bytes + version + undo unit atomically
    K-->>ABI: status + edit result
    ABI-->>KH: status + new version
    KH->>ABI: drain/read queued change notifications
    ABI->>K: notification read
    K-->>ABI: bounded event / RESYNC
    ABI-->>KH: notification result
    KH-->>RT: operation result + invalidation information
    RT->>BE: update semantic UI model
    BE->>FP: view invalidation / updated model
    FP->>FE: protocol response
    FE->>FE: recompute visual layout and render
```

*Status: `PROPOSED` for the integrated end-to-end path. The synchronous kernel-call, version-check, committed-version and bounded-notification semantics are `EXISTING` in Kernel ABI 1.0.0; Runtime Host API and Frontend Protocol integration are not claimed as implemented by the kernel package.*

### What the sequence intentionally excludes

- No frontend calls the kernel directly.
- No Lua runtime links to private kernel internals.
- No kernel call draws pixels, shapes text or writes a file.
- No notification is an unbounded callback-driven work queue; kernel notifications are bounded and may require `RESYNC` after overflow.
- No search complexity promise such as O(1) is implied. Package 1.2.1 has internal literal-search fast paths, but observable matching/range semantics and the public ABI remain the contract.

## 4. Startup, compatibility and shutdown

```mermaid
sequenceDiagram
    autonumber
    participant ROOT as cdin launcher
    participant BE as Backend
    participant K as cdin-kernel
    participant RT as Runtime (Lua)
    participant FE as Frontend

    ROOT->>BE: Start with configuration
    BE->>K: Create kernel with allocator, limits and optional lock callbacks
    BE->>K: Query ABI version and supported feature mask
    K-->>BE: ABI version 1.1.0 and feature mask
    BE->>RT: Create Lua state and register Runtime Host API
    RT-->>BE: Runtime initialized
    BE-->>ROOT: Backend ready
    ROOT->>FE: Start selected frontend with endpoint
    FE->>BE: Handshake with protocol version and capabilities
    BE-->>FE: Accept or reject and provide initial semantic UI model
    Note over ROOT,FE: Version validation and Runtime Host API integration are target requirements
    FE->>BE: Detach or quit
    BE->>RT: Stop callbacks and unload plugins
    BE->>K: Stop mutations and abort active transactions
    BE->>K: Release documents, snapshots and subscriptions
    BE->>K: Destroy kernel after all callers stop
    BE-->>ROOT: Shutdown complete
```

*Status: `PROPOSED` for application startup and shutdown as a whole. The kernel's ABI query, synchronous calls and shutdown semantics are specified in [concurrency](concurrency.md), [lifecycle](lifecycle.md) and the published header. The complete backend/runtime/frontend path still needs an integration test.*

## 5. Version and release view

Version labels describe different contracts; they are not interchangeable.

| Label | Current value | Authority | What it controls |
|---|---:|---|---|
| Kernel package | `1.2.1` | `cdin-kernel/CHANGELOG.md` / release tag | Source release, package contents and distribution workflow |
| Kernel C ABI | `1.1.0` | `include/cdin/kernel.h` | Native caller-visible names, types, layouts, constants and semantics |
| CDIN Spec release | `1.3.0` | [reference/status.md](../reference/status.md) | Current compatible specification release and architecture documentation |
| Kernel-declared Spec target | `1.1.0` | `include/cdin/kernel.h` via `CDIN_KERNEL_SPEC_VERSION_*` | Specification baseline this kernel package declares conformance to |
| Frontend Protocol version | `1.0.0` target | ADR-0018 and protocol contract | Accepted semantic/wire contract; Backend implementation conformance remains incomplete |
| Runtime Host API version | `1.0.0` stable | Backend Host API contract | Runtime-to-Backend service surface; live native integration remains a Runtime package release gate |
| Extension-contract version | follows the extension contract | `cdin` extension contract | Compatibility between runtime and `cdin-x` extensions |

## 6. Component delivery and product composition

The Registry is a generic, consumer-independent Component Orchestration system. Product Definitions provide requirements as data; Registry manages component versions, updates, resolution and source collection. CDIN consumes a prepared workspace and owns product integration, build, tests, packaging and launch.

\`\`\`mermaid
flowchart TB
    subgraph COMPONENTS["Component repositories and releases"]
        C1["Backend source units"]
        C2["Frontend variants<br/>CLI · GUI-SDL · TUI · ..."]
        C3["Runtime source units"]
        C4["Kernel library"]
        C5["Future split repositories"]
    end
    PD["Product Definition<br/>data-only requirements"]
    subgraph REGISTRY["Generic Registry — no consumer-specific logic"]
        CATALOG["Component and release catalog"]
        UPDATE["Version and update management"]
        RESOLVE["Dependency and compatibility resolution"]
        COLLECT["Source collection + immutable revision verification"]
        OUTPUT["Prepared workspace<br/>+ resolved manifest"]
        CATALOG --> UPDATE --> RESOLVE --> COLLECT --> OUTPUT
    end
    C1 --> CATALOG
    C2 --> CATALOG
    C3 --> CATALOG
    C4 --> CATALOG
    C5 --> CATALOG
    PD --> RESOLVE
    subgraph CDIN["CDIN product pipeline"]
        INTEGRATE["Product-specific integration"]
        BUILD["Build"]
        TEST["Product and integration tests"]
        RUN["Package and launch"]
        INTEGRATE --> BUILD --> TEST --> RUN
    end
    OUTPUT --> INTEGRATE
    SPEC["Spec<br/>contracts and architecture"]
    SPEC -. "defines generic contracts" .-> CATALOG
    SPEC -.-> PD
    SPEC -.-> CDIN
\`\`\`

**Core invariant:** Registry must understand requirements, not consumer identity. The same Registry can serve CDIN Editor and a future unrelated product by processing different Product Definitions without product-specific code.

### Responsibility summary

| Owner | Responsibility |
|---|---|
| Component repositories | Source, component-owned versions, tags, tests and releases |
| Product Definition | Declarative component IDs, variants, constraints and product composition requirements |
| Registry | Catalog, version/update management, resolution, source collection, verification, prepared workspace and resolved manifest |
| CDIN | Product-specific integration, configuration, build, product tests, packaging and launch |
| Spec | Normative contracts, architecture and decision records |

### Handoff contract

Registry does not hand CDIN a list of URLs and expect CDIN to fetch or resolve them. It prepares the source workspace and returns a manifest with exact component identities, versions, variants, repositories, immutable revisions and available integrity metadata.

CDIN consumes that prepared input. It does not own component discovery, version selection, update tracking, dependency solving or source collection.

### Kernel 2.0.0 and Frontend variants

A Kernel release 2.0.0 is recorded by Registry with its package version, source revision and contract declarations. A Product Definition can request the Kernel library at a compatible version while selecting only Frontend cli and gui-sdl; other Frontend variants are not collected. If Backend later splits across multiple repositories, its component metadata can describe multiple source units without changing Registry's consumer-facing behavior.

Package version 2.0.0 does not imply ABI 2.0.0; package and contract version axes remain independent.

*Status: PROPOSED. These diagrams describe the intended architecture, not an implemented Registry or a shipped workspace contract.*

