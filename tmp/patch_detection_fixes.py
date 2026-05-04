#!/usr/bin/env python3
"""Deploy two detection fixes to both bots:
1. STABLE sparse data fix: treat empty baseline window as stable if history >= 10
2. WALL threshold: ratio > 1.0 → ratio > 0.7
"""

FIXES = {
    "ncaamb": "/root/Omi-Workspace/arb-executor/ncaamb_stb.py",
    "tennis": "/root/Omi-Workspace/arb-executor/tennis_stb.py",
}

print("=" * 70)
print("DETECTION FIXES — stable sparse data + wall threshold")
print("=" * 70)

for name, path in FIXES.items():
    with open(path) as f:
        content = f.read()
    original = content
    changes = 0

    # FIX 1: STABLE sparse data
    # Replace the else: stable = False with elif/else
    old_stable = """        if len(baseline_ticks) >= 3:
            import statistics as _st
            baseline_std = _st.stdev(baseline_ticks)
            stable = baseline_std < 1.5
        else:
            stable = False"""

    new_stable = """        if len(baseline_ticks) >= 3:
            import statistics as _st
            baseline_std = _st.stdev(baseline_ticks)
            stable = baseline_std < 1.5
        elif len(history) >= 10:
            # Bid was so stable in the 5-3min window that it didn't change.
            # Few/no ticks = no movement = the definition of stable.
            stable = True
        else:
            stable = False  # truly insufficient data (new ticker)"""

    if old_stable in content:
        content = content.replace(old_stable, new_stable)
        changes += 1
        print(f"  [{name}] FIX 1: stable sparse data fix applied")
    else:
        print(f"  [{name}] FIX 1: WARN — marker not found")

    # FIX 2: WALL threshold 1.0 → 0.7
    old_wall = "            wall = depth_ratio > 1.0"
    new_wall = "            wall = depth_ratio > 0.7"

    count = content.count(old_wall)
    if count > 0:
        content = content.replace(old_wall, new_wall)
        changes += count
        print(f"  [{name}] FIX 2: wall threshold 1.0 → 0.7 ({count} occurrences)")
    else:
        print(f"  [{name}] FIX 2: WARN — marker not found")

    if content != original:
        with open(path, "w") as f:
            f.write(content)
        print(f"  [{name}] {changes} changes written")
    else:
        print(f"  [{name}] NO CHANGES")

print("\nDone.")
