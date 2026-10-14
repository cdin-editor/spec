# AGENTS.md: rules for working on the CDIN specification

## What this repository is

The design-only specification of CDIN. Markdown and Mermaid. No code beyond `scripts/check.py`.

## Hard rules

1. Never promote a status. Only the owner sets `ACCEPTED` or `DEFERRED`.
2. Never reuse or renumber a requirement ID.
3. Never invent history, dates or test results. No test has been run.
4. Every `EXISTING` statement carries an `Anchor:` into the `cdin` tree.
5. Diagrams: use the vocabulary in `docs/reference/conventions.md` §4; caption any `PROPOSED` flow.

## After touching what

| You touched | Run |
| --- | --- |
| any page | `python3 scripts/check.py` |
| requirements added or removed | `python3 scripts/check.py --stats`, then update `docs/reference/status.md` |
| a diagram | `python3 scripts/check.py --render` (needs `mmdc`) |
| the file layout | `psx check` |

## When to ask

An ambiguity whose wrong guess changes an `ACCEPTED` item. Otherwise decide, and say what you decided.
