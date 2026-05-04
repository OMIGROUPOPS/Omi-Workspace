#!/usr/bin/env python3
"""Fix async race condition causing double entries.

Root cause: entered_sides.add(ticker) happens AFTER the maker buy phase
(which includes a 3s sleep). During that sleep, WS messages trigger
a second execute_entry for the same ticker.

Fix: Add an _entry_in_progress set. Check it before calling execute_entry
in the WS handler, add ticker at the top of execute_entry, remove on
early return (rejection). entered_sides.add remains where it is for
permanent tracking after successful entry.
"""


def patch_file(path, label):
    with open(path, 'r') as f:
        content = f.read()
    original = content
    changes = 0

    # ===================================================================
    # 1. Add _entry_in_progress set to __init__
    # ===================================================================
    old_init = 'self.entered_sides: Set[str] = set()         # tickers we\'ve entered (never re-enter)'
    new_init = (
        'self.entered_sides: Set[str] = set()         # tickers we\'ve entered (never re-enter)\n'
        '        self._entry_in_progress: Set[str] = set()    # guard against async race during maker buy'
    )
    if old_init in content and '_entry_in_progress' not in content:
        content = content.replace(old_init, new_init, 1)
        changes += 1
        print(f'  [{label}] Added _entry_in_progress set to __init__')

    # ===================================================================
    # 2. Guard the WS handler entry call
    #    Old: if ticker not in self.entered_sides and self.check_entry(ticker):
    #             await self.execute_entry(ticker)
    #    New: if ticker not in self.entered_sides and ticker not in self._entry_in_progress and self.check_entry(ticker):
    #             await self.execute_entry(ticker)
    # ===================================================================
    old_guard = 'if ticker not in self.entered_sides and self.check_entry(ticker):\n            await self.execute_entry(ticker)'
    new_guard = 'if ticker not in self.entered_sides and ticker not in self._entry_in_progress and self.check_entry(ticker):\n            await self.execute_entry(ticker)'
    if old_guard in content:
        content = content.replace(old_guard, new_guard, 1)
        changes += 1
        print(f'  [{label}] Added _entry_in_progress guard in WS handler')

    # ===================================================================
    # 3. Add ticker to _entry_in_progress at top of execute_entry
    #    After: """Buy at ASK via taker order."""
    #    Add:   self._entry_in_progress.add(ticker)
    # ===================================================================
    old_entry_top = (
        '    async def execute_entry(self, ticker: str, is_reentry: bool = False, original_price: int = 0):\n'
        '        """Buy at ASK via taker order."""\n'
        '        book = self.books[ticker]'
    )
    new_entry_top = (
        '    async def execute_entry(self, ticker: str, is_reentry: bool = False, original_price: int = 0):\n'
        '        """Buy at ASK via taker order."""\n'
        '        # Guard against async race: prevent second entry during maker buy wait\n'
        '        if ticker in self._entry_in_progress and not is_reentry:\n'
        '            return\n'
        '        self._entry_in_progress.add(ticker)\n'
        '        try:\n'  # We'll remove from _entry_in_progress in finally
        '            return await self._execute_entry_inner(ticker, is_reentry, original_price)\n'
        '        finally:\n'
        '            self._entry_in_progress.discard(ticker)\n'
        '\n'
        '    async def _execute_entry_inner(self, ticker: str, is_reentry: bool = False, original_price: int = 0):\n'
        '        """Inner entry logic (wrapped by execute_entry for race guard)."""\n'
        '        book = self.books[ticker]'
    )
    if old_entry_top in content and '_execute_entry_inner' not in content:
        content = content.replace(old_entry_top, new_entry_top, 1)
        changes += 1
        print(f'  [{label}] Wrapped execute_entry with _entry_in_progress guard + try/finally')
    else:
        print(f'  [{label}] WARN: Could not find execute_entry top pattern')

    if content != original:
        with open(path, 'w') as f:
            f.write(content)
        print(f'  {label}: {changes} changes applied')
    else:
        print(f'  {label}: NO CHANGES')

    return changes


print('=== FIXING ASYNC RACE CONDITION ===')
c1 = patch_file('/root/Omi-Workspace/arb-executor/ncaamb_stb.py', 'ncaamb')
print()
c2 = patch_file('/root/Omi-Workspace/arb-executor/tennis_stb.py', 'tennis')
print(f'\nTOTAL: {c1 + c2} changes')
