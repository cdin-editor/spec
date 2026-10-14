# scripts/

`check.py` is the only script. Standard library only.

| Command | Does |
| --- | --- |
| `python3 scripts/check.py` | ids, links, refs, index, diagrams |
| `python3 scripts/check.py --stats` | the counts `docs/reference/status.md` quotes |
| `python3 scripts/check.py --render` | also renders every diagram with `mmdc` |
| `python3 scripts/check.py --only ids,links` | a subset |

It checks form and internal consistency, not correctness against the `cdin` code.
