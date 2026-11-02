# Conformance testing

This document defines a language-neutral conformance approach. A conformance vector is input plus expected observable output, not a test that inspects private implementation state.

## Existing executable suites

- `cdin-editor/kernel` contains a C vector parser/runner, public ABI vectors and Kernel unit/fuzz tests. The public header on the inspected `main` branch declares C ABI `1.1.0`.
- `cdin-editor/backend` contains a standalone `cdin_protocol` codec, schema tests, bounded protocol-server tests, a headless Frontend driver, bidirectional frame tests and a deterministic event replay path. Its local `make protocol-test` command passed on 2026-11-02.
- The Backend also contains service E2E tests. These do not replace a live Lua 5.4 + real Kernel adapter test.

## Required conformance layers

1. **Contract vectors.** Every public message and status has valid and invalid cases. Byte strings include NUL and invalid UTF-8. Numeric boundaries, unknown optional fields, duplicate keys, truncated frames and oversized messages are exercised.
2. **Component tests.** Kernel tests run against the public C ABI; Runtime tests run against Lua 5.4 and a contract-compliant Host; protocol codec/server tests run without a GUI or Kernel.
3. **Adapter tests.** Run Kernel vectors through the Backend's real C adapter and verify exact status/detail preservation, ownership and cleanup.
4. **Bidirectional session tests.** A headless Frontend attaches, negotiates capabilities, receives UI state, requests lines, sends input, receives Runtime effects, replays a trace and checks the final model/revision.
5. **Platform matrix.** Run the same public contract suite on Linux, macOS and Windows. A configured CI matrix is not evidence until its jobs have completed successfully.

## Current limits

The protocol codec validates the message catalogue in its supported v0.2.0 subset; the Headless Frontend and server queue provide deterministic local evidence. The remaining integration requirements include Runtime UI-model projection to protocol messages, complete inbound dispatch from the Backend queue to the Lua Runtime, OS socket/pipe adapters, live Lua 5.4 + Kernel adapter tests, fuzz-run evidence and completed macOS/Windows CI. See the Backend's [`docs/1.0.0-readiness.md`](https://github.com/cdin-editor/backend/blob/main/docs/1.0.0-readiness.md) before treating the system as release-ready.
