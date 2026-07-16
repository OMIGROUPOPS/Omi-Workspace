#!/usr/bin/env python3
"""[C-ONE-TRUTH v1, 07-16] truth/INDEX.json — THE ONE TRUTH, rebuilt at
every C50. Four sections: laws (doctrine_registry ABSORBED — id ->
file:line -> status -> date) · surfaces (path -> what it fits -> fitted
date -> consuming decision sites) · sites (every decision point -> the
laws + surfaces it must consult) · studies (archive pointer -> one-line
finding). Also REGENERATES the HANDOFF disk map between markers — the
map is never hand-maintained again. Prior art absorbed:
analysis/doctrine_registry_build.py (its scan IS the laws section)."""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
ARB = WS / "arb-executor"
OUT = WS / "truth" / "INDEX.json"

# ---------- laws: absorb the registry (run its builder, read it) ------
subprocess.run([sys.executable,
                str(ARB / "analysis/doctrine_registry_build.py")],
               capture_output=True, timeout=300)
reg = json.loads((WS / ".claude/doctrine_registry.json").read_text(
    encoding="utf-8"))
laws = reg.get("entries", [])

# ---------- surfaces: fitted files -> consumers ------------------------
SURFACE_DEFS = [
    (".claude/trendpath/ATLAS_V1.json",
     "path aims + contention per cat|side|band (the entry law)",
     ["_trendpath_atlas", "_selector_verdict"]),
    (".claude/takerreach/LAW.json",
     "reach law: P(fill) = 1-exp(-rate x residency) per cat|flow",
     ["_reach_law", "reach_law"]),
    (".claude/seqfloor_20260708/recut_cells.json",
     "sequential floor recut cells (dynamic S, cell-keyed aim)",
     ["recut_cells"]),
    (".claude/trendpath/LIBRARY_V1.json",
     "W1 cohort library (dip_freq, depth quantiles, gun-axis "
     "lawful_share -> the cash-window stamp)",
     ["LIBRARY_V1", "w1_cohort"]),
    (".claude/trendpath/ORIENT_V1.json",
     "oriented tells (SHADOW, own n>=300 clock)",
     ["ORIENT_V1", "_orient_read"]),
    (".claude/render/knob_citations.json",
     "knob provenance: FITTED/DECREED/NAKED (a citation is the only "
     "exit from NAKED)", ["knob_citations"]),
    ("arb-executor/config/deploy_v5_live.json",
     "THE live config (every armed knob)", ["CONFIG_PATH"]),
]
engine_src = (ARB / "live_v4.py").read_text(encoding="utf-8",
                                            errors="replace")
surfaces = []
for rel, fits, probes in SURFACE_DEFS:
    p = WS / rel
    consumers = sorted({pr for pr in probes if pr in engine_src})
    surfaces.append({
        "path": rel, "fits": fits,
        "exists": p.exists(),
        "fitted_date": (datetime.fromtimestamp(
            p.stat().st_mtime).strftime("%Y-%m-%d")
            if p.exists() else None),
        "consuming_probes_found_in_engine": consumers})

# ---------- sites: decision points -> laws + surfaces ------------------
SITES = [
    ("path_chokepoint",
     "every entry conception (aims, selector, pair law, floors, "
     "W1-preference, expression)",
     ["ATLAS_V1.json", "LAW.json", "deploy_v5_live.json"],
     ["trendpath_live_aim", "below_discovery_floor_refused",
      "corridor_refused_w1_preference"]),
    ("entry_dossier",
     "the ten-surface consultation on every placement/refusal",
     ["ATLAS_V1.json", "LAW.json", "LIBRARY_V1.json"],
     ["_entry_dossier", "cash_window"]),
    ("gun_sources",
     "the fused gun (te/schedule/tape_latch/divergence/fallback/"
     "self_fill/percat/tape_flow) + per-source grace",
     ["deploy_v5_live.json"],
     ["_gun_stamp", "tape_flow_gun_enabled", "tape_flow_grace_sec"]),
    ("completion_engine",
     "one-sided pair verdicts (hold/flatten/taker; cross cap; leashes)",
     ["deploy_v5_live.json"],
     ["_completion_execute", "cross_over_combined_cap"]),
    ("exit_machinery",
     "band exits (cell -> band_x), zero-tolerance W2 stamp",
     ["deploy_v5_live.json"],
     ["v4_exit_posted", "w2_fill_violation"]),
    ("audit_exchange_truth",
     "steady-cadence audit (no_exit, healer, settlement_pending)",
     [],
     ["post_boot_audit", "fill_book_skip", "settlement_pending"]),
]
sites = []
for name, what, needs, probes in SITES:
    found = sorted({pr for pr in probes if pr in engine_src})
    sites.append({"site": name, "what": what,
                  "required_surfaces": needs,
                  "probes": probes,
                  "probes_found_in_engine": found,
                  "wired_in_source": len(found) == len(probes)})

# ---------- studies: every dated artifact -> one-line finding ----------
studies = []
cl = WS / ".claude"
for p in sorted(cl.iterdir()):
    if not re.search(r"_?20\d{6}", p.name):
        continue
    finding = "finding line pending"
    try:
        if p.is_dir():
            mds = sorted(p.glob("*.md"),
                         key=lambda x: -x.stat().st_size)
            if mds:
                for ln in open(mds[0], encoding="utf-8",
                               errors="replace"):
                    ln = ln.strip()
                    if ln.startswith("#"):
                        finding = ln.lstrip("# ").strip()[:180]
                        break
        elif p.suffix == ".md":
            for ln in open(p, encoding="utf-8", errors="replace"):
                ln = ln.strip()
                if ln.startswith("#"):
                    finding = ln.lstrip("# ").strip()[:180]
                    break
        else:
            continue
    except OSError:
        continue
    studies.append({"archive": "truth/archive/" + p.name,
                    "source": ".claude/" + p.name,
                    "finding": finding})

index = {"built": datetime.now().strftime("%Y-%m-%d %H:%M"),
         "law": "C-ONE-TRUTH v1 (07-16): outside this root = doesn't "
                "exist; rebuilt every C50; both consumers enforced "
                "(engine boot wiring + seat session-zero); the gate "
                "refuses unregistered laws/surfaces/studies",
         "laws_n": len(laws), "laws": laws,
         "surfaces": surfaces, "sites": sites,
         "studies_n": len(studies), "studies": studies}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(index, indent=1), encoding="utf-8")

# ---------- regenerate the HANDOFF disk map (never hand-maintained) ----
hp = WS / ".claude/HANDOFF_FABLE.md"
hs = hp.read_text(encoding="utf-8")
MAP = """<!--TRUTH-MAP-START (generated by truth/build_index.py — never hand-edit)-->
## THE DISK MAP — generated from truth/INDEX.json (C-ONE-TRUTH v1)
**SESSION-ZERO READ: `truth/INDEX.json` FIRST** — laws (%d) · surfaces (%d) · sites (%d) · studies (%d). Everything below is a pointer INTO the index's members:
1. .claude/BOARD.md (truth/BOARD.md) — the standing queue.
2. arb-executor/docs/LIVING_VAULT.md (truth/VAULT.md) — the ledger; front page = entry doctrine + laws.
3. arb-executor/docs/THE_DAILY_STANDARD.md (truth/STANDARD.md) — the OS's day, census-enforced.
4. docs/LESSONS.md (truth/LESSONS.md) — A-G principles.
5. .claude/rulings/ (truth/rulings/) — verbatim law.
6. Fitted surfaces: see INDEX.surfaces (paths + consumers).
7. Dated studies: truth/archive/ — one-line finding each in INDEX.studies.
LIVE STATE: .claude/live_20260705/LIVE_STATUS.md · TODAY SHEET: .claude/today_sheet/LATEST.md · FUND: state/fund_equity.db (tracker 8788).
<!--TRUTH-MAP-END-->""" % (len(laws), len(surfaces), len(sites),
                           len(studies))
if "<!--TRUTH-MAP-START" in hs:
    hs = re.sub(r"<!--TRUTH-MAP-START.*?<!--TRUTH-MAP-END-->", MAP, hs,
                flags=re.S)
else:
    hs = hs.replace("## THE DISK MAP — read order, every session, law:",
                    MAP + "\n\n## THE OLD HAND-MAINTAINED MAP "
                    "(superseded by the generated map above; kept one "
                    "cycle for diff):", 1)
hp.write_text(hs, encoding="utf-8")
print("INDEX built: laws %d | surfaces %d | sites %d (wired %d) | "
      "studies %d -> %s" % (len(laws), len(surfaces), len(sites),
                            sum(1 for s in sites if s["wired_in_source"]),
                            len(studies), OUT))
