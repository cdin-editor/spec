# Test matrix

Maps each requirement group to verification methods and conformance-vector families. Planned coverage is not evidence of execution. The evidence snapshot at the end records only tests actually run against the Backend workspace on 2026-11-02; it does not make every linked Spec requirement conformant.

| # | Requirement group | Requirement IDs | Verification | Vector family | Status |
|---:|---|---|---|---|---|
| 1 | ABI versioning and public header shape | ABI-001 to ABI-020 | BUILD, CONF | `abi.*` | Kernel vectors and C ABI checks exist in `cdin-editor/kernel`; Backend adapter integration remains incomplete |
| 2 | Byte-preserving text and positions | TEXT-001 to TEXT-060, POS-001 to POS-040 | CONF, FUZZ, SAN | `text.*`, `pos.*`, `unicode.*` | Kernel vectors and fuzz targets exist; Backend-to-Runtime live tests remain incomplete |
| 3 | Edits, versions and transactions | EDIT-001 to EDIT-050, TXN-001 to TXN-030 | CONF, INTEG, FUZZ | `edit.*`, `txn.*` | Kernel tests exist; complete production Host adapter tests remain a gate |
| 4 | Undo/redo and selection metadata | UNDO-001 to UNDO-040 | CONF, INTEG | `undo.*` | Kernel history tests exist; Runtime integration requires live tests |
| 5 | Notifications and concurrency | NOTIF-001 to NOTIF-040, CONC-001 to CONC-040 | CONF, SAN | `notif.*`, `conc.*` | Kernel queues and callback constraints are implemented; full Backend Runtime pumping requires live integration |
| 6 | Search | SEARCH-001 to SEARCH-040 | CONF, FUZZ | `search.*` | Kernel literal/byte coverage exists; regex is unsupported in ABI 1.1.0 |
| 7 | Runtime and Host API | RT-001 to RT-021, HOST-001 to HOST-040 | INTEG, SAN | Runtime integration fixtures | Runtime unit/integration source exists; no live Lua 5.4 + Kernel run was available in this workspace |
| 8 | Frontend Protocol | PROTO-001 to PROTO-042 | CONF, FUZZ, INTEG | `proto.*` | Backend codec/server/headless tests run locally; UI-model projection, Lua dispatch and real OS transport remain incomplete |
| 9 | Backend lifecycle and OS services | BE-001 to BE-011, LIFE-001 to LIFE-020 | INTEG, SAN, PERF | Backend service tests | Existing job/platform/process E2E tests pass locally; cross-platform execution is not established by this local run |
| 10 | Packaging and release | REL-001 to REL-030 | BUILD, INTEG | release artifact checks | Release pipeline exists; 1.0.0 gate remains open |

## Execution evidence — 2026-11-02

The following limited evidence was collected in the Backend workspace in the current environment:

| Target | Command | Result | Scope / limitation |
|---|---|---|---|
| Protocol codec, headless Frontend, server queue | `make protocol-test` | PASS | Strict C11 standalone tests. Does not prove Lua dispatch, sockets/named pipes, or full Runtime UI projection. |
| Backend service E2E | `make e2e` | PASS | Exercises existing service-level E2E fixtures; not the Kernel/Runtime production adapter. |
| Protocol-only CMake build and CTest | `cmake -S . -B build-delivery-check -DCDIN_BUILD_BACKEND=OFF -DCDIN_BUILD_EXAMPLES=OFF -DBUILD_TESTING=ON`, `cmake --build build-delivery-check --parallel`, then `ctest --test-dir build-delivery-check --output-on-failure` | PASS (7/7, final local run) | Protocol and existing Backend service targets build without the Kernel package. Does not compile the production Kernel/Lua adapter. |
| LibFuzzer smoke | `./build-fuzz-final/cdin_protocol_decode_fuzz build-fuzz-final/corpus -runs=5000 -max_len=4096` after a fresh Clang ASan/UBSan build | PASS (5,000 runs) | Three source seeds copied to the build directory; generated corpus remained outside the source tree. Smoke test only, not a sustained campaign or proof of complete parser coverage. |
| Lua 5.4 + real Kernel integration | `runtime-integration.yml` | NOT RUN locally | Lua 5.4 development files and installed `cdin-kernel` pkg-config package were unavailable. |
| macOS / Windows matrix | `ci.yml` | NOT RUN locally | CI matrix is configured; only CI execution can establish those platform results. |

The Backend's detailed source-to-Spec mapping and remaining blockers are recorded in its [`spec-traceability.md`](https://github.com/cdin-editor/backend/blob/main/docs/spec-traceability.md). A pass in one row is not a blanket claim about Frontend Protocol or CDIN release conformance.
