# ABI and compatibility

Every native binary boundary between CDIN components uses the **C ABI** (`ACCEPTED`). The current standalone `cdin-kernel` header publishes ABI `1.1.0` in package `1.2.1`; ABI major `1` retains the frozen numeric values, existing structure layout and function signatures, with compatible additive minor growth. ABI `1.0.0` is the original stable baseline. The sibling `cdin-kernel` repository header is authoritative; this Spec archive records its synchronization in [implementation status](../kernel/implementation-status.md). The Frontend Protocol is a separate versioned contract; its wire encoding and client-library location are resolved by [ADR-0018](../adr/ADR-0018-frontend-protocol-wire.md).

## Version labels are independent

| Label | Value for this sync | Source of truth |
|---|---:|---|
| Kernel package release | `1.2.1` | Kernel package metadata and release tag |
| C ABI | `1.1.0` | `cdin-kernel/include/cdin/kernel.h` |
| Spec release | `1.4.0` | `docs/reference/status.md` |
| Kernel-declared Spec target | `1.1.0` | The header's `CDIN_KERNEL_SPEC_VERSION_*` macros |

Package `1.2.1` publishes ABI `1.1.0`. The ABI 1.1 addition includes the Kernel-owned logging API (`cdin_kernel_log` and logger configuration); it does not renumber existing statuses or change existing ABI 1.x layouts/signatures. Package and ABI versions are independent: never derive one from the other. Any future contract change must update the header, compatibility declaration and conformance evidence together.

## 1. Which boundaries are binary

| Boundary | Binary C ABI? | Notes |
|---|---|---|
| backend ↔ kernel | **Yes** | The primary ABI. Defined in [kernel/](../kernel/overview.md). |
| frontend ↔ backend, in-process transport | **Yes** | Same messages as the serialized transport, carried through C functions. See [frontend-protocol.md](frontend-protocol.md). |
| frontend ↔ backend, serialized transport | No (byte protocol) | Language-neutral; versioned separately from the C ABI. |
| runtime ↔ backend | No (Lua API) | The Lua environment is a contract (`EXISTING` extension contract + runtime host API), backed by C inside the backend. |
| cdin-x ↔ runtime | No (Lua API) | Extension contract. |
| backend internals (OS services) | No | Internal C APIs; not stable ABI. |

An ABI boundary does **not** imply a dynamically loaded module. Components MAY be statically linked into one executable; the ABI rules still apply so that any component can later be swapped or separated. (`ACCEPTED`, see ABI-013.)

## 2. Rules

- **ABI-001** `ACCEPTED` Binary boundaries between modules use the C ABI. — *Verify:* STATIC, INSPECT
- **ABI-002** `ACCEPTED` Each ABI has a semantic version `MAJOR.MINOR.PATCH`. A breaking change increments MAJOR; compatible additive capabilities increment MINOR; compatible defect corrections increment PATCH. ABI `1.0.0` is the first stable kernel ABI. — *Verify:* INSPECT, CONF
- **ABI-003** `ACCEPTED` Every public request/result struct with a size prefix begins with `struct_size`; v1 callers set it to the full structure size from the compiled header. Kernel ABI 1 rejects smaller known-structure sizes, validates unknown trailing bytes as zero, and requires exact sizes for nested by-value service vtables. Unknown flags MUST be rejected, never silently ignored. — *Verify:* CONF, FUZZ
- **ABI-004** `ACCEPTED` Objects are exposed as opaque handles. The layout of any internal structure MUST NOT be visible in public headers. — *Verify:* STATIC
- **ABI-005** `ACCEPTED` Handles carry a generation. Using a closed or never-issued handle MUST return `INVALID_HANDLE`, not crash. — *Verify:* CONF, SAN
- **ABI-006** `ACCEPTED` Every fallible public Kernel API operation returns a `cdin_status`; result data and typed error details are returned through caller-provided output structures or parameters. `cdin_status_name` is the non-fallible helper that maps a status to its stable symbolic name. — *Verify:* STATIC, INSPECT
- **ABI-007** `PROPOSED` No exception, `longjmp` or process termination MAY cross a boundary. A module MUST NOT call `exit` or `abort` because of caller input. — *Verify:* STATIC, FUZZ
- **ABI-008** `ACCEPTED` Ownership is explicit at the public API: caller buffers are borrowed for the duration of a synchronous call unless the header says they are copied; Kernel-owned handles and snapshots have explicit release/close operations; memory allocated for Kernel-owned state uses the configured allocator. — *Verify:* SAN, INSPECT
- **ABI-009** `ACCEPTED` Arbitrary document, search-pattern and other binary payloads use pointer-plus-length pairs; document content is bytes and may contain NUL or invalid UTF-8. C-string parameters are identified as such in the header and MUST NOT be confused with document byte buffers. — *Verify:* CONF, FUZZ
- **ABI-010** `ACCEPTED` ABI 1 public enum-like fields use fixed-width `uint32_t` types with named numeric constants; handles, versions and byte offsets use 64-bit unsigned types where declared. Native structs may contain pointers and `size_t` and therefore follow the target platform C ABI; they are not packed wire structs, and implicit padding is governed by the platform ABI. — *Verify:* STATIC
- **ABI-011** `ACCEPTED` Within one MAJOR version, evolution is additive only; existing values, field order, widths and function prototypes MUST remain stable. Since v1 rejects smaller known structs and requires zero unknown tails, struct extension requires a MINOR-versioned compatibility rule and a new implementation that expressly supports that extension. Unknown enum-like values return `UNSUPPORTED` where applicable. — *Verify:* INSPECT, CONF
- **ABI-012** `PROPOSED` Each function documents its thread-safety class: `ANY_THREAD` (safe concurrently), `SERIALIZED_PER_OBJECT` (safe if calls on one object do not overlap), or `OWNER_THREAD` (one designated thread). — *Verify:* INSPECT, SAN
- **ABI-013** `ACCEPTED` A component with an ABI is not required to be a separately loaded dynamic module. — *Verify:* INSPECT
- **ABI-014** `ACCEPTED` The kernel exposes ABI-version and feature queries; callers MUST detect an incompatible ABI major at startup and fail clearly. — *Verify:* CONF, INTEG
- **ABI-015** `ACCEPTED` Public Kernel API symbols use the `cdin_` component prefix. Implementation-private helpers are not part of the public header or supported ABI. — *Verify:* STATIC, INSPECT
- **ABI-016** `ACCEPTED` Kernel wakeup/log callbacks supplied by callers are documented and MUST NOT be invoked while the kernel lock is held; their thread and reentrancy constraints are documented by the public header. — *Verify:* SAN, INSPECT
- **ABI-017** `ACCEPTED` Kernel-owned data allocations use the allocator callbacks supplied at Kernel creation (allocate, reallocate and free with a context pointer). This does not claim control over allocations made internally by an external logger or other explicitly configured third-party facility. — *Verify:* INSPECT, SAN
- **ABI-018** `PROPOSED` The two-call pattern applies to variable-length outputs: the caller passes a buffer and capacity, the module reports the required size, and returns `BUFFER_TOO_SMALL` when capacity is insufficient. Alternatively the module returns an owned buffer released by its release function. A function documents which. — *Verify:* CONF

## 3. Stable kernel ABI versus Frontend Protocol

The kernel header is the authority for the current ABI 1.1.0 names, types, constants, layouts and prototypes. The short sketch below is historical illustration only and MUST NOT be copied as a declaration of the current API.

```c
/* ILLUSTRATIVE ONLY. Consult cdin-kernel/include/cdin/kernel.h for ABI 1.1.0. */
typedef struct cdin_kernel      cdin_kernel;           /* opaque */
typedef uint64_t                cdin_doc;              /* handle: index + generation */

typedef struct {
    uint32_t struct_size;
    void *(*alloc)(void *ctx, size_t n);
    void *(*realloc)(void *ctx, void *p, size_t old_n, size_t new_n);
    void  (*free)(void *ctx, void *p, size_t n);
    void  *ctx;
} cdin_allocator;

typedef struct {
    uint32_t struct_size;
    uint64_t expected_version;     /* or CDIN_ANY_VERSION */
    uint64_t start, end;           /* byte offsets, half-open */
    const uint8_t *bytes; size_t len;
} illustrative_replace_request;

cdin_status cdin_kernel_create(const cdin_kernel_config *cfg, cdin_kernel **out);
cdin_status cdin_doc_replace(cdin_kernel *k, cdin_doc d,
                             const cdin_replace_request *req,
                             cdin_edit_result *out);
```

## 4. Compatibility policy

- **ABI-020** `PROPOSED` A component MUST state, in its documentation, the ABI MAJOR range it supports. The composition root MUST refuse to start when the provided versions fall outside it. — *Verify:* INTEG
- **ABI-021** `PROPOSED` A breaking ABI change requires an ADR, a MAJOR increment, and a migration note. An ABI-major increment requires an ADR and a migration note. — *Verify:* INSPECT
- **ABI-022** `PROPOSED` Behaviour that is not in the contract is not guaranteed. A change to unspecified behaviour is not a breaking change, but the specification SHOULD be corrected to say so. — *Verify:* INSPECT

## 5. Contrast with the Lua contract

The Lua extension contract already uses the same discipline: "If something is not in this document, it is not a contract, and changing it is a breaking change" (`EXISTING`, `docs/architecture/extension-contract.md`, introduction). The ABI rules extend that principle to binary boundaries.
