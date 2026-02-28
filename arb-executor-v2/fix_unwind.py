import json

with open('trades.json') as f:
    trades = json.load(f)

for t in trades:
    if t.get('sport') != 'UFC' and 'UFC' not in t.get('game_id', ''):
        continue
    
    # Skip if no unwind
    if not t.get('unwind_close_action'):
        continue
    
    team = t.get('team', '?')
    opp = t.get('opponent', '?')
    team_full = t.get('team_full_name') or team
    opp_full = t.get('opponent_full_name') or opp
    direction = t.get('direction', '')
    pbs = t.get('pm_is_buy_short', False)
    qty = t.get('contracts_filled', 0)
    arb_net_cpc = t.get('arb_net_cents_per_contract', 0)
    
    # What was the ORIGINAL PM buy?
    if direction == 'BUY_K_SELL_PM':
        if pbs:
            # Originally bought opponent YES on PM, unwind exits that and buys team YES
            orig_fighter = opp_full
            new_fighter = team_full
        else:
            orig_fighter = team_full
            new_fighter = opp_full
    else:  # BUY_PM_SELL_K
        if pbs:
            orig_fighter = opp_full
            new_fighter = team_full
        else:
            # Originally bought team YES on PM, unwind exits that and buys opponent YES
            orig_fighter = team_full
            new_fighter = opp_full
    
    t['unwind_close_action'] = "Exited YES {} {}x on PM".format(orig_fighter, qty)
    t['unwind_reopen_action'] = "BUY YES {} {}x on PM ({}c/ct net)".format(new_fighter, qty, arb_net_cpc)

with open('trades.json', 'w') as f:
    json.dump(trades, f, indent=2)

print("Updated unwind strings:")
for t in trades:
    if t.get('sport') == 'UFC' or 'UFC' in t.get('game_id', ''):
        close = t.get('unwind_close_action', 'N/A')
        reopen = t.get('unwind_reopen_action', 'N/A')
        print("  {}/{}: {} -> {}".format(t['team'], t['opponent'], close, reopen))
