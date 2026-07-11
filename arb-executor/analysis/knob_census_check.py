#!/usr/bin/env python3
"""[C-KNOB-CANON v1 Part 4] census regeneration + CODE-DRIFT hash.
The census (KNOB_CENSUS.md) is pinned to the source it inventoried: this
stores sha256(live_v4.py + deploy_v5_live.json) beside the census and
compares on every run; the viewer flags DRIFT when they differ -- the map
cannot silently rot. Also counts the live knob population mechanically
(config keys + self.config.get sites) so the census totals are checkable."""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = [ROOT / "live_v4.py", ROOT / "config/deploy_v5_live.json"]
PIN = ROOT.parent / ".claude/render/census_source_hash.json"

def digest():
    h = hashlib.sha256()
    for p in SRC:
        h.update(p.read_bytes())
    return h.hexdigest()

def knob_count():
    src = (ROOT / "live_v4.py").read_text(encoding="utf-8", errors="replace")
    cfg = json.loads((ROOT / "config/deploy_v5_live.json").read_text())
    code_knobs = set(re.findall(r"self\.config\.get\(\s*[\"']([a-z0-9_]+)[\"']", src))
    return {"config_keys": len(cfg), "code_config_gets": len(code_knobs),
            "union": len(code_knobs | set(cfg))}

def emit_census():
    """[C-SYSTEM-PAGE] build-time census artifact: every knob (config keys +
    code config.get sites), classification COMPUTED from knob_citations.json
    -- new/uncited knobs land NAKED until a person cites a source (the
    spec's red line: no auto-classifier, full stop)."""
    src = (ROOT / "live_v4.py").read_text(encoding="utf-8", errors="replace")
    cfg = json.loads((ROOT / "config/deploy_v5_live.json").read_text())
    code_knobs = set(re.findall(r"self\.config\.get\(\s*[\"']([a-z0-9_]+)[\"']", src))
    try:
        cites = json.loads((ROOT.parent / ".claude/render/knob_citations.json")
                           .read_text(encoding="utf-8"))
    except OSError:
        cites = {}
    rows = []
    for k in sorted(code_knobs | set(cfg)):
        c = cites.get(k)
        rows.append({"knob": k, "in_config": k in cfg,
                     "config_value": cfg.get(k),
                     "class": (c[0] if c else "NAKED"),
                     "citation": (c[1] if c else "UNCITED -- lands NAKED until a person cites a source"),
                     "step": (c[2] if c else "?")})
    art = {"generated_hash": digest(), "counts": knob_count(),
           "by_class": {cl: sum(1 for r in rows if r["class"] == cl)
                        for cl in ("FITTED", "DECREED", "NAKED")},
           "rows": rows}
    op = ROOT.parent / ".claude/render/knob_census_artifact.json"
    op.write_text(json.dumps(art, indent=1), encoding="utf-8")
    print("CENSUS_ARTIFACT", art["by_class"])
    return art


if __name__ == "__main__":
    d = digest()
    counts = knob_count()
    if "--emit" in sys.argv:
        emit_census()
        sys.exit(0)
    if "--pin" in sys.argv or not PIN.exists():
        PIN.write_text(json.dumps({"sha256": d, "counts": counts}, indent=1))
        print("PINNED", d[:16], counts)
    else:
        old = json.loads(PIN.read_text())
        drift = old["sha256"] != d
        print("DRIFT" if drift else "CLEAN", "| pinned", old["sha256"][:16],
              "| now", d[:16], "|", counts)
        sys.exit(1 if drift else 0)
