# Search engine

Advanced search is part of the kernel, not UI logic of a search box (`ACCEPTED`).

## Implementation note — package 1.1.0

The public contract remains the one declared by ABI 1.0.0. The 1.1.0 implementation adds forward literal-search fast paths: Linux may use `memmem` only for byte-exact, uncancellable requests with a full candidate-window budget; other supported platforms use a selective-byte anchor to skip unnecessary full comparisons. Requests that need cancellation, step accounting or partial-result behavior remain on the incremental path. These are private implementation choices, not promises of O(1) complexity or a specific latency. Any optimization must return the same ranges and statuses as the portable path.

## 1. Required capabilities (`ACCEPTED`)

- **SEARCH-001** `ACCEPTED` Literal search. — *Verify:* CONF
- **SEARCH-002** `ACCEPTED` Case-sensitive and case-insensitive search. — *Verify:* CONF
- **SEARCH-003** `ACCEPTED` Forward and backward search. — *Verify:* CONF
- **SEARCH-004** `DEFERRED` Regular-expression search is not part of Kernel ABI 1.0.0; `CDIN_SEARCH_REGEX` returns `CDIN_UNSUPPORTED` and its feature bit is not advertised. Keep this requirement ID reserved; do not claim regex support until a later ABI explicitly adds and tests it. — *Verify:* CONF
- **SEARCH-005** `ACCEPTED` Unicode text, including Persian. — *Verify:* CONF
- **SEARCH-006** `ACCEPTED` Multiline search. — *Verify:* CONF
- **SEARCH-007** `ACCEPTED` Results identify the document version they were computed against. — *Verify:* CONF
- **SEARCH-008** `ACCEPTED` Behaviour on documents containing invalid UTF-8 is defined. — *Verify:* CONF

## 2. Query and result model

```mermaid
flowchart TB
    Q["search request: pattern bytes, mode, flags, direction, start position, limits, snapshot or version"]
    SNAP["acquire snapshot of requested version"]
    VAL{"query valid? pattern compiles, flags known"}
    ERR["PATTERN_INVALID or INVALID_ARGUMENT or UNSUPPORTED"]
    MODE{"mode"}
    LIT["literal matcher"]
    RX["regex: UNSUPPORTED in ABI 1.0.0"]
    RAW["raw-byte matcher"]
    LIM{"step limit or cancel?"}
    CAN["LIMIT_EXCEEDED or CANCELLED, no results"]
    RES["result: matches as byte ranges, snapshot version"]

    Q --> SNAP --> VAL
    VAL -- "no" --> ERR
    VAL -- "yes" --> MODE
    MODE -- "literal" --> LIT --> LIM
    MODE -- "regex" --> RX --> ERR
    MODE -- "bytes" --> RAW --> LIM
    LIM -- "yes" --> CAN
    LIM -- "no" --> RES
    classDef bad fill:#fee2e2,stroke:#b91c1c,color:#0f172a
    classDef ok fill:#dcfce7,stroke:#15803d,color:#0f172a
    class CAN,ERR bad
    class RES ok
```

*Caption: `PROPOSED` search lifecycle. Regex is deferred; edge cases for raw-byte adjacency remain open (OD-11).*

- **SEARCH-010** `ACCEPTED` A search runs against a pinned immutable content block and reports the document version searched. The search does not hold the Kernel lock for the full scan. — *Verify:* CONF, INSPECT
- **SEARCH-011** `ACCEPTED` Search returns byte ranges, supports a caller-specified result limit, and reports continuation positions (`next_from` / `next_bound`) for forward or backward scans. Results are tied to the reported content version. — *Verify:* CONF
- **SEARCH-012** `ACCEPTED` Searching is not the place that adjusts for later edits: the caller maps results across subsequent versions using change events (POS-050) or re-runs the search. — *Verify:* INSPECT
- **SEARCH-013** `ACCEPTED` Search supports deterministic candidate-step limits and caller cancellation. With `CDIN_SEARCH_WANT_PARTIAL`, matches found before a limit or cancellation are retained and the result reports that it is partial. — *Verify:* CONF, SAN
- **SEARCH-014** `ACCEPTED` ABI 1.0.0 exposes `literal`, `bytes`, and a reserved `regex` mode value; `literal` and `bytes` are supported, while `regex` returns `UNSUPPORTED`. — *Verify:* CONF

## 3. Matching rules

### Case

- **SEARCH-020** `ACCEPTED` Case-insensitive matching is Unicode-aware, locale-independent, and uses simple case folding by default, relative to the pinned Unicode version ([ADR-0010](../adr/ADR-0010-unicode-version.md)). Full case folding is a separate explicit option. — *Verify:* CONF

### Persian and Arabic letters

- **SEARCH-021** `ACCEPTED` The system MUST NOT automatically treat different Arabic and Persian letters as equivalent. For example Persian `ی` (U+06CC) and Arabic `ي` (U+064A) are different letters unless an explicit option says otherwise. — *Verify:* CONF
- **SEARCH-022** `ACCEPTED` Unicode normalization, removal of diacritics (for example Arabic marks), character folding and language-specific equivalences MUST be separate, explicit capabilities, never implied by the case flag. — *Verify:* CONF
- **SEARCH-023** `PROPOSED` Such capabilities are expressed as named options in the request (for example `normalize=nfc`, `ignore_marks`, `fold_profile=<name>`). All are off by default. The set offered in the first version is an open scope item ([OD-29](../adr/open-decisions.md)). — *Verify:* CONF
- **SEARCH-024** `PROPOSED` Each such option is defined by a published table or algorithm tied to the pinned Unicode version, so two implementations agree. — *Verify:* CONF

### Multiline

- **SEARCH-030** `ACCEPTED` A literal query MAY contain line terminators. Regex multiline behaviour is deferred. Searching never normalizes line endings (TEXT-003, ARCH-020). — *Verify:* CONF
- **SEARCH-031** `PROPOSED` In multiline mode `^` matches at the start of the document and after each line terminator; `$` matches at the end of the document and before each line terminator. A CRLF pair is one terminator and is never split by an anchor. `.` does not match a line terminator unless a dotall flag is set. — *Verify:* CONF
- **SEARCH-032** `ACCEPTED` For a literal query whose text contains `\n` (LF), whether it matches CRLF or CR terminators is controlled by an explicit option `any_newline`; default is exact bytes. — *Verify:* CONF

### Invalid UTF-8

- **SEARCH-040** `ACCEPTED` Literal search matches only within valid UTF-8 regions. Raw/invalid regions are skipped and reported through `cdin_search_result.skipped_raw`. — *Verify:* CONF
- **SEARCH-041** `ACCEPTED` Byte search is exact and may match any byte sequence anywhere in the document, including inside or across valid and raw regions. — *Verify:* CONF
- **SEARCH-042** `ACCEPTED` Literal search exposes whether raw/invalid UTF-8 regions were skipped through the `skipped_raw` result field. — *Verify:* CONF

## 4. Regular-expression engine

- **SEARCH-050** `PROPOSED` If regex is accepted for a later ABI, use an existing portable library rather than writing one from scratch; the library and syntax subset are not chosen. See [ADR-0009](../adr/ADR-0009-regex-engine.md). — *Verify:* INSPECT
- **SEARCH-051** `PROPOSED` The contract MUST specify: supported syntax (a documented subset that the engine guarantees), invalid-pattern errors (`PATTERN_INVALID` with a position), zero-length match behaviour, multiline mode, resource limits, and cancellation. — *Verify:* CONF, INSPECT
- **SEARCH-052** `PROPOSED` Catastrophic patterns are bounded by the step limit (SEARCH-013), not by the clock. — *Verify:* CONF, FUZZ
- **SEARCH-053** `PROPOSED` Zero-length matches: a find-all MUST advance by one code point (or one raw byte) after a zero-length match to guarantee progress. — *Verify:* CONF

## 5. Existing behaviour

- **EXISTING** The supplied `cdin` snapshot has a small native search module and Lua document search; these remain migration references and are not the ABI 1.0.0 kernel implementation. — *Anchor:* `src/search/find.c`, `data/core/doc/search.lua`
