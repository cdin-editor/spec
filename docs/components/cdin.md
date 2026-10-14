# cdin: the composition root

`cdin` is the point where the components of CDIN are assembled, built, bundled and launched. It contains no domain logic.

## 1. Purpose

- Build every component for every supported platform.
- Bundle the runtime, the mandatory set from `cdin-x`, and frontends into a runnable product.
- Release (packaging, installers, workflows) and developer tooling (benchmarks, checks, size and memory measurements).
- Launch: choose a frontend, start the backend, attach.

## 2. Is and is not

| Is | Is not |
|---|---|
| The only place that depends on everything | A place where kernel, runtime, backend or frontend logic is reimplemented |
| Build files, release workflows, installer scripts, launcher | Depended on by any component |
| The home of tooling that checks the include-direction rules | A shared-code repository (ARCH-005) |

## 3. Requirements

- **ROOT-001** `ACCEPTED` The composition root MUST NOT reimplement kernel, runtime, frontend or backend logic (ARCH-001). — *Verify:* INSPECT
- **ROOT-002** `PROPOSED` No component MAY depend on the composition root (ARCH-045). — *Verify:* STATIC
- **ROOT-003** `EXISTING` The build can produce the binary alone (`make bin`) or a runnable tree (`make`, which assembles `data/`). — *Verify:* INTEG — *Anchor:* `mk/bundle.mk`
- **ROOT-004** `EXISTING` The only build-time knowledge of `cdin-x` is the path variable `CDINX_DIR`; the default is a sibling checkout (`../cdin-x`). Nothing is fetched at build or run time. — *Verify:* INTEG — *Anchor:* `mk/bundle.mk`, `scripts/assemble_data.py`
- **ROOT-005** `EXISTING` The `bare` build target produces a tree with the core, fonts and themes and no plugins, used to measure startup and idle behaviour without any extension. — *Verify:* INTEG — *Anchor:* `mk/bundle.mk` (`bare`)
- **ROOT-006** `PROPOSED` The launcher selects a frontend by name and passes it the backend's endpoint (in-process or serialized transport). Adding a frontend MUST NOT require changing the backend. — *Verify:* INTEG
- **ROOT-007** `PROPOSED` The composition root MUST check ABI compatibility of the components it assembles (ABI-020) and refuse an incompatible set at build or start. — *Verify:* INTEG
- **ROOT-008** `PROPOSED` Include-direction rules (ARCH-046) are enforced by tooling hosted here (today `scripts/check.py`). — *Verify:* STATIC
- **ROOT-009** `EXISTING` Release workflows exist for Linux, Windows and macOS, with Docker and a website deployment; the composition root keeps ownership of them. — *Verify:* INSPECT — *Anchor:* `.github/workflows/`
- **ROOT-010** `PROPOSED` The kernel, when it becomes its own repository, is consumed by `cdin` as a pinned version (a release or a submodule at a tag), never as a floating branch. — *Verify:* INSPECT

## 4. Existing layout mapped here

| Existing | Role |
|---|---|
| `Makefile`, `mk/*.mk` | build orchestration (`platform`, `version`, `config`, `build`, `test`, `check`, `install`, `bundle`) |
| `scripts/_cdin/*.py`, `scripts/*.py` | install, update, uninstall, build, bench, size and measurement tooling |
| `Dockerfile`, `docker-compose.yml` | containerized builds |
| `.github/` | CI, release, issue and PR templates |
| `psx.yml` | project-structure configuration |
| `docs/` | documentation of the product (the specification lives in the `spec` repository) |

The tooling stays here; it depends on the layout of `src/` and on the Makefile, so a separate scripts repository would break whenever the layout changes. (Rationale in [ADR-0001](../adr/ADR-0001-repository-topology.md).)

## 5. Launch sequence

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant L as launcher
    participant B as backend
    participant F as chosen frontend
    U->>L: run cdin (options: frontend, files)
    L->>B: start backend (config, site directory)
    B-->>L: ready (endpoint)
    L->>F: start frontend (endpoint)
    F->>B: hello / attach
    B-->>F: hello_ack, initial UI
    U->>F: edits
    F->>B: input events
    U->>F: quit
    F->>B: detach
    L->>B: shutdown
```

*Caption: `PROPOSED`. Today the GUI and backend are one process and the launcher is `src/main.c`.*
