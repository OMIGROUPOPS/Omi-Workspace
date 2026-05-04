#!/usr/bin/env python3
"""Fix position reads: position -> position_fp (Kalshi API migration).

position_fp is a string like "50.00", position is now always 0.
"""


def patch_file(path, label):
    with open(path, 'r') as f:
        content = f.read()
    original = content
    changes = 0

    # Helper function to safely read position from API response
    helper = '''
def _read_position(p):
    """Read position count from API response (handles both old and new fields)."""
    # New API: position_fp is a string like "50.00"
    fp = p.get("position_fp", None)
    if fp is not None:
        try:
            return int(float(fp))
        except (ValueError, TypeError):
            pass
    # Old API fallback: position is an int
    return p.get("position", 0)

'''
    # Insert after _parse_price function
    if '_read_position' not in content:
        marker = 'def _parse_price(val):'
        if marker in content:
            # Find end of _parse_price function (next blank line after it)
            idx = content.find(marker)
            # Find the "return 0" at the end of _parse_price
            end_idx = content.find('\n\n', idx + len(marker))
            if end_idx > 0:
                content = content[:end_idx] + '\n' + helper + content[end_idx:]
                changes += 1
                print('  [%s] Added _read_position helper' % label)
        else:
            print('  [%s] WARN: _parse_price not found, inserting before class' % label)

    # --- Fix 1: Anti-stack in execute_entry_92plus ---
    # p.get("position", 0) > 0
    old1 = 'existing = [p for p in pos_check.get("market_positions", []) if p.get("position", 0) > 0]'
    new1 = 'existing = [p for p in pos_check.get("market_positions", []) if _read_position(p) > 0]'
    c = content.count(old1)
    if c > 0:
        content = content.replace(old1, new1)
        changes += c
        print('  [%s] Fixed anti-stack position read (%d occurrences)' % (label, c))

    # existing[0].get('position',0)
    old2 = "existing[0].get('position',0)"
    new2 = "_read_position(existing[0])"
    c = content.count(old2)
    if c > 0:
        content = content.replace(old2, new2)
        changes += c
        print('  [%s] Fixed anti-stack position display (%d occurrences)' % (label, c))

    # --- Fix 2: Anti-stack in execute_entry ---
    old3 = 'existing_pos = [p for p in pos_check.get("market_positions", []) if p.get("position", 0) > 0]'
    new3 = 'existing_pos = [p for p in pos_check.get("market_positions", []) if _read_position(p) > 0]'
    c = content.count(old3)
    if c > 0:
        content = content.replace(old3, new3)
        changes += c
        print('  [%s] Fixed execute_entry anti-stack position read (%d)' % (label, c))

    old4 = 'held = existing_pos[0].get("position", 0)'
    new4 = 'held = _read_position(existing_pos[0])'
    c = content.count(old4)
    if c > 0:
        content = content.replace(old4, new4)
        changes += c
        print('  [%s] Fixed execute_entry held display (%d)' % (label, c))

    # --- Fix 3: reconcile_existing_positions ---
    old5 = 'position = p.get("position", 0)'
    new5 = 'position = _read_position(p)'
    c = content.count(old5)
    if c > 0:
        content = content.replace(old5, new5)
        changes += c
        print('  [%s] Fixed reconcile position read (%d)' % (label, c))

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print('  %s: %d changes applied' % (label, changes))
    else:
        print('  %s: NO CHANGES' % label)

    return changes


print('=== FIXING position -> position_fp ===')
c1 = patch_file('/root/Omi-Workspace/arb-executor/ncaamb_stb.py', 'ncaamb')
print()
c2 = patch_file('/root/Omi-Workspace/arb-executor/tennis_stb.py', 'tennis')
print('\nTOTAL: %d changes' % (c1 + c2))
