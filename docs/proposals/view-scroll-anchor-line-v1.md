# Versioned scroll-anchor line projection v1

**Status:** `PROPOSED`. This optional extension does not change the accepted
Runtime UI Model or Frontend Protocol 1.0.0 until owner acceptance.

**Related:** [Spec #23](https://github.com/cdin-editor/spec/issues/23),
[Frontend #15](https://github.com/cdin-editor/frontend/issues/15),
[Runtime UI Model](../architecture/ui-model-v1.md),
[Protocol wire contract](../architecture/protocol-wire.md).

## 1. Ownership and invariants

The Runtime owns the semantic scroll anchor as an exact zero-based document
byte offset at a document version. That meaning does not change.

The Frontend needs a logical line index to issue the existing pull-based
`view.request_lines(first_line, count)` operation. It cannot derive an
arbitrary byte offset's line number from a bounded cache containing only a
visible window. Fetching all preceding lines or the whole document is not an
acceptable fallback.

The Runtime/Kernel document line index is the only authoritative byte-to-line
mapping. Backend projects the Runtime's version-pinned result; Frontend uses it
only to select a bounded visible window.

## 2. Negotiation and compatibility

The optional capability is `view-scroll-anchor-line/1`.

- Frontend requests it in `hello.capabilities`.
- Backend accepts it only if the Runtime can supply the line index atomically
  with the exact cursor document version.
- When accepted, the matching `view.cursor` payload may include
  `scroll_anchor_line:uint`.
- The field is zero-based and uses exactly the same logical-line indexing as
  `view.request_lines.first_line` and `view.lines.first_line`.
- When the capability is absent, the existing byte-only `scroll_anchor`
  remains unchanged and no line projection is emitted. Old peers continue
  their existing behavior; no new request type is required.

The extension does not change `view.request_lines`, `view.lines` or the
meaning/units of the existing `scroll_anchor` field.

## 3. Snapshot fields and version pairing

For a view at document version `V`:

| Field | Type | Meaning |
|---|---|---|
| `version` | uint | Document version that owns the cursor/anchor |
| `position` | uint | Cursor byte offset, unchanged |
| `scroll_anchor` | uint | Exact logical document byte offset, unchanged |
| `scroll_anchor_line` | uint | Optional zero-based logical line index containing `scroll_anchor` at `version` |

When the extension is accepted, Backend MUST emit `scroll_anchor_line` in the
same `view.cursor` message as `version` and `scroll_anchor`. It MUST NOT
combine a line index computed for one version with an anchor from another.

Runtime obtains the line index from the Kernel's authoritative line-start
index (equivalent to its `line_of(document, offset)` operation). Backend MUST
NOT scan Frontend cache contents, estimate from byte offsets, or calculate
line numbers from character counts.

## 4. Logical line mapping

The line index uses the Kernel's canonical line arithmetic and is zero-based.
Line terminators are LF, CRLF (one terminator), and lone CR. This extension
does not normalize or rewrite line-ending bytes.

For a document with line-start offsets `starts[]`, the line for an anchor
`offset` is the greatest index `i` for which `starts[i] <= offset`.

Consequences:

- Empty documents have one logical line, line 0, with anchor 0.
- An anchor on a terminator byte belongs to the line ending at that terminator.
- The byte immediately after LF, CRLF or lone CR belongs to the next line.
- A document ending in a line terminator has a final empty logical line; an
  anchor at EOF belongs to that final line.
- An anchor at EOF in an unterminated final line belongs to that final line.
- Offsets must be within `0..document_length`; an out-of-range or stale anchor
  rejects the complete cursor projection rather than clamping it silently.

These rules mirror the Kernel's line-start index and avoid frontend-specific
newline interpretation.

## 5. Frontend visible-window selection

For each visible view, Frontend receives the byte anchor and line index at the
same version. It calculates a bounded window around that line using the
available line capacity and the existing per-view scroll policy:

`first_line = max(0, scroll_anchor_line - leading_context)`

The requested count MUST NOT exceed the view's configured visible-line
capacity or remaining known `total_lines`. If `total_lines` is known, the
Frontend clamps the last requested line to that count. If the anchor line is
at or beyond a newly reported total line count, the complete stale cursor /
line-count pair is discarded and the latest snapshot is awaited; it is not
silently mapped to the final line.

The exact leading-context policy (top-aligned, centered, or cursor-biased)
remains Frontend presentation policy, not Runtime semantics. The default
v1 policy is top-aligned: `leading_context = 0`. User scrolling may update
local presentation state and request a new bounded window, but Runtime remains
the owner of the semantic byte anchor.

Every outstanding request remains pinned to view ID, document version,
first_line and count. A response for another view, an older version, or a
different requested range is rejected using the existing correlation rules.
Per-view and aggregate cache budgets remain unchanged.

## 6. Failure and fallback behavior

- A peer without the capability receives no `scroll_anchor_line`.
- A stale line index MUST NOT be combined with a newer document version.
- A malformed, negative (where representable), out-of-range or inconsistent
  line index rejects the complete cursor payload.
- A missing field after capability acceptance is a protocol conformance error;
  Frontend retains the last committed snapshot and requests normal recovery.
- A document edit that changes bytes before the anchor requires Runtime to
  transform the byte anchor and recompute the line index against the new
  version before publication.
- A view switch, detach/reconnect or snapshot replacement preserves independent
  state per view; no global first-line value is shared across views.

## 7. Conformance vectors

The companion
[view-scroll-anchor-line-v1.json](../testing/vectors/view-scroll-anchor-line-v1.json)
covers empty documents, LF, CRLF, lone CR, terminator positions, EOF and
trailing terminators, edit/version changes, stale projection, per-view requests,
legacy capability fallback and out-of-range rejection.

The fixture line indices follow the Kernel's zero-based line-start arithmetic.
These are proposed contract vectors, not passing test evidence.

## 8. Non-goals

This extension does not define pixel scrolling, font metrics, wrapped visual
rows, bidi visual order, cursor drawing, smooth animation, scrollbars or
frontend-specific wheel acceleration. Those remain presentation concerns.
