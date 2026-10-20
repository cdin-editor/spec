# ADR-0010: Unicode version policy

- **ID:** ADR-0010
- **Status:** `ACCEPTED`. Each kernel release pins a queryable Unicode data version.

## Context
Open decision OD-10. Grapheme boundaries, case folding and any normalization or mark-removal option depend on a Unicode version. Different versions give different results for the same text.

## Problem
Which Unicode version does the kernel use, and can callers rely on it?

## Decision
- Each kernel release **pins** one Unicode version.
- The pinned version is queryable at run time (POS-032).
- Every Unicode-dependent behaviour (grapheme segmentation, case folding, normalization, mark handling) is defined against that version.
- Changing the pinned version is a MINOR change of the kernel, documented in release notes, and conformance vectors that depend on it state the version they target.

## Options
- **A. Pin per release (accepted).** Pros: reproducible; two implementations can agree. Cons: periodic table updates.
- **B. Track the latest at build time.** Pros: no manual updates. Cons: results change silently between builds.
- **C. Runtime-selectable version.** Pros: maximum control. Cons: large tables, complex testing.

## Trade-offs
Reproducibility is worth the update chore; text search results and cursor behaviour must not change under a user without a visible release.

## Consequences
Tables are generated from the Unicode data files for the pinned version by a build step in the kernel repository. Persian/Arabic letter distinctness is *not* a Unicode-version matter: it is a rule (SEARCH-021) that holds under any version.

## References
POS-032, SEARCH-020, SEARCH-024, [OD-10](open-decisions.md).
