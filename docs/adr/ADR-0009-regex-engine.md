# ADR-0009: Regular-expression engine

- **ID:** ADR-0009
- **Status:** `OPEN`. The direction (use an existing portable engine; do not write one from scratch) is approved in principle. The engine itself is not chosen.

## Context
Kernel ABI 1.0.0 deliberately does not implement regex search: `CDIN_SEARCH_REGEX` returns `CDIN_UNSUPPORTED`. If regex is proposed for a future ABI, it must have a documented syntax, Unicode and invalid-UTF-8 contract, resource limits and cancellation (SEARCH-004, SEARCH-050 to SEARCH-053). The kernel is deterministic and has no clock (KERNEL-007), so bounds are in steps. The public API MUST NOT expose the engine's types or syntax identifiers (KERNEL-010).

## Problem
Which library, and which guaranteed syntax subset?

## Selection criteria
1. C-callable with a stable, small API.
2. UTF-8 mode with predictable behaviour on invalid input.
3. A **step or match limit** and a way to **cancel** a running match.
4. Multiline anchors and a dotall option with documented semantics.
5. Licence compatible with the project.
6. Portability to the three target platforms and the existing build.
7. Behaviour on pathological patterns.

## Candidates (to be verified in a spike; statements below are from general knowledge, not from testing)
| Candidate | Notes |
|---|---|
| PCRE2 | C library; UTF mode; match, depth and heap limits; callouts allow aborting a match; backtracking so pathological patterns exist but are bounded by limits |
| Oniguruma | C library; many syntax profiles; Ruby-style behaviour; match-stack and retry limits |
| RE2 | Linear-time guarantee, no backreferences or lookaround; implemented in C++ with a C wrapper available; the C++ dependency conflicts with a C-only kernel build |
| TRE and others | smaller libraries; Unicode and limit support to be checked |
| Written in-house | rejected as a preferred direction by the owner (not from scratch) |

## Decision
None yet. `PROPOSED` direction: choose from PCRE2 or Oniguruma by spike, against the criteria above, with a written subset of guaranteed syntax in the contract.

## Trade-offs
Backtracking engines offer rich syntax and need limits to bound cost; linear-time engines bound cost by construction and give up features. The step-limit requirement (SEARCH-013) is satisfiable with either, but only if the library exposes a hook.

## Consequences
Whatever is chosen sits behind an internal interface (KERNEL-010). Conformance vectors for regex are written against the documented subset, not the engine's full syntax. Changing the engine later is allowed if vectors still pass.

## References
[search-engine.md](../kernel/search-engine.md), [OD-09](open-decisions.md), SEARCH-050 to SEARCH-053.
