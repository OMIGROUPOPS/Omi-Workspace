"""
Unified edge calculation — ONE formula for the entire OMI backend.

Edge = |fairProb - bookProb| × 100, always expressed as a logistic
probability difference percentage.

All edge calculations across the codebase MUST use these functions.
No other formula should exist for computing edge percentages.
"""
import math

# Logistic scaling constants per sport: k = linear_rate * 4.
# Calibrated so slope at spread=0 matches the empirical rates.
SPREAD_TO_PROB_K = {
    "basketball_nba": 0.132,
    "basketball_ncaab": 0.120,
    "americanfootball_nfl": 0.108,
    "americanfootball_ncaaf": 0.108,
    "icehockey_nhl": 0.320,
    "baseball_mlb": 0.360,
    "soccer_epl": 0.800,
    "soccer_usa_mls": 0.800,
    "soccer_spain_la_liga": 0.800,
    "soccer_italy_serie_a": 0.800,
    "soccer_germany_bundesliga": 0.800,
    "soccer_france_ligue_one": 0.800,
    "soccer_uefa_champs_league": 0.800,
}


def spread_to_win_prob(spread: float, sport_key: str) -> float:
    """Logistic spread-to-probability: P(win) = 1 / (1 + exp(spread * k)).
    Negative spread = favorite → probability > 0.50."""
    k = SPREAD_TO_PROB_K.get(sport_key, 0.120)
    return 1.0 / (1.0 + math.exp(spread * k))


def american_to_prob(odds: float) -> float:
    """Convert American odds to implied probability (0-1).
    -120 → 0.5455, +150 → 0.4000"""
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    return 100.0 / (odds + 100)


def calculate_edge(
    book_value: float,
    fair_value: float,
    market_type: str,
    sport_key: str,
) -> float:
    """Unified edge calculation — ONE formula for the entire backend.

    Spread: both sides through logistic, diff in probability.
    Total:  difference (bookTotal - fairTotal) through logistic vs 0.50.
    ML:     fairSpread through logistic vs book ML through american_to_prob.

    Returns edge as a percentage (e.g. 1.5 for 1.5%).
    """
    if market_type in ("ml", "moneyline", "h2h"):
        # fair_value = fair spread, book_value = book American ML odds
        fair_prob = spread_to_win_prob(fair_value, sport_key)
        book_prob = american_to_prob(book_value)
        return abs(fair_prob - book_prob) * 100

    if market_type in ("total", "totals"):
        # Treat the total difference as a "spread" — book total implies 50/50
        diff = book_value - fair_value  # positive = book higher than fair
        over_prob = spread_to_win_prob(diff, sport_key)
        return abs(over_prob - 0.50) * 100

    # Spread: logistic probability difference
    book_prob = spread_to_win_prob(float(book_value), sport_key)
    fair_prob = spread_to_win_prob(float(fair_value), sport_key)
    return abs(fair_prob - book_prob) * 100


def calculate_max_edge(
    fair_spread, book_spread,
    fair_total, book_total,
    sport_key: str,
) -> float:
    """Calculate max edge % across spread and total markets.
    Uses logistic probability differences for both."""
    max_edge = 0.0

    if fair_spread is not None and book_spread is not None:
        edge = calculate_edge(float(book_spread), float(fair_spread), "spread", sport_key)
        max_edge = max(max_edge, edge)

    if fair_total is not None and book_total is not None:
        edge = calculate_edge(float(book_total), float(fair_total), "total", sport_key)
        max_edge = max(max_edge, edge)

    return round(max_edge, 2)
