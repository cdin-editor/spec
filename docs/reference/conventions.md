# Conventions

How to read and write this specification.

## 1. Status labels

Every requirement, decision and diagram element carries exactly one status.

| Label | Meaning | Who may set it |
|---|---|---|
| `EXISTING` | Behaviour verified against an identified supplied repository/archive snapshot or its documents. Must cite a **code/document anchor** (file, symbol or section), with snapshot identity and inspection limits recorded in `docs/reference/status.md`. It does not imply access to upstream Git history or CI. | Anyone, after verifying. |
| `ACCEPTED` | A decision explicitly made by the project owner. | Project owner only. |
| `PROPOSED` | A recommendation awaiting a decision. Never to be treated as settled. | Anyone. |
| `OPEN` | An unresolved question. Appears only in the [Open Decisions Register](../adr/open-decisions.md), never as a requirement. | Anyone. |
| `DEFERRED` | Intentionally postponed to a later phase. | Project owner. |

Allowed transitions: `OPEN → PROPOSED → ACCEPTED`; any state `→ DEFERRED`; `DEFERRED → PROPOSED`. A status change that affects a contract requires an ADR.

An `EXISTING` item that stops matching the code is a **contradiction**; it is recorded in [status.md](status.md) and fixed, not silently edited.

## 2. Requirement format

Normative requirements are single lines in this exact shape (tools may parse them):

```
- **KERNEL-007** `PROPOSED` The kernel MUST NOT read the clock. — *Verify:* INSPECT, CONF
```

- `ID`: `PREFIX-NNN`, stable forever. IDs are never reused or renumbered; a withdrawn requirement keeps its ID with status `DEFERRED` or a note.
- Keywords MUST, MUST NOT, SHOULD, SHOULD NOT, MAY are used as in RFC 2119, and only in requirement lines.
- A requirement with status `EXISTING` also carries `Anchor:` after the verify field.

### ID prefixes

| Prefix | Area |
|---|---|
| `ARCH` | System architecture, boundaries, topology |
| `ABI` | Binary interface rules |
| `PROTO` | Frontend Protocol |
| `CONC` | Concurrency |
| `LIFE` | Lifecycles |
| `ERR` | Error model |
| `KERNEL` | Kernel scope and properties |
| `DOC` | Document model and lifecycle |
| `TEXT` | Text model, encoding, line endings |
| `POS` | Positions and ranges |
| `EDIT` | Editing operations |
| `TXN` | Transactions |
| `UNDO` | Undo and redo |
| `NOTIF` | Change notifications |
| `SEARCH` | Search engine |
| `BE` | Backend |
| `RT` | Runtime |
| `FE` | Frontends |
| `EXT` | Extensions and cdin-x |
| `DATA` | Data / persistence |
| `ROOT` | `cdin` composition root |
| `SPEC` | This specification's own process |
| `TEST` | Verification design |

Open decisions use `OD-NN`; architecture decision records use `ADR-NNNN`.

## 3. Verification methods

Every requirement names how it will be verified. Because this repository is design-only, these are **plans**, not artifacts.

| Method | Meaning |
|---|---|
| `INSPECT` | Verified by review of design or code against the requirement. |
| `STATIC` | Verified by a static rule: include-direction check, symbol-visibility check, lint. |
| `CONF` | Verified by a **conformance vector**: a data-driven case run through the public contract against any implementation. See [conformance.md](../testing/conformance.md). |
| `FUZZ` | Verified by fuzzing the input boundary. |
| `SAN` | Verified under sanitizers (address, undefined-behaviour, thread). |
| `PERF` | Verified by a measured budget against a recorded baseline. |
| `INTEG` | Verified by an end-to-end scenario across components. |

No requirement may be reported as verified unless its verification has actually been run. The Spec structural checker and the separate `cdin-kernel` implementation suite are different verification targets and must be reported independently.

## 4. Diagrams

All diagrams are Mermaid, and they share one vocabulary:

| Shape / colour | Means |
|---|---|
| blue rectangle | a component |
| violet hexagon | a contract: an ABI, a protocol, a host API |
| grey cylinder | something outside the specification: the OS, a store |
| grey, dashed | `DEFERRED` |
| green / red | a successful / a rejected outcome in a flow |
| orange | a raw (invalid UTF-8) region |
| dotted arrow | a build-time, bundling or contract relationship, not a call |

 A diagram must not present an `OPEN` behaviour as settled; where a diagram shows a `PROPOSED` flow it says so in its caption. Diagrams and prose must agree; a disagreement is a defect.

## 5. ADR format

Each ADR in [docs/adr/](../adr/) has: ID, title, status, context, problem, decision (or the question when not yet decided), options, trade-offs, consequences, and references. ADRs carry no invented dates or histories.

## 6. Code anchors

An anchor names a path relative to the `cdin` repository root and, where useful, a section or symbol: `AGENTS.md §2.6`, `mk/bundle.mk`, `src/loop/loop.c`. Anchors refer to the working tree inspected, recorded in [status.md](status.md).
