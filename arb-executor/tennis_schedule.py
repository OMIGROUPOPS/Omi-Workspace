#!/usr/bin/env python3
"""
Tennis Schedule Fetcher — TennisExplorer (primary) + ESPN (backup)
=================================================================
Returns match start times and live status for ATP/WTA Main + Challengers.
Keyed by 6-char pair code (first 3 of each player's last name) for Kalshi matching.
"""

import json
import re
import time
import urllib.request
from datetime import datetime, timezone, timedelta


def _normalize_last(full_name):
    """'Orlov V.' -> 'ORLOV', 'Villalon N.' -> 'VILLALON', 'Tiafoe F.' -> 'TIAFOE'"""
    if not full_name or full_name in ("?", "TBD"):
        return ""
    name = full_name.strip()
    # TennisExplorer format: "LastName F." — last name is the first word
    # ESPN format: "Frances Tiafoe" — last name is the last word
    parts = name.split()
    if not parts:
        return ""
    # If last part is a single letter + period (initial), first part is the last name
    if len(parts) >= 2 and len(parts[-1]) <= 2:
        last = parts[0]  # TennisExplorer: "Orlov V." -> "Orlov"
    else:
        last = parts[-1]  # ESPN: "Frances Tiafoe" -> "Tiafoe"
    return re.sub(r"[^A-Z]", "", last.upper())


def _make_keys(name1, name2):
    """Generate all possible Kalshi-style pair codes for matching."""
    n1 = _normalize_last(name1)
    n2 = _normalize_last(name2)
    if not n1 or not n2:
        return []
    return [
        n1[:3] + n2[:3],  # ORLVIL
        n2[:3] + n1[:3],  # VILORL
    ]


def _parse_cet_to_utc(time_str, ref_date=None):
    """Parse 'HH:MM' CET (GMT+1) time string into UTC ISO timestamp.
    TennisExplorer returns all times in CET (Berlin/Prague/Vienna).
    Before last Sunday of March and after last Sunday of October: CET = UTC+1.
    During summer (last Sun Mar to last Sun Oct): CEST = UTC+2.
    Uses today's date if ref_date not provided."""
    if not time_str or not re.match(r"\d{2}:\d{2}", time_str):
        return ""
    h, m = int(time_str[:2]), int(time_str[3:5])
    if ref_date:
        dt = ref_date.replace(hour=h, minute=m, second=0, microsecond=0)
    else:
        dt = datetime.now(timezone.utc).replace(hour=h, minute=m, second=0, microsecond=0)
    # Determine CET vs CEST: last Sunday of March to last Sunday of October = CEST (UTC+2)
    year = dt.year
    # Last Sunday of March
    mar31 = datetime(year, 3, 31, tzinfo=timezone.utc)
    spring_switch = mar31 - timedelta(days=(mar31.weekday() + 1) % 7)
    # Last Sunday of October
    oct31 = datetime(year, 10, 31, tzinfo=timezone.utc)
    fall_switch = oct31 - timedelta(days=(oct31.weekday() + 1) % 7)
    if spring_switch <= dt.replace(tzinfo=timezone.utc) < fall_switch:
        offset_hours = 2  # CEST
    else:
        offset_hours = 1  # CET
    dt_utc = dt - timedelta(hours=offset_hours)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


# ══════════════════════════════════════════════════════════════════
# TennisExplorer — primary source (covers ALL categories)
# ══════════════════════════════════════════════════════════════════
def _fetch_tennisexplorer(year, month, day):
    """Fetch and parse TennisExplorer for ATP + WTA singles."""
    schedule = {}
    ref_date = datetime(year, month, day, tzinfo=timezone.utc)

    for tour, league in [("atp-single", "ATP"), ("wta-single", "WTA")]:
        url = ("https://www.tennisexplorer.com/matches/?type=%s&year=%d&month=%02d&day=%02d"
               % (tour, year, month, day))
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            })
            html = urllib.request.urlopen(req, timeout=20).read().decode(errors="replace")
        except Exception as e:
            print("[SCHED_ERR] TennisExplorer %s: %s" % (tour, e))
            continue

        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
        current_tourney = ""
        i = 0
        while i < len(rows):
            row = rows[i]

            # Tournament header
            tm = re.search(r't-name"[^>]*colspan="2"[^>]*>.*?<a[^>]*>(.*?)</a>', row, re.DOTALL)
            if tm:
                current_tourney = re.sub(r"<[^>]+>", "", tm.group(1)).strip()
                # Clean &nbsp; artifacts
                current_tourney = current_tourney.replace("\xa0", " ").replace("&nbsp;", "").strip()
                i += 1
                continue

            # Match row with time
            time_m = re.search(r'first time"[^>]*>(\d{2}:\d{2})', row)
            if time_m:
                match_time = time_m.group(1)
                p1_m = re.search(r't-name"><a[^>]*>([^<]+)</a>', row)
                r1_m = re.search(r'class="result">(\d*)', row)
                p1 = p1_m.group(1).strip() if p1_m else ""
                r1 = r1_m.group(1) if r1_m else ""

                p2 = ""
                r2 = ""
                if i + 1 < len(rows):
                    row2 = rows[i + 1]
                    p2_m = re.search(r't-name"><a[^>]*>([^<]+)</a>', row2)
                    r2_m = re.search(r'class="result">(\d*)', row2)
                    p2 = p2_m.group(1).strip() if p2_m else ""
                    r2 = r2_m.group(1) if r2_m else ""
                    i += 1

                # Status
                if r1 and r2 and r1.isdigit() and r2.isdigit():
                    total_sets = int(r1) + int(r2)
                    if total_sets >= 2:
                        status = "completed"
                    else:
                        status = "live"
                elif r1 or r2:
                    status = "live"
                else:
                    status = "scheduled"

                # Category
                is_chall = "challenger" in current_tourney.lower()
                if league == "ATP":
                    cat = "ATP_CHALL" if is_chall else "ATP_MAIN"
                else:
                    cat = "WTA_CHALL" if is_chall else "WTA_MAIN"

                start_iso = _parse_cet_to_utc(match_time, ref_date)

                entry = {
                    "start_time": start_iso,
                    "status": status,
                    "p1": p1,
                    "p2": p2,
                    "tournament": current_tourney,
                    "category": cat,
                    "source": "tennisexplorer",
                }

                for key in _make_keys(p1, p2):
                    if key not in schedule:  # don't overwrite
                        schedule[key] = entry

            i += 1

    return schedule


# ══════════════════════════════════════════════════════════════════
# ESPN — backup for Main draws (higher time accuracy for big events)
# ══════════════════════════════════════════════════════════════════
def _fetch_espn():
    """Fetch ESPN ATP + WTA scoreboard. Covers Main draws only."""
    schedule = {}

    for league_slug in ["atp", "wta"]:
        url = "https://site.api.espn.com/apis/site/v2/sports/tennis/%s/scoreboard" % league_slug
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        except Exception as e:
            print("[SCHED_ERR] ESPN %s: %s" % (league_slug, e))
            continue

        for event in data.get("events", []):
            for grouping in event.get("groupings", []):
                gname = grouping.get("grouping", {}).get("displayName", "")
                if "Singles" not in gname:
                    continue
                for comp in grouping.get("competitions", []):
                    status_obj = comp.get("status", {}).get("type", {})
                    state = status_obj.get("state", "")
                    competitors = comp.get("competitors", [])
                    if len(competitors) < 2:
                        continue
                    p1 = competitors[0].get("athlete", {}).get("displayName", "")
                    p2 = competitors[1].get("athlete", {}).get("displayName", "")
                    if not p1 or not p2 or "TBD" in p1 or "TBD" in p2:
                        continue

                    start_str = comp.get("startDate", comp.get("date", ""))

                    # Map ESPN state to our status
                    if state == "post":
                        status = "completed"
                    elif state == "in":
                        status = "live"
                    else:
                        status = "scheduled"

                    entry = {
                        "start_time": start_str,
                        "status": status,
                        "p1": p1,
                        "p2": p2,
                        "tournament": event.get("name", ""),
                        "category": "ATP_MAIN" if league_slug == "atp" else "WTA_MAIN",
                        "source": "espn",
                    }

                    for key in _make_keys(p1, p2):
                        schedule[key] = entry  # ESPN overwrites TE for main draws

    return schedule


# ══════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════
def get_match_schedule(year=None, month=None, day=None):
    """Fetch today's full tennis schedule.
    Returns { pair_code: {start_time, status, p1, p2, tournament, category, source} }
    TennisExplorer is primary (all categories). ESPN overlays for Main draws.
    """
    now = datetime.now(timezone.utc)
    if year is None:
        year, month, day = now.year, now.month, now.day

    # Primary: TennisExplorer (all categories including Challengers)
    schedule = _fetch_tennisexplorer(year, month, day)
    te_count = len(set(id(v) for v in schedule.values()))

    # Backup/overlay: ESPN (Main draws only, higher accuracy)
    espn = _fetch_espn()
    espn_overlay = 0
    for key, entry in espn.items():
        # Detect ESPN midnight placeholder (00:00 ET = "after prev match")
        espn_start = entry.get("start_time", "")
        is_midnight = False
        if espn_start:
            try:
                _et = timezone(timedelta(hours=-4))
                _parsed = datetime.fromisoformat(espn_start.replace("Z", "+00:00"))
                _local = _parsed.astimezone(_et)
                is_midnight = (_local.hour == 0 and _local.minute == 0)
            except Exception:
                pass
        if is_midnight:
            if key in schedule:
                # Keep TE entry — ESPN midnight is unreliable
                print("[ESPN_PLACEHOLDER] %s — ESPN 00:00, keeping TE schedule" % key)
            else:
                # No TE entry either — add ESPN but flag it
                entry["espn_midnight"] = True
                schedule[key] = entry
                print("[ESPN_PLACEHOLDER] %s — ESPN 00:00, no TE fallback" % key)
            continue
        if key in schedule:
            # ESPN overwrites TennisExplorer for Main draws (better time accuracy)
            schedule[key] = entry
            espn_overlay += 1
        else:
            schedule[key] = entry

    espn_new = len(set(id(v) for v in espn.values())) - espn_overlay
    print("[SCHEDULE] %d matches from TennisExplorer, %d ESPN overlays, %d ESPN-only" % (
        te_count, espn_overlay, espn_new))

    return schedule


def match_kalshi_event(kalshi_event_ticker, schedule, kalshi_player_names=None):
    """Match a Kalshi event ticker to the schedule.
    KXATPCHALLENGERMATCH-26MAR24ORLVIL -> looks up 'ORLVIL' in schedule.

    Matching strategy:
      1. Direct 6-char pair code lookup (fast path)
      2. Fuzzy fallback: if kalshi_player_names provided, check if any TE
         player surname is a substring of either Kalshi full player name.
         This handles double-barreled names (Silva vs Ferreira Silva).

    kalshi_player_names: list of full player names from V1 API, e.g.
      ["Frederico Ferreira Silva", "Sascha Gueymard Wayenburg"]

    Returns the schedule entry or None.
    """
    parts = kalshi_event_ticker.split("-")
    if len(parts) < 2:
        return None
    raw = parts[-1]
    m = re.match(r"\d{2}[A-Z]{3}\d{2}(.+)", raw)
    pair_code = m.group(1) if m else raw

    # 1. Direct lookup
    result = schedule.get(pair_code)
    if result:
        return result

    # 2. Fuzzy fallback using full player names
    if not kalshi_player_names:
        return None

    kalshi_names_upper = [n.upper() for n in kalshi_player_names if n]

    # Build unique entries to search (deduplicate by p1+p2)
    seen = set()
    candidates = []
    for key, entry in schedule.items():
        sig = (entry.get("p1", ""), entry.get("p2", ""))
        if sig in seen:
            continue
        seen.add(sig)
        candidates.append(entry)

    for entry in candidates:
        te_p1 = _normalize_last(entry.get("p1", ""))
        te_p2 = _normalize_last(entry.get("p2", ""))
        if not te_p1 or not te_p2:
            continue

        # Check if BOTH TE surnames appear as substrings in the Kalshi names
        te_p1_found = any(te_p1 in kn for kn in kalshi_names_upper)
        te_p2_found = any(te_p2 in kn for kn in kalshi_names_upper)

        if te_p1_found and te_p2_found:
            return entry

    return None


# ══════════════════════════════════════════════════════════════════
# Test
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Fetching schedule...\n")
    schedule = get_match_schedule()

    # Deduplicate
    seen = set()
    unique = []
    for key, entry in schedule.items():
        sig = (entry["p1"], entry["p2"])
        if sig in seen:
            continue
        seen.add(sig)
        unique.append((key, entry))

    unique.sort(key=lambda x: x[1]["start_time"])

    print("\n%-8s %-22s %-22s %-10s %-10s %-8s %s" % (
        "Key", "Player 1", "Player 2", "Start(UTC)", "Status", "Source", "Tournament"))
    print("-" * 120)

    for key, e in unique:
        if e["status"] == "completed":
            continue
        start_short = e["start_time"][11:16] if len(e["start_time"]) > 11 else e["start_time"]
        print("%-8s %-22s %-22s %-10s %-10s %-8s %s" % (
            key[:8], e["p1"][:22], e["p2"][:22], start_short,
            e["status"], e["source"][:8], e["tournament"][:30]))

    # Test Kalshi matching
    print("\n=== KALSHI MATCHING TEST ===")
    test_tickers = [
        "KXATPMATCH-26MAR24SINMIC",
        "KXATPMATCH-26MAR24ETCPAU",
        "KXATPMATCH-26MAR24HUMCER",
        "KXATPCHALLENGERMATCH-26MAR24VARMIG",
        "KXATPCHALLENGERMATCH-26MAR24YUNWIS",
        "KXATPCHALLENGERMATCH-26MAR24PAVWAL",
        "KXATPCHALLENGERMATCH-26MAR24FICVAL",
        "KXWTAMATCH-26MAR24BENGAU",
    ]

    for tk in test_tickers:
        result = match_kalshi_event(tk, schedule)
        if result:
            # Parse start time to show gate window
            try:
                st = datetime.fromisoformat(result["start_time"].replace("Z", "+00:00"))
                gate_open = (st - timedelta(minutes=30)).strftime("%H:%M")
                gate_close = (st + timedelta(minutes=30)).strftime("%H:%M")
                start_et = (st - timedelta(hours=4)).strftime("%I:%M %p")
            except:
                gate_open = gate_close = start_et = "?"
            print("  %-45s -> %s vs %s | start=%s ET | gate=%s-%s UTC | %s (%s)" % (
                tk, result["p1"][:15], result["p2"][:15], start_et,
                gate_open, gate_close, result["status"], result["source"]))
        else:
            print("  %-45s -> NO MATCH" % tk)
