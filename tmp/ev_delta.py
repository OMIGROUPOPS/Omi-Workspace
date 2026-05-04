"""Task 4: Deploy V3 EV delta calculation."""
DAYS = 33

gate_extend = {
    'ATP_CHALL_leader_55-59':    (84, 0.650, -0.118),
    'ATP_CHALL_leader_60-64':    (70, 0.276, 0.007),
    'ATP_CHALL_leader_80-84':    (33, 1.064, 0.829),
    'ATP_CHALL_underdog_20-24':  (56, 0.440, 0.276),
    'ATP_CHALL_underdog_40-44':  (82, 0.210, -0.048),
    'ATP_MAIN_leader_55-59':     (36, 0.601, 0.412),
    'ATP_MAIN_leader_70-74':     (28, 1.053, 0.833),
}

disables = {
    'ATP_MAIN_leader_60-64':     (44, -0.048),
    'ATP_MAIN_underdog_20-24':   (16, -0.340),
    'ATP_MAIN_underdog_25-29':   (19, -0.029),
    'WTA_MAIN_leader_55-59':     (28, -0.173),
}

total_delta = 0

print('=== DEPLOY V3 EV DELTA ===')
print()
print('Gate extensions (EV_A replaces EV_B):')
for cn, (n, ev_a, ev_b) in gate_extend.items():
    delta_per = ev_a - ev_b
    mpd = n / DAYS
    daily = mpd * delta_per
    total_delta += daily
    print('  %-40s delta/match=$%+.3f x %.1f/day = $%+.3f/day ($%+.1f/wk)' % (cn, delta_per, mpd, daily, daily*7))

print()
print('New disables (remove negative EV):')
for cn, (n, ev_b) in disables.items():
    delta_per = -ev_b
    mpd = n / DAYS
    daily = mpd * delta_per
    total_delta += daily
    print('  %-40s remove $%+.3f/match x %.1f/day = $%+.3f/day ($%+.1f/wk)' % (cn, ev_b, mpd, daily, daily*7))

print()
print('TOTAL DAILY EV DELTA: $%+.3f/day' % total_delta)
print('TOTAL WEEKLY EV DELTA: $%+.1f/week' % (total_delta * 7))
print('At full 80/40 sizing (8x): $%+.0f/week' % (total_delta * 7 * 8))
