# Byte-anchored visible line windows v1

**Status:** `PROPOSED`. This is an additive Protocol 1.0.0 extension proposal. It does not amend the accepted wire contract until the owner accepts it. Implementations MUST NOT advertise the capability while it remains proposed.

**Related:** [Spec #25](https://github.com/cdin-editor/spec/issues/25), [Frontend #15](https://github.com/cdin-editor/frontend/issues/15), [UI Model v1](../architecture/ui-model-v1.md), [Protocol wire v1.0.0](../architecture/protocol-wire.md).

## 1. Problem and goals

The accepted Runtime UI Model stores a view's scroll anchor as a logical document byte offset. The existing line request identifies its window by logical line number. A bounded Frontend cache cannot derive the logical line for an arbitrary byte anchor without scanning all prior lines.

This proposal lets a negotiated Frontend ask Backend for a bounded line window beginning at the logical line that contains a byte anchor. The response identifies the exact document byte offset of its first returned line so the Frontend can map cursor, selection and scroll offsets into that window without assuming UTF-8 character counts or line lengths.

The extension preserves Kernel ownership of canonical bytes and Runtime ownership of the semantic byte anchor. Backend performs a version-pinned index lookup; Frontend performs local visual layout only.

## 2. Capability and compatibility

The exact optional capability is `byte-anchored-lines/1`.

A Frontend requests it in `hello.capabilities`. Backend returns it in `hello_ack.accepted_capabilities` only when it implements the complete version-pinned lookup and response metadata. Requesting the capability alone does not activate it.

The existing required `first_line` field remains present in every `view.request_lines` request. When the capability is accepted, a new Frontend MAY also send `anchor_byte`. Backend uses `anchor_byte` to resolve the actual starting line; otherwise it uses the existing `first_line`.

This fallback preserves the existing Protocol 1.0.0 shape:
- An old Backend ignores the unknown optional `anchor_byte` field and continues from `first_line`.
- An old Frontend ignores the unknown optional `first_byte` response field.
- A peer that did not negotiate the capability MUST NOT rely on anchor-based behavior or send the new field.

No mandatory core message, namespace or protocol version is changed.

## 3. Request extension

The existing request remains:

```cbor
view.request_lines {
  view_id: text,
  first_line: uint,
  line_count: uint,
  version: uint
}
```

When `byte-anchored-lines/1` is accepted, the Frontend may append:

| Field | Type | Meaning |
|---|---|---|
| `anchor_byte` | uint | Zero-based document byte offset whose containing logical line becomes the first returned line |

When present, `anchor_byte` takes precedence over `first_line`; `first_line` is still required as a compatibility fallback for older peers. Backend rejects an anchor beyond the document length with `OUT_OF_RANGE`. It never clamps an invalid anchor silently.

The request remains bounded by the existing `line_count` and response-byte limits. It is still pinned to the exact required `version`. A stale version returns `STALE_VERSION` and no line data.

## 4. Anchor-to-line semantics

The document is interpreted as the Kernel's logical byte sequence and line index at the requested version. Backend finds the greatest logical line-start byte offset that is less than or equal to `anchor_byte`.

- An offset at a logical line start selects that line.
- An offset in the content or stored line terminator bytes selects the line containing those bytes.
- An offset exactly at the next line's start selects the next line.
- For a document ending in a line terminator, the final empty logical line starts at EOF and is selectable.
- For a document without a final line terminator, EOF selects the final non-empty logical line.
- Empty documents select their single empty logical line at byte offset zero.
- CR, LF and CRLF semantics are those of the Kernel's existing line index. No newline normalization occurs.
- Invalid UTF-8, NUL and raw bytes have no special effect on the byte offset. No UTF-8 decoding is needed to resolve the anchor.

The lookup MUST run against one immutable Kernel snapshot whose version equals the request's `version`. It MUST use public Kernel line-index services; Backend MUST NOT copy the entire document into a Frontend-visible buffer or derive a line index from an unpinned live document.

A binary search over the version-pinned line-start index is the expected implementation. The required complexity is logarithmic in the number of logical lines, excluding the bounded work to read and encode the requested window.

## 5. Response extension

When the capability was accepted, Backend adds this optional field to the existing `view.lines` response:

| Field | Type | Meaning |
|---|---|---|
| `first_byte` | uint | Exact document byte offset of the first returned logical line |

The response continues to contain the existing `view_id`, `version`, `first_line`, `lines` and optional `total_lines` fields. `first_line` is the actual resolved logical line index, not the compatibility fallback supplied by the request.

For every subsequent line in the same response, its document byte start is obtained by adding the exact byte length of each preceding returned line. The line byte strings retain their original terminator bytes, so this mapping is exact. A Frontend MUST NOT count Unicode scalar values, grapheme clusters or rendered glyphs to derive document byte offsets.

`first_byte` is emitted only to a peer that negotiated `byte-anchored-lines/1`. A response remains pinned to the exact requested document version and participates in the existing response-scoped `ui.flush`/ACK flow. Short windows caused by the existing byte budget retain their actual `first_line`, `first_byte`, `version` and returned line count; the Frontend requests the next window from the actual `first_line + returned_count` and derives its byte start by adding the returned raw byte lengths.

## 6. Frontend usage and ownership

Runtime continues to publish a logical byte `scroll_anchor` in `view.cursor`. It does not store a visual line number, pixel position, line height or shaped glyph index.

A negotiated Frontend can request a visible window with:
- its stable Runtime View ID;
- the view's current document version;
- the persisted `scroll_anchor` as `anchor_byte`;
- its bounded visible line count;
- `first_line=0` as the compatibility fallback.

The response's `first_line` and `first_byte` establish the logical line and byte interval covered by the window. Frontend can then map the view's cursor and selection byte offsets into the returned rows, and only later map them through its own text shaping and visual layout.

Frontend caches remain disposable and per-view. A new document version invalidates the old byte-to-line mapping. A response for another view, version or outstanding request MUST NOT be used.

## 7. Errors and limits

The request is rejected without line data when:
- the sender is not authorized to issue the existing line request;
- the view/document does not exist;
- the requested document version is stale;
- `anchor_byte` exceeds the document byte length;
- the request exceeds the existing line-count or frame-byte budget.

The Backend does not return partial UTF-8 code points or split a logical line to satisfy the byte budget. Existing complete-line and bounded-response behavior is retained. If the first selected line alone exceeds the existing line-response budget, the Backend returns the existing structured `LIMIT_EXCEEDED` error.

## 8. Conformance vectors

The companion [byte-anchored-lines-v1.json](../testing/vectors/byte-anchored-lines-v1.json) remains `PROPOSED`. It covers empty documents, line starts, content offsets, CR/LF/CRLF bytes, trailing empty lines, EOF, NUL, invalid UTF-8, stale versions, out-of-range anchors, legacy fallback and short bounded windows.

These fixtures are not passing test evidence. Frontend and Backend conformance runners must consume the same vectors after owner acceptance.

## 9. Non-goals

This extension does not define visual scrolling, smooth-scroll animation, wrapping, font metrics, glyph shaping, bidi, cursor rendering or selection painting. It supplies exact logical line/byte mapping only; those visual responsibilities remain in Frontend.
