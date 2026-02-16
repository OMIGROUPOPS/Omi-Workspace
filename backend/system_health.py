"""
System Health Monitor

Checks the health of all OMI backend subsystems:
- exchange_sync: Kalshi/Polymarket data freshness
- pillar_health: Are pillars producing non-neutral scores?
- odds_polling: cached_odds freshness
- grading_pipeline: prediction_grades being created
- pregame_capture: pregame_snapshots freshness
- composite_recalc: composite_history freshness
- closing_line_capture: closing_lines freshness

Status levels: OK, WARNING, CRITICAL
"""

import logging
from datetime import datetime, timezone, timedelta

from database import db

logger = logging.getLogger(__name__)

# Freshness thresholds (minutes)
THRESHOLDS = {
    "exchange_sync": {"warning": 30, "critical": 60},
    "odds_polling": {"warning": 45, "critical": 90},
    "pregame_capture": {"warning": 30, "critical": 60},
    "composite_recalc": {"warning": 45, "critical": 90},
    "closing_line_capture": {"warning": 20, "critical": 45},
    "grading_pipeline": {"warning": 120, "critical": 360},
}

# Pillar neutrality threshold: if this % of scores are 0.50, it's a problem
PILLAR_NEUTRAL_WARNING = 0.50
PILLAR_NEUTRAL_CRITICAL = 0.70


class SystemHealth:
    """Runs health checks across all OMI subsystems."""

    def run_all_checks(self) -> dict:
        """Run all health checks, return full report."""
        now = datetime.now(timezone.utc)
        checks = {}

        checks["exchange_sync"] = self._check_table_freshness(
            "exchange_data", "snapshot_time", THRESHOLDS["exchange_sync"], now
        )
        checks["odds_polling"] = self._check_table_freshness(
            "cached_odds", "updated_at", THRESHOLDS["odds_polling"], now
        )
        checks["pregame_capture"] = self._check_table_freshness(
            "pregame_snapshots", "snapshot_time", THRESHOLDS["pregame_capture"], now
        )
        checks["composite_recalc"] = self._check_table_freshness(
            "composite_history", "timestamp", THRESHOLDS["composite_recalc"], now
        )
        checks["closing_line_capture"] = self._check_table_freshness(
            "closing_lines", "captured_at", THRESHOLDS["closing_line_capture"], now
        )
        checks["grading_pipeline"] = self._check_table_freshness(
            "prediction_grades", "graded_at", THRESHOLDS["grading_pipeline"], now
        )
        checks["pillar_health"] = self._check_pillar_health(now)

        # Overall status = worst of all checks
        statuses = [c["status"] for c in checks.values()]
        if "CRITICAL" in statuses:
            overall = "CRITICAL"
        elif "WARNING" in statuses:
            overall = "WARNING"
        else:
            overall = "OK"

        return {
            "overall_status": overall,
            "timestamp": now.isoformat(),
            "checks": checks,
        }

    def _check_table_freshness(
        self, table: str, time_col: str, thresholds: dict, now: datetime
    ) -> dict:
        """Check how recently a table was updated."""
        try:
            if not db._is_connected():
                return {"status": "CRITICAL", "message": "Database not connected"}

            result = db.client.table(table).select(time_col).order(
                time_col, desc=True
            ).limit(1).execute()

            if not result.data:
                return {
                    "status": "WARNING",
                    "message": f"No rows in {table}",
                    "last_update": None,
                    "age_minutes": None,
                }

            last_ts = result.data[0].get(time_col)
            if not last_ts:
                return {
                    "status": "WARNING",
                    "message": f"Null {time_col} in {table}",
                    "last_update": None,
                    "age_minutes": None,
                }

            last_dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
            age_minutes = (now - last_dt).total_seconds() / 60

            if age_minutes > thresholds["critical"]:
                status = "CRITICAL"
            elif age_minutes > thresholds["warning"]:
                status = "WARNING"
            else:
                status = "OK"

            return {
                "status": status,
                "last_update": last_ts,
                "age_minutes": round(age_minutes, 1),
                "threshold_warning": thresholds["warning"],
                "threshold_critical": thresholds["critical"],
            }

        except Exception as e:
            return {"status": "CRITICAL", "message": f"Error checking {table}: {e}"}

    def _check_pillar_health(self, now: datetime) -> dict:
        """Check if pillars are producing non-neutral scores (not all 0.50)."""
        try:
            if not db._is_connected():
                return {"status": "CRITICAL", "message": "Database not connected"}

            # Look at predictions from the last 24 hours
            cutoff = (now - timedelta(hours=24)).isoformat()
            result = db.client.table("predictions").select(
                "pillar_execution, pillar_incentives, pillar_shocks, "
                "pillar_time_decay, pillar_flow"
            ).gt("updated_at", cutoff).limit(200).execute()

            rows = result.data or []
            if not rows:
                return {
                    "status": "WARNING",
                    "message": "No predictions in last 24h",
                    "sample_size": 0,
                }

            # Count how many pillar values are exactly 0.5 (neutral)
            total_values = 0
            neutral_values = 0
            pillar_cols = [
                "pillar_execution", "pillar_incentives", "pillar_shocks",
                "pillar_time_decay", "pillar_flow",
            ]

            for row in rows:
                for col in pillar_cols:
                    val = row.get(col)
                    if val is not None:
                        total_values += 1
                        if abs(val - 0.5) < 0.005:
                            neutral_values += 1

            if total_values == 0:
                return {
                    "status": "WARNING",
                    "message": "No pillar values found",
                    "sample_size": len(rows),
                }

            neutral_pct = neutral_values / total_values

            if neutral_pct >= PILLAR_NEUTRAL_CRITICAL:
                status = "CRITICAL"
            elif neutral_pct >= PILLAR_NEUTRAL_WARNING:
                status = "WARNING"
            else:
                status = "OK"

            return {
                "status": status,
                "neutral_pct": round(neutral_pct * 100, 1),
                "sample_size": len(rows),
                "total_values": total_values,
                "neutral_values": neutral_values,
            }

        except Exception as e:
            return {"status": "CRITICAL", "message": f"Error checking pillars: {e}"}


def run_health_check() -> dict:
    """Entry point for scheduler. Logs results, returns report."""
    health = SystemHealth()
    report = health.run_all_checks()

    overall = report["overall_status"]
    checks = report["checks"]

    # Log each check
    for name, check in checks.items():
        status = check["status"]
        if status == "CRITICAL":
            logger.error(f"[HealthCheck] CRITICAL: {name} — {check}")
        elif status == "WARNING":
            logger.warning(f"[HealthCheck] WARNING: {name} — {check}")
        else:
            logger.info(f"[HealthCheck] OK: {name}")

    # Log overall
    if overall == "CRITICAL":
        logger.error(f"[HealthCheck] Overall: CRITICAL — check logs above")
    elif overall == "WARNING":
        logger.warning(f"[HealthCheck] Overall: WARNING — some subsystems degraded")
    else:
        logger.info(f"[HealthCheck] Overall: OK — all systems healthy")

    return report
