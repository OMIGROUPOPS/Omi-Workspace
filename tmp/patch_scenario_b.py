#!/usr/bin/env python3
"""Deploy Scenario B: spike gate on MAKER entries only.

Changes per bot:
1. STB pre-check: remove spike gate (all STB entries pass)
2. Reentry path: remove spike gate (all reentries pass)
3. 92+ maker path: ADD spike gate (C-tier + spike>10c → reject)
"""

BOTS = {
    "ncaamb": "/root/Omi-Workspace/arb-executor/ncaamb_stb.py",
    "tennis": "/root/Omi-Workspace/arb-executor/tennis_stb.py",
}

for name, path in BOTS.items():
    with open(path) as f:
        content = f.read()
    original = content
    changes = 0

    # ──────────────────────────────────────────────────────────
    # FIX 1: STB pre-check — remove spike gate, log only
    # ──────────────────────────────────────────────────────────
    old_stb_gate = '''            if _pre_sc < 10 and _ds_m == "SPIKE":
                log(f"[REJECT_CTIER_SPIKE] {_side} pre-score={_pre_sc} chain={_chain_score}/3 "
                    f"spike={_spike_m:+d}c — C-tier spike rejected")
            else:
                if _pre_sc < 10:
                    log(f"[WARN_CTIER] {_side} pre-score={_pre_sc} chain={_chain_score}/3 "
                        f"type={_ds_m} spike={_spike_m:+d}c — C-tier dip/flat, entering")
                await self.execute_entry(ticker, bounce_chain=_chain_score, chain_detail=_chain_detail)'''

    new_stb_gate = '''            if _pre_sc < 10:
                log(f"[WARN_CTIER] {_side} pre-score={_pre_sc} chain={_chain_score}/3 "
                    f"type={_ds_m} spike={_spike_m:+d}c — C-tier STB, entering (Scenario B: no STB gate)")
            await self.execute_entry(ticker, bounce_chain=_chain_score, chain_detail=_chain_detail)'''

    if old_stb_gate in content:
        content = content.replace(old_stb_gate, new_stb_gate)
        changes += 1
        print(f"  [{name}] FIX 1: STB pre-check spike gate REMOVED (log only)")
    else:
        print(f"  [{name}] FIX 1: WARN — STB pre-check pattern not found")

    # ──────────────────────────────────────────────────────────
    # FIX 2: Reentry path — remove spike gate, log only
    # ──────────────────────────────────────────────────────────
    old_reentry_gate = '''                    if _re_score < 10 and _re_ds == "SPIKE":
                        log(f"[REJECT_CTIER_SPIKE] {side} score={_re_score} "
                            f"chain={_re_chain}/3 spike={_re_spike:+d}c — C-tier spike rejected")
                        self.entered_sides.add(ticker)
                        continue
                    elif _re_score < 10:
                        log(f"[WARN_CTIER] {side} score={_re_score} chain={_re_chain}/3 "
                            f"type={_re_ds} — C-tier but not spike, entering with caution")'''

    new_reentry_gate = '''                    if _re_score < 10:
                        log(f"[WARN_CTIER] {side} score={_re_score} chain={_re_chain}/3 "
                            f"type={_re_ds} spike={_re_spike:+d}c — C-tier reentry, entering (Scenario B: no STB gate)")'''

    if old_reentry_gate in content:
        content = content.replace(old_reentry_gate, new_reentry_gate)
        changes += 1
        print(f"  [{name}] FIX 2: Reentry spike gate REMOVED (log only)")
    else:
        print(f"  [{name}] FIX 2: WARN — reentry pattern not found")

    # ──────────────────────────────────────────────────────────
    # FIX 3: 92+ maker path — ADD spike gate
    # ──────────────────────────────────────────────────────────
    if name == "ncaamb":
        # ncaamb calls execute_entry_92plus after sustained check
        old_maker = '''                    if not skip_expiry:
                        if self._check_sustained_90(ticker, book92.best_ask):
                            await self.execute_entry_92plus(ticker)'''

        new_maker = '''                    if not skip_expiry:
                        if self._check_sustained_90(ticker, book92.best_ask):
                            # Scenario B: spike gate on MAKER entries only
                            _m_fsp = self.first_seen_prices.get(ticker, 0)
                            _m_spike = (book92.best_ask - _m_fsp) if _m_fsp > 0 else 0
                            _m_chain, _m_detail = self.compute_bounce_chain(ticker)
                            _m_score = _m_chain * 8
                            if _m_spike > 10: _m_score -= 8
                            elif _m_spike > 5: _m_score -= 5
                            elif _m_spike > 2: _m_score -= 2
                            _m_side = ticker.split("-")[-1]
                            if _m_score < 10 and _m_spike > 10:
                                log(f"[REJECT_MAKER_SPIKE] {_m_side} score={_m_score} "
                                    f"chain={_m_chain}/3 spike={_m_spike:+d}c fsp={_m_fsp}c "
                                    f"— C-tier maker spike>10c rejected")
                            else:
                                if _m_spike > 10:
                                    log(f"[MAKER_SPIKE_OK] {_m_side} score={_m_score} "
                                        f"chain={_m_chain}/3 spike={_m_spike:+d}c — tier OK, entering")
                                await self.execute_entry_92plus(ticker)'''

    else:  # tennis
        # tennis calls post_92c_maker_bid after sustained check
        old_maker = '''                                if not skip_expiry:
                                    await self.post_92c_maker_bid(ticker)'''

        new_maker = '''                                if not skip_expiry:
                                    # Scenario B: spike gate on MAKER entries only
                                    _m_fsp = self.first_seen_prices.get(ticker, 0)
                                    _m_spike = (book92.best_ask - _m_fsp) if _m_fsp > 0 and book92 else 0
                                    _m_chain, _m_detail = self.compute_bounce_chain(ticker)
                                    _m_score = _m_chain * 8
                                    if _m_spike > 10: _m_score -= 8
                                    elif _m_spike > 5: _m_score -= 5
                                    elif _m_spike > 2: _m_score -= 2
                                    _m_side = ticker.split("-")[-1]
                                    if _m_score < 10 and _m_spike > 10:
                                        log(f"[REJECT_MAKER_SPIKE] {_m_side} score={_m_score} "
                                            f"chain={_m_chain}/3 spike={_m_spike:+d}c fsp={_m_fsp}c "
                                            f"— C-tier maker spike>10c rejected")
                                    else:
                                        if _m_spike > 10:
                                            log(f"[MAKER_SPIKE_OK] {_m_side} score={_m_score} "
                                                f"chain={_m_chain}/3 spike={_m_spike:+d}c — tier OK, entering")
                                        await self.post_92c_maker_bid(ticker)'''

    if old_maker in content:
        content = content.replace(old_maker, new_maker)
        changes += 1
        print(f"  [{name}] FIX 3: 92+ maker spike gate ADDED")
    else:
        print(f"  [{name}] FIX 3: WARN — maker entry pattern not found")

    if content != original:
        with open(path, "w") as f:
            f.write(content)
        print(f"  [{name}] ✓ {changes} changes written")
    else:
        print(f"  [{name}] NO CHANGES")

print("\nDone. Scenario B deployed.")
