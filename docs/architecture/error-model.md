# Error model

One error vocabulary for every ABI boundary and for the Frontend Protocol.

## 1. Principles

- **ERR-001** `PROPOSED` Every operation that can fail returns a status. Failure is data, never a crash, never a silent no-op. — *Verify:* CONF, FUZZ
- **ERR-002** `PROPOSED` A failed mutation MUST leave the document unchanged and its version unchanged. — *Verify:* CONF
- **ERR-003** `PROPOSED` Errors are structured: a status code, a human-readable UTF-8 message, and typed details where the code defines them. Callers MUST branch on the code, never on the message. — *Verify:* CONF, INSPECT
- **ERR-004** `PROPOSED` Invalid input from a caller is an error status, never undefined behaviour. This includes invalid handles, out-of-range positions, malformed requests and unknown flags. — *Verify:* FUZZ, SAN
- **ERR-005** `PROPOSED` Out-of-memory is reported as `NO_MEMORY` with the operation left unapplied. — *Verify:* CONF (with an injected failing allocator), SAN

## 2. Status codes (kernel ABI 1.0.0; protocol mapping remains `PROPOSED`)

| Code | Meaning | Details |
|---|---|---|
| `OK` | Success | |
| `INVALID_ARGUMENT` | Malformed argument or request | field name |
| `INVALID_HANDLE` | Closed, stale or never-issued handle | |
| `STALE_VERSION` | `expected version` did not match the current version | expected, current |
| `OUT_OF_RANGE` | Position or range beyond the document | requested, length |
| `INVALID_POSITION` | Position splits a valid multibyte sequence | position |
| `INVALID_STATE` | Operation not valid in the current state (for example nested transaction) | |
| `BUSY` | Document has an active transaction that is not the caller's | |
| `LIMIT_EXCEEDED` | A configured cap was reached | which limit |
| `NO_MEMORY` | Allocation failed | |
| `PATTERN_INVALID` | Invalid literal search pattern where reported | pattern position where available |
| `CANCELLED` | Cancelled by the caller | |
| `SHUTDOWN` | Component is shutting down or stopped | |
| `UNSUPPORTED` | Unknown flag, enum value, feature or version | |
| `BUFFER_TOO_SMALL` | Output buffer too small (two-call pattern) | required size |
| `VERSION_MISMATCH` | Incompatible ABI or protocol versions | supported, requested |
| `INTERNAL` | A defect inside the component | |

- **ERR-010** `PROPOSED` `STALE_VERSION` MUST report both the expected version and the current version. — *Verify:* CONF (restates the accepted behaviour in EDIT-004)
- **ERR-011** `PROPOSED` `INTERNAL` indicates a bug. A component that returns it MUST remain safe to destroy, and SHOULD keep unaffected documents usable. Whether the affected document is poisoned is `PROPOSED` as: the document refuses further mutation with `INTERNAL` until closed. — *Verify:* CONF
- **ERR-012** `PROPOSED` Codes are never reused for a different meaning. New codes are additive (ABI-011). A caller that receives an unknown code MUST treat it as a failure of unknown cause. — *Verify:* CONF

## 3. Errors across components

| Boundary | How errors travel |
|---|---|
| kernel ABI | status return plus an optional error-details out-parameter |
| Frontend Protocol | an `error` message referencing the request id, with status and details |
| runtime host API (Lua) | Lua errors with a stable error table (code, message, details); existing Lua error convention is kept |
| plugins | governed by the extension contract's error policy |

- **EXISTING** The C layer already defines a small shared error vocabulary for Lua (`src/lua/error.h`, `src/base/error.h`), and the extension contract has an "error policy" section. The new status model MUST map onto them rather than replace them. — *Verify:* INSPECT — *Anchor:* `src/lua/error.h`, `src/base/error.h`, `docs/architecture/extension-contract.md` ("The error policy")
- **ERR-020** `PROPOSED` Mapping from kernel status codes to the runtime's Lua errors MUST be one-to-one and documented in [runtime.md](../components/runtime.md). — *Verify:* INSPECT, INTEG

## 4. Diagnostics

- **ERR-030** `PROPOSED` Components emit diagnostics through an injected log sink (a callback with level and UTF-8 message). A component MUST NOT write to standard streams on its own initiative. — *Verify:* INSPECT, STATIC
