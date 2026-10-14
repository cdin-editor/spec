#!/usr/bin/env python3
"""Structural checks for the specification. Design-only: no code is executed.

Checks form and internal consistency, not correctness against the cdin code.

  ids       every requirement ID is unique, well formed, uses a registered prefix,
            carries a registered status and a registered verification method;
            every EXISTING requirement carries an anchor
  links     every relative Markdown link resolves, including #fragments
  refs      every mentioned requirement, ADR and OD exists
  index     every page under docs/ is reachable from docs/README.md
  diagrams  every Mermaid block opens with a known diagram type
            (with --render, each one is also rendered by the Mermaid CLI)

Usage:
  python3 scripts/check.py              run every check
  python3 scripts/check.py --stats      print the counts docs/reference/status.md quotes
  python3 scripts/check.py --render     also render every diagram (needs `mmdc`)
  python3 scripts/check.py --only ids,links

Exit status: 0 clean, 1 findings, 2 the checker itself could not run.
A check that cannot run prints SKIPPED with the reason and does not fail.
"""

import argparse
import collections
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATUSES = {"EXISTING", "ACCEPTED", "PROPOSED", "OPEN", "DEFERRED"}
METHODS = {"INSPECT", "STATIC", "CONF", "FUZZ", "SAN", "PERF", "INTEG"}
PREFIXES = {
    "ARCH", "ABI", "PROTO", "CONC", "LIFE", "ERR", "KERNEL", "DOC", "TEXT", "POS",
    "EDIT", "TXN", "UNDO", "NOTIF", "SEARCH", "BE", "RT", "FE", "EXT", "DATA",
    "ROOT", "SPEC", "TEST",
}
DIAGRAMS = ("flowchart", "graph", "sequenceDiagram", "stateDiagram-v2",
            "classDiagram", "erDiagram", "gantt", "journey", "timeline")

REQ = re.compile(r"^- \*\*([A-Z]+-\d{3})\*\* `(\w+)`(.*)$", re.M)
EXISTING_BARE = re.compile(r"^- \*\*EXISTING\*\*(.*)$", re.M)
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
MERMAID = re.compile(r"^```mermaid\n(.*?)^```", re.M | re.S)
ID_MENTION = re.compile(r"\b((?:%s)-\d{3})\b" % "|".join(sorted(PREFIXES)))
ADR_MENTION = re.compile(r"\bADR-(\d{4})\b")
OD_MENTION = re.compile(r"\bOD-(\d{2})\b")


def pages():
    return sorted(p for p in ROOT.rglob("*.md")
                  if ".git" not in p.parts and "node_modules" not in p.parts)


def rel(p):
    return p.relative_to(ROOT).as_posix()


def slug(heading):
    s = re.sub(r"[`*_]", "", heading.strip().lower())
    s = re.sub(r"[^\w\- ]", "", s, flags=re.U)
    return s.replace(" ", "-")


def anchors_of(path, cache={}):
    if path not in cache:
        text = FENCE.sub("", path.read_text())
        seen, out = collections.Counter(), set()
        for m in re.finditer(r"^#{1,6}\s+(.*)$", text, re.M):
            s = slug(m.group(1))
            out.add(s if not seen[s] else f"{s}-{seen[s]}")
            seen[s] += 1
        # explicit anchors, e.g. <a id="od-01"></a>
        out.update(re.findall(r'<a\s+(?:id|name)="([^"]+)"', path.read_text()))
        cache[path] = out
    return cache[path]


def collect():
    reqs = []  # (id, status, rest, file)
    for p in pages():
        for m in REQ.finditer(FENCE.sub("", p.read_text())):
            reqs.append((m.group(1), m.group(2), m.group(3), p))
    return reqs


# ── checks ────────────────────────────────────────────────────────────────────

def check_ids():
    errs, seen = [], {}
    for rid, status, rest, p in collect():
        where = f"{rel(p)}: {rid}"
        if rid in seen:
            errs.append(f"{where}: duplicate (first in {rel(seen[rid])})")
        seen[rid] = p
        prefix = rid.split("-")[0]
        if prefix not in PREFIXES:
            errs.append(f"{where}: unregistered prefix {prefix}")
        if status not in STATUSES:
            errs.append(f"{where}: unknown status {status}")
        m = re.search(r"\*Verify:\*\s*(.*?)(?:\s+—\s+\*|$)", rest)
        if not m:
            errs.append(f"{where}: no *Verify:* field")
        else:
            lead = re.match(r"[A-Z]+(?:\s*,\s*[A-Z]+)*", m.group(1))
            names = re.split(r"\s*,\s*", lead.group(0)) if lead else []
            if not names or not set(names) <= METHODS:
                errs.append(f"{where}: verification method not registered: {m.group(1)[:40]}")
        if status == "EXISTING" and "*Anchor" not in rest:
            errs.append(f"{where}: EXISTING without an anchor")
    for p in pages():
        for m in EXISTING_BARE.finditer(FENCE.sub("", p.read_text())):
            if "*Anchor" not in m.group(1):
                errs.append(f"{rel(p)}: EXISTING statement without an anchor: {m.group(1)[:50].strip()}")
    return errs


def check_links():
    errs = []
    for p in pages():
        text = FENCE.sub("", p.read_text())
        for m in LINK.finditer(text):
            target = m.group(1)
            if re.match(r"^(https?:|mailto:)", target):
                continue
            path, _, frag = target.partition("#")
            dest = p if not path else (p.parent / path).resolve()
            if not dest.exists():
                errs.append(f"{rel(p)}: broken link {target}")
            elif frag and dest.is_file() and dest.suffix == ".md":
                if frag not in anchors_of(dest):
                    errs.append(f"{rel(p)}: no heading #{frag} in {rel(dest)}")
    return errs


def check_refs():
    errs = []
    ids = {r[0] for r in collect()}
    adrs = {m.group(1) for f in (ROOT / "docs/adr").glob("ADR-*.md")
            for m in [re.match(r"ADR-(\d{4})", f.name)] if m}
    reg = ROOT / "docs/adr/open-decisions.md"
    ods = set(re.findall(r"^\|\s*\[OD-(\d{2})\]", reg.read_text(), re.M)) if reg.exists() else set()
    for p in pages():
        text = FENCE.sub("", p.read_text())
        for m in ID_MENTION.finditer(text):
            if m.group(1) not in ids:
                errs.append(f"{rel(p)}: {m.group(1)} is not defined anywhere")
        for m in ADR_MENTION.finditer(text):
            if m.group(1) not in adrs:
                errs.append(f"{rel(p)}: ADR-{m.group(1)} has no file")
        for m in OD_MENTION.finditer(text):
            if ods and m.group(1) not in ods:
                errs.append(f"{rel(p)}: OD-{m.group(1)} is not in the register")
    return sorted(set(errs))


def check_index():
    index = ROOT / "docs/README.md"
    if not index.exists():
        return ["docs/README.md is missing"]
    # a page counts as reachable if the index, or an index of its own directory, links to it
    linked = set()
    for idx in [index] + sorted((ROOT / "docs").rglob("README.md")):
        for m in LINK.finditer(FENCE.sub("", idx.read_text())):
            t = m.group(1).partition("#")[0]
            if t and not re.match(r"^(https?:|mailto:)", t):
                linked.add((idx.parent / t).resolve())
    errs = []
    for p in sorted((ROOT / "docs").rglob("*.md")):
        if p.name == "README.md":
            continue
        if p.resolve() not in linked:
            errs.append(f"{rel(p)}: not linked from docs/README.md or its directory index")
    return errs


def diagram_blocks():
    for p in pages():
        for i, m in enumerate(MERMAID.finditer(p.read_text()), 1):
            yield p, i, m.group(1)


def check_diagrams(render):
    errs = []
    for p, i, body in diagram_blocks():
        lines = [l for l in body.splitlines()
                 if l.strip() and not l.strip().startswith("%%")]
        first = lines[0].strip() if lines else ""
        if not first.startswith(DIAGRAMS):
            errs.append(f"{rel(p)}: diagram {i} starts with {first[:30]!r}")
    if render:
        mmdc = shutil.which("mmdc")
        if not mmdc:
            print("  SKIPPED  render: `mmdc` (@mermaid-js/mermaid-cli) not on PATH")
            return errs
        with tempfile.TemporaryDirectory() as td:
            for p, i, body in diagram_blocks():
                src, dst = Path(td) / "d.mmd", Path(td) / "d.svg"
                src.write_text(body)
                r = subprocess.run([mmdc, "-q", "-i", str(src), "-o", str(dst)],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    errs.append(f"{rel(p)}: diagram {i} does not render: "
                                f"{(r.stderr or r.stdout).strip().splitlines()[-1:]}")
    return errs


def stats():
    reqs = collect()
    by = collections.Counter(r[1] for r in reqs)
    print(f"Markdown files           {len(pages())}")
    print(f"Normative requirements   {len(reqs)}")
    for s in ("ACCEPTED", "EXISTING", "PROPOSED", "DEFERRED"):
        print(f"  {s:<22} {by.get(s, 0)}")
    print(f"ADRs                     {len(list((ROOT / 'docs/adr').glob('ADR-*.md')))}")
    print(f"Mermaid diagrams         {sum(1 for _ in diagram_blocks())}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--only", help="comma-separated subset of: ids,links,refs,index,diagrams")
    a = ap.parse_args()
    if a.stats:
        stats()
        return 0
    wanted = set(a.only.split(",")) if a.only else {"ids", "links", "refs", "index", "diagrams"}
    runners = {"ids": check_ids, "links": check_links, "refs": check_refs,
               "index": check_index, "diagrams": lambda: check_diagrams(a.render)}
    bad = 0
    for name in ("ids", "links", "refs", "index", "diagrams"):
        if name not in wanted:
            continue
        errs = runners[name]()
        print(f"{'FAIL' if errs else 'ok  '}  {name}" + (f"  ({len(errs)})" if errs else ""))
        for e in errs:
            print(f"      {e}")
        bad += len(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # the checker failing is not the spec failing
        print(f"check.py could not run: {e}", file=sys.stderr)
        sys.exit(2)
