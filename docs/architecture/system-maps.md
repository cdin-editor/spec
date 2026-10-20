# System maps

This page collects architecture views at different levels of abstraction. Read them in order: landscape, dependency boundaries, request flow, then startup and release. These diagrams describe the target architecture unless marked `EXISTING`; they do not promote `PROPOSED` or `OPEN` work to implemented status.

## 1. Landscape view — who plays which role?

```mermaid
flowchart TB
    USER(["User / automation"])

    subgraph PRESENTATION["Frontends — presentation and input"]
        GUI["gui-sdl"]
        TUI["tui — DEFERRED"]
        HL["headless / cli"]
    end
    FP{{"Frontend Protocol<br/>versioned semantic contract"}}

    subgraph CORE["CDIN core — headless-capable"]
        BE["Backend<br/>session and orchestration"]
        RT["Runtime · Lua<br/>policy and UI model"]
        RHA{{"Runtime Host API<br/>PROPOSED"}}
        KH["Kernel host"]
        ABI{{"C ABI 1.0.0"}}
        K["cdin-kernel<br/>package 1.1.0"]
        OS[("OS services")]
    end
    EXTC{{"Lua Extension Contract"}}
    X["cdin-x<br/>extension ecosystem"]
    ROOT["cdin<br/>composition and delivery"]
    SPEC["spec<br/>architecture governance"]

    USER --> GUI
    USER --> TUI
    USER --> HL
    GUI <--> FP
    TUI <--> FP
    HL <--> FP
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
    class GUI,HL,BE,RT,KH,K,X,ROOT,SPEC comp
    class FP,RHA,ABI,EXTC contract
    class OS,USER external
    class TUI deferred
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
    ABI{{"Kernel C ABI 1.0.0"}}

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
- **The language bridge remains an implementation choice.** Lua C API binding, LuaJIT FFI or an intermediary such as MetaCall must stay behind the Runtime Host API/kernel adapter and requires a separate decision; see [OD-32](../adr/open-decisions.md).

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
- No search complexity promise such as O(1) is implied. Package 1.1.0 adds internal literal-search fast paths, but observable matching/range semantics and the public ABI remain the contract.

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
    K-->>BE: ABI version 1.0.0 and feature mask
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
| Kernel package | `1.1.0` | `cdin-kernel/CHANGELOG.md` / release tag | Source release, package contents and distribution workflow |
| Kernel C ABI | `1.0.0` | `include/cdin/kernel.h` | Native caller-visible names, types, layouts, constants and semantics |
| CDIN Spec release | `1.1.0` | [reference/status.md](../reference/status.md) | Current compatible specification release and architecture documentation |
| Kernel-declared Spec target | `1.0.0` | `include/cdin/kernel.h` via `CDIN_KERNEL_SPEC_VERSION_*` | Specification baseline this kernel package declares conformance to |
| Frontend Protocol version | not frozen | Open decisions and protocol page | Frontend/backend messages; serialization is still open |
| Runtime Host API version | not published | Open decision / future implementation | Runtime-to-backend service surface |
| Extension-contract version | follows the extension contract | `cdin` extension contract | Compatibility between runtime and `cdin-x` extensions |

The package `1.1.0` change is package-compatible with ABI `1.0.0`: public declarations and result-range semantics remain stable. Spec release `1.1.0` is separately versioned from the Spec `1.0.0` conformance target declared by this kernel. If the accepted kernel contract changes, update the kernel ABI and its declared Spec target through an explicit review, and update the Spec release according to `SPEC-010`; do not infer a kernel ABI bump from package-only or documentation-only changes.
