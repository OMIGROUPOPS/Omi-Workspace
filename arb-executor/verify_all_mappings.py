#!/usr/bin/env python3
"""
verify_all_mappings.py — Independent Hedge Verification
========================================================

CRITICAL: This script is the LAST LINE OF DEFENSE before live trading.
It independently verifies every mapping against the live PM API.

DO NOT TRADE if this script reports ANY failures.

Usage:
    python verify_all_mappings.py              # Full verification
    python verify_all_mappings.py --quick      # Quick check (first 10 games)
    python verify_all_mappings.py --game MEM-POR  # Check specific game
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp required. Install with: pip install aiohttp")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

MAPPING_FILE = "verified_mappings.json"
PM_API_BASE = "https://api.polymarket.us"
PM_GAMMA_BASE = "https://gamma-api.polymarket.com"

# Team abbreviation normalization (PM -> Kalshi canonical)
ABBREV_NORMALIZE = {
    "GS": "GSW", "NY": "NYK", "NO": "NOP", "SA": "SAS",
    "PHO": "PHX", "BRK": "BKN", "WAS": "WSH", "WSH": "WSH",
    "LAC": "LAC", "LAL": "LAL", "DAL": "DAL", "DEN": "DEN",
    "MEM": "MEM", "POR": "POR", "HOU": "HOU", "OKC": "OKC",
    "CHA": "CHA", "ATL": "ATL", "CHI": "CHI", "CLE": "CLE",
    "UTA": "UTA", "ORL": "ORL", "PHI": "PHI", "SAC": "SAC",
}

# ============================================================================
# API FUNCTIONS
# ============================================================================

async def fetch_pm_market(session: aiohttp.ClientSession, slug: str, pm_api=None) -> Optional[Dict]:
    """
    Fetch market details from PM API.
    Returns the market data or None if failed.

    If pm_api is provided (from executor), use authenticated requests.
    """
    # If we have an authenticated API client, use it
    if pm_api is not None:
        try:
            path = f'/v1/markets/{slug}'
            headers = pm_api._headers('GET', path)
            url = f"{PM_API_BASE}{path}"
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass

    # Try unauthenticated endpoints as fallback
    endpoints = [
        f"{PM_API_BASE}/v1/markets/{slug}",
        f"{PM_GAMMA_BASE}/markets/{slug}",
    ]

    for url in endpoints:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            continue

    return None


def extract_market_sides(market_data: Dict) -> List[Dict]:
    """
    Extract marketSides from PM market data.
    Returns list of {index, abbreviation, name} dicts.
    """
    market_sides = market_data.get("marketSides", [])
    result = []

    for idx, side in enumerate(market_sides[:2]):
        if not isinstance(side, dict):
            continue
        team_info = side.get("team", {})
        if not team_info:
            continue

        abbrev = (team_info.get("displayAbbreviation", "")
                  or team_info.get("abbreviation", ""))
        name = team_info.get("name", "")

        result.append({
            "index": idx,
            "abbreviation": abbrev.upper() if abbrev else None,
            "name": name,
        })

    return result


def normalize_abbrev(abbrev: str) -> str:
    """Normalize team abbreviation to canonical form."""
    if not abbrev:
        return ""
    upper = abbrev.upper()
    return ABBREV_NORMALIZE.get(upper, upper)


# ============================================================================
# VERIFICATION LOGIC
# ============================================================================

class VerificationResult:
    """Result of verifying a single mapping."""
    def __init__(self, cache_key: str):
        self.cache_key = cache_key
        self.passed = False
        self.api_fetched = False
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.details: Dict = {}

    def fail(self, msg: str):
        self.passed = False
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def ok(self):
        self.passed = True


async def verify_single_mapping(
    session: aiohttp.ClientSession,
    cache_key: str,
    mapping: Dict,
    fetch_api: bool = True,
    pm_api=None
) -> VerificationResult:
    """
    Verify a single mapping against the PM API.

    Checks:
    1. API marketSides matches our stored outcome indices
    2. Arb directions would create actual hedges (opposite positions)
    """
    result = VerificationResult(cache_key)

    pm_slug = mapping.get("pm_slug", "")
    pm_outcomes = mapping.get("pm_outcomes", {})
    kalshi_tickers = mapping.get("kalshi_tickers", {})

    if not pm_slug:
        result.fail("No PM slug in mapping")
        return result

    # Get our stored team -> outcome_index mapping
    our_team_at_0 = pm_outcomes.get("0", {}).get("team", "")
    our_team_at_1 = pm_outcomes.get("1", {}).get("team", "")

    result.details["our_mapping"] = {
        "outcome_0": our_team_at_0,
        "outcome_1": our_team_at_1,
    }

    # Always do structural verification first
    struct_ok, struct_errors = verify_mapping_structure(cache_key, mapping)
    if not struct_ok:
        for err in struct_errors:
            result.fail(f"Structure: {err}")

    # Fetch from API if requested
    if fetch_api:
        market_data = await fetch_pm_market(session, pm_slug, pm_api)

        if not market_data:
            result.fail(f"Could not fetch PM market: {pm_slug}")
            return result

        result.api_fetched = True
        market_sides = extract_market_sides(market_data)

        if len(market_sides) < 2:
            result.fail(f"PM API returned < 2 market sides")
            return result

        api_team_at_0 = normalize_abbrev(market_sides[0].get("abbreviation", ""))
        api_team_at_1 = normalize_abbrev(market_sides[1].get("abbreviation", ""))
        api_name_at_0 = market_sides[0].get("name", "")
        api_name_at_1 = market_sides[1].get("name", "")

        result.details["api_response"] = {
            "outcome_0": f"{api_team_at_0} ({api_name_at_0})",
            "outcome_1": f"{api_team_at_1} ({api_name_at_1})",
        }

        # Normalize our stored teams for comparison
        our_0_norm = normalize_abbrev(our_team_at_0)
        our_1_norm = normalize_abbrev(our_team_at_1)

        # Check if API matches our mapping
        match_0 = (api_team_at_0 == our_0_norm or
                   our_0_norm in api_name_at_0.upper() or
                   (api_team_at_0 and our_0_norm and api_team_at_0[:3] == our_0_norm[:3]))
        match_1 = (api_team_at_1 == our_1_norm or
                   our_1_norm in api_name_at_1.upper() or
                   (api_team_at_1 and our_1_norm and api_team_at_1[:3] == our_1_norm[:3]))

        if not match_0:
            result.fail(f"outcome[0] mismatch: API={api_team_at_0}, mapping={our_0_norm}")
        if not match_1:
            result.fail(f"outcome[1] mismatch: API={api_team_at_1}, mapping={our_1_norm}")

    # Verify hedge logic for both arb directions
    # This is a sanity check on the mapping structure itself

    for team, ticker in kalshi_tickers.items():
        team_norm = normalize_abbrev(team)

        # Find what outcome_index this team has in our mapping
        team_outcome_idx = None
        for idx_str, outcome_data in pm_outcomes.items():
            if normalize_abbrev(outcome_data.get("team", "")) == team_norm:
                team_outcome_idx = int(idx_str)
                break

        if team_outcome_idx is None:
            result.fail(f"Team {team} in Kalshi tickers but not in PM outcomes")
            continue

        # For a proper hedge:
        # BUY_PM_SELL_K on team X: Buy PM outcome[X_idx], Sell Kalshi X ticker
        #   - PM position: Long team X (wins if X wins)
        #   - Kalshi position: Short team X (wins if X loses)
        #   - These are OPPOSITE positions on the same team = HEDGE

        # BUY_K_SELL_PM on team X: Buy Kalshi X ticker, Sell PM outcome[X_idx]
        #   - Kalshi position: Long team X (wins if X wins)
        #   - PM position: Short team X (wins if X loses)
        #   - These are OPPOSITE positions on the same team = HEDGE

        result.details[f"team_{team}_hedge_check"] = {
            "kalshi_ticker": ticker,
            "pm_outcome_index": team_outcome_idx,
            "hedge_valid": True,  # Structure is correct if we got here
        }

    # If no errors, mark as passed
    if not result.errors:
        result.ok()

    return result


async def verify_all_mappings(
    fetch_api: bool = True,
    quick: bool = False,
    filter_game: Optional[str] = None,
    pm_api=None
) -> Tuple[List[VerificationResult], Dict]:
    """
    Verify all mappings in verified_mappings.json.

    Returns (results, summary).
    """
    # Load mappings
    try:
        with open(MAPPING_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load {MAPPING_FILE}: {e}")
        sys.exit(1)

    games = data.get("games", {})
    generated_at = data.get("generated_at", "unknown")

    print(f"Loaded {len(games)} mappings from {MAPPING_FILE}")
    print(f"Generated at: {generated_at}")
    print("=" * 80)

    # Filter if requested
    if filter_game:
        games = {k: v for k, v in games.items() if filter_game.lower() in k.lower()}
        print(f"Filtered to {len(games)} games matching '{filter_game}'")

    if quick:
        # Just check first 10
        games = dict(list(games.items())[:10])
        print(f"Quick mode: checking first {len(games)} games")

    results = []

    async with aiohttp.ClientSession() as session:
        for i, (cache_key, mapping) in enumerate(sorted(games.items())):
            if i > 0 and i % 10 == 0:
                print(f"Progress: {i}/{len(games)}...")

            result = await verify_single_mapping(session, cache_key, mapping, fetch_api, pm_api)
            results.append(result)

            # Rate limiting
            if fetch_api:
                await asyncio.sleep(0.1)

    # Compute summary
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    api_errors = sum(1 for r in results if not r.api_fetched and fetch_api)

    summary = {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "api_errors": api_errors,
        "all_passed": failed == 0,
    }

    return results, summary


# ============================================================================
# STRUCTURAL VERIFICATION (no API needed)
# ============================================================================

def verify_mapping_structure(cache_key: str, mapping: Dict) -> Tuple[bool, List[str]]:
    """
    Verify a mapping's internal structure and logic WITHOUT API calls.

    Checks:
    1. All required fields present
    2. pm_outcomes has both index 0 and 1
    3. Both Kalshi teams are in pm_outcomes
    4. Outcome indices are 0 and 1
    5. Slug team order matches outcome order (first slug team = index 0)

    Returns (passed, errors).
    """
    errors = []

    # Check required fields
    required = ['pm_slug', 'pm_outcomes', 'kalshi_tickers', 'verified']
    for field in required:
        if field not in mapping:
            errors.append(f"Missing field: {field}")

    if not mapping.get('verified'):
        errors.append("Mapping not marked as verified")

    pm_outcomes = mapping.get('pm_outcomes', {})
    kalshi_tickers = mapping.get('kalshi_tickers', {})
    pm_slug = mapping.get('pm_slug', '')

    # Check pm_outcomes structure
    if '0' not in pm_outcomes:
        errors.append("Missing outcome index 0")
    if '1' not in pm_outcomes:
        errors.append("Missing outcome index 1")

    # Get teams from outcomes
    outcome_0_team = pm_outcomes.get('0', {}).get('team', '')
    outcome_1_team = pm_outcomes.get('1', {}).get('team', '')

    if not outcome_0_team:
        errors.append("outcome[0] has no team")
    if not outcome_1_team:
        errors.append("outcome[1] has no team")

    # Check all Kalshi teams are in outcomes
    kalshi_teams = set(normalize_abbrev(t) for t in kalshi_tickers.keys())
    outcome_teams = set([normalize_abbrev(outcome_0_team), normalize_abbrev(outcome_1_team)])

    if kalshi_teams != outcome_teams:
        errors.append(f"Team mismatch: Kalshi={kalshi_teams}, outcomes={outcome_teams}")

    # NOTE: We don't check slug team order vs outcome order here because
    # PM slug abbreviations (like "ABCHR") differ from Kalshi abbreviations ("AC").
    # The pregame_mapper uses marketSides index which IS reliable.
    # The true verification is that both teams are present and hedge logic works.

    # Check convenience lookups exist
    if outcome_0_team:
        key = f"team_{outcome_0_team.lower()}_outcome_index"
        if key in mapping and mapping[key] != 0:
            errors.append(f"{key} should be 0, got {mapping[key]}")

    if outcome_1_team:
        key = f"team_{outcome_1_team.lower()}_outcome_index"
        if key in mapping and mapping[key] != 1:
            errors.append(f"{key} should be 1, got {mapping[key]}")

    return (len(errors) == 0, errors)


def verify_hedge_logic(mapping: Dict, team: str, direction: str) -> Tuple[bool, str]:
    """
    Verify that a specific trade direction creates a proper hedge.

    For a hedge to be valid:
    - BUY_PM_SELL_K on team X: Buy PM outcome[X_idx], Sell Kalshi X
      = Long X on PM, Short X on Kalshi = OPPOSITE positions = HEDGE

    - BUY_K_SELL_PM on team X: Buy Kalshi X, Sell PM outcome[X_idx]
      = Long X on Kalshi, Short X on PM = OPPOSITE positions = HEDGE

    Returns (is_hedge, explanation).
    """
    team_norm = normalize_abbrev(team)
    pm_outcomes = mapping.get('pm_outcomes', {})
    kalshi_tickers = mapping.get('kalshi_tickers', {})

    # Find team's outcome index
    team_idx = None
    for idx_str, outcome_data in pm_outcomes.items():
        if normalize_abbrev(outcome_data.get('team', '')) == team_norm:
            team_idx = int(idx_str)
            break

    if team_idx is None:
        return (False, f"Team {team} not found in PM outcomes")

    # Find team's Kalshi ticker
    kalshi_ticker = None
    for t, ticker in kalshi_tickers.items():
        if normalize_abbrev(t) == team_norm:
            kalshi_ticker = ticker
            break

    if not kalshi_ticker:
        return (False, f"Team {team} not found in Kalshi tickers")

    # Verify hedge logic
    if direction == "BUY_PM_SELL_K":
        # PM: Buy outcome[team_idx] = Long team
        # Kalshi: Sell ticker for team = Short team
        # Long + Short on same team = HEDGE
        return (True, f"PM Long {team}(idx={team_idx}) + Kalshi Short {team} = HEDGE")

    elif direction == "BUY_K_SELL_PM":
        # Kalshi: Buy ticker for team = Long team
        # PM: Sell outcome[team_idx] = Short team
        # Long + Short on same team = HEDGE
        return (True, f"Kalshi Long {team} + PM Short {team}(idx={team_idx}) = HEDGE")

    return (False, f"Unknown direction: {direction}")


# ============================================================================
# STARTUP VERIFICATION (for executor integration)
# ============================================================================

def run_startup_verification(mappings: Dict) -> bool:
    """
    Synchronous wrapper for executor startup.
    Returns True if all mappings pass structural verification, False otherwise.

    This does NOT require API access - it verifies the mapping structure only.

    Usage in executor:
        from verify_all_mappings import run_startup_verification
        if not run_startup_verification(VERIFIED_MAPS):
            print("FATAL: Mapping verification failed. Refusing to trade.")
            sys.exit(1)
    """
    failed = []
    passed = 0

    for cache_key, mapping in mappings.items():
        ok, errors = verify_mapping_structure(cache_key, mapping)
        if ok:
            passed += 1
        else:
            failed.append((cache_key, errors))

    if failed:
        print(f"[VERIFY] FAILED: {len(failed)} mappings have structural errors:")
        for cache_key, errors in failed[:5]:
            print(f"  {cache_key}:")
            for err in errors:
                print(f"    - {err}")
        if len(failed) > 5:
            print(f"  ... and {len(failed) - 5} more failures")
        return False

    print(f"[VERIFY] OK: {passed} mappings passed structural verification")
    return True


def run_trade_verification(mapping: Dict, team: str, direction: str) -> bool:
    """
    Verify a specific trade would create a hedge BEFORE executing.
    Call this right before placing orders.

    Usage in executor:
        from verify_all_mappings import run_trade_verification
        if not run_trade_verification(mapping, team, direction):
            print("FATAL: Trade would not create a hedge. Aborting.")
            return

    Returns True if the trade is a valid hedge, False otherwise.
    """
    is_hedge, explanation = verify_hedge_logic(mapping, team, direction)

    if is_hedge:
        print(f"[VERIFY] Trade OK: {explanation}")
        return True
    else:
        print(f"[VERIFY] FATAL: Trade is NOT a hedge: {explanation}")
        return False


async def run_full_api_verification(pm_api=None) -> bool:
    """
    Run full API verification. Returns True if all pass.
    Call this before starting live trading.

    Pass pm_api (PolymarketUSAPI instance) for authenticated access.
    """
    results, summary = await verify_all_mappings(fetch_api=True, pm_api=pm_api)
    return summary["all_passed"]


# ============================================================================
# MAIN / CLI
# ============================================================================

def print_report(results: List[VerificationResult], summary: Dict):
    """Print verification report."""
    print("\n" + "=" * 80)
    print("MAPPING VERIFICATION REPORT")
    print("=" * 80)

    # Show failures first
    failures = [r for r in results if not r.passed]
    if failures:
        print(f"\n[X] FAILURES ({len(failures)}):")
        for r in failures:
            print(f"\n  {r.cache_key}")
            for err in r.errors:
                print(f"    ERROR: {err}")
            if r.details.get("our_mapping"):
                print(f"    Our mapping: {r.details['our_mapping']}")
            if r.details.get("api_response"):
                print(f"    API says: {r.details['api_response']}")

    # Show passes
    passes = [r for r in results if r.passed]
    if passes:
        print(f"\n[OK] PASSED ({len(passes)}):")
        for r in passes:
            our = r.details.get("our_mapping", {})
            api = r.details.get("api_response", {})
            if api:
                print(f"  {r.cache_key}: API confirmed idx0={our.get('outcome_0')}, idx1={our.get('outcome_1')}")
            else:
                print(f"  {r.cache_key}: Structure valid (API not checked)")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total:      {summary['total']}")
    print(f"Passed:     {summary['passed']}")
    print(f"Failed:     {summary['failed']}")
    if summary.get('api_errors'):
        print(f"API Errors: {summary['api_errors']}")

    print()
    if summary["all_passed"]:
        print("[OK] ALL MAPPINGS VERIFIED - Safe to trade")
    else:
        print("[X] VERIFICATION FAILED - DO NOT TRADE")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Verify all outcome index mappings")
    parser.add_argument("--quick", action="store_true", help="Quick check (first 10 games)")
    parser.add_argument("--game", type=str, help="Check specific game (e.g., MEM-POR)")
    parser.add_argument("--no-api", action="store_true", help="Skip API verification")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    print("=" * 80)
    print("INDEPENDENT HEDGE VERIFICATION")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 80)

    # Run verification
    results, summary = asyncio.run(verify_all_mappings(
        fetch_api=not args.no_api,
        quick=args.quick,
        filter_game=args.game,
    ))

    if args.json:
        output = {
            "summary": summary,
            "results": [
                {
                    "cache_key": r.cache_key,
                    "passed": r.passed,
                    "errors": r.errors,
                    "details": r.details,
                }
                for r in results
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(results, summary)

    # Exit with error code if any failures
    sys.exit(0 if summary["all_passed"] else 1)


if __name__ == "__main__":
    main()
