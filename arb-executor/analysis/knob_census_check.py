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

if __name__ == "__main__":
    d = digest()
    counts = knob_count()
    if "--pin" in sys.argv or not PIN.exists():
        PIN.write_text(json.dumps({"sha256": d, "counts": counts}, indent=1))
        print("PINNED", d[:16], counts)
    else:
        old = json.loads(PIN.read_text())
        drift = old["sha256"] != d
        print("DRIFT" if drift else "CLEAN", "| pinned", old["sha256"][:16],
              "| now", d[:16], "|", counts)
        sys.exit(1 if drift else 0)
