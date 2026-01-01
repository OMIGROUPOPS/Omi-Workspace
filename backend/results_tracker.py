"""
OMI Edge - Results Tracking & Grading System
Tracks predictions vs actual results for accountability
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional
import httpx
from supabase import create_client, Client

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# Sport key mapping
ODDS_API_SPORTS = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba", 
    "NHL": "icehockey_nhl",
    "NCAAF": "americanfootball_ncaaf",
    "NCAAB": "basketball_ncaab",
}

class ResultsTracker:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase credentials")
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def snapshot_prediction_at_close(self, game_id: str, sport: str) -> Optional[dict]:
        """
        Capture our prediction right before game starts.
        Call this ~30 min before game time.
        """
        # Get the prediction
        result = self.client.table("predictions").select("*").eq(
            "game_id", game_id
        ).eq("sport_key", sport).single().execute()
        
        if not result.data:
            print(f"[Results] No prediction found for {game_id}")
            return None
        
        pred = result.data
        edges = pred.get("edges_json", {}) or {}
        pillars = pred.get("pillars_json", {}) or {}
        consensus = pred.get("consensus_odds_json", {}) or {}
        
        # Get closing lines
        closing_spread = consensus.get("spreads", {}).get("home", {}).get("line")
        closing_spread_odds = consensus.get("spreads", {}).get("home", {}).get("odds")
        closing_ml_home = consensus.get("h2h", {}).get("home")
        closing_ml_away = consensus.get("h2h", {}).get("away")
        closing_total = consensus.get("totals", {}).get("over", {}).get("line")
        closing_total_odds = consensus.get("totals", {}).get("over", {}).get("odds")
        
        # Build the record
        record = {
            "game_id": game_id,
            "sport_key": sport,
            "home_team": pred.get("home_team"),
            "away_team": pred.get("away_team"),
            "commence_time": pred.get("commence_time"),
            
            # Closing lines
            "closing_spread_home": closing_spread,
            "closing_spread_odds": closing_spread_odds,
            "closing_ml_home": closing_ml_home,
            "closing_ml_away": closing_ml_away,
            "closing_total_line": closing_total,
            "closing_total_over_odds": closing_total_odds,
            
            # Our edges
            "our_edge_spread_home": edges.get("spread_home", {}).get("edge_pct", 0),
            "our_edge_spread_away": edges.get("spread_away", {}).get("edge_pct", 0),
            "our_edge_ml_home": edges.get("ml_home", {}).get("edge_pct", 0),
            "our_edge_ml_away": edges.get("ml_away", {}).get("edge_pct", 0),
            "our_edge_total_over": edges.get("total_over", {}).get("edge_pct", 0),
            "our_edge_total_under": edges.get("total_under", {}).get("edge_pct", 0),
            
            # Composite
            "composite_score": pred.get("composite_score"),
            "confidence_level": pred.get("overall_confidence"),
            
            # Pillars
            "pillar_execution": pred.get("pillar_execution"),
            "pillar_incentives": pred.get("pillar_incentives"),
            "pillar_shocks": pred.get("pillar_shocks"),
            "pillar_time_decay": pred.get("pillar_time_decay"),
            "pillar_flow": pred.get("pillar_flow"),
            
            # Best bet
            "best_bet_market": pred.get("best_bet_market"),
            "best_bet_edge": pred.get("best_edge_pct"),
        }
        
        # Upsert to game_results
        self.client.table("game_results").upsert(record).execute()
        print(f"[Results] Snapshotted prediction for {game_id}")
        return record
    
    def grade_game(self, game_id: str, home_score: int, away_score: int) -> Optional[dict]:
        """
        Grade a completed game against our predictions.
        """
        # Get the game result record
        result = self.client.table("game_results").select("*").eq(
            "game_id", game_id
        ).single().execute()
        
        if not result.data:
            print(f"[Results] No result record for {game_id}, creating one...")
            # Try to create from predictions
            pred_result = self.client.table("predictions").select("*").eq(
                "game_id", game_id
            ).single().execute()
            
            if pred_result.data:
                self.snapshot_prediction_at_close(game_id, pred_result.data.get("sport_key", ""))
                result = self.client.table("game_results").select("*").eq(
                    "game_id", game_id
                ).single().execute()
        
        if not result.data:
            print(f"[Results] Could not find or create record for {game_id}")
            return None
        
        record = result.data
        
        # Calculate actuals
        final_spread = home_score - away_score  # positive = home won by X
        final_total = home_score + away_score
        winner = "home" if home_score > away_score else ("away" if away_score > home_score else "push")
        
        # Grade spread
        spread_result = None
        if record.get("closing_spread_home") is not None:
            spread_line = record["closing_spread_home"]
            # If we had edge on home spread
            if record.get("our_edge_spread_home", 0) > 0:
                # Home needs to cover (actual spread > line means home covered)
                if final_spread > spread_line:
                    spread_result = "win"
                elif final_spread < spread_line:
                    spread_result = "loss"
                else:
                    spread_result = "push"
            # If we had edge on away spread
            elif record.get("our_edge_spread_away", 0) > 0:
                if final_spread < spread_line:
                    spread_result = "win"
                elif final_spread > spread_line:
                    spread_result = "loss"
                else:
                    spread_result = "push"
        
        # Grade moneyline
        ml_result = None
        if record.get("our_edge_ml_home", 0) > 0:
            ml_result = "win" if winner == "home" else ("push" if winner == "push" else "loss")
        elif record.get("our_edge_ml_away", 0) > 0:
            ml_result = "win" if winner == "away" else ("push" if winner == "push" else "loss")
        
        # Grade total
        total_result = None
        if record.get("closing_total_line") is not None:
            total_line = record["closing_total_line"]
            if record.get("our_edge_total_over", 0) > 0:
                if final_total > total_line:
                    total_result = "win"
                elif final_total < total_line:
                    total_result = "loss"
                else:
                    total_result = "push"
            elif record.get("our_edge_total_under", 0) > 0:
                if final_total < total_line:
                    total_result = "win"
                elif final_total > total_line:
                    total_result = "loss"
                else:
                    total_result = "push"
        
        # Grade best bet
        best_bet_result = None
        best_bet_market = record.get("best_bet_market")
        if best_bet_market:
            if "spread_home" in best_bet_market:
                best_bet_result = "win" if final_spread > record.get("closing_spread_home", 0) else "loss"
            elif "spread_away" in best_bet_market:
                best_bet_result = "win" if final_spread < record.get("closing_spread_home", 0) else "loss"
            elif "ml_home" in best_bet_market:
                best_bet_result = "win" if winner == "home" else "loss"
            elif "ml_away" in best_bet_market:
                best_bet_result = "win" if winner == "away" else "loss"
            elif "total_over" in best_bet_market:
                best_bet_result = "win" if final_total > record.get("closing_total_line", 0) else "loss"
            elif "total_under" in best_bet_market:
                best_bet_result = "win" if final_total < record.get("closing_total_line", 0) else "loss"
            
            # Handle pushes
            if best_bet_market and "spread" in best_bet_market:
                if final_spread == record.get("closing_spread_home"):
                    best_bet_result = "push"
            if best_bet_market and "total" in best_bet_market:
                if final_total == record.get("closing_total_line"):
                    best_bet_result = "push"
        
        # Update record
        update = {
            "home_score": home_score,
            "away_score": away_score,
            "final_spread": final_spread,
            "final_total": final_total,
            "winner": winner,
            "spread_result": spread_result,
            "ml_result": ml_result,
            "total_result": total_result,
            "best_bet_result": best_bet_result,
            "graded_at": datetime.now(timezone.utc).isoformat(),
        }
        
        self.client.table("game_results").update(update).eq("game_id", game_id).execute()
        print(f"[Results] Graded {game_id}: spread={spread_result}, ml={ml_result}, total={total_result}, best={best_bet_result}")
        
        return {**record, **update}
    
    def get_recent_results(self, limit: int = 50, sport: Optional[str] = None) -> list:
        """Get recent graded games."""
        query = self.client.table("game_results").select("*").not_.is_("graded_at", "null")
        
        if sport:
            query = query.eq("sport_key", sport)
        
        result = query.order("commence_time", desc=True).limit(limit).execute()
        return result.data or []
    
    def get_performance_summary(self, sport: Optional[str] = None, days: int = 30) -> dict:
        """Get performance summary stats."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        query = self.client.table("game_results").select("*").not_.is_(
            "graded_at", "null"
        ).gte("commence_time", cutoff)
        
        if sport:
            query = query.eq("sport_key", sport)
        
        result = query.execute()
        games = result.data or []
        
        if not games:
            return {
                "total_games": 0,
                "best_bet_record": "0-0-0",
                "best_bet_win_pct": 0,
                "spread_record": "0-0-0",
                "ml_record": "0-0-0",
                "total_record": "0-0-0",
                "by_confidence": {},
                "by_sport": {},
            }
        
        # Calculate records
        def calc_record(results: list, key: str) -> tuple:
            wins = sum(1 for g in results if g.get(key) == "win")
            losses = sum(1 for g in results if g.get(key) == "loss")
            pushes = sum(1 for g in results if g.get(key) == "push")
            return wins, losses, pushes
        
        bb_w, bb_l, bb_p = calc_record(games, "best_bet_result")
        sp_w, sp_l, sp_p = calc_record(games, "spread_result")
        ml_w, ml_l, ml_p = calc_record(games, "ml_result")
        to_w, to_l, to_p = calc_record(games, "total_result")
        
        # By confidence
        by_confidence = {}
        for conf in ["STRONG_EDGE", "EDGE", "WATCH", "PASS"]:
            conf_games = [g for g in games if g.get("confidence_level") == conf]
            w, l, p = calc_record(conf_games, "best_bet_result")
            by_confidence[conf] = {
                "record": f"{w}-{l}-{p}",
                "win_pct": round(w / (w + l) * 100, 1) if (w + l) > 0 else 0,
                "games": len(conf_games),
            }
        
        # By sport
        by_sport = {}
        for sport_key in set(g.get("sport_key") for g in games):
            sport_games = [g for g in games if g.get("sport_key") == sport_key]
            w, l, p = calc_record(sport_games, "best_bet_result")
            by_sport[sport_key] = {
                "record": f"{w}-{l}-{p}",
                "win_pct": round(w / (w + l) * 100, 1) if (w + l) > 0 else 0,
                "games": len(sport_games),
            }
        
        return {
            "total_games": len(games),
            "period_days": days,
            "best_bet_record": f"{bb_w}-{bb_l}-{bb_p}",
            "best_bet_win_pct": round(bb_w / (bb_w + bb_l) * 100, 1) if (bb_w + bb_l) > 0 else 0,
            "spread_record": f"{sp_w}-{sp_l}-{sp_p}",
            "ml_record": f"{ml_w}-{ml_l}-{ml_p}",
            "total_record": f"{to_w}-{to_l}-{to_p}",
            "by_confidence": by_confidence,
            "by_sport": by_sport,
        }
    
    def get_price_movement(self, game_id: str, market_type: str = "spread", book: str = "fanduel") -> dict:
        """
        Get price movement for a specific market.
        Returns opening price, current price, and % change.
        """
        result = self.client.table("line_snapshots").select("*").eq(
            "game_id", game_id
        ).eq("market_type", market_type).eq("book_key", book).order(
            "snapshot_time", desc=False
        ).execute()
        
        snapshots = result.data or []
        
        if len(snapshots) < 1:
            return {
                "has_data": False,
                "opening_odds": None,
                "current_odds": None,
                "odds_change_pct": 0,
                "opening_line": None,
                "current_line": None,
                "line_movement": 0,
                "snapshots": 0,
            }
        
        opening = snapshots[0]
        current = snapshots[-1]
        
        opening_odds = opening.get("odds", -110)
        current_odds = current.get("odds", -110)
        
        # Calculate odds change as "value" change
        # More negative = worse for bettor, more positive = better
        # -110 to -115 = worse (negative change)
        # -110 to -105 = better (positive change)
        # +100 to +110 = better (positive change)
        
        def odds_to_implied(odds: int) -> float:
            if odds < 0:
                return abs(odds) / (abs(odds) + 100)
            return 100 / (odds + 100)
        
        opening_implied = odds_to_implied(opening_odds)
        current_implied = odds_to_implied(current_odds)
        
        # Positive = better value (implied prob went down)
        # Negative = worse value (implied prob went up)
        odds_change_pct = (opening_implied - current_implied) * 100
        
        return {
            "has_data": True,
            "opening_odds": opening_odds,
            "current_odds": current_odds,
            "odds_change_pct": round(odds_change_pct, 2),
            "opening_line": opening.get("line"),
            "current_line": current.get("line"),
            "line_movement": (current.get("line") or 0) - (opening.get("line") or 0),
            "snapshots": len(snapshots),
            "first_snapshot": opening.get("snapshot_time"),
            "last_snapshot": current.get("snapshot_time"),
        }


# API endpoints to add to server.py
"""
Add these endpoints to backend/api/server.py:

@app.post("/api/results/snapshot/{sport}/{game_id}")
async def snapshot_prediction(sport: str, game_id: str):
    tracker = ResultsTracker()
    result = tracker.snapshot_prediction_at_close(game_id, sport)
    return {"status": "ok", "data": result}

@app.post("/api/results/grade/{game_id}")
async def grade_game(game_id: str, home_score: int, away_score: int):
    tracker = ResultsTracker()
    result = tracker.grade_game(game_id, home_score, away_score)
    return {"status": "ok", "data": result}

@app.get("/api/results/recent")
async def get_recent_results(limit: int = 50, sport: str = None):
    tracker = ResultsTracker()
    results = tracker.get_recent_results(limit, sport)
    return {"results": results, "count": len(results)}

@app.get("/api/results/summary")
async def get_performance_summary(sport: str = None, days: int = 30):
    tracker = ResultsTracker()
    summary = tracker.get_performance_summary(sport, days)
    return summary

@app.get("/api/results/price-movement/{game_id}")
async def get_price_movement(game_id: str, market: str = "spread", book: str = "fanduel"):
    tracker = ResultsTracker()
    movement = tracker.get_price_movement(game_id, market, book)
    return movement
"""