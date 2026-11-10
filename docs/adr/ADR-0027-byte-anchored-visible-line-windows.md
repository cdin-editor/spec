# ADR-0027: Byte-anchored visible line windows

- **ID:** ADR-0027
- **Status:** `ACCEPTED`
- **Decision scope:** An additive, capability-negotiated extension to Frontend Protocol 1.0.0 line-window requests.

## Context

The accepted Runtime UI Model stores `scroll_anchor` as an exact document byte offset at a document version. The existing Frontend Protocol requests visible content by logical `first_line`. A Frontend cache is intentionally bounded and may begin far after byte zero, so it cannot derive the line containing an arbitrary scroll anchor without fetching or scanning the preceding document.

Backend already has a public Host API bridge to the Kernel's version-pinned line-index lookup, and its line-window read uses a Kernel snapshot. The missing piece is an interoperable wire request and byte-start metadata for the returned window.

## Problem

The extension must preserve raw bytes, NUL, invalid UTF-8 and stored line terminators; handle LF, CRLF and lone CR consistently with Kernel; reject stale/out-of-range anchors; support bounded complete-line windows; and remain compatible with peers that know only `first_line`.

It must also avoid taking separate snapshots for the resolved line and returned bytes. Doing so could pair metadata from one document version with line content from another.

## Proposed decision

Adopt the optional capability `byte-anchored-lines/1` as specified in [Byte-anchored visible line windows v1](../proposals/byte-anchored-line-windows-v1.md).

1. Keep the existing required `first_line`, `line_count` and `version` fields. When the capability is accepted, a Frontend MAY add `anchor_byte`; that offset takes precedence over `first_line`, which remains a valid compatibility fallback.
2. Resolve the anchor with the Kernel's public line index against the same immutable snapshot used to read the requested line bytes. Backend MUST NOT scan the document prefix, use Frontend cache contents or take a second snapshot.
3. Add `first_byte` to each `view.lines` response only for a peer that accepted the capability. It is the exact byte start of the actual returned `first_line`. It is emitted for both anchor-based and legacy line-number-only requests from negotiated peers.
4. Retain the exact original line bytes, including terminators. A Frontend derives later line starts by adding each previous returned line's byte length; it MUST NOT count code points, graphemes or glyphs.
5. A stale version or anchor beyond document length returns the existing structured error and no line data. EOF and final-empty-line behavior follows the Kernel line index exactly.
6. Without capability acceptance, old `first_line` behavior is unchanged, `anchor_byte` is not sent and `first_byte` is not relied upon.

This extension adds no Kernel ABI service and no new required core message. It is a Backend projection of existing Kernel line-index behavior, with Frontend using the result only for its bounded presentation cache. Runtime remains the owner of the byte scroll anchor.

## Options considered

### Project a logical line number into Runtime's cursor snapshot

Not selected. The earlier design is preserved in [view-scroll-anchor-line-v1.md](../proposals/view-scroll-anchor-line-v1.md), but it creates another derived field in the Runtime UI model and makes the projection dependency less explicit. The selected proposal keeps the canonical anchor as bytes and resolves the line only when Backend serves a window.

### Scan from the beginning of the document in Frontend

Rejected. It defeats bounded caches and makes scrolling cost proportional to the preceding document size.

### Fetch all preceding lines or all document bytes

Rejected. It increases memory, bandwidth and latency without improving the canonical position contract.

### Change the meaning of `first_line` or require a Protocol major bump

Rejected. A separate optional capability and additive fields preserve existing Protocol 1.0.0 peers.

### Take a second snapshot to calculate `first_byte`

Rejected. It can mix a line-number result and bytes from different versions during concurrent edits. Both must come from one immutable snapshot.

## Trade-offs

- The request carries a compatibility fallback even when the anchor is authoritative; this keeps old Backend behavior well-defined.
- Negotiated peers receive one extra integer field per line-window response.
- The Backend/Kernel boundary must expose the first byte of the actual line window from the same snapshot read; no public Kernel ABI change is needed.

## Consequences

- This ADR remains a proposal and does not amend the accepted Protocol contract until the project owner accepts it.
- [Spec #25](https://github.com/cdin-editor/spec/issues/25) tracks the contract and shared vectors.
- The current Backend line-index service is the correct implementation foundation; the missing work is version-pinned request/response projection and its regression suite.
- Frontend's bounded per-view cache and production scrolling remain part of [Frontend #15](https://github.com/cdin-editor/frontend/issues/15).
- CDIN verifies the composed behavior with the exact immutable component pins under [CDIN #111](https://github.com/cdin-editor/cdin/issues/111).

## References

- [Runtime UI Model v1](../architecture/ui-model-v1.md)
- [Frontend Protocol wire contract](../architecture/protocol-wire.md)
- [Byte-anchored line-window proposal](../proposals/byte-anchored-line-windows-v1.md)
- [Byte-anchored line-window conformance vectors](../testing/vectors/byte-anchored-lines-v1.json)
- [Backend Host API](https://github.com/cdin-editor/backend/blob/main/docs/host-api.md)
- [ADR-0018 — Frontend Protocol wire format and mutation authority](ADR-0018-frontend-protocol-wire.md)
