# ADR-0018: Frontend Protocol wire format, client boundary and mutation authority

- **ID:** ADR-0018
- **Status:** `ACCEPTED`
- **Date:** 2026-11-02
- **Resolves:** OD-22, OD-23, OD-24

## Context

ADR-0005 already accepts a transport-independent semantic protocol. The remaining open choices blocked interoperable byte streams, shared test vectors and safe multi-frontend input. Document data is an arbitrary byte sequence; treating it as UTF-8 or embedding it in ordinary JSON would corrupt valid Kernel content. The first implementation already has bounded per-client outbound queues, flush groups, ACK/backpressure and a provisional driver/observer split.

## Decisions

### Wire encoding (OD-22)

1. Serialized messages use **deterministic CBOR** as specified by RFC 8949, with the additional CDIN profile below.
2. Every stream frame begins with a four-byte unsigned **big-endian** body length. The prefix is not included in that length. Exactly one CBOR envelope follows.
3. The top-level envelope is a definite-length map with exactly these fields: `v` (two-element unsigned integer array `[major, minor]`), `ns` (text namespace), `seq` (unsigned message sequence), `type` (text message name), and `payload` (message-specific map).
4. Core messages use namespace `core`. An implementation MUST ignore unknown optional namespaces only when explicitly negotiated; unknown messages in `core` return `UNSUPPORTED`.
5. Text strings are valid UTF-8. Opaque document and paste content is a CBOR byte string. No data path may silently transcode bytes to text.
6. Only definite-length CBOR arrays/maps/strings are accepted. Duplicate map keys, non-shortest integer/length encodings, trailing bytes, indefinite-length items, unsupported simple values and all CBOR floating-point values are rejected. Map keys in CDIN-defined maps are UTF-8 text.
7. The default maximum frame body is 1 MiB. Deployments may lower this limit, but may not accept a frame above the negotiated/local cap.
8. A reader MUST handle partial stream reads and writes. A transport implementation supplies byte read/write callbacks; the codec owns framing and validation, not sockets, named pipes or event loops.

### Client library location (OD-23)

The reference C codec is a separately linkable `cdin_protocol` target in `cdin-editor/backend`. It installs `include/cdin/protocol.h` and has no dependency on Backend internals, Lua, the Kernel, GUI code or OS services. The Spec remains documentation and conformance vectors only. Other language clients implement the stable wire contract and run the same vectors; none links `cdin_backend` to encode/decode a protocol frame.

### Mutation authority (OD-24)

A session has one driver lease. The first attached client becomes driver; all other clients are observers. Only the driver may send `input.key`, `input.text`, `input.mouse`, `input.paste`, `window.resize`, `focus`, `view.set_position` or `request.command`. Observers may ACK outbound flushes, request visible line ranges and return responses to capability-backed requests addressed to them. On driver detach/close, the oldest still-attached observer is promoted. The Backend serializes event acceptance on the Runtime owner thread; arrival time is not a last-writer ordering guarantee.

## Versioning

This decision establishes Frontend Protocol `0.2.0`. Its major version remains `0` while the contract is pre-1.0; the minor version changes for additive schema/transport evolution. Incompatible changes require a major version change. Unknown optional payload fields are ignored; required fields and core message names are not optional.

## Consequences

- The Backend owns the reference C codec and shared vectors; the frontend can consume only the codec target or independently implement the wire format.
- The existing in-process queue remains a transport of the same typed messages and validated CBOR payload maps.
- A driver disconnect is the only automatic lease-transfer point. There is no implicit simultaneous-writer mode.
- This ADR does not assert that every protocol message, transport adapter, runtime event handler or platform build has already shipped. Evidence is tracked in Backend `docs/spec-traceability.md` and the release verification report.

## References

- [ADR-0005](ADR-0005-frontend-protocol.md)
- [Frontend Protocol](../architecture/frontend-protocol.md)
- [Wire and message schemas](../architecture/protocol-wire.md)
