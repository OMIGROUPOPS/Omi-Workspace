#!/usr/bin/env python3
"""[C-ONE-RECORD Part 3, 07-15] doctrine_registry.json — machine-built
from the stack (LIVING_VAULT front page + ledger entries + class ledger +
rulings dir): term -> law -> file:line -> status -> date. Rebuilt at
every C50 (and nightly for safety). The seat-preflight receipt: no
doctrine-touching output without the registry visible."""
import json, re, glob
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT.parent
OUT = WS / ".claude/doctrine_registry.json"
entries = []

def scan(fp, kinds):
    try:
        lines = open(fp, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return
    rel = str(Path(fp).relative_to(WS)).replace("\\", "/")
    for i, ln in enumerate(lines, 1):
        for pat, kind in kinds:
            m = re.match(pat, ln)
            if m:
                term = re.sub(r"[*#⛔>]+", "", ln).strip()[:160]
                status = ("RETIRED" if re.search(
                    r"RETIRE|SUPERSED|FROZEN tombstone|GRAVE|STRUCK",
                    ln, re.I) else
                          "AMENDED" if "AMEND" in ln.upper() else "RULING")
                dm = re.search(r"(2026-\d\d-\d\d|\d\d-\d\d)", ln)
                entries.append({"term": term, "kind": kind,
                                "file": rel, "line": i,
                                "status": status,
                                "date": dm.group(1) if dm else None})
                break

scan(ROOT / "docs/LIVING_VAULT.md",
     [(r"^### ", "ledger_entry"), (r"^## ", "front_page_section"),
      (r"^⛔", "standing_order"),
      (r"^\*\*[A-Z§T].*(LAW|DOCTRINE|INVARIANT|FRAME|CLAUSE|MANDATE|"
       r"DEFINITIONS|RULING)", "law")])
scan(ROOT / "docs/CLASS_LEDGER.md", [(r"^> ", "class")])
for f in glob.glob(str(WS / ".claude/rulings/*.md")):
    scan(f, [(r"^# ", "ruling")])
scan(ROOT / "docs/OPERATOR_CONSTRAINTS.md", [(r"^\d+\.", "constraint"),
                                             (r"^- ", "constraint")])

reg = {"built": datetime.now().strftime("%Y-%m-%d %H:%M"),
       "law": "C-ONE-RECORD (operator mandate): the consolidated record "
              "IS the operation; nothing speaks or trades from memory "
              "when the disk disagrees. Seat preflight: no "
              "doctrine-touching output without this registry's receipt.",
       "n": len(entries), "entries": entries}
OUT.write_text(json.dumps(reg, indent=1), encoding="utf-8")
print("doctrine_registry.json: %d entries" % len(entries))
